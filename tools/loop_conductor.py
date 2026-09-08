#!/usr/bin/env python3
"""loop_conductor - the headless research-loop run (v2.3 skeleton).

`docs/self_rebuild_v2.md` sections 4 & 8. Composes the deterministic spine into one
run of the loop:

    pick the increment (under the IDLE-STATE RULE constraint)
      -> ledger task
      -> supervisor dispatches it to a worker            (the generative edge, caller-supplied)
      -> the worker returns a graph patch + gate inputs
      -> validate the patch                              (knowledge_graph.check_patch)
      -> acceptance_gate.check                            (held-out + PACE + process + forecast)
      -> on accept: apply the patch + commit/push         (caller-supplied hooks)
      -> record

Everything model-touching or side-effectful - the worker, the patch apply, the
commit/push - is a caller-supplied callback. The conductor itself is deterministic
pure-stdlib and calls no model and no git.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from task_ledger import Ledger          # noqa: E402
from supervisor import Supervisor       # noqa: E402
import acceptance_gate                  # noqa: E402
try:
    from harness_registry import Registry as _HarnessRegistry  # noqa: E402
except Exception:                       # pragma: no cover - defensive
    _HarnessRegistry = None

# IDLE-STATE RULE (loop_policy.json, run 80): the increment kinds that count as
# "genuine work" when the loop is otherwise idle.
ABC_KINDS = ("deepen", "probe", "consistency")
NON_IDLE_KINDS = ("fold", "build", "fix")
PLATEAU_WINDOW = 3


@dataclass
class RunPlan:
    reason: str
    allowed_kinds: tuple
    must_be_abc: bool = False


@dataclass
class RunRecord:
    run_no: int
    plan: RunPlan
    accepted: bool
    reason: str = ""
    certificate: dict | None = None
    ledger_summary: dict = field(default_factory=dict)


NOVELTY_FLOOR = 0.34   # loop_metrics THRESHOLDS["run_novelty"]


def _corpus_drift(runs_dir=None):
    """Read the run corpus via the janitor and return (idle_streak, novelty_ratio).
    Returns (None, None) if the corpus can't be read - callers fall back to
    `recent_kinds`."""
    try:
        import janitor
        runs = janitor.load_runs(runs_dir) if runs_dir else janitor.load_runs()
        if len(runs) < PLATEAU_WINDOW + 1:
            return None, None
        rep = janitor.drift_report(runs, window=6)
        import re
        idle = re.search(r"idle streak\*\*:\s*(\d+)", rep)
        nov = re.search(r"novelty ratio\*\*:\s*([\d.]+|None)", rep)
        idle_v = int(idle.group(1)) if idle else None
        nov_v = None if (not nov or nov.group(1) == "None") else float(nov.group(1))
        return idle_v, nov_v
    except Exception:
        return None, None


def pick_increment(recent_kinds, *, selftest_green=True, frontier_swept=True,
                   runs_dir=None, use_corpus=True):
    """Deterministic IDLE-STATE gate on what kind of increment this run may be.
    `recent_kinds` = the kinds of the last few runs, newest last. When `use_corpus`
    is set (default) it also consults the janitor's drift report over the real run
    corpus - an idle streak >= PLATEAU_WINDOW OR a novelty ratio below NOVELTY_FLOOR
    forces the (a)/(b)/(c) IDLE-STATE clause even if `recent_kinds` looks active."""
    if not selftest_green:
        return RunPlan("selftest is RED - the only valid increment is a fix", ("fix",))
    if not frontier_swept:
        return RunPlan("literature frontier not swept - fold the next item", ("fold", "build"))

    tail = tuple(recent_kinds[-PLATEAU_WINDOW:])
    idle_tail = len(tail) >= PLATEAU_WINDOW and all(
        k in ("doc", "consistency", "other") for k in tail)

    corpus_idle = corpus_nov = None
    if use_corpus:
        corpus_idle, corpus_nov = _corpus_drift(runs_dir)
    plateau_by_corpus = (
        (corpus_idle is not None and corpus_idle >= PLATEAU_WINDOW)
        or (corpus_nov is not None and corpus_nov < NOVELTY_FLOOR))

    if idle_tail or plateau_by_corpus:
        why = []
        if idle_tail:
            why.append(f"the last {PLATEAU_WINDOW} runs were doc/hygiene")
        if corpus_idle is not None and corpus_idle >= PLATEAU_WINDOW:
            why.append(f"the corpus idle streak is {corpus_idle}")
        if corpus_nov is not None and corpus_nov < NOVELTY_FLOOR:
            why.append(f"the corpus novelty ratio is {corpus_nov} (< {NOVELTY_FLOOR})")
        return RunPlan(
            f"{' and '.join(why)}, and the frontier is swept - the IDLE-STATE RULE "
            f"requires (a) deepen one node via a citation sweep, (b) dry-run a probe, "
            f"or (c) a genuine consistency/adversarial pass",
            ABC_KINDS, must_be_abc=True)
    return RunPlan("normal run - highest-value increment, any kind",
                   ABC_KINDS + NON_IDLE_KINDS + ("doc",))


class Conductor:
    def __init__(self, *, ledger_path, run_worker, apply_patch, commit_push,
                 graph_path=None, choose_increment=pick_increment,
                 gate=None, clock=time.time, task_deadline_secs=1800,
                 harness_registry=None, require_blessed_manifest=True):
        self.ledger_path = Path(ledger_path)
        self.run_worker = run_worker
        self.apply_patch = apply_patch
        self.commit_push = commit_push
        self.graph_path = Path(graph_path) if graph_path else (
            ROOT / "knowledge" / "graph" / "agentic_universe_graph.json")
        self.choose_increment = choose_increment
        self.gate = gate or acceptance_gate.check
        self.clock = clock
        self.task_deadline_secs = task_deadline_secs
        # MLAS coverage-map addition (3): refuse to run if the live harness has
        # drifted from the owner-blessed baseline. Active drift (a baseline exists
        # and the live hash differs) ALWAYS halts. `require_blessed_manifest` only
        # decides the "never blessed" case: True = halt (be explicit, the default),
        # False = allow (bootstrap / tests).
        self.harness_registry = harness_registry or (
            _HarnessRegistry() if _HarnessRegistry else None)
        self.require_blessed_manifest = require_blessed_manifest

    def preflight(self):
        """(ok, reason). Checks the live harness manifest against the blessed
        baseline before any increment runs. Halt-don't-heal: a mismatch returns
        (False, ...) and the caller aborts the run - it never re-blesses."""
        reg = self.harness_registry
        if reg is None:
            return True, "no harness registry available - preflight skipped"
        try:
            drifted, cur, blessed = reg.manifest_drift()
        except Exception as e:                    # pragma: no cover - defensive
            return True, f"manifest_drift raised ({e}) - preflight skipped"
        if drifted is None:
            if self.require_blessed_manifest:
                return (False, f"harness manifest {cur} has never been blessed - "
                               f"run `python tools/harness_registry.py bless` (owner) first")
            return True, f"harness manifest {cur} not blessed (allowed by config)"
        if drifted:
            return (False, f"harness manifest drift: live {cur} != blessed {blessed} - "
                           f"halt. An owner re-blesses after an intended harness edit; "
                           f"the loop never self-heals this.")
        return True, f"harness manifest {cur} matches the blessed baseline"

    def _load_graph(self):
        try:
            return json.loads(self.graph_path.read_text(encoding="utf-8"))
        except Exception:
            return {"nodes": [], "edges": []}

    def conduct(self, run_no, *, recent_kinds=(), selftest_green=True, frontier_swept=True,
                use_corpus=True, runs_dir=None):
        pf_ok, pf_reason = self.preflight()
        if not pf_ok:
            halt_plan = RunPlan(f"preflight halt: {pf_reason}", ())
            return RunRecord(run_no, halt_plan, False,
                             reason=f"preflight halt: {pf_reason}")

        try:
            plan = self.choose_increment(list(recent_kinds), selftest_green=selftest_green,
                                         frontier_swept=frontier_swept,
                                         use_corpus=use_corpus, runs_dir=runs_dir)
        except TypeError:
            # a caller-supplied choose_increment without the corpus kwargs
            plan = self.choose_increment(list(recent_kinds), selftest_green=selftest_green,
                                         frontier_swept=frontier_swept)

        L = Ledger(self.ledger_path)
        tid = L.add(f"run {run_no}: {plan.reason}", meta={"run_no": run_no,
                                                          "allowed_kinds": list(plan.allowed_kinds)})
        sup = Supervisor(L, self.run_worker, task_deadline_secs=self.task_deadline_secs,
                         clock=self.clock)
        sup.run()
        task = L.get(tid)

        if task["status"] != "done":
            return RunRecord(run_no, plan, False,
                             reason=f"worker did not complete (status={task['status']})",
                             ledger_summary=L.summary())

        out = task.get("result_ref")
        if not isinstance(out, dict) or "patch" not in out:
            return RunRecord(run_no, plan, False,
                             reason="worker returned no patch", ledger_summary=L.summary())

        kind = out.get("kind", "other")
        if kind not in plan.allowed_kinds:
            return RunRecord(run_no, plan, False,
                             reason=f"increment kind {kind!r} not allowed this run "
                                    f"({plan.reason})", ledger_summary=L.summary())

        # structural patch check
        try:
            from knowledge_graph import check_patch
            perrs = check_patch(out["patch"], self._load_graph())
        except Exception as e:                       # pragma: no cover - defensive
            perrs = [f"check_patch raised: {e}"]
        if perrs:
            return RunRecord(run_no, plan, False,
                             reason="patch failed check_patch: " + "; ".join(perrs[:3]),
                             ledger_summary=L.summary())

        # the exogenous acceptance gate
        cert = self.gate(out["patch"], out["baseline_scores"], out["candidate_scores"],
                         out["forecast"], repaired=out.get("repaired", False))
        if not cert["decision"].startswith("accept"):
            return RunRecord(run_no, plan, False, reason="acceptance gate rejected",
                             certificate=cert, ledger_summary=L.summary())

        self.apply_patch(out["patch"])
        self.commit_push(run_no, plan, cert)
        return RunRecord(run_no, plan, True,
                         reason=cert["decision"], certificate=cert,
                         ledger_summary=L.summary())


def _selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="conductor-"))
    checks = {}

    def _tmpgate(*a, **k):          # run 368: selftest certs -> tmp, not the production log
        return acceptance_gate.check(*a, cert_dir=tmp, **k)

    graph_path = tmp / "g.json"
    graph_path.write_text(json.dumps({
        "nodes": [{"id": "concept_anchor", "label": "anchor", "type": "concept"}],
        "edges": []}), encoding="utf-8")

    good_patch = {
        "proposal_metadata": {"generated_by": "test"},
        "add_nodes": [{"id": "concept_new", "label": "new", "type": "concept"}],
        "add_edges": [{"id": "e1", "source": "concept_new", "target": "concept_anchor",
                       "type": "supports"}],
    }
    base = {f"t{i}": (1.0 if i < 8 else 0.0) for i in range(17)}
    cand = {f"t{i}": (1.0 if i < 12 else 0.0) for i in range(17)}
    worker_out = {"kind": "fold", "patch": good_patch, "baseline_scores": base,
                  "candidate_scores": cand, "forecast": {"metric": "coverage", "predicted_prob": 0.7},
                  "repaired": False}

    applied, committed = [], []
    def ok_worker(task, *, hints):
        return True, dict(worker_out), "done"
    def apply_patch(p):
        applied.append(p)
    def commit_push(run_no, plan, cert):
        committed.append((run_no, cert["decision"]))

    c = Conductor(require_blessed_manifest=False, gate=_tmpgate, ledger_path=tmp / "led1.json", run_worker=ok_worker, apply_patch=apply_patch,
                  commit_push=commit_push, graph_path=graph_path, clock=lambda: 1000.0)
    rec = c.conduct(400, recent_kinds=["build", "fold", "doc"], frontier_swept=False)
    checks["a clean fold run is accepted, applied and committed"] = (
        rec.accepted and applied and committed == [(400, "accept")])
    checks["the certificate rides on the record"] = rec.certificate["decision"] == "accept"

    # a worker that never completes -> not accepted, nothing applied
    def dead_worker(task, *, hints):
        return False, None, "worker crashed"
    applied.clear()
    c2 = Conductor(require_blessed_manifest=False, gate=_tmpgate, ledger_path=tmp / "led2.json", run_worker=dead_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 2000.0)
    rec2 = c2.conduct(401, recent_kinds=["fold", "fold", "fold"], frontier_swept=False)
    checks["a failed worker yields an unaccepted record"] = (not rec2.accepted and not applied)
    checks["a failed run names the worker status"] = "did not complete" in rec2.reason

    # IDLE-STATE: three doc runs + swept frontier -> only a/b/c allowed; a 'fold' is refused
    def fold_worker(task, *, hints):
        return True, {**worker_out, "kind": "fold"}, "done"
    c3 = Conductor(require_blessed_manifest=False, gate=_tmpgate, ledger_path=tmp / "led3.json", run_worker=fold_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 3000.0)
    rec3 = c3.conduct(402, recent_kinds=["doc", "consistency", "doc"], frontier_swept=True,
                      use_corpus=False)
    checks["IDLE-STATE: a fold is refused after three doc runs"] = (
        not rec3.accepted and "not allowed" in rec3.reason)
    plan_idle = pick_increment(["doc", "consistency", "doc"], frontier_swept=True, use_corpus=False)
    checks["pick_increment flags must_be_abc on a plateau"] = plan_idle.must_be_abc
    plan_red = pick_increment([], selftest_green=False)
    checks["pick_increment forces a fix when selftest is RED"] = plan_red.allowed_kinds == ("fix",)

    # corpus-driven plateau: an "active"-looking recent_kinds but a low-novelty corpus -> must_be_abc
    cdir = tmp / "corpus"; cdir.mkdir()
    for i in range(1, 5):     # 4 folds, all re-citing one root -> novelty 0.0 over the window
        (cdir / f"run-{i}.json").write_text(json.dumps({
            "run": i, "increment": f"fold arXiv:2699.0001 again ({i})",
            "graph_delta": {"nodes": 1, "edges": 1},
            "distinct_evidence_roots": ["arXiv:2699.0001"]}), encoding="utf-8")
    for i in range(5, 12):
        (cdir / f"run-{i}.json").write_text(json.dumps({
            "run": i, "increment": f"fold arXiv:2699.0001 again ({i})",
            "graph_delta": {"nodes": 1, "edges": 1},
            "distinct_evidence_roots": ["arXiv:2699.0001"]}), encoding="utf-8")
    plan_corpus = pick_increment(["fold", "fold", "build"], frontier_swept=True,
                                 use_corpus=True, runs_dir=cdir)
    checks["pick_increment: a low-novelty corpus forces must_be_abc despite active recent_kinds"] = (
        plan_corpus.must_be_abc and "novelty ratio" in plan_corpus.reason)
    plan_ok = pick_increment(["fold", "fold", "build"], frontier_swept=True, use_corpus=False)
    checks["pick_increment: without the corpus, active recent_kinds is a normal run"] = (
        not plan_ok.must_be_abc)

    # a patch that fails check_patch (dangling edge) -> rejected before the gate
    bad_patch = {"proposal_metadata": {}, "add_nodes": [],
                 "add_edges": [{"id": "e", "source": "nope", "target": "concept_anchor", "type": "supports"}]}
    def badpatch_worker(task, *, hints):
        return True, {**worker_out, "patch": bad_patch}, "done"
    applied.clear()
    c4 = Conductor(require_blessed_manifest=False, gate=_tmpgate, ledger_path=tmp / "led4.json", run_worker=badpatch_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 4000.0)
    rec4 = c4.conduct(403, recent_kinds=["fold"], frontier_swept=False)
    checks["a structurally broken patch is rejected before the gate"] = (
        not rec4.accepted and "check_patch" in rec4.reason and not applied)

    # a regressing patch -> gate rejects, nothing applied
    worse = {f"t{i}": (1.0 if i < 5 else 0.0) for i in range(17)}
    def regress_worker(task, *, hints):
        return True, {**worker_out, "candidate_scores": worse}, "done"
    applied.clear()
    c5 = Conductor(require_blessed_manifest=False, gate=_tmpgate, ledger_path=tmp / "led5.json", run_worker=regress_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 5000.0)
    rec5 = c5.conduct(404, recent_kinds=["fold"], frontier_swept=False)
    checks["a held-out regression is rejected by the gate, nothing applied"] = (
        not rec5.accepted and rec5.certificate and rec5.certificate["decision"] == "reject"
        and not applied)

    # MLAS addition (3): preflight against the blessed harness manifest
    if _HarnessRegistry is not None:
        hreg = _HarnessRegistry(base=tmp / "harness")
        hreg.set("prompt", "p", "hello")
        cpf = Conductor(gate=_tmpgate, ledger_path=tmp / "ledpf.json", run_worker=ok_worker,
                        apply_patch=apply_patch, commit_push=commit_push, graph_path=graph_path,
                        clock=lambda: 6000.0, harness_registry=hreg)
        rec_unblessed = cpf.conduct(405, recent_kinds=["fold"], frontier_swept=False)
        checks["preflight: an unblessed manifest halts the run (require=True default)"] = (
            not rec_unblessed.accepted and "never been blessed" in rec_unblessed.reason)
        hreg.bless(note="test")
        applied.clear(); committed.clear()
        rec_blessed = cpf.conduct(406, recent_kinds=["build", "fold", "doc"], frontier_swept=False)
        checks["preflight: a blessed matching manifest lets the run proceed"] = (
            rec_blessed.accepted and committed == [(406, "accept")])
        hreg.set("prompt", "p", "hello -- drifted")
        rec_drift = cpf.conduct(407, recent_kinds=["fold"], frontier_swept=False)
        checks["preflight: manifest drift from the blessed baseline halts the run"] = (
            not rec_drift.accepted and "drift" in rec_drift.reason)
        hreg2 = _HarnessRegistry(base=tmp / "harness2")
        hreg2.set("prompt", "p", "never blessed")
        ok_pf, _ = Conductor(ledger_path=tmp / "x.json", run_worker=ok_worker,
                             apply_patch=apply_patch, commit_push=commit_push,
                             harness_registry=hreg2, require_blessed_manifest=False).preflight()
        checks["preflight: require_blessed_manifest=False tolerates an unblessed manifest"] = ok_pf
        drift_still_halts, _ = Conductor(ledger_path=tmp / "y.json", run_worker=ok_worker,
                                         apply_patch=apply_patch, commit_push=commit_push,
                                         harness_registry=hreg,
                                         require_blessed_manifest=False).preflight()
        checks["preflight: active drift halts even with require_blessed_manifest=False"] = (
            not drift_still_halts)

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    pk = sub.add_parser("plan")
    pk.add_argument("recent_kinds", nargs="*", help="kinds of the last few runs, oldest first")
    pk.add_argument("--selftest-red", action="store_true")
    pk.add_argument("--frontier-open", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "plan":
        plan = pick_increment(args.recent_kinds, selftest_green=not args.selftest_red,
                              frontier_swept=not args.frontier_open)
        print(json.dumps({"reason": plan.reason, "allowed_kinds": list(plan.allowed_kinds),
                          "must_be_abc": plan.must_be_abc}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

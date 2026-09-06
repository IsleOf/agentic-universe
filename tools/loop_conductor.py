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


def pick_increment(recent_kinds, *, selftest_green=True, frontier_swept=True):
    """Deterministic IDLE-STATE gate on what kind of increment this run may be.
    `recent_kinds` = the kinds of the last few runs, newest last."""
    if not selftest_green:
        return RunPlan("selftest is RED - the only valid increment is a fix", ("fix",))
    if not frontier_swept:
        return RunPlan("literature frontier not swept - fold the next item", ("fold", "build"))
    tail = tuple(recent_kinds[-PLATEAU_WINDOW:])
    idle_tail = len(tail) >= PLATEAU_WINDOW and all(
        k in ("doc", "consistency", "other") for k in tail)
    if idle_tail:
        return RunPlan(
            f"last {PLATEAU_WINDOW} runs were doc/hygiene and the frontier is swept - "
            f"the IDLE-STATE RULE requires (a) deepen one node via a citation sweep, "
            f"(b) dry-run a probe, or (c) a genuine consistency/adversarial pass",
            ABC_KINDS, must_be_abc=True)
    return RunPlan("normal run - highest-value increment, any kind",
                   ABC_KINDS + NON_IDLE_KINDS + ("doc",))


class Conductor:
    def __init__(self, *, ledger_path, run_worker, apply_patch, commit_push,
                 graph_path=None, choose_increment=pick_increment,
                 gate=None, clock=time.time, task_deadline_secs=1800):
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

    def _load_graph(self):
        try:
            return json.loads(self.graph_path.read_text(encoding="utf-8"))
        except Exception:
            return {"nodes": [], "edges": []}

    def conduct(self, run_no, *, recent_kinds=(), selftest_green=True, frontier_swept=True):
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

    c = Conductor(ledger_path=tmp / "led1.json", run_worker=ok_worker, apply_patch=apply_patch,
                  commit_push=commit_push, graph_path=graph_path, clock=lambda: 1000.0)
    rec = c.conduct(400, recent_kinds=["build", "fold", "doc"], frontier_swept=False)
    checks["a clean fold run is accepted, applied and committed"] = (
        rec.accepted and applied and committed == [(400, "accept")])
    checks["the certificate rides on the record"] = rec.certificate["decision"] == "accept"

    # a worker that never completes -> not accepted, nothing applied
    def dead_worker(task, *, hints):
        return False, None, "worker crashed"
    applied.clear()
    c2 = Conductor(ledger_path=tmp / "led2.json", run_worker=dead_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 2000.0)
    rec2 = c2.conduct(401, recent_kinds=["fold", "fold", "fold"], frontier_swept=False)
    checks["a failed worker yields an unaccepted record"] = (not rec2.accepted and not applied)
    checks["a failed run names the worker status"] = "did not complete" in rec2.reason

    # IDLE-STATE: three doc runs + swept frontier -> only a/b/c allowed; a 'fold' is refused
    def fold_worker(task, *, hints):
        return True, {**worker_out, "kind": "fold"}, "done"
    c3 = Conductor(ledger_path=tmp / "led3.json", run_worker=fold_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 3000.0)
    rec3 = c3.conduct(402, recent_kinds=["doc", "consistency", "doc"], frontier_swept=True)
    checks["IDLE-STATE: a fold is refused after three doc runs"] = (
        not rec3.accepted and "not allowed" in rec3.reason)
    plan_idle = pick_increment(["doc", "consistency", "doc"], frontier_swept=True)
    checks["pick_increment flags must_be_abc on a plateau"] = plan_idle.must_be_abc
    plan_red = pick_increment([], selftest_green=False)
    checks["pick_increment forces a fix when selftest is RED"] = plan_red.allowed_kinds == ("fix",)

    # a patch that fails check_patch (dangling edge) -> rejected before the gate
    bad_patch = {"proposal_metadata": {}, "add_nodes": [],
                 "add_edges": [{"id": "e", "source": "nope", "target": "concept_anchor", "type": "supports"}]}
    def badpatch_worker(task, *, hints):
        return True, {**worker_out, "patch": bad_patch}, "done"
    applied.clear()
    c4 = Conductor(ledger_path=tmp / "led4.json", run_worker=badpatch_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 4000.0)
    rec4 = c4.conduct(403, recent_kinds=["fold"], frontier_swept=False)
    checks["a structurally broken patch is rejected before the gate"] = (
        not rec4.accepted and "check_patch" in rec4.reason and not applied)

    # a regressing patch -> gate rejects, nothing applied
    worse = {f"t{i}": (1.0 if i < 5 else 0.0) for i in range(17)}
    def regress_worker(task, *, hints):
        return True, {**worker_out, "candidate_scores": worse}, "done"
    applied.clear()
    c5 = Conductor(ledger_path=tmp / "led5.json", run_worker=regress_worker, apply_patch=apply_patch,
                   commit_push=commit_push, graph_path=graph_path, clock=lambda: 5000.0)
    rec5 = c5.conduct(404, recent_kinds=["fold"], frontier_swept=False)
    checks["a held-out regression is rejected by the gate, nothing applied"] = (
        not rec5.accepted and rec5.certificate and rec5.certificate["decision"] == "reject"
        and not applied)

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

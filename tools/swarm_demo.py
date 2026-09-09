#!/usr/bin/env python3
"""swarm_demo — the week-1 acceptance test for the non-hierarchical swarm substrate.

`docs/swarm-substrate-prototype.md` week-1 build list item 6. A runnable
research -> draft -> critique -> final -> done pipeline where EVERY coordination
decision goes through the four substrate pieces and NOTHING through an orchestrator
object:

  * `task_ledger.py`  — what to do, in what order (`next_ready()` by stage)
  * `pheromone.py`    — where the signal is (the board every agent reads/writes)
  * `relay.py`        — how work moves between stages + the anti-ping-pong guard
  * `reputation.py`   — which agent picks up the next task (UCB, decayed)
  * `gates.py`        — G1 after research, G4 before done

The `run()` function is a `while` loop that reads `ledger.next_ready()`, asks
`reputation.select()` who should take it (excluding the task's own contributors),
lets that agent `contribute()`, drops the contribution on the board, and relays to
the next stage. It holds NO decision state — it is the deterministic substrate, the
same shape as `fractal_flock.run()`. A different agent set, a different pipeline,
a restart mid-run: the file decides what happens next, not the loop.

`contribute(agent_id, stage, task, board_reads)` is the caller's generative work.
The demo ships a `_fake_worker` (no model calls) that writes a plausible stub per
stage and, at the research stage, emits an `evidence` list so G1 has something to
check.

`agent_models={agent: {"family", "tier"}}` (run 449, arXiv:2609.04270): when set,
`_fresh_validator` prefers a validator whose model family differs from the task's
executor and whose tier is >= it, and the gate transcript entries REPORT
`same_model_review` / `weaker_reviewer` when no such validator is available -
same-model review over-rejects ~35% of correct answers, a weaker reviewer is
negative value. REPORT, never block.

CLI: run / selftest.  Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from task_ledger import Ledger, STAGES  # noqa: E402
from pheromone import Pheromone  # noqa: E402
from relay import Relay, RelayRefused  # noqa: E402
from reputation import Reputation  # noqa: E402
from gates import g1_evidence, g4_release, GateRefused  # noqa: E402


def _fake_worker(agent_id, stage, task, board):
    """A stub contributor — no model calls. Returns
    {"text": str, "evidence": [links], "utility": float, "confidence": float}."""
    if stage == "research":
        return {
            "text": (f"[{agent_id}] researched: 3 sources on '{task['goal']}'. "
                     f"Key finding cited [see tools/relay.py]. "
                     f"SwarmSys reports gains (arXiv:2510.10047)."),
            "evidence": ["tools/relay.py", "https://arxiv.org/abs/2510.10047"],
            "utility": 0.6, "confidence": 0.8,
        }
    if stage == "draft":
        return {"text": f"[{agent_id}] drafted from the research [see tools/relay.py].",
                "evidence": ["tools/relay.py"], "utility": 0.5, "confidence": 0.7}
    if stage == "critique":
        return {"text": f"[{agent_id}] critique: structure ok, one claim needs a hedge.",
                "evidence": [], "utility": 0.3, "confidence": 0.6}
    return {"text": f"[{agent_id}] finalized.", "evidence": ["tools/relay.py"],
            "utility": 0.4, "confidence": 0.75}


class SwarmDemo:
    def __init__(self, work_dir, agents, *, contribute=_fake_worker, computable_ok=True,
                 defer_consensus=True, agent_models=None):
        self.dir = Path(work_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        # run 439 (ArcticSwarm, arXiv:2609.01870): the research contribution is
        # posted as a private (isolated) working note and released at the G1
        # commitment boundary; before G4 a fresh agent records that a competing
        # hypothesis was considered, so the commit gate is not single-candidate.
        self.defer_consensus = defer_consensus
        self.ledger = Ledger(self.dir / "ledger.json")
        self.pher = Pheromone(self.dir / "pheromone.db")
        # relay shares the demo's live ledger + pheromone objects — two Ledger
        # instances on one file do not share in-memory state
        self.relay = Relay(ledger=self.ledger, pheromone=self.pher,
                           ledger_path=self.dir / "ledger.json",
                           window=4, min_unique=2)
        self.rep = Reputation(self.dir / "reputation.json")
        self.agents = list(agents)
        self.contribute = contribute
        self.computable_ok = computable_ok
        # run 449 (arXiv:2609.04270): reviewer capability governs rejection targeting.
        # {agent: {"family": str, "tier": int}}. When set, _fresh_validator prefers a
        # validator whose model family differs from the task's executor and whose tier
        # is >= the executor's, and the gate transcript REPORTS same_model_review /
        # weaker_reviewer when no such validator is available. REPORT, never block.
        self.agent_models = dict(agent_models or {})
        self.transcript = []

    def _pick(self, task):
        """reputation.select() among agents who did NOT already contribute to this
        task — so the pipeline hands work to fresh eyes and gates stay valid."""
        contributors = set(self.pher.read(task["id"])["contributors"])
        load = {a: sum(1 for t in self.ledger.tasks.values()
                       if t["status"] == "active" and t["owner"] == a)
                for a in self.agents}
        candidates = [a for a in self.agents if a not in contributors] or self.agents
        return self.rep.select(candidates, load_of=load)

    def run(self, goal, *, max_steps=40):
        root = self.ledger.add(goal, stage="research")
        self.pher.annotate(root, "utility", 0.5, 0.6, agent="seed",
                           evidence={"origin": "swarm_demo goal"})
        released = None
        for _ in range(max_steps):
            task = self.ledger.next_ready()
            if task is None:
                break
            agent = self._pick(task)
            self.ledger.claim(task["id"], agent)
            board = self.pher.read(task["id"])
            out = self.contribute(agent, task["stage"], task, board)

            stage = task["stage"]
            # research work is posted ISOLATED (a private working note) and released
            # at the G1 boundary; every other stage posts straight to the shared board
            isolate = self.defer_consensus and stage == "research"
            self.pher.annotate(task["id"], "utility", out["utility"], out["confidence"],
                               agent=agent, isolated=isolate,
                               evidence={"text": out["text"], "stage": task["stage"],
                                         "evidence": out.get("evidence", [])})
            self.transcript.append({"task": task["id"], "stage": task["stage"],
                                    "agent": agent, "text": out["text"],
                                    **({"isolated": True} if isolate else {})})

            if stage == "research":
                # commitment boundary: release the isolated research note to the
                # shared board so the G1 validator (and the draft stage) can see it
                if isolate:
                    n = self.pher.release_isolation(task["id"], agent=agent)
                    self.transcript.append({"event": "release_isolation",
                                            "task": task["id"], "agent": agent, "n": n})
                # G1 by a fresh validator (run 449: prefer a cross-family / >= tier one)
                v_agent = self._fresh_validator(task["id"], executor=agent)
                try:
                    g1 = g1_evidence(task["id"], out["text"],
                                     evidence_links=out.get("evidence", []),
                                     validator_agent=v_agent, pheromone=self.pher)
                    self.transcript.append({"gate": "G1", "task": task["id"],
                                            "validator": v_agent, "pass": g1["pass"],
                                            **self._reviewer_model_report(v_agent, agent)})
                    if not g1["pass"]:
                        self.ledger.fail(task["id"], f"G1 failed: {g1['reasons']}")
                        self.rep.record(agent, "failure")
                        continue
                except GateRefused as e:
                    self.transcript.append({"gate": "G1", "refused": str(e)})

            if stage == STAGES[-1]:              # final -> release via G4
                self.relay.complete(task["id"], from_agent=agent,
                                    artifact_ref=self.dir.name + "/artifact.md")
                self.rep.record(agent, "success")
                # before G4: record that a competing hypothesis was considered, so
                # the commit gate is not single-candidate (ArcticSwarm). Needs a
                # non-contributor to spare — and one more left for the G4 validator.
                if self.defer_consensus:
                    non_contrib = [a for a in self.agents if a not in
                                   set(self.pher.read(task["id"])["contributors"])]
                    if len(non_contrib) >= 2:
                        alt = self.rep.select(non_contrib)
                        self.pher.note_alternative(
                            task["id"], agent=alt,
                            hypothesis=f"considered an alternative framing of '{goal}'")
                        self.transcript.append({"event": "note_alternative",
                                                "task": task["id"], "agent": alt})
                v_agent = self._fresh_validator(task["id"], executor=agent)
                try:
                    g4 = g4_release(task["id"], validator_agent=v_agent, pheromone=self.pher,
                                    computable_ok=self.computable_ok, min_quorum=2)
                    self.transcript.append({"gate": "G4", "task": task["id"],
                                            "validator": v_agent, "pass": g4["pass"],
                                            "quorum": g4["quorum"],
                                            "no_alternative_hypothesis":
                                                g4["no_alternative_hypothesis"],
                                            **self._reviewer_model_report(v_agent, agent)})
                    if g4["pass"]:
                        released = task["id"]
                        break
                except GateRefused as e:
                    self.transcript.append({"gate": "G4", "refused": str(e)})
                break

            # not final -> hand off to the next stage
            try:
                self.relay.handoff(task["id"], from_agent=agent,
                                   message=out["text"][:120],
                                   context={"evidence": out.get("evidence", [])},
                                   to_hint=f"a strong {STAGES[STAGES.index(stage) + 1]}er")
                self.rep.record(agent, "success")
            except RelayRefused as e:
                self.transcript.append({"handoff": "refused", "why": str(e)})
                self.ledger.block(task["id"], "relay refused (ping-pong guard)")
                break
        return {"released": released, "root": root,
                "steps": len(self.transcript), "transcript": self.transcript}

    def _fresh_validator(self, task_ref, *, executor=None):
        contributors = set(self.pher.read(task_ref)["contributors"])
        pool = [a for a in self.agents if a not in contributors]
        if not pool:
            return self.agents[-1]
        if self.agent_models and executor in self.agent_models:
            ex = self.agent_models[executor]
            # prefer: different family AND tier >= executor's, then reputation order
            def _key(a):
                m = self.agent_models.get(a, {})
                diff_family = m.get("family") != ex.get("family")
                tier_ok = m.get("tier", 0) >= ex.get("tier", 0)
                return (not (diff_family and tier_ok), not diff_family, not tier_ok)
            pool = sorted(pool, key=lambda a: (_key(a), a))
            # reputation.select only among the best-keyed tier so it still breaks ties
            best = _key(pool[0])
            top = [a for a in pool if _key(a) == best]
            return self.rep.select(top) or pool[0]
        return self.rep.select(pool)

    def _reviewer_model_report(self, validator, executor):
        """arXiv:2609.04270: flag when the chosen validator shares the executor's
        model family (self-review over-rejects) or is a weaker tier (negative value).
        REPORT only - returned in the gate transcript entry."""
        if not self.agent_models or executor not in self.agent_models \
                or validator not in self.agent_models:
            return {}
        ex, va = self.agent_models[executor], self.agent_models[validator]
        return {
            "same_model_review": va.get("family") == ex.get("family"),
            "weaker_reviewer": va.get("tier", 0) < ex.get("tier", 0),
            "reviewer_tier_delta": va.get("tier", 0) - ex.get("tier", 0),
        }

    def audit_ok(self):
        """Every closed task has an audit line; every stage that ran left a board
        trace; a released run has a G4 PASS annotation on the final task."""
        prob = []
        for t in self.ledger.tasks.values():
            if t["status"] in ("done", "failed"):
                stages_seen = {a["evidence"].get("stage")
                               for a in self.pher.read(t["id"])["annotations"]
                               if isinstance(a.get("evidence"), dict)}
                if t["stage"] not in stages_seen and t["status"] == "done":
                    prob.append(f"{t['id']} done but no board trace for its stage")
        return (not prob), prob

    def close(self):
        self.pher.close()
        self.relay.close()


# --------------------------------------------------------------------------- #
def _selftest():
    import shutil
    tmp = Path(tempfile.mkdtemp(prefix="swarmdemo-"))
    checks = {}
    try:
        # 1. the happy path: 4 agents (the ArcticSwarm deferred-consensus flow needs
        #    one spare agent for the alternative-hypothesis note + the G4 validator),
        #    fake workers, computable checks pass -> release
        d = SwarmDemo(tmp / "happy", ["a1", "a2", "a3", "a4"], computable_ok=True)
        r = d.run("map the auth flow and find the race")
        checks["the pipeline runs end to end and releases an artifact"] = r["released"] is not None
        stages_run = {e["stage"] for e in r["transcript"] if "stage" in e}
        checks["every pipeline stage ran"] = stages_run == set(STAGES)
        checks["G1 ran and passed"] = any(
            e.get("gate") == "G1" and e.get("pass") for e in r["transcript"])
        checks["G4 ran and passed"] = any(
            e.get("gate") == "G4" and e.get("pass") for e in r["transcript"])
        # run 439: the ArcticSwarm deferred-consensus flow ran end to end
        checks["the research note was posted isolated then released at the G1 boundary"] = (
            any(e.get("isolated") for e in r["transcript"] if e.get("stage") == "research")
            and any(e.get("event") == "release_isolation" and e.get("n", 0) >= 1
                    for e in r["transcript"]))
        checks["a competing hypothesis was recorded before G4"] = any(
            e.get("event") == "note_alternative" for e in r["transcript"])
        checks["G4's verdict is not flagged no_alternative_hypothesis"] = any(
            e.get("gate") == "G4" and e.get("no_alternative_hypothesis") is False
            for e in r["transcript"])
        ok, prob = d.audit_ok()
        checks["the audit trail is clean"] = ok
        # no orchestrator/chief CLASS DEFINITION anywhere in the module (regex so the
        # check string itself does not count as a match)
        import re as _re
        src = Path(__file__).read_text(encoding="utf-8")
        checks["no orchestrator/chief class definition in the module"] = not _re.search(
            r"^class \w*(Orchestrator|Chief|Boss|Manager)\b", src, _re.M)
        d.close()

        # 1b. defer_consensus=False: the old straight-to-board behaviour still works,
        #     and G4 is then correctly flagged no_alternative_hypothesis
        d1b = SwarmDemo(tmp / "nodefer", ["a1", "a2", "a3", "a4"], computable_ok=True,
                        defer_consensus=False)
        r1b = d1b.run("map the auth flow")
        checks["defer_consensus=False still releases"] = r1b["released"] is not None
        checks["defer off: no isolation / note_alternative events"] = not any(
            e.get("event") in ("release_isolation", "note_alternative")
            for e in r1b["transcript"])
        checks["defer off: G4 IS flagged no_alternative_hypothesis"] = any(
            e.get("gate") == "G4" and e.get("no_alternative_hypothesis") is True
            for e in r1b["transcript"])
        d1b.close()

        # 1c. run 449: validator model-family / tier awareness (arXiv:2609.04270)
        models_ok = {"a1": {"family": "X", "tier": 2}, "a2": {"family": "Y", "tier": 2},
                     "a3": {"family": "Y", "tier": 3}, "a4": {"family": "X", "tier": 1}}
        d1c = SwarmDemo(tmp / "models_ok", ["a1", "a2", "a3", "a4"], computable_ok=True,
                        agent_models=models_ok)
        r1c = d1c.run("map the auth flow")
        gates1c = [e for e in r1c["transcript"] if e.get("gate") in ("G1", "G4")]
        checks["with a cross-family >= tier validator available, no gate flags same_model_review"] = (
            r1c["released"] is not None
            and gates1c and not any(e.get("same_model_review") for e in gates1c))
        checks["the model report is stamped into gate transcript entries"] = any(
            "same_model_review" in e for e in gates1c)
        d1c.close()

        # all one family -> same_model_review flagged, but still releases (REPORT not block)
        models_mono = {a: {"family": "X", "tier": 2} for a in ("m1", "m2", "m3", "m4")}
        d1d = SwarmDemo(tmp / "models_mono", ["m1", "m2", "m3", "m4"], computable_ok=True,
                        agent_models=models_mono)
        r1d = d1d.run("something")
        checks["an all-one-family fleet flags same_model_review at a gate"] = any(
            e.get("same_model_review") for e in r1d["transcript"] if e.get("gate"))
        checks["...but still releases - it is a REPORT, not a block"] = r1d["released"] is not None
        d1d.close()

        # 2. a failing computable check -> G4 does NOT release, but the run still
        #    terminates cleanly (no exception, no infinite loop)
        d2 = SwarmDemo(tmp / "blocked", ["b1", "b2", "b3"], computable_ok=False)
        r2 = d2.run("a task whose tests fail")
        checks["a failing computable check blocks release"] = r2["released"] is None
        checks["the blocked run still terminates"] = r2["steps"] > 0
        checks["G4 ran and did NOT pass"] = any(
            e.get("gate") == "G4" and not e.get("pass") for e in r2["transcript"])
        d2.close()

        # 3. coordination is genuinely decentralised: different agents touch
        #    different stages (fresh-eyes rule), and validators are never contributors
        d3 = SwarmDemo(tmp / "decent", ["c1", "c2", "c3", "c4"], computable_ok=True)
        r3 = d3.run("something")
        contribs = [(e["stage"], e["agent"]) for e in r3["transcript"] if "stage" in e]
        gate_agents = [(e["gate"], e["validator"]) for e in r3["transcript"]
                       if e.get("validator")]
        # for each gate, the validator did not contribute to that task
        bad = []
        for e in r3["transcript"]:
            if e.get("validator"):
                tref = e["task"]
                cset = {c["agent"] for c in r3["transcript"]
                        if c.get("task") == tref and "stage" in c}
                if e["validator"] in cset:
                    bad.append(e)
        checks["a gate validator never contributed to the task it gates"] = not bad
        checks["more than one distinct agent did the work"] = (
            len({a for _, a in contribs}) >= 2)
        d3.close()

        # 4. k=2 CANNOT run a gated pipeline: by the final stage both agents have
        #    contributed, so no non-author validator is left for G4. The run must
        #    fail CLEANLY (GateRefused in the transcript, no exception, no hang) —
        #    a real "3-15 agents" floor for gated work, recorded not hidden.
        d2a = SwarmDemo(tmp / "k2", ["w0", "w1"], computable_ok=True)
        r2a = d2a.run("two-agent test")
        checks["k=2: does NOT release (no non-author validator for the gates)"] = (
            r2a["released"] is None)
        checks["k=2: fails cleanly with a GateRefused, not an exception or a hang"] = any(
            e.get("refused") for e in r2a["transcript"]) and r2a["steps"] > 0
        d2a.close()

        # 5. pool-size sweep from k=3 — the driver holds no state that breaks as agents grow
        for k in range(3, 10):
            dk = SwarmDemo(tmp / f"k{k}", [f"w{i}" for i in range(k)], computable_ok=True)
            rk = dk.run("scale test")
            checks[f"k={k}: the pipeline runs and releases"] = rk["released"] is not None
            dk.close()

        for key, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {key}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    rp = sub.add_parser("run")
    rp.add_argument("goal")
    rp.add_argument("--agents", nargs="+", default=["a1", "a2", "a3"])
    rp.add_argument("--dir", default=None)
    rp.add_argument("--tests-fail", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    wd = Path(args.dir) if args.dir else Path(tempfile.mkdtemp(prefix="swarmdemo-run-"))
    d = SwarmDemo(wd, args.agents, computable_ok=not args.tests_fail)
    out = d.run(args.goal)
    d.close()
    print(json.dumps({k: v for k, v in out.items() if k != "transcript"}, indent=2))
    print("\ntranscript:")
    for e in out["transcript"]:
        print("  " + json.dumps(e))
    print(f"\nwork dir: {wd}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

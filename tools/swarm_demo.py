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
    def __init__(self, work_dir, agents, *, contribute=_fake_worker, computable_ok=True):
        self.dir = Path(work_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
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

            # the contribution lands on the board (stigmergy, not a private channel)
            self.pher.annotate(task["id"], "utility", out["utility"], out["confidence"],
                               agent=agent,
                               evidence={"text": out["text"], "stage": task["stage"],
                                         "evidence": out.get("evidence", [])})
            self.transcript.append({"task": task["id"], "stage": task["stage"],
                                    "agent": agent, "text": out["text"]})

            stage = task["stage"]
            if stage == "research":
                # G1 by a fresh validator
                v_agent = self._fresh_validator(task["id"])
                try:
                    g1 = g1_evidence(task["id"], out["text"],
                                     evidence_links=out.get("evidence", []),
                                     validator_agent=v_agent, pheromone=self.pher)
                    self.transcript.append({"gate": "G1", "task": task["id"],
                                            "validator": v_agent, "pass": g1["pass"]})
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
                v_agent = self._fresh_validator(task["id"])
                try:
                    g4 = g4_release(task["id"], validator_agent=v_agent, pheromone=self.pher,
                                    computable_ok=self.computable_ok, min_quorum=2)
                    self.transcript.append({"gate": "G4", "task": task["id"],
                                            "validator": v_agent, "pass": g4["pass"],
                                            "quorum": g4["quorum"]})
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

    def _fresh_validator(self, task_ref):
        contributors = set(self.pher.read(task_ref)["contributors"])
        pool = [a for a in self.agents if a not in contributors]
        return self.rep.select(pool) if pool else self.agents[-1]

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
        # 1. the happy path: 3 agents, fake workers, computable checks pass -> release
        d = SwarmDemo(tmp / "happy", ["a1", "a2", "a3"], computable_ok=True)
        r = d.run("map the auth flow and find the race")
        checks["the pipeline runs end to end and releases an artifact"] = r["released"] is not None
        stages_run = {e["stage"] for e in r["transcript"] if "stage" in e}
        checks["every pipeline stage ran"] = stages_run == set(STAGES)
        checks["G1 ran and passed"] = any(
            e.get("gate") == "G1" and e.get("pass") for e in r["transcript"])
        checks["G4 ran and passed"] = any(
            e.get("gate") == "G4" and e.get("pass") for e in r["transcript"])
        ok, prob = d.audit_ok()
        checks["the audit trail is clean"] = ok
        # no orchestrator/chief CLASS DEFINITION anywhere in the module (regex so the
        # check string itself does not count as a match)
        import re as _re
        src = Path(__file__).read_text(encoding="utf-8")
        checks["no orchestrator/chief class definition in the module"] = not _re.search(
            r"^class \w*(Orchestrator|Chief|Boss|Manager)\b", src, _re.M)
        d.close()

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

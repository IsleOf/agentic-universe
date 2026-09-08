#!/usr/bin/env python3
"""The relay — handoff and completion for a coordinator-free swarm.

`docs/swarm-substrate-prototype.md` week-1 build list item 3. Ports the two things
the Strands Agents Swarm pattern
(https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/) gets right,
onto this repo's own substrate (`task_ledger.py` + `pheromone.py`):

  * `handoff(...)`  — an agent finishes its piece and passes the work on, leaving a
    context-rich trace. Strands' `handoff_to_agent(name, message, context)`; here
    the "name" is a *hint*, not an address — the relay picks the next task off the
    ledger by stage, and the message + context land as a `kind=done` pheromone
    annotation so the next agent reads them from the board, not from a private
    channel.

  * `complete(...)` — `complete_swarm_task(...)`: the pipeline's last stage closes
    the task and posts the final artifact reference.

  * THE ANTI-PING-PONG GUARD. Strands' `repetitive_handoff_detection_window` /
    `repetitive_handoff_min_unique_agents`: if the last `window` handoffs used
    fewer than `min_unique` distinct agents, the swarm is bouncing work between the
    same two agents and the relay refuses the handoff. Here the handoff history is
    itself on the ledger audit + a small state file, so the guard is deterministic
    and survives a restart.

NO MODEL CALLS. The relay moves work and leaves traces; deciding *what* to
contribute is the caller's. Pure stdlib.

Usage:
    r = Relay(ledger_path=..., pheromone_path=...)
    r.handoff(task_ref, from_agent="a1", message="research done, 3 sources; draft next",
              context={"sources": [...]}, to_hint="a strong writer")
    r.complete(final_task_ref, from_agent="a4", artifact_ref="docs/out.md")

CLI: handoff / complete / history / selftest.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from task_ledger import Ledger, STAGES, STAGE_RANK, DEFAULT_STAGE  # noqa: E402
from pheromone import Pheromone  # noqa: E402

DEFAULT_WINDOW = 6           # Strands repetitive_handoff_detection_window
DEFAULT_MIN_UNIQUE = 3       # Strands repetitive_handoff_min_unique_agents


def _now():
    return round(time.time(), 3)


class RelayRefused(RuntimeError):
    """A handoff the anti-ping-pong guard would not allow."""


class Relay:
    def __init__(self, *, ledger_path, pheromone_path, window=DEFAULT_WINDOW,
                 min_unique=DEFAULT_MIN_UNIQUE):
        self.ledger = Ledger(ledger_path)
        self.pher = Pheromone(pheromone_path)
        self.window = window
        self.min_unique = min_unique
        self._state_path = Path(ledger_path).with_suffix(".relay.json")
        self._hist = self._load_hist()

    # -- handoff history (deterministic, survives restart) --------------------
    def _load_hist(self):
        if self._state_path.exists():
            return json.loads(self._state_path.read_text(encoding="utf-8"))
        return {"handoffs": []}     # each: {ts, task_ref, from, stage_from, stage_to}

    def _save_hist(self):
        tmp = self._state_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._hist, indent=2), encoding="utf-8")
        tmp.replace(self._state_path)

    def _recent_agents(self):
        return [h["from"] for h in self._hist["handoffs"][-self.window:]]

    def would_refuse(self, from_agent):
        """True if adding a handoff BY `from_agent` now would leave the last
        `window` handoffs with fewer than `min_unique` distinct agents. A short
        history (< window handoffs) never refuses — the swarm has not had a chance
        to diversify yet."""
        recent = self._recent_agents() + [from_agent]
        recent = recent[-self.window:]
        if len(recent) < self.window:
            return False
        return len(set(recent)) < self.min_unique

    # -- the two operations --------------------------------------------------
    def handoff(self, task_ref, *, from_agent, message, context=None, to_hint=None,
                next_goal=None):
        """Finish `task_ref` and thread the pipeline to the next stage.

        Leaves a `kind=done` pheromone annotation carrying `message`, `to_hint` and
        `context` so the next agent reads the handoff from the board. Creates the
        next-stage task (via `Ledger.next_stage`) unless `task_ref` is already at
        the final stage, in which case use `complete()` instead.

        Raises `RelayRefused` if the anti-ping-pong guard trips.
        """
        t = self.ledger.get(task_ref)
        stage = t.get("stage", DEFAULT_STAGE)
        if STAGE_RANK[stage] + 1 >= len(STAGES):
            raise ValueError(f"{task_ref} is at the final stage {stage!r}; call complete()")
        if self.would_refuse(from_agent):
            raise RelayRefused(
                f"handoff by {from_agent!r} refused: the last {self.window} handoffs "
                f"would use < {self.min_unique} distinct agents "
                f"({sorted(set(self._recent_agents() + [from_agent]))}) — the swarm is "
                f"bouncing work; route via a fresh agent or the board")

        # close the current task
        if t["status"] == "pending":
            self.ledger.claim(task_ref, from_agent)
        if self.ledger.get(task_ref)["status"] == "active":
            self.ledger.complete(task_ref, result_ref={"handoff_by": from_agent})

        # the handoff trace goes on the board, not a private channel
        self.pher.annotate(
            task_ref, "done",
            utility=0.0, confidence=1.0, agent=from_agent,
            evidence={"message": message, "to_hint": to_hint, "context": context or {},
                      "next_stage": STAGES[STAGE_RANK[stage] + 1]},
        )

        nxt = self.ledger.next_stage(
            task_ref,
            next_goal or f"{STAGES[STAGE_RANK[stage] + 1]}: continue from {task_ref}",
        )
        # a fresh, positive marker on the next task so the board surfaces it
        self.pher.annotate(nxt, "utility", utility=0.5, confidence=0.6, agent=from_agent,
                           evidence={"handed_off_from": task_ref})

        self._hist["handoffs"].append({
            "ts": _now(), "task_ref": task_ref, "from": from_agent,
            "stage_from": stage, "stage_to": STAGES[STAGE_RANK[stage] + 1],
            "next_task": nxt,
        })
        self._save_hist()
        return nxt

    def complete(self, task_ref, *, from_agent, artifact_ref, note=None):
        """Close the pipeline's final task and post the artifact reference."""
        t = self.ledger.get(task_ref)
        if t["status"] == "pending":
            self.ledger.claim(task_ref, from_agent)
        if self.ledger.get(task_ref)["status"] == "active":
            self.ledger.complete(task_ref, result_ref={"artifact": artifact_ref,
                                                       "by": from_agent})
        self.pher.annotate(task_ref, "done", utility=0.0, confidence=1.0, agent=from_agent,
                           evidence={"artifact": artifact_ref, "note": note,
                                     "final": True})
        self._hist["handoffs"].append({
            "ts": _now(), "task_ref": task_ref, "from": from_agent,
            "stage_from": t.get("stage", DEFAULT_STAGE), "stage_to": "done",
            "artifact": artifact_ref,
        })
        self._save_hist()
        return artifact_ref

    def history(self, limit=20):
        return self._hist["handoffs"][-limit:]

    def close(self):
        self.pher.close()


# --------------------------------------------------------------------------- #
def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="relay-"))
    checks = {}
    try:
        r = Relay(ledger_path=tmp / "l.json", pheromone_path=tmp / "p.db",
                  window=4, min_unique=2)
        research = r.ledger.add("research the auth flow", stage="research")

        # 1. a normal handoff threads research -> draft and leaves a board trace
        draft = r.handoff(research, from_agent="a1",
                          message="3 sources found; the race is in token refresh",
                          context={"sources": ["s1", "s2", "s3"]}, to_hint="a writer")
        checks["handoff completes the research task"] = (
            r.ledger.get(research)["status"] == "done")
        checks["handoff creates the next-stage task depending on it"] = (
            r.ledger.get(draft)["stage"] == "draft" and r.ledger.get(draft)["deps"] == [research])
        board_research = r.pher.read(research)
        checks["the handoff message lands on the board, not a private channel"] = any(
            a["kind"] == "done" and a["evidence"]["message"].startswith("3 sources")
            for a in board_research["annotations"])
        checks["the next task gets a fresh positive marker"] = r.pher.read(draft)["signal"] > 0

        # 2. cannot handoff from the final stage
        crit = r.handoff(draft, from_agent="a2", message="draft done", to_hint="a critic")
        fin = r.handoff(crit, from_agent="a3", message="critique done", to_hint="finalizer")
        try:
            r.handoff(fin, from_agent="a4", message="nope")
            checks["handoff from the final stage raises"] = False
        except ValueError:
            checks["handoff from the final stage raises"] = True

        # 3. complete() closes the final task with an artifact
        art = r.complete(fin, from_agent="a4", artifact_ref="docs/auth_flow.md")
        checks["complete closes the final task"] = r.ledger.get(fin)["status"] == "done"
        checks["complete posts the artifact ref to the board"] = any(
            a["evidence"].get("artifact") == "docs/auth_flow.md"
            for a in r.pher.read(fin)["annotations"])

        # 4. THE ANTI-PING-PONG GUARD (window=4, min_unique=2). Drive the history
        #    directly so the pipeline length is not the constraint being tested.
        g = Relay(ledger_path=tmp / "g.json", pheromone_path=tmp / "g.db",
                  window=4, min_unique=2)
        # window after adding "b": [x,y,b,b][-4:] with +b -> [y,b,b,b]? no: prev [x,y,b,b] + b -> [x,y,b,b,b][-4:] = [y,b,b,b] -> {y,b}=2, allowed
        g._hist["handoffs"] = [{"from": a} for a in ("x", "y", "b", "b")]
        checks["guard allows when the window keeps exactly min_unique distinct"] = (
            not g.would_refuse("b"))
        # prev [y,b,b,b] + b -> [b,b,b,b] -> {b}=1 < 2, refused
        g._hist["handoffs"] = [{"from": a} for a in ("y", "b", "b", "b")]
        checks["guard refuses when the window would collapse below min_unique"] = (
            g.would_refuse("b"))
        checks["a fresh agent breaks the loop"] = not g.would_refuse("z")
        # and handoff() actually raises RelayRefused (research-stage task, stage is not the blocker)
        stuck = g.ledger.add("stuck task", stage="research")
        try:
            g.handoff(stuck, from_agent="b", message="m")
            checks["a refused handoff raises RelayRefused"] = False
        except RelayRefused:
            checks["a refused handoff raises RelayRefused"] = True
        g.close()

        # 5. a short history never refuses
        r3 = Relay(ledger_path=tmp / "l3.json", pheromone_path=tmp / "p3.db",
                   window=6, min_unique=3)
        root3 = r3.ledger.add("x", stage="research")
        checks["a short history (< window) never refuses"] = not r3.would_refuse("solo")
        r3.close()

        # 6. history survives a restart (state file). `r` did 3 handoffs + 1 complete.
        hist_before = list(r.history())
        r.close()
        r_reload = Relay(ledger_path=tmp / "l.json", pheromone_path=tmp / "p.db",
                         window=4, min_unique=2)
        checks["handoff history persists across a restart"] = (
            r_reload.history() == hist_before and len(hist_before) == 4)
        r_reload.close()

        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for name in ("handoff", "complete", "history"):
        sp = sub.add_parser(name)
        sp.add_argument("--ledger", required=True)
        sp.add_argument("--pheromone", required=True)
        if name == "handoff":
            sp.add_argument("task_ref")
            sp.add_argument("--from", dest="from_agent", required=True)
            sp.add_argument("--message", required=True)
            sp.add_argument("--to-hint", default=None)
        if name == "complete":
            sp.add_argument("task_ref")
            sp.add_argument("--from", dest="from_agent", required=True)
            sp.add_argument("--artifact", required=True)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    r = Relay(ledger_path=args.ledger, pheromone_path=args.pheromone)
    if args.cmd == "handoff":
        print(r.handoff(args.task_ref, from_agent=args.from_agent, message=args.message,
                        to_hint=args.to_hint))
    elif args.cmd == "complete":
        print(r.complete(args.task_ref, from_agent=args.from_agent, artifact_ref=args.artifact))
    elif args.cmd == "history":
        print(json.dumps(r.history(), indent=2))
    r.close()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

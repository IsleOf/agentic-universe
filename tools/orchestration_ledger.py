#!/usr/bin/env python3
"""A deterministic, file-backed record of the RESEARCH LOOP's own dispatch state.

Run 464. The loop's orchestration layer — which run is next, what is dispatched
but not yet landed — has lived in a *session's conversation context*. That is
exactly the CordisBench finding
`pattern_deterministic_task_ledger_is_the_orchestration_source_of_truth`
(run 244) warns against, applied one level up: task state must not live in the
model's context. A fresh session, or the cron, cannot see what a previous
session had "in flight".

This ledger is a plain JSON file the loop reads and writes so that dispatch
state survives a context reset:

  * `.claim(run_no, agent=None)` marks a run `dispatched` with a timestamp.
    Idempotent (re-claiming a still-dispatched run is a no-op refresh); refuses
    to re-claim a run already `done`.
  * `.complete(run_no, sha, node_delta=None, edge_delta=None)` marks it `done`.
  * `.status()` is the deterministic pick a fresh session needs: the highest
    `done` run, any `dispatched`-but-not-`done` runs (stale in-flight — a
    session died mid-run), and the next run number.
  * `.record_gate(run_no, verdict)` stores a `sweep_audit` verdict string on the
    run entry. Advisory only — it never blocks a claim or a complete.

Same discipline as `tools/task_ledger.py`: every mutation writes the whole file
atomically (tmp + `os.replace`) and appends a line to a sibling `.audit` log, so
the dispatch history is inspectable and uncompressed.

PORTABILITY CLASS: FIXED-SCHEMA. Every field is a fixed key with a
machine-checkable value (run_no / state / dispatched_at / done_at / sha / ...);
nothing here is a model-compressed note, so it transfers across a model swap.

Pure stdlib.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "runtime/observations/orchestration_ledger.json"

DISPATCHED = "dispatched"
DONE = "done"
STATES = (DISPATCHED, DONE)


def _now():
    return round(time.time(), 3)


class OrchestrationLedger:
    def __init__(self, path=DEFAULT):
        self.path = Path(path)
        self.audit_path = self.path.with_suffix(self.path.suffix + ".audit")
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._data = {"runs": {}, "created": _now()}
            self._flush("init")

    # --- persistence -----------------------------------------------------
    def _flush(self, event):
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, self.path)
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": _now(), "event": event}) + "\n")

    @property
    def runs(self):
        return self._data["runs"]

    def get(self, run_no):
        return self._data["runs"].get(str(int(run_no)))

    # --- mutations -----------------------------------------------------
    def claim(self, run_no, agent=None):
        """Mark `run_no` dispatched. Idempotent while still dispatched; refuses
        to re-claim a run already done."""
        key = str(int(run_no))
        cur = self._data["runs"].get(key)
        if cur is not None and cur["state"] == DONE:
            raise ValueError(f"run {key} is already done; refusing to re-claim")
        if cur is not None and cur["state"] == DISPATCHED:
            cur["dispatched_at"] = _now()
            if agent is not None:
                cur["agent"] = agent
            self._flush(f"reclaim {key} (refresh)")
            return cur
        self._data["runs"][key] = {
            "run_no": int(run_no),
            "state": DISPATCHED,
            "agent": agent,
            "dispatched_at": _now(),
            "done_at": None,
            "sha": None,
            "node_delta": None,
            "edge_delta": None,
            "gate_verdict": None,
        }
        self._flush(f"claim {key} by {agent}")
        return self._data["runs"][key]

    def complete(self, run_no, sha, node_delta=None, edge_delta=None):
        key = str(int(run_no))
        cur = self._data["runs"].get(key)
        if cur is None:
            # completing a run that was never claimed — record it anyway
            cur = self.claim(run_no)
        cur["state"] = DONE
        cur["done_at"] = _now()
        cur["sha"] = sha
        cur["node_delta"] = node_delta
        cur["edge_delta"] = edge_delta
        self._flush(f"complete {key} @ {sha}")
        return cur

    def record_gate(self, run_no, verdict):
        """Store a sweep_audit verdict on the run entry. Advisory; never blocks."""
        key = str(int(run_no))
        cur = self._data["runs"].get(key)
        if cur is None:
            cur = self.claim(run_no)
        cur["gate_verdict"] = verdict
        self._flush(f"gate {key}: {verdict}")
        return cur

    # --- queries -----------------------------------------------------
    def check_startable(self, run_no, max_stale_hours=48):
        """Run 465. Refuse to start `run_no` if a *different, lower* run is still
        `dispatched` and older than `max_stale_hours` -- a crashed prior run that
        never completed. A fresh session / the cron calls this before starting.

        Returns (ok: bool, reason: str). ok=True with reason "" when clear.
        A recent in-flight run (younger than the threshold) does NOT block: the
        assumption is another session is legitimately mid-run.
        """
        now = _now()
        cutoff = max_stale_hours * 3600.0
        stale = []
        for r in self._data["runs"].values():
            if r["state"] != DISPATCHED:
                continue
            if int(r["run_no"]) >= int(run_no):
                continue
            age = now - (r.get("dispatched_at") or now)
            if age > cutoff:
                stale.append((int(r["run_no"]), age))
        if stale:
            stale.sort()
            rn, age = stale[0]
            return (False, f"run {rn} still dispatched and stale "
                           f"({age / 3600.0:.1f}h > {max_stale_hours}h); "
                           f"resolve it before starting run {run_no}")
        return (True, "")

    def status(self):
        done = sorted(int(r["run_no"]) for r in self._data["runs"].values()
                      if r["state"] == DONE)
        in_flight = sorted(int(r["run_no"]) for r in self._data["runs"].values()
                           if r["state"] == DISPATCHED)
        highest_done = done[-1] if done else None
        # next run: one past the max of (highest done, highest in-flight, 0)
        seen = done + in_flight
        next_run = (max(seen) + 1) if seen else 1
        return {
            "highest_done": highest_done,
            "in_flight": in_flight,
            "next_run": next_run,
            "n_done": len(done),
        }


def _selftest():
    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="orch-ledger-"))
    checks = {}
    try:
        p = tmp / "orchestration_ledger.json"
        L = OrchestrationLedger(p)

        # --- sweep a size-like parameter: claim/complete n for n in 2..15 ---
        for n in range(2, 16):
            L.claim(n, agent=f"sess-{n}")
            st = L.status()
            checks[f"n={n}: in_flight while dispatched"] = st["in_flight"] == [n]
            checks[f"n={n}: next_run is n+1 while in flight"] = st["next_run"] == n + 1
            L.complete(n, sha=f"sha{n:03d}", node_delta=1, edge_delta=3)
            st = L.status()
            checks[f"n={n}: highest_done tracks n"] = st["highest_done"] == n
            checks[f"n={n}: no in_flight after complete"] = st["in_flight"] == []
            checks[f"n={n}: next_run is n+1 after complete"] = st["next_run"] == n + 1
        checks["after sweep, n_done == 14"] = L.status()["n_done"] == 14

        # --- stale in-flight: claim without complete ---
        L.claim(16, agent="sess-16")
        L.claim(17, agent="sess-17")
        st = L.status()
        checks["two stale in-flight runs surface, sorted"] = st["in_flight"] == [16, 17]
        checks["highest_done unchanged by stale claims"] = st["highest_done"] == 15
        checks["next_run is past the highest in-flight"] = st["next_run"] == 18
        L.complete(16, sha="sha016")
        checks["completing one leaves the other stale"] = L.status()["in_flight"] == [17]

        # --- idempotency: re-claim a still-dispatched run ---
        before = dict(L.get(17))
        L.claim(17, agent="sess-17b")
        after = L.get(17)
        checks["re-claim keeps state dispatched"] = after["state"] == DISPATCHED
        checks["re-claim refreshes agent"] = after["agent"] == "sess-17b"
        checks["re-claim does not create a duplicate"] = len(
            [r for r in L.runs.values() if r["run_no"] == 17]) == 1
        checks["re-claim moved dispatched_at forward"] = (
            after["dispatched_at"] >= before["dispatched_at"])

        # --- re-claim refusal: a done run cannot be re-claimed ---
        try:
            L.claim(5)
            checks["re-claiming a done run raises"] = False
        except ValueError:
            checks["re-claiming a done run raises"] = True

        # --- record_gate is advisory ---
        L.record_gate(15, "audit ok")
        checks["gate verdict stored on the run entry"] = L.get(15)["gate_verdict"] == "audit ok"
        checks["record_gate did not change state"] = L.get(15)["state"] == DONE
        L.record_gate(99, "audit suf!")  # unknown run -> auto-claimed
        checks["record_gate on unknown run auto-claims it"] = L.get(99) is not None
        checks["... and that run is now in flight"] = 99 in L.status()["in_flight"]

        # --- audit log + reload from disk ---
        checks["audit log has many lines"] = (
            L.audit_path.exists() and L.audit_path.read_text(encoding="utf-8").count("\n") > 20)
        L2 = OrchestrationLedger(p)
        checks["reload: same run set"] = set(L2.runs) == set(L.runs)
        checks["reload: status is identical"] = L2.status() == L.status()
        checks["reload: completed sha survives"] = L2.get(10)["sha"] == "sha010"

        # --- empty ledger ---
        E = OrchestrationLedger(tmp / "empty.json")
        checks["empty ledger: next_run is 1"] = E.status()["next_run"] == 1
        checks["empty ledger: highest_done is None"] = E.status()["highest_done"] is None

        # --- run 465: check_startable stale-in-flight guard ---
        S = OrchestrationLedger(tmp / "startable.json")
        S.claim(40, agent="crashed")          # a prior run that never completed
        S.claim(41, agent="also-crashed")
        # sweep the threshold and the stale run's age; assert the boundary flips
        for max_stale in (6, 12, 24, 48):
            for age_h in range(2, 16):
                S.get("40")["dispatched_at"] = _now() - age_h * 3600.0
                S.get("41")["dispatched_at"] = _now() - age_h * 3600.0
                ok, reason = S.check_startable(42, max_stale_hours=max_stale)
                expect_ok = age_h <= max_stale
                checks[f"startable(max={max_stale}h, age={age_h}h) -> {expect_ok}"] = (
                    ok == expect_ok)
                if not ok:
                    checks[f"...reason names the stale run (max={max_stale},age={age_h})"] = (
                        "40" in reason)
        # boundary is clean: at exactly the threshold it is still ok, one past it blocks
        S.get("40")["dispatched_at"] = _now() - 24 * 3600.0
        S.get("41")["dispatched_at"] = _now() - 24 * 3600.0
        checks["startable: age == threshold is ok"] = S.check_startable(42, 24)[0] is True
        S.get("40")["dispatched_at"] = _now() - 24 * 3600.0 - 1
        checks["startable: age just past threshold blocks"] = (
            S.check_startable(42, 24)[0] is False)
        # no stale run -> ok
        S.complete(40, sha="x"); S.complete(41, sha="y")
        checks["startable: no stale run -> ok"] = S.check_startable(42, 24) == (True, "")
        # recent in-flight -> ok (another session legitimately mid-run)
        S.claim(43, agent="live")
        checks["startable: recent in-flight -> ok"] = S.check_startable(44, 24)[0] is True
        # a HIGHER dispatched run never blocks a lower start number
        checks["startable: a higher in-flight run does not block"] = (
            S.check_startable(42, 24)[0] is True)

        for k, ok in checks.items():
            if not ok:
                print(f"  [FAIL] {k}")
        allok = all(checks.values())
        print(f"  {sum(checks.values())}/{len(checks)} checks passed")
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for name in ("status", "claim", "complete", "gate"):
        sp = sub.add_parser(name)
        sp.add_argument("--ledger", default=str(DEFAULT))
        if name == "claim":
            sp.add_argument("run_no", type=int)
            sp.add_argument("--agent", default=None)
        elif name == "complete":
            sp.add_argument("run_no", type=int)
            sp.add_argument("sha")
            sp.add_argument("--node-delta", type=int, default=None)
            sp.add_argument("--edge-delta", type=int, default=None)
        elif name == "gate":
            sp.add_argument("run_no", type=int)
            sp.add_argument("verdict")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    L = OrchestrationLedger(args.ledger)
    if args.cmd == "status":
        print(json.dumps(L.status(), indent=2))
    elif args.cmd == "claim":
        print(json.dumps(L.claim(args.run_no, agent=args.agent), indent=2))
    elif args.cmd == "complete":
        print(json.dumps(L.complete(args.run_no, args.sha,
                                    node_delta=args.node_delta,
                                    edge_delta=args.edge_delta), indent=2))
    elif args.cmd == "gate":
        print(json.dumps(L.record_gate(args.run_no, args.verdict), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

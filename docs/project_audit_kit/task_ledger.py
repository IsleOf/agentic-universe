#!/usr/bin/env python3
"""A deterministic task ledger — the source of truth for what an agent
orchestration has to do, is doing, and has done.

`docs/practicing_what_we_preach.md` §4, "tasks get dropped": the research the
loop has folded (CordisBench — LLM state-reasoning degrades with system size;
ASPIRE — continued open-ended search erases earlier gains) says **do not let the
model hold task state in its context**. The ledger is a file the orchestrator
reads and writes; the LLM proposes tasks and reports outcomes, the ledger
decides what is ready and what has been dropped.

Anti-"dropped task" mechanisms:

  * `next_ready()` is a deterministic pick (oldest ready `pending` task whose
    deps are all `done`), so the orchestrator never has to *reason* about what
    to do next.
  * `sweep_stale(max_active_secs)` returns any task that was `claim`ed but not
    finished within a timeout back to `pending` — a worker that died or lost
    context does not silently lose its task (the PILOT supervisor pattern:
    re-dispatch from the ledger).
  * every mutation writes the whole ledger atomically and appends an audit line,
    so the history is inspectable (`ledger.audit`).

Statuses: `pending -> active -> done` on the happy path; `blocked` (waiting on an
external thing), `failed` (retries exhausted), `abandoned` (deliberately
dropped).

Pure stdlib. Not wired into the loop — it is a reference implementation of the
pattern for the owner's orchestrations (poly-bot etc.).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

OPEN = ("pending", "active", "blocked")
CLOSED = ("done", "failed", "abandoned")
STATUSES = OPEN + CLOSED
MAX_ATTEMPTS_DEFAULT = 3


def _now():
    return round(time.time(), 3)


class Ledger:
    def __init__(self, path, *, max_attempts=MAX_ATTEMPTS_DEFAULT):
        self.path = Path(path)
        self.max_attempts = max_attempts
        self.audit_path = self.path.with_suffix(self.path.suffix + ".audit")
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self._data = {"tasks": {}, "created": _now()}
            self._flush("init")

    # --- persistence -------------------------------------------------------
    def _flush(self, event):
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self._data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": _now(), "event": event}) + "\n")

    @property
    def tasks(self):
        return self._data["tasks"]

    def get(self, tid):
        return self._data["tasks"][tid]

    # --- mutations -------------------------------------------------------
    def add(self, goal, *, deps=(), owner=None, meta=None):
        tid = f"t_{uuid.uuid4().hex[:8]}"
        self._data["tasks"][tid] = {
            "id": tid, "goal": goal, "status": "pending",
            "deps": list(deps), "owner": owner, "meta": meta or {},
            "attempts": 0, "result_ref": None, "notes": [],
            "created": _now(), "updated": _now(), "claimed_at": None,
        }
        self._flush(f"add {tid}")
        return tid

    def _set(self, tid, **fields):
        t = self._data["tasks"][tid]
        t.update(fields)
        t["updated"] = _now()

    def claim(self, tid, owner):
        t = self.get(tid)
        if t["status"] != "pending":
            raise ValueError(f"{tid} is {t['status']!r}, not pending")
        if not self._deps_done(tid):
            raise ValueError(f"{tid} has unfinished deps")
        self._set(tid, status="active", owner=owner, claimed_at=_now())
        self._flush(f"claim {tid} by {owner}")

    def complete(self, tid, result_ref=None):
        self._set(self.get(tid)["id"], status="done", result_ref=result_ref, claimed_at=None)
        self._flush(f"complete {tid}")

    def fail(self, tid, note):
        t = self.get(tid)
        t["attempts"] += 1
        t["notes"].append({"ts": _now(), "note": note})
        if t["attempts"] >= self.max_attempts:
            self._set(tid, status="failed", claimed_at=None)
            self._flush(f"fail {tid} (attempts exhausted)")
        else:
            self._set(tid, status="pending", owner=None, claimed_at=None)
            self._flush(f"fail {tid} -> pending (retry {t['attempts']}/{self.max_attempts})")

    def block(self, tid, note):
        t = self.get(tid)
        t["notes"].append({"ts": _now(), "note": note})
        self._set(tid, status="blocked", claimed_at=None)
        self._flush(f"block {tid}")

    def unblock(self, tid):
        self._set(self.get(tid)["id"], status="pending")
        self._flush(f"unblock {tid}")

    def abandon(self, tid, note):
        t = self.get(tid)
        t["notes"].append({"ts": _now(), "note": note})
        self._set(tid, status="abandoned", claimed_at=None)
        self._flush(f"abandon {tid}")

    # --- queries -------------------------------------------------------
    def _deps_done(self, tid):
        return all(self._data["tasks"].get(d, {}).get("status") == "done"
                   for d in self._data["tasks"][tid]["deps"])

    def next_ready(self, owner=None):
        """Deterministic: the oldest `pending` task whose deps are all done.
        Returns the task dict or None."""
        ready = [t for t in self._data["tasks"].values()
                 if t["status"] == "pending" and self._deps_done(t["id"])]
        ready.sort(key=lambda t: (t["created"], t["id"]))
        return ready[0] if ready else None

    def sweep_stale(self, max_active_secs):
        """Any `active` task claimed longer ago than `max_active_secs` goes back
        to `pending` (a worker died or lost context). Returns the ids swept."""
        cutoff = _now() - max_active_secs
        swept = []
        for t in self._data["tasks"].values():
            if t["status"] == "active" and (t["claimed_at"] or 0) < cutoff:
                t["attempts"] += 1
                t["notes"].append({"ts": _now(), "note": f"stale sweep (claimed_at {t['claimed_at']})"})
                if t["attempts"] >= self.max_attempts:
                    self._set(t["id"], status="failed", owner=None, claimed_at=None)
                else:
                    self._set(t["id"], status="pending", owner=None, claimed_at=None)
                swept.append(t["id"])
        if swept:
            self._flush(f"sweep_stale {swept}")
        return swept

    def summary(self):
        by = {s: 0 for s in STATUSES}
        for t in self._data["tasks"].values():
            by[t["status"]] += 1
        return {"total": len(self._data["tasks"]), "by_status": by,
                "open": sum(by[s] for s in OPEN), "closed": sum(by[s] for s in CLOSED)}


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="task-ledger-"))
    try:
        L = Ledger(tmp / "ledger.json", max_attempts=2)
        a = L.add("do A")
        b = L.add("do B", deps=[a])
        c = L.add("do C")

        checks = {}
        checks["next_ready is the oldest dep-free pending task (A, not B)"] = \
            L.next_ready()["id"] == a
        L.claim(a, "worker-1")
        checks["claimed A is active"] = L.get(a)["status"] == "active"
        checks["next_ready skips B (dep A not done) -> C"] = L.next_ready()["id"] == c
        try:
            L.claim(b, "worker-2"); checks["claiming a dep-blocked task raises"] = False
        except ValueError:
            checks["claiming a dep-blocked task raises"] = True
        L.complete(a, result_ref="out/a.txt")
        checks["A done, result_ref stored"] = \
            L.get(a)["status"] == "done" and L.get(a)["result_ref"] == "out/a.txt"
        checks["now B is ready"] = L.next_ready()["id"] == b

        # retry then exhaust
        L.claim(b, "worker-3")
        L.fail(b, "boom 1")
        checks["fail below max -> back to pending, attempts=1"] = \
            L.get(b)["status"] == "pending" and L.get(b)["attempts"] == 1
        L.claim(b, "worker-3")
        L.fail(b, "boom 2")
        checks["fail at max -> failed"] = L.get(b)["status"] == "failed"

        # stale sweep: claim C, pretend it was claimed long ago
        L.claim(c, "worker-4")
        L.get(c)["claimed_at"] = _now() - 10_000
        swept = L.sweep_stale(max_active_secs=3600)
        checks["stale active task swept back to pending"] = \
            swept == [c] and L.get(c)["status"] == "pending" and L.get(c)["owner"] is None

        # audit + reload
        checks["audit log has lines"] = L.audit_path.exists() and L.audit_path.read_text().count("\n") > 5
        L2 = Ledger(tmp / "ledger.json")
        checks["ledger reloads from disk"] = set(L2.tasks) == {a, b, c}
        s = L2.summary()
        checks["summary counts add up"] = s["total"] == 3 and s["open"] + s["closed"] == 3

        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        allok = all(checks.values())
        print(f"\n  final summary: {json.dumps(L2.summary())}")
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for name, args in [("add", ["goal"]), ("claim", ["tid", "owner"]), ("complete", ["tid"]),
                       ("fail", ["tid", "note"]), ("block", ["tid", "note"]), ("next", []),
                       ("sweep", ["secs"]), ("summary", []), ("list", [])]:
        sp = sub.add_parser(name)
        if name not in ("selftest",):
            sp.add_argument("--ledger", default="task_ledger.json")
        for a in args:
            sp.add_argument(a)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    L = Ledger(args.ledger)
    if args.cmd == "add":
        print(L.add(args.goal))
    elif args.cmd == "claim":
        L.claim(args.tid, args.owner); print("claimed")
    elif args.cmd == "complete":
        L.complete(args.tid); print("done")
    elif args.cmd == "fail":
        L.fail(args.tid, args.note); print(L.get(args.tid)["status"])
    elif args.cmd == "block":
        L.block(args.tid, args.note); print("blocked")
    elif args.cmd == "next":
        t = L.next_ready(); print(json.dumps(t, indent=2) if t else "(nothing ready)")
    elif args.cmd == "sweep":
        print("swept:", L.sweep_stale(float(args.secs)))
    elif args.cmd == "summary":
        print(json.dumps(L.summary(), indent=2))
    elif args.cmd == "list":
        for t in sorted(L.tasks.values(), key=lambda x: x["created"]):
            print(f"{t['id']}  {t['status']:9}  {t['goal']}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

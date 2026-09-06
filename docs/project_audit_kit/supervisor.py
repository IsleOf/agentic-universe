#!/usr/bin/env python3
"""A PILOT-pattern live supervisor over a `task_ledger`.

`docs/practicing_what_we_preach.md` §4 recommendation #5, and the folded
research it rests on:

  * `concept_self_improvement_should_be_live_a_supervisor_steers_and_aborts_the_active_worker`
    (PILOT, arXiv:2608.26530) — a *separate* supervisor that can redirect or
    ABORT the active worker mid-run, and distils failure modes into reusable
    notes during execution.
  * `concept_component_lifecycle_reasoning_degrades_with_size` (CordisBench) —
    the supervisor's decisions (dispatch what, abort what) are computed from the
    ledger, not reasoned by an LLM.
  * `concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic`
    (run 218) — the ledger's dep graph is the deterministic decomposition; each
    task's `result_ref` is its verifiable outcome.

This is a *skeleton*: `run_worker` is a callable you supply — it takes a task
dict and returns `(ok: bool, result_ref: str | None, note: str)`. Swap in a real
CLI-agent invocation. The supervisor supplies everything else: dispatch order,
stale recovery, per-task deadlines with abort, retry budgeting, and a
failure-mode digest that rides along on later dispatches of the same task.

Pure stdlib. Not wired into the loop — a reference implementation for the
owner's orchestrations.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from task_ledger import Ledger  # noqa: E402


class Supervisor:
    """Drives a Ledger to completion (or to `failed`/`blocked`) via `run_worker`.

    `run_worker(task, *, hints)` -> (ok, result_ref, note). `hints` carries the
    failure-mode digest for this task (PILOT's live self-evolution, lightweight).
    """

    def __init__(self, ledger, run_worker, *, task_deadline_secs=1800,
                 stale_after_secs=None, max_ticks=10_000, clock=time.time):
        self.L = ledger if isinstance(ledger, Ledger) else Ledger(ledger)
        self.run_worker = run_worker
        self.task_deadline_secs = task_deadline_secs
        self.stale_after_secs = stale_after_secs or (task_deadline_secs * 2)
        self.max_ticks = max_ticks
        self.clock = clock
        self._failure_digest = {}   # goal -> [notes] (survives task id churn within a run)
        self.log = []               # (tick, event, detail)

    def _hints_for(self, task):
        return list(self._failure_digest.get(task["goal"], []))

    def _record_failure(self, task, note):
        self._failure_digest.setdefault(task["goal"], []).append(note)

    def tick(self):
        """One supervision step. Returns an event string, or 'idle' / 'done'."""
        L = self.L
        # 1. recover anything a dead worker abandoned
        swept = L.sweep_stale(self.stale_after_secs)
        if swept:
            self.log.append((len(self.log), "sweep_stale", swept))
            return f"swept {swept}"
        # 2. abort an active task past its deadline (live steering)
        now = self.clock()
        for t in list(L.tasks.values()):
            if t["status"] == "active" and t["claimed_at"] and now - t["claimed_at"] > self.task_deadline_secs:
                L.fail(t["id"], f"aborted by supervisor: past {self.task_deadline_secs}s deadline")
                self._record_failure(t, "previous attempt exceeded the deadline — decompose or narrow scope")
                self.log.append((len(self.log), "abort", t["id"]))
                return f"aborted {t['id']}"
        # 3. dispatch the next ready task
        t = L.next_ready()
        if t is None:
            summ = L.summary()
            return "done" if summ["open"] == 0 else "idle"
        L.claim(t["id"], owner="supervisor-worker")
        t0 = self.clock()
        ok, result_ref, note = self.run_worker(dict(L.get(t["id"])), hints=self._hints_for(t))
        elapsed = self.clock() - t0
        if ok and elapsed > self.task_deadline_secs:
            # the worker finished, but over the deadline — for a live orchestration
            # the supervisor would have aborted it; here we reject the result and
            # let the retry budget handle it (PILOT: don't trust an over-budget run)
            ok, note = False, (note or "") + f" [over deadline: {elapsed:.0f}s > {self.task_deadline_secs}s]"
        if ok:
            L.complete(t["id"], result_ref=result_ref)
            self.log.append((len(self.log), "complete", t["id"]))
            return f"completed {t['id']}"
        L.fail(t["id"], note or "worker reported failure")
        self._record_failure(t, note or "worker reported failure")
        self.log.append((len(self.log), "fail", t["id"]))
        return f"failed {t['id']}"

    def run(self):
        """Tick until nothing is open (or max_ticks). Returns the final summary."""
        for _ in range(self.max_ticks):
            ev = self.tick()
            if ev == "done":
                break
            if ev == "idle":
                # nothing ready and nothing to recover, but tasks are still open
                # (all blocked, or deps on a failed task) — stop, don't spin.
                break
        return self.L.summary()


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="supervisor-"))
    try:
        L = Ledger(tmp / "ledger.json", max_attempts=3)
        a = L.add("task A")
        b = L.add("task B", deps=[a])
        c = L.add("flaky C")

        # a flaky worker: A ok; B ok; C fails twice then succeeds. Records that
        # it saw the failure-mode hint on the retry.
        state = {"c_calls": 0, "saw_hint_on_retry": False}
        def worker(task, *, hints):
            if task["goal"] == "flaky C":
                state["c_calls"] += 1
                if state["c_calls"] >= 2 and hints:
                    state["saw_hint_on_retry"] = True
                if state["c_calls"] < 3:
                    return (False, None, "C: transient error")
                return (True, "out/c.txt", "")
            return (True, f"out/{task['goal'][-1].lower()}.txt", "")

        sup = Supervisor(L, worker, max_ticks=50)
        summary = sup.run()

        checks = {
            "all three tasks reached done": summary["by_status"]["done"] == 3,
            "nothing left open": summary["open"] == 0,
            "flaky C was retried to success (3 calls)": state["c_calls"] == 3,
            "the failure-mode digest reached the retry": state["saw_hint_on_retry"],
            "B completed after A (dep order held)":
                [e for e in sup.log if e[1] == "complete" and e[2] == a][0][0]
                < [e for e in sup.log if e[1] == "complete" and e[2] == b][0][0],
            "supervisor log records completes and fails":
                sum(1 for e in sup.log if e[1] == "complete") == 3
                and sum(1 for e in sup.log if e[1] == "fail") == 2,
        }

        # stale-recovery: a worker that claims and never returns
        L2 = Ledger(tmp / "l2.json")
        d = L2.add("hangs")
        L2.claim(d, "dead-worker")
        L2.get(d)["claimed_at"] = time.time() - 10_000
        recovered = {"n": 0}
        def worker2(task, *, hints):
            recovered["n"] += 1
            return (True, "out/d.txt", "")
        sup2 = Supervisor(L2, worker2, stale_after_secs=3600, max_ticks=20)
        s2 = sup2.run()
        checks["a hung worker's task is swept and re-dispatched"] = \
            s2["by_status"]["done"] == 1 and recovered["n"] == 1

        # deadline abort: a worker that "runs long" (simulated via a fake clock)
        L3 = Ledger(tmp / "l3.json", max_attempts=1)
        e = L3.add("slow")
        clk = {"t": 1000.0}
        def worker3(task, *, hints):
            clk["t"] += 5000          # the "work" took 5000s
            return (True, "out/e.txt", "")
        sup3 = Supervisor(L3, worker3, task_deadline_secs=1800,
                          clock=lambda: clk["t"], max_ticks=20)
        s3 = sup3.run()
        checks["a task that blew its deadline ends failed, not silently done"] = \
            s3["by_status"]["failed"] == 1 and s3["by_status"]["done"] == 0

        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        allok = all(checks.values())
        print(f"\n  run 1 summary: {json.dumps(summary)}")
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

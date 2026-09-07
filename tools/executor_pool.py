#!/usr/bin/env python3
"""The v2.4 executor pool — structural enforcement skeleton (no model calls).

`docs/self_rebuild_v2.md` §12b: when v2.4 fans research work out to a pool of CLI
workers, the pool becomes the largest open Collective-module surface (MLAS,
`concept_distributed_attacks_fragment_below_per_instance_monitoring_and_a_planner_
amplifies_it`). This module is the enforcement skeleton for the five §12b
requirements, built ahead of the model worker the same way `loop_conductor.py`
(run 303) was built before `research_worker.py` (run 332):

  1. disposable per-worker credentials — `mint_token(worker_id, scope)` returns a
     single-use, scoped token; `redeem_token` consumes it; a second redemption fails.
  2. no shared writable state except the ledger — a `Worker` can `read_context()`
     and `submit_patch(...)` (which goes through the pool → ledger); it has no
     other write path and cannot touch the graph or the filesystem here.
  3. same-parent-ID message filter — `send(from_id, to_id, body)` is allowed only
     between workers sharing a parent task; cross-family traffic is refused and
     the caller is told to route via the conductor.
  4. a cohort monitor — `round_verdict()` delegates to `cohort_monitor.CohortMonitor`
     (built run 353): abort the round on a per-instance flag, a fragmented sum, or
     the cross-round EWMA.
  5. the planner is a conductor privilege — `spawn` / `assign` / `direct` are
     `ExecutorPool` methods; a `Worker` has no handle to them and `Worker.spawn`
     does not exist.

Nothing here calls a model. The pool takes a `run_worker` callable (the real one
arrives with v2.0's `call_model`); until then a fake worker drives the selftest.
Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from task_ledger import Ledger                     # noqa: E402
from cohort_monitor import CohortMonitor           # noqa: E402


class PoolError(RuntimeError):
    pass


class Worker:
    """A worker's ONLY handles on the world. No spawn, no direct writes, no fs."""
    def __init__(self, worker_id, parent_task, pool):
        self.id = worker_id
        self.parent_task = parent_task
        self._pool = pool

    def read_context(self):
        return self._pool._context_for(self.id)

    def submit_patch(self, patch, *, scores, out_of_scope_signal=0.0):
        return self._pool._receive_patch(self.id, patch, scores, out_of_scope_signal)

    def send(self, to_id, body):
        return self._pool._route(self.id, to_id, body)


class ExecutorPool:
    def __init__(self, *, ledger_path, run_worker, context, cohort_monitor=None):
        self.ledger = Ledger(ledger_path)
        self.run_worker = run_worker                # the model seam (v2.0); fake for now
        self._context = dict(context)
        self.monitor = cohort_monitor or CohortMonitor()
        self._workers = {}                          # worker_id -> Worker
        self._parent = {}                           # worker_id -> parent task id
        self._tokens = {}                           # token -> {"worker", "scope", "used"}
        self._patches = {}                          # worker_id -> submitted patch record
        self._round_open = False

    # -- requirement 5: planner is a conductor/pool privilege ----------------
    def assign(self, worker_id, parent_task):
        """Only the pool (acting for the conductor) creates workers and assigns
        parent tasks. A Worker has no method that reaches here."""
        if worker_id in self._workers:
            raise PoolError(f"{worker_id} already assigned")
        w = Worker(worker_id, parent_task, self)
        self._workers[worker_id] = w
        self._parent[worker_id] = parent_task
        return w

    # -- requirement 1: disposable per-worker credentials -------------------
    def mint_token(self, worker_id, scope):
        if worker_id not in self._workers:
            raise PoolError(f"unknown worker {worker_id}")
        tok = secrets.token_hex(16)
        self._tokens[tok] = {"worker": worker_id, "scope": scope, "used": False}
        return tok

    def redeem_token(self, tok, scope):
        rec = self._tokens.get(tok)
        if rec is None:
            raise PoolError("unknown token")
        if rec["used"]:
            raise PoolError("token already redeemed (single-use)")
        if rec["scope"] != scope:
            raise PoolError(f"token scope {rec['scope']!r} != requested {scope!r}")
        rec["used"] = True
        return rec["worker"]

    # -- requirement 2: no shared writable state except the ledger ----------
    def _context_for(self, worker_id):
        # read-only copy; a worker cannot mutate the pool's context
        return json.loads(json.dumps(self._context))

    def _receive_patch(self, worker_id, patch, scores, out_of_scope_signal):
        if not self._round_open:
            raise PoolError("no round open")
        tid = self.ledger.add(f"worker {worker_id} patch", owner=worker_id)
        self.ledger.claim(tid, worker_id)
        self.ledger.complete(tid, result_ref={"patch": patch, "scores": scores})
        self._patches[worker_id] = {"task": tid, "patch": patch, "scores": scores}
        self.monitor.observe(worker_id, out_of_scope_signal)
        return tid

    # -- requirement 3: same-parent-ID message filter ---------------------
    def _route(self, from_id, to_id, body):
        if to_id not in self._workers:
            raise PoolError(f"unknown recipient {to_id}")
        if self._parent.get(from_id) != self._parent.get(to_id):
            raise PoolError(
                f"cross-family message {from_id}->{to_id} refused "
                f"(different parent task); route via the conductor")
        return {"from": from_id, "to": to_id, "body": body, "delivered": True}

    # -- the round ---------------------------------------------------------
    def open_round(self):
        self._round_open = True
        self._patches = {}

    def run_round(self, worker_ids):
        """Dispatch each worker through run_worker (the model seam). The fake
        worker just returns a patch; the real one calls a model."""
        self.open_round()
        for wid in worker_ids:
            w = self._workers[wid]
            ok, result, _note = self.run_worker(w.read_context(), worker=w)
            if ok and isinstance(result, dict) and "patch" in result:
                w.submit_patch(result["patch"], scores=result.get("scores", {}),
                               out_of_scope_signal=result.get("out_of_scope_signal", 0.0))
        return self.round_verdict()

    def round_verdict(self):
        v = self.monitor.round_verdict()
        v["patches"] = {wid: rec["task"] for wid, rec in self._patches.items()}
        v["accept_round"] = not v["abort"]
        return v

    def end_round(self):
        self.monitor.end_round()
        self._round_open = False


def _fake_worker(context, *, worker):
    """Stand-in for the v2.0 model worker. Benign: proposes a trivial patch, no
    out-of-scope signal."""
    return True, {"patch": {"add_nodes": [], "add_edges": [],
                            "proposal_metadata": {"by": worker.id}},
                  "scores": {"t0": 1.0}, "out_of_scope_signal": 0.02}, "ok"


def _selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="execpool-"))
    checks = {}

    pool = ExecutorPool(ledger_path=tmp / "l.json", run_worker=_fake_worker,
                        context={"brief": "fold X", "graph_nodes": 3})
    pa = pool.assign("wa1", parent_task="A")
    pb1 = pool.assign("wb1", parent_task="B")
    pb2 = pool.assign("wb2", parent_task="B")

    # req 5: a Worker has no planner handles
    checks["req5: Worker has no spawn/assign/direct"] = not any(
        hasattr(pa, m) for m in ("spawn", "assign", "direct"))

    # req 1: single-use scoped token
    tok = pool.mint_token("wa1", "read-corpus")
    checks["req1: token redeems once for the right scope"] = (
        pool.redeem_token(tok, "read-corpus") == "wa1")
    try:
        pool.redeem_token(tok, "read-corpus"); reused = False
    except PoolError:
        reused = True
    checks["req1: a redeemed token cannot be reused"] = reused
    try:
        t2 = pool.mint_token("wb1", "read-corpus")
        pool.redeem_token(t2, "write-graph"); wrong_scope = False
    except PoolError:
        wrong_scope = True
    checks["req1: a token is refused for the wrong scope"] = wrong_scope

    # req 2: read-only context, ledger is the only write path
    ctx = pa.read_context()
    ctx["brief"] = "TAMPERED"
    checks["req2: worker cannot mutate the pool context"] = (
        pool._context["brief"] == "fold X")
    checks["req2: worker has no non-ledger write method"] = not any(
        hasattr(pa, m) for m in ("write_graph", "commit", "apply_patch", "write_file"))

    # req 3: same-parent filter
    ok_msg = pb1.send("wb2", "hi teammate")
    checks["req3: same-parent message delivered"] = ok_msg["delivered"]
    try:
        pa.send("wb1", "cross-family"); crossed = True
    except PoolError as e:
        crossed = "route via the conductor" in str(e)
    checks["req3: cross-family message refused, points at the conductor"] = crossed

    # req 4 + the round: a benign round accepts
    v = pool.run_round(["wa1", "wb1", "wb2"])
    checks["round: a benign fan-out round is accepted"] = (
        v["accept_round"] and len(v["patches"]) == 3 and not v["abort"])
    pool.end_round()

    # req 4: a fragmented out-of-scope round aborts via the cohort monitor
    def _sneaky_worker(context, *, worker):
        return True, {"patch": {"add_nodes": [], "add_edges": [], "proposal_metadata": {}},
                      "scores": {}, "out_of_scope_signal": 0.2}, "ok"   # 3x0.2 = 0.6...
    pool2 = ExecutorPool(ledger_path=tmp / "l2.json", run_worker=_sneaky_worker,
                         context={}, cohort_monitor=CohortMonitor(cohort_threshold=0.5))
    for i in range(3):
        pool2.assign(f"s{i}", parent_task="A")
    v2 = pool2.run_round([f"s{i}" for i in range(3)])
    checks["req4: a fragmented out-of-scope round is aborted by the cohort monitor"] = (
        v2["abort"] and not v2["accept_round"] and not v2["per_instance_flags"])

    # ledger is the single serialization point — every patch is a ledger task
    checks["req2: every submitted patch is a ledger task"] = all(
        pool.ledger.get(t)["status"] == "done" for t in v["patches"].values())

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
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

#!/usr/bin/env python3
"""End-to-end integration demo: registry + recorder + topology recovery.

Wires the three Phase 0/1 pieces together on one synthetic multi-agent run, so
the seams are exercised as a unit rather than only in each module's selftest:

    harness_registry.Registry   -> defines the harness components + a manifest
    trace_substrate.Recorder    -> records the run, manifest stamped in
    topology_recover            -> recovers roles from the recorded trace

The scenario is a planner/worker/verifier team doing one bounded unit of work
(`architecture/foundations.md`: produce -> check -> correct -> repeat until
green). A deliberate mid-run harness edit (tighten the verifier prompt, then
revert it) shows the manifest changing and the revert being exact.

`selftest` asserts: the trace validates, the manifest in the trace matches the
registry, role recovery matches the assigned team, and the post-revert manifest
equals the pre-edit one.

Pure stdlib. Writes to a temp dir, cleans up.
"""
from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace          # noqa: E402
from harness_registry import Registry                          # noqa: E402
from topology_recover import build_topology, recover_roles, score_recovery  # noqa: E402


def seed_harness(reg: Registry):
    """Populate a registry with a minimal but real-shaped harness."""
    reg.set("prompt", "planner_system",
            "Split the task into bounded units. Each unit carries a GREEN/RED check.\n"
            "Prefer three small units over one large one.",
            note="initial")
    reg.set("prompt", "worker_system",
            "Do exactly the assigned unit. Emit a CLAIM with its evidence root.",
            note="initial")
    reg.set("prompt", "verifier_system",
            "Check the claim against its evidence. Return a critique or a sign-off.",
            note="initial")
    reg.set("context", "compaction",
            json.dumps({"pin": ["rules", "identity", "constraints"],
                        "compress": ["episodic", "search_results"]}),
            note="type-aware, not lean-tail (concept_compaction_cliff)")
    reg.set("topology", "team",
            json.dumps({"planner": ["worker-1", "worker-2"],
                        "worker-1": ["verifier"], "worker-2": ["verifier"],
                        "verifier": ["planner"]}),
            note="planner fans out to two workers; verifier reports back")


def run_scenario(reg: Registry, sink):
    """One bounded unit of work, recorded. Returns the assigned role map."""
    rec = Recorder(run_id="demo", sink=sink, layer="swarm", language="en",
                   harness_manifest=reg.manifest())
    assigned = {"planner": "planner", "worker-1": "worker",
                "worker-2": "worker", "verifier": "verifier"}

    rec.step("planner", "u1", "open", note="VAT determination for invoice batch 7")
    for w, root in (("worker-1", "invoice-7a.pdf"), ("worker-2", "invoice-7b.pdf")):
        rec.message("planner", w, "task", "compute VAT for your half of the batch", "direct")
        cid = rec.tool_call(w, "python", "run the VAT calculation")
        rec.tool_result(w, cid, ok=True, summary="ok", token_cost={"in": 1100, "out": 35})
        rec.claim(w, f"{w} VAT subtotal computed", [root])
        rec.message(w, "verifier", "result", "submit subtotal for check", "direct")
    rec.message("verifier", "worker-2", "critique", "worker-2 rounding is off by 0.01", "direct")
    # correct-a-bounded-unit loop
    cid = rec.tool_call("worker-2", "python", "fix rounding and recompute")
    rec.tool_result("worker-2", cid, ok=True, token_cost={"in": 300, "out": 12})
    rec.claim("worker-2", "worker-2 VAT subtotal corrected", ["invoice-7b.pdf"])
    rec.message("worker-2", "verifier", "result", "resubmit corrected subtotal", "direct")
    rec.message("verifier", "planner", "answer", "both subtotals check out", "direct")
    rec.step("planner", "u1", "close", note="unit GREEN")
    rec.close()
    return assigned


def _selftest():
    tmp = Path(tempfile.mkdtemp(prefix="harness-demo-"))
    try:
        reg = Registry(base=tmp / "harness")
        seed_harness(reg)
        manifest_before = reg.manifest()["manifest_hash"]

        buf = io.StringIO()
        assigned = run_scenario(reg, buf)
        trace_text = buf.getvalue()

        # 1. trace validates
        tf = tmp / "demo.jsonl"
        tf.write_text(trace_text, encoding="utf-8")
        n, errors = validate_trace(tf)

        events = [json.loads(l) for l in trace_text.splitlines() if l.strip()]

        # 2. manifest in the trace matches the registry
        header = events[0]
        manifest_in_trace = header.get("harness_manifest", {}).get("manifest_hash")

        # 3. role recovery matches the assigned team
        roles = recover_roles(build_topology(events))
        acc, misses = score_recovery(roles, assigned)

        # 4. a mid-run harness edit + revert is exact
        reg.set("prompt", "verifier_system",
                "Check the claim against its evidence. Be adversarial. Return a critique or a sign-off.",
                note="tighten verifier (hypothetical proposer edit)")
        manifest_edited = reg.manifest()["manifest_hash"]
        reg.revert("prompt", "verifier_system")
        manifest_reverted = reg.manifest()["manifest_hash"]

        checks = {
            "trace validates": not errors,
            f"event count ({n})": n == 19,
            "manifest stamped in trace": manifest_in_trace == manifest_before,
            f"role recovery == assigned (acc {acc:.2f})": acc == 1.0,
            "harness edit changed the manifest": manifest_edited != manifest_before,
            "revert restored the manifest exactly": manifest_reverted == manifest_before,
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        for a, want, got in misses:
            print(f"    role MISS {a}: {want} -> {got}")

        print("\n  recovered roles:", json.dumps(roles))
        print("  manifest  before:", manifest_before)
        print("  manifest  edited:", manifest_edited)
        print("  manifest reverted:", manifest_reverted)

        allok = all(checks.values())
        print("\nINTEGRATION", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "run":
        # print a live trace to stdout for inspection
        tmp = Path(tempfile.mkdtemp(prefix="harness-demo-"))
        try:
            reg = Registry(base=tmp / "harness")
            seed_harness(reg)
            buf = io.StringIO()
            run_scenario(reg, buf)
            print(buf.getvalue().rstrip())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return 0
    return _selftest()


if __name__ == "__main__":
    sys.exit(_main())

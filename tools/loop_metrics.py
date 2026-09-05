#!/usr/bin/env python3
"""Metrics over the autonomous-loop trace corpus — what Phase 3's proposer reads.

`tools/improvement_loop.py` runs its proposer on a synthetic compaction task.
For the proposer to work on the *real* loop harness it needs real signal: this
module computes it from the trace corpus (the adapter's replayed history in
`runtime/traces/loop-history.jsonl` plus live per-run summaries in
`runtime/observations/loop_runs/*.json`).

Metrics (all computed, no judgement):

  runs                        count of harness-layer run STEPs
  verified_citation_fraction  CLAIMs at full trust / all CLAIMs
  graph_write_rate            runs with a graph ARTIFACT / runs
  mean_events_per_run
  validation_pass_rate        graph_validate TOOL_RESULTs ok / total
  evidence_root_reuse         distinct roots cited by >1 run / distinct roots
                              (ancestry concentration — `concept_epistemic_sybil_collapse`)

`propose_loop_edit(metrics)` turns a below-threshold metric into a concrete
loop-harness edit (a `context`/`prompt` component change) plus a falsifiable
prediction. **The honest gap:** verifying that edit needs a frozen held-out set
of research tasks the loop can be re-run on. That does not exist. So the proposer
produces a real, grounded *proposal*; promotion stays manual until the held-out
set is built. This module is the half that can be built now.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import validate_trace  # noqa: E402

HISTORY_TRACE = ROOT / "runtime" / "traces" / "loop-history.jsonl"
LIVE_RUNS = ROOT / "runtime" / "observations" / "loop_runs"

THRESHOLDS = {
    "verified_citation_fraction": 0.60,   # most citations should be independently verified
    "validation_pass_rate": 1.00,         # the graph must never be committed invalid
}


def _load_trace(path):
    if not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def compute(trace_path=HISTORY_TRACE, live_dir=LIVE_RUNS):
    events = _load_trace(trace_path)

    run_steps = [e for e in events if e.get("kind") == "STEP" and e.get("phase") == "open"]
    runs = len(run_steps)
    claims = [e for e in events if e.get("kind") == "CLAIM"]
    verified = [c for c in claims if c.get("trust") == "full"]
    graph_writes = [e for e in events if e.get("kind") == "ARTIFACT"
                    and "graph" in str(e.get("path", ""))]
    val_results = [e for e in events if e.get("kind") == "TOOL_RESULT"]
    val_ok = [e for e in val_results if e.get("ok")]

    # evidence-root reuse across runs
    root_runs = {}
    cur_run = None
    for e in events:
        if e.get("kind") == "STEP" and e.get("phase") == "open":
            cur_run = e.get("step_id")
        if e.get("kind") == "CLAIM":
            for r in e.get("evidence_roots", []):
                root_runs.setdefault(r, set()).add(cur_run)
    reused = [r for r, rs in root_runs.items() if len(rs) > 1]

    # fold in live per-run summaries (finer-grained, authoritative where present)
    live = []
    if Path(live_dir).exists():
        for p in sorted(Path(live_dir).glob("run-*.json")):
            live.append(json.loads(p.read_text(encoding="utf-8")))
    live_cites = [c for s in live for c in s.get("citations", [])]
    live_verified = [c for c in live_cites if c.get("verified")]

    total_claims = len(claims) + len(live_cites)
    total_verified = len(verified) + len(live_verified)

    return {
        "runs": runs,
        "live_runs_recorded": len(live),
        "total_events": len(events),
        "mean_events_per_run": round(len(events) / runs, 1) if runs else 0,
        "verified_citation_fraction": round(total_verified / total_claims, 3) if total_claims else None,
        "graph_write_rate": round(len(graph_writes) / runs, 3) if runs else 0,
        "validation_pass_rate": round(len(val_ok) / len(val_results), 3) if val_results else None,
        "distinct_evidence_roots": len(root_runs),
        "evidence_root_reuse": round(len(reused) / len(root_runs), 3) if root_runs else 0,
        "reused_roots": sorted(reused),
    }


def propose_loop_edit(metrics):
    """Turn a below-threshold metric into a concrete loop-harness edit + prediction.
    Returns None if nothing is below threshold.
    """
    proposals = []
    vcf = metrics.get("verified_citation_fraction")
    if vcf is not None and vcf < THRESHOLDS["verified_citation_fraction"]:
        proposals.append({
            "component": ("context", "loop_policy"),
            "change": "add 'a run may fold at most ONE unverified citation; the rest must be "
                      "independently opened and checked' to the do_not / rules list",
            "prediction": {
                "metric": "verified_citation_fraction over the next 10 runs",
                "direction": "increase",
                "from": vcf,
                "to_at_least": THRESHOLDS["verified_citation_fraction"],
                "rationale": "the procedure already says verify three ways; making the per-run cap "
                             "explicit removes the ambiguity a busy run exploits",
            },
            "verification": "BLOCKED — needs a frozen held-out set of research tasks to re-run the "
                            "loop on; until then this is a grounded proposal, promoted manually",
        })
    vpr = metrics.get("validation_pass_rate")
    if vpr is not None and vpr < THRESHOLDS["validation_pass_rate"]:
        proposals.append({
            "component": ("prompt", "loop_procedure"),
            "change": "move the orphan check + validate step BEFORE any commit, and make a failed "
                      "validate abort the run with the graph reverted",
            "prediction": {"metric": "validation_pass_rate", "direction": "increase",
                           "from": vpr, "to_at_least": 1.0,
                           "rationale": "a validate that runs after staging can be skipped under time pressure"},
            "verification": "computable — replay the corpus and count post-edit invalid commits",
        })
    return proposals or None


def _selftest():
    import io
    import shutil
    import tempfile
    sys.path.insert(0, str(ROOT / "tools"))
    from harness_registry import Registry
    from trace_substrate import Recorder
    from loop_adapter import seed_loop_harness, replay_history, GRAPH

    tmp = Path(tempfile.mkdtemp(prefix="loop-metrics-"))
    try:
        reg = Registry(base=tmp / "h")
        seed_loop_harness(reg)
        rec = Recorder(run_id="hist", trace_dir=str(tmp / "traces"), layer="harness",
                       language="en", harness_manifest=reg.manifest())
        replay_history(GRAPH, rec)
        rec.close()
        trace = tmp / "traces" / "hist.jsonl"

        m = compute(trace_path=trace, live_dir=tmp / "none")
        n, errors = validate_trace(trace)

        checks = {
            "trace valid": not errors,
            "runs counted": m["runs"] >= 50,
            "verified_citation_fraction in [0,1]":
                m["verified_citation_fraction"] is None or 0 <= m["verified_citation_fraction"] <= 1,
            "validation_pass_rate == 1.0 (replay marks all VALID)": m["validation_pass_rate"] == 1.0,
            "evidence_root_reuse computed": 0 <= m["evidence_root_reuse"] <= 1,
            "reused roots surfaced": isinstance(m["reused_roots"], list),
            "propose_loop_edit returns a list or None":
                propose_loop_edit(m) is None or isinstance(propose_loop_edit(m), list),
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        print("\n  metrics:", json.dumps({k: v for k, v in m.items() if k != "reused_roots"}))
        print("  reused roots:", m["reused_roots"])
        props = propose_loop_edit(m)
        print("  proposal(s):", json.dumps(props) if props else "none (all metrics at/above threshold)")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Loop trace-corpus metrics (Phase 3 proposer input).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("report")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "report":
        m = compute()
        print(json.dumps(m, indent=2))
        props = propose_loop_edit(m)
        print("\nproposals:", json.dumps(props, indent=2) if props else "none")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

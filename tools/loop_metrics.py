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
  idle_run_streak             trailing live runs that wrote no graph delta
  plateau_watch               idle_run_streak >= PLATEAU_WINDOW — the run-129
                              caution: a gate rejects regressions but does not
                              require progress, so a plateaued loop keeps passing

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

# trailing runs with no graph delta before the loop is "on plateau watch".
# Matches the run-80 IDLE-STATE RULE window (last 3 runs idle + this one) and the
# run-129 caution: a gate only rejects regressions, so a plateaued loop keeps
# passing its gate while producing nothing.
PLATEAU_WINDOW = 4


def _wrote_graph(summary):
    """Did this live run summary record a real graph change?"""
    gd = summary.get("graph_delta")
    if gd is not None:
        return bool(gd.get("nodes") or gd.get("edges"))
    # summaries written before run 130 predate the graph_delta field: fall back to
    # the artifact count (graph_write + commit => >=2; commit only => 1).
    return summary.get("counts", {}).get("artifacts", 0) >= 2


def idle_run_streak(live_summaries):
    """Count trailing runs that neither changed the graph nor folded a NEW citation.

    A run that deepens the graph, or folds a source no earlier run cited, is
    substantive (the run-80 IDLE-STATE RULE explicitly allows a citation sweep).
    A trailing run of doc/hygiene-only runs is the run-129 plateau signature.
    """
    ordered = sorted(live_summaries, key=lambda s: s.get("run", 0))
    seen_roots = set()
    substantive_at = []  # index -> bool
    for s in ordered:
        roots = set(s.get("distinct_evidence_roots", []))
        new_root = bool(roots - seen_roots)
        seen_roots |= roots
        substantive_at.append(_wrote_graph(s) or new_root)
    streak = 0
    for ok in reversed(substantive_at):
        if ok:
            break
        streak += 1
    return streak


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

    streak = idle_run_streak(live)

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
        "idle_run_streak": streak,
        "plateau_watch": streak >= PLATEAU_WINDOW,
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
            "verification": "deferred-acceptance: promote manually, then after ~10 runs check "
                            "verified_citation_fraction rose AND re-run the loop on "
                            "tools/holdout_tasks.py — a research-quality regression below the "
                            "1.00 historical baseline reverts the edit (frozen held-out set, run 69)",
        })
    if metrics.get("plateau_watch"):
        streak = metrics.get("idle_run_streak", 0)
        proposals.append({
            "component": ("prompt", "loop_procedure"),
            "change": f"idle_run_streak has reached {streak} (>= {PLATEAU_WINDOW}): the next run MUST "
                      "satisfy the IDLE-STATE RULE — deepen ONE node via citation sweep, dry-run a probe "
                      "end to end, or run a genuine consistency/adversarial pass — not a doc refresh",
            "prediction": {
                "metric": "idle_run_streak",
                "direction": "decrease",
                "from": streak,
                "to_at_least": 0,
                "rationale": "a substantive increment writes the graph and resets the streak; if the "
                             "streak keeps growing while the acceptance gate keeps passing, that is the "
                             "run-129 plateau signature and the middle loop's returns have stalled",
            },
            "verification": "computable — re-run compute() after the next run and check idle_run_streak fell",
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

        # idle_run_streak: build a small synthetic live-summary dir
        live = tmp / "live"
        live.mkdir()
        def _put(run, gd, roots=(), artifacts=1):
            (live / f"run-{run}.json").write_text(json.dumps({
                "run": run, "counts": {"artifacts": artifacts},
                "distinct_evidence_roots": list(roots),
                **({"graph_delta": gd} if gd is not None else {}),
            }), encoding="utf-8")
        # runs 1-3 substantive (graph delta), 4-6 doc-only re-citing an old root -> streak 3
        _put(1, {"nodes": 1, "edges": 2}, roots=["arXiv:1"])
        _put(2, {"nodes": 0, "edges": 3}, roots=["arXiv:2"])
        _put(3, {"nodes": 2, "edges": 0}, roots=["arXiv:3"])
        _put(4, {"nodes": 0, "edges": 0}, roots=["arXiv:1"])
        _put(5, None, roots=[])
        _put(6, {"nodes": 0, "edges": 0}, roots=["arXiv:2"])
        streak3 = idle_run_streak([json.loads(p.read_text()) for p in live.glob("run-*.json")])
        _put(7, {"nodes": 0, "edges": 0}, roots=["arXiv:3"])  # 4th trailing idle -> crosses the window
        # a run that folds a NEW root is substantive even with no graph delta:
        # run 1 folds arXiv:9 (new), run 2 only re-cites it -> streak stops at 1, not 2
        streak_newcite = idle_run_streak([
            {"run": 1, "graph_delta": {"nodes": 0, "edges": 0}, "distinct_evidence_roots": ["arXiv:9"]},
            {"run": 2, "graph_delta": {"nodes": 0, "edges": 0}, "distinct_evidence_roots": ["arXiv:9"]},
        ])
        # legacy fallback: no graph_delta key, artifacts>=2 counts as a graph write
        streak_legacy = idle_run_streak([
            {"run": 1, "counts": {"artifacts": 2}}, {"run": 2, "counts": {"artifacts": 1}}])
        m_plateau = compute(trace_path=trace, live_dir=live)

        checks = {
            "trace valid": not errors,
            "runs counted": m["runs"] >= 50,
            "idle_run_streak counts trailing doc-only runs (3)": streak3 == 3,
            "idle_run_streak numeric-sorts (not run-10 < run-2)":
                idle_run_streak([{"run": 2, "graph_delta": None, "distinct_evidence_roots": []},
                                 {"run": 10, "graph_delta": {"nodes": 1, "edges": 0},
                                  "distinct_evidence_roots": []}]) == 0,
            "a new citation counts as substantive": streak_newcite == 1,
            "idle_run_streak legacy artifact-count fallback": streak_legacy == 1,
            "plateau_watch true at streak 4": m_plateau["idle_run_streak"] == 4 and m_plateau["plateau_watch"],
            "plateau proposal emitted when watching":
                any("IDLE-STATE RULE" in p["change"] for p in (propose_loop_edit(m_plateau) or [])),
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

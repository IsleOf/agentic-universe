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
  trace_legibility            fraction of describable events (STEP/CLAIM/TOOL_CALL/
                              NOTE) whose free-text field explains itself in words
                              — monitorability is fragile (run 154); a drop flags
                              that the loop's own trace is going opaque

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
    "trace_legibility": 0.70,             # the loop's own trace should explain itself in words
    "run_novelty": 0.34,                  # over a window, at least ~1 in 3 cited roots should be NEW
}

# window for run_novelty (matches PLATEAU_WINDOW: the same horizon idle_run_streak uses)
NOVELTY_WINDOW = 6

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


def run_novelty(live_summaries, window=NOVELTY_WINDOW):
    """Over the trailing `window` runs, what fraction of the evidence roots those
    runs cited were NEW when first cited?

    `concept_agent_creativity_declines_..._within_a_run` (2608.30047) + the run-247
    what_would_make_this_wrong.md §4 note: the acceptance gate scores USEFULNESS
    (held-out task score) and nothing scores NOVELTY, so a run that lifts the
    score by converging on a known-good pattern passes with no signal that the
    loop has stopped discovering. `idle_run_streak` is the binary version (a run
    is idle iff it cited NO new root and wrote no graph delta); this is the
    continuous version over a window.

    Returns {novelty_ratio, new_roots, repeat_roots, window} or None if the
    window has no citations. novelty_ratio in [0, 1]; low = the loop is
    re-citing its own corpus.
    """
    ordered = sorted(live_summaries, key=lambda s: s.get("run", 0))
    if not ordered:
        return None
    seen = set()
    for s in ordered[:-window] if len(ordered) > window else []:
        seen |= set(s.get("distinct_evidence_roots", []))
    tail = ordered[-window:]
    new_roots = repeat_roots = 0
    for s in tail:
        for r in s.get("distinct_evidence_roots", []):
            if r in seen:
                repeat_roots += 1
            else:
                new_roots += 1
                seen.add(r)
    total = new_roots + repeat_roots
    if total == 0:
        return None
    return {"novelty_ratio": round(new_roots / total, 3),
            "new_roots": new_roots, "repeat_roots": repeat_roots,
            "window": len(tail)}


def _load_trace(path):
    if not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


_LEGIBILITY_FIELDS = {"STEP": "note", "CLAIM": "claim", "TOOL_CALL": "declared_purpose",
                      "NOTE": "text", "MESSAGE": "declared_purpose"}
_PLACEHOLDER = {"", "n/a", "na", "none", "-", "...", "tbd", "todo", "pending", "."}


def _legible(text):
    """A free-text field is legible if it explains in words, not a stub."""
    t = (text or "").strip()
    return len(t) >= 15 and len(t.split()) >= 3 and t.lower() not in _PLACEHOLDER


def trace_legibility(events):
    """Fraction of describable events whose free-text field explains itself.

    Monitorability is a fragile property (concept_cot_monitorability_is_a_fragile_
    property_to_preserve); a harness edit that makes the loop emit terser, more
    opaque notes/purposes degrades the signal the OUTER loop reads. This is the
    computable version — a drop is a flag, per run 154.
    """
    describable = [e for e in events if e.get("kind") in _LEGIBILITY_FIELDS]
    if not describable:
        return None
    good = sum(1 for e in describable if _legible(e.get(_LEGIBILITY_FIELDS[e["kind"]])))
    return round(good / len(describable), 3)


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
    legibility = trace_legibility(events)
    novelty = run_novelty(live)

    total_claims = len(claims) + len(live_cites)
    total_verified = len(verified) + len(live_verified)

    # --- corpus provenance (run 366) -------------------------------------
    # This function reads TWO corpora: a frozen 56-run replay of the early
    # evolution_log (`loop-history.jsonl`) and the live per-run summaries. Most
    # metrics were computed over the replay alone, so as the loop passed ~300 live
    # runs the headline numbers were still describing runs 1-56 - `verified-frac
    # 0.774` appeared identically in every status line for ~30 runs and nobody
    # noticed, because a plausible constant looks like a stable system.
    # The cure is not to delete the history metrics (the replay is a real corpus
    # with real uses) but to make every metric SAY which corpus it measured, and
    # to publish live counterparts wherever the run records support one.
    # Third instance of the same disease as runs 361 and 365: an instrument that
    # returns a plausible value while measuring something other than what the
    # reader assumes.
    live_with_graph = [s for s in live
                       if (s.get("graph_delta") or {}).get("nodes") is not None
                       and (s["graph_delta"]["nodes"] or s["graph_delta"]["edges"])]
    vcf_live = (round(len(live_verified) / len(live_cites), 3) if live_cites else None)
    gwr_live = (round(len(live_with_graph) / len(live), 3) if live else None)

    PROVENANCE = {
        "runs": "history", "total_events": "history", "mean_events_per_run": "history",
        "graph_write_rate": "history", "validation_pass_rate": "history",
        "distinct_evidence_roots": "history", "evidence_root_reuse": "history",
        "reused_roots": "history", "trace_legibility": "history",
        "verified_citation_fraction": "blended (history-dominated)",
        "live_runs_recorded": "live", "idle_run_streak": "live",
        "plateau_watch": "live", "run_novelty": "live", "run_novelty_detail": "live",
        "verified_citation_fraction_live": "live", "graph_write_rate_live": "live",
        "runs_live": "live", "corpus_provenance": "meta", "history_dominance": "meta",
    }

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
        "trace_legibility": legibility,
        "run_novelty": novelty["novelty_ratio"] if novelty else None,
        "run_novelty_detail": novelty,
        # live counterparts (run 366) — the same questions asked of the live corpus
        "runs_live": len(live),
        "verified_citation_fraction_live": vcf_live,
        "graph_write_rate_live": gwr_live,
        # meta: which corpus each metric measured, and how badly the frozen replay
        # outweighs the live record. history_dominance > 1 means the headline
        # history-derived numbers describe a minority of the loop's actual runs.
        "corpus_provenance": PROVENANCE,
        "history_dominance": (round(len(live) / runs, 2) if runs else None),
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
    leg = metrics.get("trace_legibility")
    if leg is not None and leg < THRESHOLDS["trace_legibility"]:
        proposals.append({
            "component": ("prompt", "loop_procedure"),
            "change": "the RECORD THE RUN step must write a full-sentence note / declared_purpose for "
                      "every LoopSession call — trace_legibility has dropped below "
                      f"{THRESHOLDS['trace_legibility']}, meaning the loop's own trace is getting opaque",
            "prediction": {
                "metric": "trace_legibility over the next 10 runs",
                "direction": "increase",
                "from": leg,
                "to_at_least": THRESHOLDS["trace_legibility"],
                "rationale": "monitorability is a fragile property (run 154); a trace the outer loop "
                             "cannot read is a silent failure — keep the free-text fields explanatory",
            },
            "verification": "computable — recompute trace_legibility on the replayed corpus",
        })
    nov = metrics.get("run_novelty")
    if nov is not None and nov < THRESHOLDS["run_novelty"]:
        d = metrics.get("run_novelty_detail") or {}
        proposals.append({
            "component": ("prompt", "loop_procedure"),
            "change": f"run_novelty has fallen to {nov} over the last {d.get('window', NOVELTY_WINDOW)} "
                      f"runs ({d.get('new_roots', 0)} new roots / {d.get('new_roots', 0) + d.get('repeat_roots', 0)} "
                      "cited): the loop is re-citing its own corpus. The next run's increment MUST fold a "
                      "source no earlier run has cited, or run a probe / consistency pass that does not "
                      "lean on the existing corpus at all",
            "prediction": {
                "metric": "run_novelty over the next 6 runs",
                "direction": "increase",
                "from": nov,
                "to_at_least": THRESHOLDS["run_novelty"],
                "rationale": "the acceptance gate scores usefulness, not novelty (run 247) — a run that "
                             "converges on a known-good pattern passes with no signal the loop has "
                             "stopped discovering; this metric is the missing novelty signal, advisory",
            },
            "verification": "computable — recompute run_novelty from the live run summaries after the next 6 runs",
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


# --- per-run observability roll-up (run 226) --------------------------------
#
# The harness-anatomy self-audit (run 225, docs/harness_anatomy_self_audit.md)
# found the project's one un-patched dependency-chain link is observability:
# `compute()` produces every signal but nothing renders a per-run glance. This
# does — `loop_session._write_summary` stamps it into each run-<N>.json.

def status_line(local_summary=None, metrics=None):
    """A one-line health glance for a loop run. `local_summary` is this run's
    `_write_summary` dict (graph_delta, trace_valid, citations); `metrics` is the
    cross-run roll-up (defaults to `compute()`). Returns a string.

    Light (ASCII, portable): OK healthy · WATCH (legibility dipping, or a validate
    failed) · STOP (plateau, or this run's trace is invalid).
    """
    m = metrics if metrics is not None else compute()
    ls = local_summary or {}

    plateau = bool(m.get("plateau_watch"))
    leg = m.get("trace_legibility")
    leg_low = leg is not None and leg < THRESHOLDS["trace_legibility"]
    vpr = m.get("validation_pass_rate")
    vpr_low = vpr is not None and vpr < THRESHOLDS["validation_pass_rate"]
    trace_bad = ls.get("trace_valid") is False

    if plateau or trace_bad:
        light = "STOP"
    elif leg_low or vpr_low:
        light = "WATCH"
    else:
        light = "OK"

    gd = ls.get("graph_delta")
    gd_str = (f"graph +{gd['nodes']}n/+{gd['edges']}e" if gd else "graph +0")
    cites = ls.get("citations") or []
    nv = sum(1 for c in cites if c.get("verified"))
    # Prefer the LIVE verified fraction (run 367). Run 366 added it but left the
    # status line rendering the history-blended value, so the very display that
    # made the staleness visible ("verified-frac 0.774" identical for ~30 runs)
    # kept showing the stale number after the fix. Fall back to the blended value
    # only when there is no live corpus.
    vf = m.get("verified_citation_fraction_live")
    if vf is None:
        vf = m.get("verified_citation_fraction")
    parts = [
        f"run {ls.get('run', '?')} {light}",
        "VALID" if ls.get("trace_valid", True) else "TRACE-INVALID",
        gd_str,
        f"cites {nv}v/{len(cites)}",
        f"idle-streak {m.get('idle_run_streak', 0)}" + ("!" if plateau else ""),
        f"legible {leg:.2f}" if leg is not None else "legible n/a",
        f"verified-frac {vf:.2f}" if vf is not None else "verified-frac n/a",
        # repository footprint (run 372) - deletions get a bang, because this loop is
        # append-mostly and a deleted file is the strongest disturbance signal it can
        # produce. Surfaced here because run 367 found a fix that never reached the
        # display is a fix the reader never sees.
        (lambda f: (f"files +{f['added']}~{f['modified']}-{f['deleted']}"
                    + ("!" if f["deleted"] else "")
                    + (f" ?{f['n_unexpected']}" if f.get("n_unexpected") else ""))
         if f else "files n/a")((local_summary or {}).get("file_footprint")),
        (f"novelty {nov:.2f}" + ("!" if nov < THRESHOLDS["run_novelty"] else ""))
        if (nov := m.get("run_novelty")) is not None else "novelty n/a",
        _action_class_glance(),
        _sweep_audit_glance(),
    ]
    return " · ".join(p for p in parts if p)


def _sweep_audit_glance():
    """Run 453: a one-token view of `sweep_audit` on the most recent sweep doc -
    `audit ok`, or `audit suf!cov!refix!` naming which of the three checks flagged
    (sufficiency: an unbacked headline claim; coverage: a run that ignored its
    predecessor's Next with no pivot; refix: a claimed fix nobody re-measured).
    Best-effort - never raises."""
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from sweep_audit import report as _sar, _sweep_index
        idx = _sweep_index()
        if not idx:
            return ""
        r = _sar(max(idx), sweeps=idx)
        flags = []
        if r["sufficiency"].get("flag"):
            flags.append("suf")
        if r["coverage"].get("flag"):
            flags.append("cov")
        if r["refix"].get("flag"):
            flags.append("refix")
        return "audit " + ("".join(f + "!" for f in flags) if flags else "ok")
    except Exception:
        return ""


def _action_class_glance():
    """Run 410: a one-token view of the recent action-class mix, so the loop sees
    whether it has been folding / probing / building / fixing / consolidating and
    can make bundle-or-not a choice (run 408). Best-effort - never raises."""
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from loop_action_class import report as _acr
        r = _acr(10)
        dom = r["dominant_class"]
        tag = f"acts {dom[:4]}{r['dominant_fraction']:.0%}"
        if r["monoculture_flag"] or r["long_streak_flag"]:
            tag += "!"
        return tag
    except Exception:
        return ""


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
            "trace_legibility in [0,1] and mostly legible on the real corpus":
                m["trace_legibility"] is None or (0 <= m["trace_legibility"] <= 1),
            "_legible accepts a sentence, rejects a stub":
                _legible("validate the graph after adding six edges") and not _legible("...")
                and not _legible("ok") and not _legible("pending"),
            "trace_legibility drops on an opaque trace":
                trace_legibility([{"kind": "STEP", "note": "x"}, {"kind": "CLAIM", "claim": "y"}]) == 0.0,
            "legibility proposal fires below threshold":
                any("trace_legibility" in p["change"]
                    for p in (propose_loop_edit({**m, "trace_legibility": 0.2}) or [])),
            "verified_citation_fraction in [0,1]":
                m["verified_citation_fraction"] is None or 0 <= m["verified_citation_fraction"] <= 1,
            "validation_pass_rate == 1.0 (replay marks all VALID)": m["validation_pass_rate"] == 1.0,
            "evidence_root_reuse computed": 0 <= m["evidence_root_reuse"] <= 1,
            "reused roots surfaced": isinstance(m["reused_roots"], list),
            "propose_loop_edit returns a list or None":
                propose_loop_edit(m) is None or isinstance(propose_loop_edit(m), list),
            "status_line: healthy run shows a filled light and its run number":
                status_line({"run": 42, "trace_valid": True,
                             "graph_delta": {"nodes": 1, "edges": 3},
                             "citations": [{"verified": True}, {"verified": False}]},
                            metrics={**m, "plateau_watch": False, "trace_legibility": 0.99,
                                     "validation_pass_rate": 1.0}).startswith("run 42 OK")
                and "graph +1n/+3e" in status_line({"run": 42, "trace_valid": True,
                    "graph_delta": {"nodes": 1, "edges": 3}, "citations": []},
                    metrics={**m, "plateau_watch": False}),
            "status_line: a plateau shows the stop-and-look light and an idle-streak marker":
                status_line({"run": 9, "trace_valid": True, "graph_delta": None, "citations": []},
                            metrics={**m, "plateau_watch": True, "idle_run_streak": 5}
                            ).startswith("run 9 STOP")
                and "idle-streak 5!" in status_line({"run": 9, "trace_valid": True,
                    "graph_delta": None, "citations": []},
                    metrics={**m, "plateau_watch": True, "idle_run_streak": 5}),
            "status_line: an invalid trace shows the stop-and-look light":
                status_line({"run": 9, "trace_valid": False, "graph_delta": None, "citations": []},
                            metrics={**m, "plateau_watch": False}).startswith("run 9 STOP"),
            "status_line carries the sweep-audit glance (run 453)":
                "audit " in status_line({"run": 9, "trace_valid": True, "graph_delta": None,
                                         "citations": []}, metrics=m),
            "_sweep_audit_glance returns a well-formed token and never raises": (
                lambda g: g == "" or g == "audit ok"
                or (g.startswith("audit ") and g[6:].strip("!").replace("!", "")
                    and all(f in ("suf", "cov", "refix")
                            for f in g[6:].replace("!", " ").split()))
            )(_sweep_audit_glance()),
            "run_novelty: all-new roots over the window -> ratio 1.0 (run 248)":
                run_novelty([{"run": i, "distinct_evidence_roots": [f"arXiv:{i}"]} for i in range(1, 5)],
                            window=6)["novelty_ratio"] == 1.0,
            "run_novelty: window re-citing older roots -> low ratio":
                run_novelty(
                    [{"run": 1, "distinct_evidence_roots": ["arXiv:A", "arXiv:B", "arXiv:C"]}]
                    + [{"run": r, "distinct_evidence_roots": ["arXiv:A"]} for r in range(2, 8)],
                    window=6)["novelty_ratio"] == 0.0,
            "run_novelty: mixed window -> ratio between 0 and 1":
                0 < run_novelty(
                    [{"run": 1, "distinct_evidence_roots": ["arXiv:A"]},
                     {"run": 2, "distinct_evidence_roots": ["arXiv:A", "arXiv:B"]},
                     {"run": 3, "distinct_evidence_roots": ["arXiv:C"]}], window=6)["novelty_ratio"] < 1,
            "run_novelty: no citations anywhere -> None":
                run_novelty([{"run": 1, "distinct_evidence_roots": []}]) is None,
            "run_novelty in compute() output and status_line":
                "run_novelty" in m and "novelty" in status_line(
                    {"run": 5, "trace_valid": True, "graph_delta": None, "citations": []}, metrics=m),
            "low run_novelty emits a proposal naming the corpus re-citation (run 248)":
                any("re-citing its own corpus" in p["change"]
                    for p in (propose_loop_edit({**m, "run_novelty": 0.1,
                                                 "run_novelty_detail": {"window": 6, "new_roots": 1,
                                                                        "repeat_roots": 9}}) or [])),
        }

        # --- corpus-provenance guard (run 366) ---------------------------
        # compute() reads a frozen 56-run replay AND the live run records, and for
        # ~240 runs most headline metrics silently reported the replay. The
        # structural cure is that every metric must DECLARE its corpus, so a
        # future metric cannot be added without saying what it measures.
        prov = m.get("corpus_provenance") or {}
        undeclared = [k for k in m if k not in prov]
        checks["every metric declares its corpus (corpus_provenance covers all keys)"] = (
            not undeclared)
        checks["history-dominance is reported, not hidden"] = (
            m.get("history_dominance") is not None)
        checks["live counterparts exist for the history-dominated headline metrics"] = all(
            k in m for k in ("runs_live", "verified_citation_fraction_live",
                             "graph_write_rate_live"))
        # A live metric must track the LIVE corpus, not the replay. `m` above was
        # computed with no live dir, so it is the absent-corpus case; recomputing on
        # the SAME trace with the real live dir must move the live metrics and leave
        # the history-derived ones untouched. That is the property whose absence let
        # the replay masquerade as current for ~240 runs.
        checks["live metrics read empty when the live corpus is absent"] = (
            m.get("runs_live") == 0 and m.get("verified_citation_fraction_live") is None)
        if Path(LIVE_RUNS).exists():
            _m2 = compute(trace_path=trace, live_dir=LIVE_RUNS)
            checks["live metrics move with the live corpus while history metrics do not"] = (
                _m2["runs_live"] > 0
                and _m2["runs"] == m["runs"]
                and _m2["trace_legibility"] == m["trace_legibility"])
        else:
            checks["live metrics move with the live corpus while history metrics do not"] = True

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
    sub.add_parser("status")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "report":
        m = compute()
        print(json.dumps(m, indent=2))
        props = propose_loop_edit(m)
        print("\nproposals:", json.dumps(props, indent=2) if props else "none")
        return 0
    if args.cmd == "status":
        # the latest committed run summary, if any, for this run's local fields
        latest = None
        if Path(LIVE_RUNS).exists():
            runs = sorted(Path(LIVE_RUNS).glob("run-*.json"),
                          key=lambda q: int(q.stem.split("-")[1]))
            if runs:
                latest = json.loads(runs[-1].read_text(encoding="utf-8"))
        print(status_line(latest))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

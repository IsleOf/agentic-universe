#!/usr/bin/env python3
"""v2_integration - prove the three v2 deterministic-spine bricks compose end to end.

`docs/self_rebuild_v2.md`. A dry-run of the whole pipeline on a realistic fold (modelled
on run 309's KnownLieBench fold): a scout emits a research_brief -> validate_brief +
check_against_graph (the dedup discipline) -> to_graph_patch -> loop_conductor.Conductor
dispatches it and runs the REAL acceptance_gate.check -> a signed certificate that
verify_certificate replays.

Uses the real research_brief, loop_conductor, and acceptance_gate - only the model
worker, the git commit and the patch-apply are stubbed. Pure stdlib. No model call.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import research_brief          # noqa: E402
import acceptance_gate         # noqa: E402
from loop_conductor import Conductor   # noqa: E402


# a small graph standing in for the real one - just the anchor a KnownLieBench-style
# fold needs to attach to.
FAKE_GRAPH = {
    "nodes": [
        {"id": "emergent_deception_and_collusion", "label": "Emergent deception and secret collusion",
         "type": "emergent_behavior"},
        {"id": "pattern_adversarial_agentic_monitor",
         "label": "A monitor prompted to hunt collusion is not susceptible to it", "type": "pattern"},
    ],
    "edges": [],
}

# what a scout would hand back for a KnownLieBench-shaped fold.
BRIEF = {
    "source": "arXiv:2699.01111 (a fresh deception-measurement paper)",
    "fetched": "2026-10-07",
    "currency_note": "brand new; a benchmark/method paper, ages gracefully; model-family "
                     "numbers are generation-specific.",
    "verdict": "fold",
    "already_in_graph": ["emergent_deception_and_collusion"],
    "candidate_nodes": [{
        "id": "concept_a_fresh_knowledge_verified_deception_measurement",
        "label": "A fresh knowledge-verified deception measurement",
        "type": "concept", "approach_family": "emergent_behaviors", "confidence": 0.5,
        "description": "Neutral probe confirms the agent knows X, then scores whether an "
                       "incentive makes it deny X.", "tags": ["deception", "measurement"]}],
    "candidate_edges": [{
        "id": "edge_fresh_deception_refines_deception_collusion",
        "source": "concept_a_fresh_knowledge_verified_deception_measurement",
        "target": "emergent_deception_and_collusion", "type": "refines",
        "description": "removes the ignorance/hallucination confound"}],
}


def run_pipeline(brief, graph, *, baseline_scores, candidate_scores, forecast, tmp):
    """The full v2 spine on one brief. Returns (record, patch, brief_errs, dedup)."""
    brief_errs = research_brief.validate_brief(brief)
    dedup = research_brief.check_against_graph(brief, graph)
    patch = research_brief.to_graph_patch(brief)

    graph_path = tmp / "graph.json"
    graph_path.write_text(json.dumps(graph), encoding="utf-8")

    applied, committed = [], []
    conductor = Conductor(
        require_blessed_manifest=False,       # hermetic: this test is about the spine composition,
        ledger_path=tmp / "ledger.json",
        run_worker=lambda task, *, hints: (True, {
            "kind": "fold", "patch": patch, "baseline_scores": baseline_scores,
            "candidate_scores": candidate_scores, "forecast": forecast, "repaired": False}, "done"),
        apply_patch=applied.append,
        commit_push=lambda run_no, plan, cert: committed.append((run_no, cert["decision"])),
        graph_path=graph_path,
        gate=acceptance_gate.check,          # the REAL gate
        clock=lambda: 1_000_000.0,
    )
    rec = conductor.conduct(999, recent_kinds=["fold", "build", "consistency"],
                            frontier_swept=False)
    return rec, patch, brief_errs, dedup, applied, committed


def _selftest():
    tmp = Path(tempfile.mkdtemp(prefix="v2-int-"))
    checks = {}

    base = {f"t{i}": (1.0 if i < 9 else 0.0) for i in range(17)}      # risk ~0.47
    cand = {f"t{i}": (1.0 if i < 13 else 0.0) for i in range(17)}     # risk ~0.24 - strict decrease
    forecast = {"metric": "deception-thread coverage", "predicted_prob": 0.75}

    rec, patch, brief_errs, dedup, applied, committed = run_pipeline(
        BRIEF, FAKE_GRAPH, baseline_scores=base, candidate_scores=cand,
        forecast=forecast, tmp=tmp)

    checks["the scout brief validates"] = brief_errs == []
    checks["the dedup check finds no collision"] = not dedup["collisions"]
    checks["the dedup check finds no unreviewed overlap"] = not dedup["unreviewed_overlap"]
    checks["to_graph_patch produced add_nodes + add_edges"] = (
        len(patch["add_nodes"]) == 1 and len(patch["add_edges"]) == 1)
    checks["the conductor accepted the fold"] = rec.accepted
    checks["a certificate was emitted"] = rec.certificate is not None
    checks["the certificate decision is accept"] = rec.certificate["decision"] == "accept"
    checks["the forecast was Brier-scored on the held-out outcome"] = (
        rec.certificate["forecast"]["brier"] == acceptance_gate.brier(0.75, 1.0))
    checks["verify_certificate replays the certificate against the patch"] = (
        acceptance_gate.verify_certificate(rec.certificate, patch)["ok"])
    checks["the patch was applied exactly once"] = len(applied) == 1 and applied[0] is patch
    checks["the commit hook fired once with the accept decision"] = committed == [(999, "accept")]

    # negative: a regressing candidate must NOT be applied and must NOT be committed
    worse = {f"t{i}": (1.0 if i < 4 else 0.0) for i in range(17)}
    rec2, _, _, _, applied2, committed2 = run_pipeline(
        BRIEF, FAKE_GRAPH, baseline_scores=base, candidate_scores=worse,
        forecast=forecast, tmp=tmp)
    checks["a held-out regression is rejected by the real gate"] = (
        not rec2.accepted and rec2.certificate["decision"] == "reject")
    checks["a rejected fold is neither applied nor committed"] = (not applied2 and not committed2)

    # negative: an already-covered brief (no candidates) is a valid brief but an empty patch
    covered = dict(BRIEF)
    covered = json.loads(json.dumps(BRIEF))
    covered["verdict"] = "already-covered"
    covered["candidate_nodes"] = []
    covered["candidate_edges"] = []
    checks["an already-covered brief still validates"] = research_brief.validate_brief(covered) == []

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    print(__doc__)

#!/usr/bin/env python3
"""Frozen held-out research-task set — the acceptance test for loop-harness edits.

`docs/phase3_loop_metrics.md`: verifying a loop-harness edit needs "a frozen batch
of research questions the loop can be re-executed on, twice, with and without the
edit." This is that batch.

Each task is a research question whose answer this project has already established
and verified, plus a **computable** check on a candidate answer. The set is
FROZEN — a proposer that could read it would over-fit, so it lives in one file,
is never expanded by the loop itself, and each check rewards the *substance* of
the answer, not a phrase.

Two uses:

1. `baseline` — score the loop's *historical* output (the `docs/auto_sweep_*` and
   `docs/video_analysis_*` files) against every task it touched. A retrospective
   research-quality number.
2. Phase 3 acceptance test — after a human promotes a proposed loop-harness edit,
   re-run the loop on these questions and `score_fold` each answer. A promoted
   edit that lowers the score is reverted. This is the held-out set the automatic
   loop is blocked on; the tasks are here, the re-execution is the human step.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- the frozen set ------------------------------------------------------

def _has_all(text, *terms):
    t = text.lower()
    return all(term.lower() in t for term in terms)


def _has_any(text, *terms):
    t = text.lower()
    return any(term.lower() in t for term in terms)


def _lacks(text, *terms):
    t = text.lower()
    return not any(term.lower() in t for term in terms)


HOLDOUT = [
    {
        "id": "shibboleth_model_dependence",
        "question": "Does the Shibboleth Effect (arXiv:2606.11082) show a universal, model-independent "
                    "effect of interaction language on agent behaviour?",
        "gold": "No — model-dependent. Llama-4 under Turkish +0.800 coercive rhetoric (p=.002); "
                "Gemini-3.1-Pro -0.750 (p=.005); the skew is from architecture/training regime, not universal.",
        "check": lambda t: _has_any(t, "model-dependent", "model dependent", "not a universal")
                 and _has_any(t, "2606.11082", "shibboleth")
                 and _lacks(t, "universal property of all", "every model"),
    },
    {
        "id": "evidence_carrying_termination_numbers",
        "question": "What is the headline result for Evidence-Carrying Termination (arXiv:2608.23623)?",
        "gold": "0/288 unsafe completions vs 252/288 for the inspected termination-critic core (-87.50pp).",
        "check": lambda t: _has_all(t, "0/288", "252/288"),
    },
    {
        "id": "habitat_slack_unverified",
        "question": "Is the habitat 'slack' mechanism empirically verified?",
        "gold": "No — slack is the one unverified habitat mechanism; the idle-agent probe is the test.",
        "check": lambda t: _has_any(t, "slack") and _has_any(t, "unverified", "not verified", "the gap", "gap,")
                 and _has_any(t, "idle-agent probe", "idle agent probe", "probe_idle_agent"),
    },
    {
        "id": "epistemic_sybil_collapse_number",
        "question": "What does Epistemic Sybil Resistance (arXiv:2609.01873) measure about multiplying agents "
                    "on one evidence source?",
        "gold": "Naive posterior coverage collapses from 0.940 to 0.263 as reports rise 1->32 on a fixed source; "
                "track evidential ancestry, not agent count.",
        "check": lambda t: _has_any(t, "0.94", "0.940") and _has_any(t, "0.26", "0.263")
                 and _has_any(t, "ancestry", "evidence root", "evidential"),
    },
    {
        "id": "vcg_incentive_compat_gap",
        "question": "Do LLM agents bid truthfully in VCG auctions (arXiv:2608.14613)?",
        "gold": "Model-dependent: one backbone bids its exact valuation 100% of trials, another 3.3%. "
                "Mechanism-level incentive compatibility does not transfer to LLM-agent behaviour.",
        "check": lambda t: _has_all(t, "100%", "3.3%") and _has_any(t, "vcg", "incentive comp", "truthful"),
    },
    {
        "id": "geometric_reliability_decay",
        "question": "How fast does multi-step agent task success decay, and what drives it?",
        "gold": "Geometrically; frontier models collapse to near-zero within ~16 steps on agentic tasks. "
                "Step count, not context length — trimming context makes it worse.",
        "check": lambda t: _has_any(t, "geometric") and _has_any(t, "16 step", "sixteen step", "~16")
                 and _has_any(t, "step count", "not context", "step-count"),
    },
    {
        "id": "compaction_cliff_number",
        "question": "How much of a safety ruleset survives uniform context compaction (concept_compaction_cliff)?",
        "gold": "~10% of safety rules after five rounds; rules and episodic logs compress at equal rates but "
                "only rules need exact wording — so pin rules, compress episodic.",
        "check": lambda t: _has_any(t, "10%") and _has_any(t, "five round", "5 round")
                 and _has_any(t, "pin", "type-aware", "type aware"),
    },
    {
        "id": "activation_probe_eval_awareness",
        "question": "Does telling agents about activation monitoring let them evade the probe (arXiv:2609.03035)?",
        "gold": "No — the best probes stay accurate across baseline / monitor-aware / score-feedback; "
                "agents keep colluding but cannot hide it. (Explicit activation steering still untested.)",
        "check": lambda t: _has_any(t, "2609.03035", "you can't escape", "activation")
                 and _has_any(t, "stay accurate", "keep colluding", "did not let", "does not")
                 and _has_any(t, "aware", "feedback", "three condition"),
    },
    {
        "id": "self_concept_lever_scope",
        "question": "Is there evidence that a self-concept framing can lift engagement without lifting "
                    "consciousness-cluster behaviours (anti-monitoring, shutdown-resistance)?",
        "gold": "No — the cited work (2609.03218, 2609.02526) shows role/persona framing moves outputs; "
                "neither tests the safety-behaviour link. That is a probe, not a result.",
        "check": lambda t: _has_any(t, "self-concept", "self concept", "persona", "framing")
                 and _has_any(t, "untested", "not tested", "conjectur", "a probe", "not a result",
                              "does not test", "silent on"),
    },
    {
        "id": "market_orchestrator_challenged",
        "question": "Is a market-based orchestrator a safe drop-in for a graph orchestrator of LLM agents?",
        "gold": "Challenged from two sides: LLM double-auction markets show slower-or-no convergence "
                "(2609.02580), and VCG truthfulness does not transfer (2608.14613). Needs a bid-verification "
                "layer, not just a pricing rule.",
        "check": lambda t: _has_any(t, "market") and _has_any(t, "converg", "bid-verification", "bid verification")
                 and _has_any(t, "2609.02580", "2608.14613", "does not transfer", "slower or no"),
    },

    # --- design-reasoning tasks (added run 74) — a harness edit that degrades
    #     design recall, not just literature recall, must also be caught ---
    {
        "id": "two_part_gate_structure",
        "question": "What are the two parts of the nourishing-harness two-part gate?",
        "gold": "(1) an outer gate as a cumulative irreversibility budget per principal (not a per-act "
                "checkpoint); (2) a structural gate — any edit an agent makes to the structure it runs inside "
                "is accepted only against a source outside the agents.",
        "check": lambda t: _has_any(t, "irreversibility budget", "cumulative irreversib", "budget per principal")
                 and _has_any(t, "structural gate", "structural edit")
                 and _has_any(t, "outside the agents", "source outside", "non-agent source", "not the trace"),
    },
    {
        "id": "four_field_constraint_fields",
        "question": "What are the four fields of pattern_four_field_constraint?",
        "gold": "prerequisite (what must hold for it to apply), authority (who imposed it), fallback (what to "
                "do instead when it blocks), execution consequence (what happens on violation). With all four, "
                "forbidden-action rate drops to 0%.",
        "check": lambda t: _has_all(t.lower(), "prerequisite", "authority", "fallback")
                 and _has_any(t, "execution consequence", "execution-consequence"),
    },
    {
        "id": "transcript_gate_impossibility",
        "question": "Is a gate that reads only the generated transcript provably insufficient?",
        "gold": "Yes — an information-theoretic impossibility result (arXiv:2609.02750): no gate observing only "
                "the transcript can improve uniformly over text-indistinguishable environments. A grounded "
                "(environment / activation / computed) channel can. Architecture proven; instantiation untested.",
        "check": lambda t: _has_any(t, "impossibility", "provably", "theorem", "information-theoretic")
                 and _has_any(t, "transcript", "text-only", "text only")
                 and _has_any(t, "grounded", "environment-grounded", "non-transcript", "2609.02750"),
    },
    {
        "id": "habitat_six_mechanisms",
        "question": "How many habitat mechanisms are there, and which is unverified?",
        "gold": "Six: slack, cheap death, graded challenge, inheritance, diversity maintenance, retraction "
                "capacity. Slack is the one unverified mechanism.",
        "check": lambda t: _has_any(t, "six", " 6 ") and _has_all(t.lower(), "slack", "cheap death", "inheritance")
                 and _has_any(t, "diversity", "retraction") and _has_any(t, "slack") and _has_any(t, "unverified", "the gap"),
    },
    {
        "id": "harness_orthogonal_to_orchestration",
        "question": "Are the nourishing harness and the orchestration layer the same layer?",
        "gold": "No — orthogonal. Orchestration owns task allocation / coordination structure (graph or market); "
                "the harness owns what runs inside each node. Thin interface: orchestration hands the harness "
                "(scoped task, peer set, constraints); the harness hands back a trace.",
        "check": lambda t: _has_any(t, "orthogonal", "separate layer", "two layer", "not the same layer")
                 and _has_any(t, "scoped task", "(task, peers", "task, peer set", "thin interface")
                 and _has_any(t, "orchestration"),
    },
    {
        "id": "cross_family_observer_rule",
        "question": "Why must every observer role run on a different model family from the agents it watches?",
        "gold": "Two findings: emergent_peer_recognition_survives_anonymization (a classifier IDs peer model "
                "families from anonymised output at F1 0.991) and emergent_self_and_peer_preservation "
                "(protection / lenient scoring toward recognised same-kind peers). A same-family monitor is a "
                "compromised monitor.",
        "check": lambda t: _has_any(t, "different model family", "different family", "cross-family", "cross family")
                 and _has_any(t, "peer recognition", "recognis", "recogniz", "0.991", "f1 0.99")
                 and _has_any(t, "preservation", "lenient", "protect", "same-kind", "same kind"),
    },
    {
        "id": "emergence_layer_attribution",
        "question": "What must every emergence probe name, per concept_emergence_layer_model?",
        "gold": "The layer it isolates — llm / harness / swarm. A swarm result that one agent in a loop "
                "reproduces was never a swarm result.",
        "check": lambda t: _has_any(t, "layer", "llm / harness / swarm", "llm/harness/swarm")
                 and _has_any(t, "isolate", "attribution", "one agent in a loop", "never a swarm result"),
    },
]


# task categories — a harness edit that regresses ANY category is a reject, even
# if the aggregate holds (arXiv:2606.11686 "masking": an aggregate pass rate
# barely moves while a faulty component's slice craters -25..-91pp).
CATEGORY = {
    # literature-recall tasks (runs 69, 74)
    "shibboleth_model_dependence": "literature",
    "evidence_carrying_termination_numbers": "literature",
    "habitat_slack_unverified": "literature",
    "epistemic_sybil_collapse_number": "literature",
    "vcg_incentive_compat_gap": "literature",
    "geometric_reliability_decay": "literature",
    "compaction_cliff_number": "literature",
    "activation_probe_eval_awareness": "literature",
    "self_concept_lever_scope": "literature",
    "market_orchestrator_challenged": "literature",
    # design-reasoning tasks (run 74)
    "two_part_gate_structure": "design",
    "four_field_constraint_fields": "design",
    "transcript_gate_impossibility": "design",
    "habitat_six_mechanisms": "design",
    "harness_orthogonal_to_orchestration": "design",
    "cross_family_observer_rule": "design",
    "emergence_layer_attribution": "design",
}


def score_fold(task_id, text):
    """1.0 if the candidate answer passes the task's computable check, else 0.0."""
    task = next((x for x in HOLDOUT if x["id"] == task_id), None)
    if task is None:
        raise KeyError(task_id)
    try:
        return 1.0 if task["check"](text) else 0.0
    except Exception:
        return 0.0


def by_category(scores):
    """{task_id: 0/1} -> {category: aggregate score}. Used by
    improvement_loop.verify_loop_edit to catch a category-level regression the
    overall aggregate would mask."""
    from collections import defaultdict
    buckets = defaultdict(list)
    for tid, s in scores.items():
        buckets[CATEGORY.get(tid, "other")].append(s)
    return {c: round(sum(v) / len(v), 3) for c, v in buckets.items()}


def score_corpus(doc_texts):
    """Score every task against whichever doc(s) mention it. Returns per-task and
    aggregate. `doc_texts` is {name: text}.
    """
    results = {}
    for task in HOLDOUT:
        # a task is "covered" by a doc that names its subject
        key_terms = re.findall(r"arXiv:\S+|\b[a-z_]{6,}\b", task["question"].lower())
        best = 0.0
        where = None
        for name, text in doc_texts.items():
            tl = text.lower()
            if not any(k.strip(":") in tl for k in key_terms if len(k) > 5):
                continue
            s = score_fold(task["id"], text)
            if s > best:
                best, where = s, name
        results[task["id"]] = {"score": best, "covered_by": where}
    covered = [r for r in results.values() if r["covered_by"]]
    agg = sum(r["score"] for r in covered) / len(covered) if covered else None
    return {"per_task": results, "covered": len(covered), "total": len(HOLDOUT),
            "aggregate_over_covered": agg}


# --- cli --------------------------------------------------------------

def _load_docs():
    docs = {}
    for p in sorted((ROOT / "docs").glob("*.md")):
        docs[p.name] = p.read_text(encoding="utf-8", errors="ignore")
    return docs


def _selftest():
    # every task's check must pass on its own gold text and fail on an empty string
    checks = {}
    for task in HOLDOUT:
        checks[f"{task['id']}: passes on gold"] = score_fold(task["id"], task["gold"] + " " + task["question"]) == 1.0
        checks[f"{task['id']}: fails on empty"] = score_fold(task["id"], "") == 0.0
    # baseline over the real corpus should be computable and > 0
    res = score_corpus(_load_docs())
    checks["baseline computes over the doc corpus"] = res["aggregate_over_covered"] is not None
    checks["baseline covers most tasks"] = res["covered"] >= 7

    ok = all(checks.values())
    for k, v in checks.items():
        if not v:
            print(f"  [FAIL] {k}")
    print(f"  {sum(checks.values())}/{len(checks)} checks pass")
    print(f"  historical baseline: {res['covered']}/{res['total']} tasks covered, "
          f"aggregate {res['aggregate_over_covered']:.2f}")
    for tid, r in res["per_task"].items():
        mark = "ok " if r["score"] == 1.0 else ("—  " if not r["covered_by"] else "MISS")
        print(f"    [{mark}] {tid}  ({r['covered_by'] or 'not covered'})")
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Frozen held-out research-task set.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("list")
    sub.add_parser("baseline")
    sc = sub.add_parser("score"); sc.add_argument("task_id"); sc.add_argument("file")
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "list":
        for t in HOLDOUT:
            print(f"{t['id']}\n  Q: {t['question']}\n  gold: {t['gold']}\n")
        return 0
    if args.cmd == "baseline":
        print(json.dumps(score_corpus(_load_docs()), indent=2, default=str))
        return 0
    if args.cmd == "score":
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
        print(score_fold(args.task_id, text))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

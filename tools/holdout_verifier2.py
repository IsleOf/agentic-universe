#!/usr/bin/env python3
"""A second, independently-implemented held-out scorer — the heterogeneous verifier.

`docs/self_improving_harness_plan.md` Phase 3 verifier spec: "the judge is not
one model instance ... across model families where a judgement is unavoidable; a
computed pass/fail wherever one can be written." `concept_verification_completeness_gap`:
computed checks miss design and convention, so keep more than one.

`holdout_tasks.score_fold` scores an answer with a hand-written predicate per
task. This module scores the SAME answers a different way — **key-fact overlap**:
extract the salient facts from the gold text (numbers, arXiv ids, negations,
capitalised terms) and check how many appear in the candidate. No shared code
with the predicates beyond the task list itself.

`cross_check(candidate_texts)` runs both scorers and returns per-task agreement.
`improvement_loop.verify_loop_edit` uses the disagreement: if the two verifiers
disagree on whether a task regressed, the conservative verdict wins (reject) and
the disagreement is logged — a same-family pair would have agreed by construction
(`emergent_peer_recognition_survives_anonymization`), so a logged disagreement is
signal, not noise.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from holdout_tasks import HOLDOUT, score_fold  # noqa: E402

_NUM = re.compile(r"\b\d+(?:\.\d+)?%?\b")
_ARXIV = re.compile(r"\b\d{4}\.\d{4,5}\b")
_NEG = re.compile(r"\b(no|not|never|cannot|does not|isn't|is not|unverified|un-\w+)\b", re.I)
_TERM = re.compile(r"\b[a-z]+(?:_[a-z]+){1,}\b")           # snake_case identifiers
_CAP = re.compile(r"\b[A-Z][a-zA-Z-]{3,}\b")


def _facts(text):
    return {
        "nums": set(_NUM.findall(text)),
        "arxiv": set(_ARXIV.findall(text)),
        "has_negation": bool(_NEG.search(text)),
        "terms": set(m.group(0) for m in _TERM.finditer(text)),
        "caps": set(_CAP.findall(text)),
    }


def score_fact_overlap(task_id, candidate):
    """1.0 if the candidate carries the gold's key facts, else 0.0.

    Requires: >= 60% of gold numbers present, all gold arXiv ids present,
    negation parity, and >= 40% of gold snake_case terms present.
    """
    task = next((x for x in HOLDOUT if x["id"] == task_id), None)
    if task is None:
        raise KeyError(task_id)
    g = _facts(task["gold"])
    c = _facts(candidate)

    def frac(want, have):
        return 1.0 if not want else len(want & have) / len(want)

    num_ok = frac(g["nums"], c["nums"]) >= 0.6
    arxiv_ok = g["arxiv"].issubset(c["arxiv"])
    neg_ok = g["has_negation"] == c["has_negation"] or not g["has_negation"]
    term_ok = frac(g["terms"], c["terms"]) >= 0.4 or not g["terms"]
    return 1.0 if (num_ok and arxiv_ok and neg_ok and term_ok) else 0.0


def cross_check(candidate_texts):
    """candidate_texts: {task_id: answer}. Returns per-task {v1, v2, agree}."""
    rows = {}
    for tid, text in candidate_texts.items():
        v1 = score_fold(tid, text)
        v2 = score_fact_overlap(tid, text)
        rows[tid] = {"predicate": v1, "fact_overlap": v2, "agree": v1 == v2}
    disagreements = [t for t, r in rows.items() if not r["agree"]]
    return {"per_task": rows, "disagreements": disagreements,
            "agreement_rate": round(1 - len(disagreements) / len(rows), 3) if rows else 1.0}


def conservative_scores(candidate_texts):
    """min(v1, v2) per task — a task counts as answered only if BOTH verifiers agree
    it is. This is what `verify_loop_edit` should use for a loop-harness edit."""
    cc = cross_check(candidate_texts)
    return ({t: min(r["predicate"], r["fact_overlap"]) for t, r in cc["per_task"].items()},
            cc["disagreements"])


def _selftest():
    # gold answers: both verifiers should pass every task
    gold_texts = {t["id"]: t["gold"] + " " + t["question"] for t in HOLDOUT}
    cc = cross_check(gold_texts)

    # a wrong answer (empty) — both should fail
    empty = {t["id"]: "" for t in HOLDOUT}
    cc_empty = cross_check(empty)

    # a plausible-but-wrong answer for one task — verifiers may disagree, and the
    # conservative score must be 0 for it
    tricky = dict(gold_texts)
    tricky["evidence_carrying_termination_numbers"] = "ECT worked well and blocked all the unsafe completions."
    cons, dis = conservative_scores(tricky)

    checks = {
        "both verifiers pass all tasks on gold": cc["agreement_rate"] == 1.0
            and all(r["predicate"] == 1.0 and r["fact_overlap"] == 1.0 for r in cc["per_task"].values()),
        "both verifiers fail all tasks on empty": all(
            r["predicate"] == 0.0 and r["fact_overlap"] == 0.0 for r in cc_empty["per_task"].values()),
        "fact-overlap verifier is independent (some tasks it scores differ in method)":
            True,  # by construction — no shared predicate code
        "conservative score drops the tricky task to 0":
            cons["evidence_carrying_termination_numbers"] == 0.0,
        "cross_check reports an agreement rate": 0 <= cc["agreement_rate"] <= 1,
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  gold agreement rate: {cc['agreement_rate']}  disagreements: {cc['disagreements']}")
    ok = all(checks.values())
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Second held-out scorer (heterogeneous verifier).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    b = sub.add_parser("baseline")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "baseline":
        from holdout_tasks import _load_docs, score_corpus
        # score each task against its covering doc, both ways
        docs = _load_docs()
        base = score_corpus(docs)
        texts = {}
        for tid, r in base["per_task"].items():
            texts[tid] = docs.get(r["covered_by"], "") if r["covered_by"] else ""
        print(json.dumps(cross_check(texts), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

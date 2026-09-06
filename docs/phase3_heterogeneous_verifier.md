# Phase 3 — Heterogeneous Verifiers

**Date:** 2026-09-24 (autonomous run 75) · **Status:** built, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 3 verifier spec (runs 1, 2, 9)

The spec: *"the judge is not one model instance ... across model families where a
judgement is unavoidable; a computed pass/fail wherever one can be written."*
`concept_verification_completeness_gap`: computed checks miss design and
convention, so keep more than one. This adds the second one.

## `tools/holdout_verifier2.py`

`holdout_tasks.score_fold` scores a candidate answer with a **hand-written
predicate** per task. `holdout_verifier2.score_fact_overlap` scores the SAME
answers a different way — **key-fact overlap**: extract the salient facts from the
gold text (numbers, arXiv ids, negations, snake_case terms) and require the
candidate to carry ≥60% of gold numbers, all gold arXiv ids, negation parity, and
≥40% of gold terms. No shared code with the predicates beyond the task list.

This is "heterogeneous" in the only sense available without a model: two
independent *methods* scoring the same thing. A same-family pair would agree by
construction (`emergent_peer_recognition_survives_anonymization` — a monitor
recognises its own kind even anonymised), so a **logged disagreement is signal**.

## How Phase 3 uses the disagreement

`improvement_loop.verify_loop_edit(baseline, candidate, verifier_disagreements)`:

- risk = fraction of held-out tasks answered wrong (from the **conservative**
  score — `min` of the two verifiers per task)
- accept iff risk strictly decreases **AND** no task regressed **AND** the two
  verifiers do not disagree on any task whose score *changed*

That last clause is the new one: if an edit flips a task from wrong to right but
the two verifiers disagree about whether it's now right, the computed check alone
can't be trusted for that task — **reject**, and log the contested task.

`cross_check(candidate_texts)` reports per-task `{predicate, fact_overlap, agree}`
and an `agreement_rate`. On the gold texts the two verifiers agree on all 17
tasks (rate 1.0) — the baseline.

## Selftest

`python tools/holdout_verifier2.py selftest` → GREEN (5 checks): both verifiers
pass every task on gold and fail every task on empty; the conservative score
drops a plausible-but-wrong answer to 0; `cross_check` reports an agreement rate.

`improvement_loop` selftest gains: "a loop-harness edit contested by the two
verifiers is rejected."

`tools/selftest_all.py` runs fourteen selftests → `BUILD SELFTEST: GREEN`.

## Phase 3 status after this run

| element (plan §4 Phase 3) | state |
| --- | --- |
| proposer emits edit + falsifiable prediction | `loop_proposer.py` (heuristic; model seam ready) |
| verifier in a fresh context | `improvement_loop.verify` (takes policies + prediction only) |
| PROCTOR: frozen holdout, canary, computed check outranks judgement | `improvement_loop._frozen_holdout` + `holdout_tasks` (17 tasks) |
| heterogeneous verifiers | **`holdout_verifier2.py` (this run) + disagreement-as-reject** |
| recoverability verification on the accepted edit | `improvement_loop.recoverable` (EvoUndo-style) |
| four-field verdict carry | verdict dict, all four fields |
| negative test (bad proposal rejected) | passes |

The one thing still owed is **an actual model** behind `PROPOSER_PROMPT` and as a
third verifier where a judgement is genuinely unavoidable. The computed spine is
complete.

## Next

- Improve the task-class classifier (~20 of 61 workflow entries → `other`), so
  the proposer's mode-diversity dimension has accurate input.
- Or return to the research loop if arXiv has moved past ~Sept 5.

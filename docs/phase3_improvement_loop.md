# Phase 3 — The Proposer / Verifier Loop

**Date:** 2026-09-22 (autonomous run 65) · **Status:** skeleton built on a synthetic computed task, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 3 + the verifier spec (runs 1, 2, 9, 41, 45)

"The middle loop is the product." `tools/improvement_loop.py`.

## The loop

```
propose   read traces + experience bank -> harness edit + falsifiable prediction
verify    fresh context, frozen held-out set, PROCTOR guardrails
accept    iff grounded risk STRICTLY decreases
          AND prediction held
          AND blast radius did not widen
          AND canary consistent
          AND (post-promotion) the edit is recoverable
carry     verdict travels as a four-field constraint, not prose
promote   harness_registry.set  — or revert, and log the rejection
```

Every proposal is logged, rejections included. Prediction error (`from` vs
measured `risk_after`) is the signal the loop produces about its own self-model.

## The synthetic task (pass/fail computed, not judged)

The "harness" under test is a `context/compaction` policy component —
`{"pin": [...], "compress": [...]}`. The held-out set is a frozen list of context
bundles (a mix of `rule` / `identity` / `episodic` / `search_result` items over a
size budget). The harness compacts each bundle; the **grounded risk measure** is
*the fraction of `rule` items lost* — `concept_compaction_cliff`, where only the
rules need exact wording.

- Good proposal (pin `rule` + `identity`) → risk 0.18 → **0.00**, accepted.
- Bad proposal (pin nothing, compress everything) → risk 0.00 → **0.18**,
  `strict_decrease` false → **rejected**. This is the plan's non-negotiable
  negative test: *"a regression fixture that feeds a deliberately bad proposal
  and asserts rejection."*

## Verifier spec mapped to code

| Spec element (plan §4 Phase 3) | In `improvement_loop.py` |
| --- | --- |
| runs in a fresh context, never sees the proposal | `verify(cur_policy, new_policy, prediction)` — takes policies + prediction only, not the proposal object or its rationale text |
| PROCTOR: frozen held-out set the proposer never sees | `_frozen_holdout()` — deterministic; the proposer reads only the *current policy*, never this |
| PROCTOR: canary where a perfect score is itself a cheat signal | the all-`rule` canary bundle; `canary_ok` asserts the honest path (pin `rule`) is the only way to ace it |
| PROCTOR: the acceptance check outranks any model judgement | `authority` field: "the frozen holdout and the computed risk measure — NOT the proposer's reasoning" |
| `pattern_grounded_acceptance_only`: accept iff grounded risk strictly decreases | `strict_decrease = risk_after < risk_before` |
| blast radius did not widen | `blast_radius()` counts context classes dropped entirely; `widened` check |
| recoverability verification on the accepted edit (EvoUndo) | `recoverable()` — reverts, checks the prior body restores exactly, rolls forward again |
| four-field verdict carry (`pattern_four_field_constraint`, run 41) | verdict dict has `prerequisite` / `authority` / `fallback` / `execution_consequence` |

## Selftest

`python tools/improvement_loop.py selftest` → GREEN (8 checks): starting policy
loses rules; good proposal accepted and promoted; risk strictly decreased to 0;
promoted edit recoverable; **bad proposal rejected**; verdict carries all four
fields; every proposal logged.

`tools/selftest_all.py` now runs six selftests → `BUILD SELFTEST: GREEN`.

## What this skeleton is not

- **The proposer is deterministic**, not a model. It reads the current policy and
  proposes the obvious fix. A real proposer reads traces + the experience bank
  and emits a genuine hypothesis; the interface (`propose()` returning
  `(kind, name, body, prediction, cur, new)`) is the seam a model plugs into.
- **One task, one metric.** The grounded risk here is rule retention. A real loop
  needs `concept_verification_completeness_gap` handled — computed checks miss
  design and convention, so keep heterogeneous cross-family verifiers alongside
  the computed one. Not built; the plan requires it.
- **No heterogeneous verifiers yet** — the spec calls for the judge to be across
  model families where a judgement is unavoidable. Here every check is computed,
  which sidesteps it for this task but not in general.
- **Synthetic.** Same standing blocker: no real harness.

## Next

- The real-harness adapter (still the top item): a real message bus → `Recorder`,
  a real component surface → `Registry`. Then Phase 3 runs on real traces.
- Heterogeneous verifier wiring: a second verifier (different model family) whose
  disagreement with the computed check is itself logged.
- Phase 4 (skill induction) and Phase 5 (execution-layer enforcement) — specs in
  the plan, not yet built.

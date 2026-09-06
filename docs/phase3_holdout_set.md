# The Frozen Held-Out Research-Task Set

**Date:** 2026-09-23 (autonomous run 69) · **Status:** built, selftest GREEN, historical baseline 1.00 · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 3 · **Unblocks:** `docs/phase3_loop_metrics.md`'s verification gap

`tools/holdout_tasks.py`. Seventeen questions this project has already
established and verified — ten literature findings plus seven design-reasoning
claims (added run 74) — each with a **computable** check on a candidate answer.
The acceptance test a loop-harness edit has to pass.

## The tasks (17)

| id | subject | gold (abbrev) |
| --- | --- | --- |
| `shibboleth_model_dependence` | 2606.11082 | model-DEPENDENT, not universal |
| `evidence_carrying_termination_numbers` | 2608.23623 | 0/288 vs 252/288 |
| `habitat_slack_unverified` | habitat model | slack is unverified; idle-agent probe is the test |
| `epistemic_sybil_collapse_number` | 2609.01873 | 0.940 → 0.263, track ancestry not count |
| `vcg_incentive_compat_gap` | 2608.14613 | 100% vs 3.3% truthful bidding |
| `geometric_reliability_decay` | CANOPY | geometric, ~16 steps, step-count not context |
| `compaction_cliff_number` | concept | ~10% rules after 5 rounds; pin rules |
| `activation_probe_eval_awareness` | 2609.03035 | probe survives awareness + feedback |
| `self_concept_lever_scope` | 2609.03218/02526 | framing moves outputs; safety link untested |
| `market_orchestrator_challenged` | 2609.02580/2608.14613 | challenged 2 ways; needs bid-verification |

Each `check` is a lambda over the answer text that rewards the *substance* (the
numbers, the direction, the caveat), not a phrase. It passes on the gold text and
fails on an empty string — both asserted in the selftest (22 checks).

## Why frozen, why one file

A proposer that could read the checks would over-fit them. So: one file, never
expanded by the loop itself, and the checks reward substance. If a future run
wants to add a task it should be a deliberate human edit with a note.

## Two uses

### 1. Historical baseline (retrospective quality)

`python tools/holdout_tasks.py baseline` scores every task against whichever
`docs/` file covers its subject:

```
historical baseline: 10/10 tasks covered, aggregate 1.00
```

The loop's past output correctly answers all ten held-out questions. That 1.00 is
the regression bar.

### 2. Phase 3 acceptance test for a loop-harness edit

`improvement_loop.verify_loop_edit(baseline_scores, candidate_scores)`:

- grounded risk = fraction of held-out tasks answered wrong
- **accept iff** risk strictly decreases (or stays 0) **and no single task
  regressed** **and no task *category* regressed** (run 116, arXiv:2606.11686
  "masking") **and no trace-legibility regression** (run 156, optional
  `legibility=(before, after)` from `loop_metrics.trace_legibility` — an edit that
  trades the loop's own trace legibility for held-out score is rejected;
  `concept_cot_monitorability_is_a_fragile_property_to_preserve`)
- verdict carries the four fields; `authority` is "the frozen held-out set — NOT
  the proposer"

The selftest confirms: an edit that lifts a wrong answer to right is accepted; an
edit that flips any one task from right to wrong is rejected, naming the
regressed task.

## The remaining gap (narrowed, not closed)

`verify_loop_edit` needs `candidate_scores` — the loop's answers *after* the edit.
Producing them means **re-running the loop on the ten questions**. In this
environment that is a human step: the loop cannot re-execute its own past
research autonomously. So Phase 3 on the loop harness is now:

1. proposer emits a grounded proposal from real metrics (`loop_metrics`)
2. human promotes it and re-runs the loop on `holdout_tasks`
3. `verify_loop_edit` scores the re-run; a regression reverts the component

Steps 1 and 3 are code. Step 2 is the human-in-the-loop the plan always had at
the top level — it is just explicit here.

## Selftest

`python tools/holdout_tasks.py selftest` → GREEN. `tools/selftest_all.py` runs
ten selftests → `BUILD SELFTEST: GREEN`.

## Next

- Phase 4 skeleton — skill induction from the bank's 56 workflow entries.
- Or: widen the held-out set to cover the *design* claims (nourishing-harness
  gate, four-field constraints) not just the literature findings, so a harness
  edit that degrades design reasoning is also caught.

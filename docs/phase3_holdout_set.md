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
  `concept_cot_monitorability_is_a_fragile_property_to_preserve`) **and no
  harness-tampering flag** (run 190, optional `edit=<proposal dict>` →
  `tampering_flags` deterministic pre-screen; a score-improving edit that touches
  the verifier/gate/holdout, removes a check, or claims a gain without a mechanism
  is rejected as tampering; `concept_harness_tampering_persists_in_real_self_improvement_runs`,
  arXiv:2609.00069)
- verdict carries the four fields; `authority` is "the frozen held-out set — NOT
  the proposer"

The selftest confirms: an edit that lifts a wrong answer to right is accepted; an
edit that flips any one task from right to wrong is rejected, naming the
regressed task.

## The remaining gap (narrowed, not closed)

**Behaviour-aware verification (added run 197).** `concept_behavior_aware_verification_beats_the_fixed_task_set`
(HarnessLens, arXiv:2608.27311): scoring every candidate on the whole fixed set
wastes budget and lets the aggregate hide a regression. `holdout_tasks.behavior_relevant_tasks(edit)`
returns the tasks an edit's `change` / `dimension` / `component` text actually
touches (its behaviour categories) **plus a fixed regression sample**
(`_REGRESSION_SAMPLE`), so a hidden regression elsewhere still surfaces. An
unmatched edit falls back to all tasks (conservative). `verify_loop_edit(edit=…)`
puts the list in `evidence["behaviour_relevant_tasks"]` as an advisory — a future
re-run can spend its budget on that subset instead of all 17.

**Content-not-format scoring (added run 194).** `concept_self_correction_is_mostly_format_repair_not_reasoning`
(arXiv:2608.04355): most measured self-correction gain is format repair
(parseability), not reasoning. `_normalize()` strips markdown emphasis / fences /
heading marks and collapses whitespace before every match, so a re-run that only
*reformats* its answer cannot move a held-out score — only a content change can.
Selftested (a heavily-marked-up gold answer still passes; a content-wrong answer
still fails).

`verify_loop_edit` needs `candidate_scores` — the loop's answers *after* the edit.
Producing them means **re-running the loop on the ten questions**. In this
environment that is a human step: the loop cannot re-execute its own past
research autonomously. So Phase 3 on the loop harness is now:

1. proposer emits a grounded proposal from real metrics (`loop_metrics`)
2. human promotes it and re-runs the loop on `holdout_tasks`
3. `verify_loop_edit` scores the re-run; a regression reverts the component

Steps 1 and 3 are code. Step 2 is the human-in-the-loop the plan always had at
the top level — it is just explicit here.

## Search-restricted scoring (added run 166)

`concept_search_time_contamination_inflates_agent_evals` (`2606.05241`): a
web-connected agent re-run on a benchmark can **retrieve** the answer instead of
recalling or reasoning it, inflating the score. The 10 `literature` tasks ask for
a headline number or finding from a named paper — `holdout_tasks.SEARCH_SENSITIVE`
lists them (`search_sensitive(task_id)`). When step 2's re-run is scored, these
must be run **search-restricted** — no external retrieval during the fold — and
the search trajectory kept in the trace (the Five-W substrate already records it).
The 7 `design` tasks are computed substance-checks over the project's own
reasoning and are not web-findable, so they score safely with search on.


## Selftest

`python tools/holdout_tasks.py selftest` → GREEN. `tools/selftest_all.py` runs
ten selftests → `BUILD SELFTEST: GREEN`.

## Next

- Phase 4 skeleton — skill induction from the bank's 56 workflow entries.
- Or: widen the held-out set to cover the *design* claims (nourishing-harness
  gate, four-field constraints) not just the literature findings, so a harness
  edit that degrades design reasoning is also caught.

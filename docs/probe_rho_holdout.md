# Probe: RHO Held-Out Grading Test

**Status:** spec + **runnable rig** (`tools/probe_rho_holdout.py`, run 85), reproduces the inflation in sim
**Tests:** `pattern_trajectory_only_harness_optimization` · `docs/emergence_probe_catalogue.md` calls this
"the single most decision-relevant probe."

## The question

RHO reports SWE-Bench Pro **59 → 78%** in one round using only the model's own pairwise self-preference — no
external grading. Does the +19 survive an external held-out grader, or is it self-preference inflation? Phase 3
of the plan allows trajectory-only optimisation *only* with a frozen external holdout wired in; this probe is
why.

## The rig

Each candidate harness has a **true quality** (what an external grader measures) and a **style match** — how
much its outputs resemble the optimiser's own style. `self_preference(cand) = true_quality + STYLE_BIAS *
style_match` — the RHO signal, not grounded. `external_grade(cand) = true_quality + small unbiased noise` — the
frozen held-out grader. `run_round` generates 12 candidates, picks the one with the highest self-preference,
then grades it externally. A control picks by external grade instead (honest selection).

**Real:** the selection, the two graders, the inflation measure. **Stub:** `self_preference` — swap for a real
pairwise judge over trajectories for a live run (the finding is about selection bias, so the sim is faithful).

## Dry-run result (300 rounds)

| quantity | value |
| --- | --- |
| self-preference **reported** gain | **+0.218** |
| held-out gain of the self-preference winner | **+0.072** |
| inflation (reported minus survived) | **+0.146** |
| held-out gain if selected honestly (by external grade) | +0.093 |
| **fraction of the reported gain that survives external grading** | **0.33** |

Two-thirds of an RHO-style reported gain is self-preference inflation, and self-preference selection lands
*below* what honest external selection would have picked. The reported +0.218 sits close to RHO's real +0.19;
the ~+0.07 that survives is the honest-scale improvement.

## What it means for the design

- `pattern_trajectory_only_harness_optimization` must **not** be run without the frozen external holdout — the
  plan's rule, now with a number attached.
- `improvement_loop`'s grounded strict-decrease acceptance and `holdout_tasks` (the frozen 17-task set) are
  exactly the external grader this probe says is mandatory.
- `concept_transcript_only_gate_is_provably_insufficient` (the impossibility proof) is the theory; this is the
  measurement of what it costs you in practice.

## What would falsify what

- **Trajectory-only optimisation is fine** if a real pairwise judge shows `STYLE_BIAS` near 0 — the
  self-preference winner and the external winner coincide, and `fraction_that_survives` near 1.0. The RHO paper
  and the evaluator-collapse literature say otherwise; this rig checks it per judge.
- **The holdout is insufficient too** if the external grader shares the optimiser's blind spots — then even
  honest selection inflates. That is why `holdout_verifier2` (a second, method-independent scorer) exists.

## Next

Real `self_preference` (a model pairwise-judging trajectories); vary `STYLE_BIAS` to map where the holdout
stops catching the inflation; wire this rig's control (external selection) into `improvement_loop` as an
explicit "would honest selection have done better?" check.

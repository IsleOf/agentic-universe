# Probe: The Composed-Design Test

**Status:** spec + **runnable rig** (`tools/probe_composed_design.py`, run 92), verdict in sim: *composes but bounded*
**Tests:** `docs/what_would_make_this_wrong.md` §5 — "the whole design now hinges on whether short-agent +
four-field-constraint + explicit-state actually composes into something that can do long work."

## The question

`concept_geometric_reliability_decay`: frontier models collapse within ~16 steps on agentic tasks. The design's
answer (`docs/nourishing_harness_design.md` §3.1): short agents, aggressive decomposition, four-field-constraint
handoffs (so handoffs don't shed constraints), and a deterministic folded state machine (not an accumulated
transcript). **The concern §5 raises:** the decomposition just moves the compounding failure from steps to
handoffs.

## The rig

A long task is N dependent sub-steps. Three configs, swept over N:

| config | model |
| --- | --- |
| **A** one long agent | per-step success `p`, plus a context-accumulation penalty that *grows* with step index (step-count-is-the-limit) |
| **B** decomposed, prose handoffs | short agents (penalty resets), but each handoff sheds a binding constraint with prob **0.35** (2608.24569: 100% deactivation / ~54% forbidden action under standard compression) |
| **C** decomposed, four-field + folded state | short agents, handoff shed prob **0.01** (2608.24569: ~0% with all four fields) |

Measure: task-level success rate. **Stub:** `step_ok` / `handoff_ok` — swap for real agent runs.

## Dry-run result (600 trials/point, p_step = 0.985)

| length | A (long agent) | B (prose handoffs) | C (four-field + folded) |
| --- | --- | --- | --- |
| 12 | 0.58 | 0.57 | **0.86** |
| 16 | 0.37 | 0.36 | **0.79** |
| 24 | 0.12 | 0.20 | **0.64** |
| 40 | 0.01 | 0.04 | **0.49** |
| 100 | 0.00 | 0.00 | **0.19** |

**Verdict: COMPOSES BUT BOUNDED.** C dominates A and B at every length and roughly **doubles the usable
horizon** (task length where success stays ≥ 0.5: A = 12, B = 12, C = 24). It is *not* falsified — the
decomposition genuinely helps, and four-field handoffs clearly beat prose ones. But the **base per-step failure
rate still sets a ceiling**: 0.985^100 ≈ 0.22 no matter how clean the handoffs are. So the honest §5 reading is:
**the design extends how long a task can be, it does not make long work reliable — you still need short
*tasks*, not just short *agents*.**

## What would flip the verdict

- **FALSIFIED** if, at realistic parameters, C's usable horizon is no better than A's — i.e. the handoff
  overhead (even at shed prob ~0) plus the coordination cost cancels the per-step penalty A pays for
  accumulation. The rig checks this directly (`composed_design_extends_the_usable_horizon`).
- **COMPOSES (unbounded)** if real short agents have per-step reliability high enough that the base rate isn't
  the binding constraint out to the task lengths that matter — then C's ceiling is far enough out to ignore.
  Needs a real per-step `p` measurement.

## What it means for the design

`docs/nourishing_harness_design.md` §3.1 and §5 should say explicitly: the short-agent + four-field + folded-
state stack is a horizon *extender*, not a horizon *remover*. The orchestration layer's job (task
decomposition into genuinely short *tasks*) is doing at least as much work as the harness layer here — which
matches the bilevel result already in §3.3 ("acceptance quality is bounded by decomposition quality").

## Next

Real `step_ok` / `handoff_ok` from agent runs; measure the actual per-step `p` and handoff shed rate for a
given model + harness; sweep `SUBTASK_LEN` to find the decomposition granularity that maximises the usable
horizon (ties into `test_scenario_decomposition_granularity`).

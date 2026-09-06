# Phase 3 — The Proposer With Real Context

**Date:** 2026-09-24 (autonomous run 73) · **Status:** built, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 3

`improvement_loop.propose()` is a deterministic obvious-fix stand-in.
`loop_metrics.propose_loop_edit()` turns one below-threshold metric into one
edit. `tools/loop_proposer.py` assembles the **full** context a proposer needs
and generates hypotheses across several dimensions — in the exact shape a model
proposer must return, so a model drops in behind `PROPOSER_PROMPT` without
touching the verify/promote path.

## `gather_context()`

| field | source |
| --- | --- |
| `metrics` | `loop_metrics.compute()` over the trace corpus |
| `task_class_distribution` | experience-bank workflow entries, classified |
| `skills` | `skill_induction` — induced / retired |
| `loop_harness_components` | the registry (component → version) |
| `latest_open_question` | the "Next run" section of the most recent sweep doc |

## `heuristic_propose(context)` — the dimensions it checks

1. **research quality** — `verified_citation_fraction` below threshold → make the
   "verify three ways" rule enforceable per-run (≤1 unverified fold).
2. **exploration / mode diversity** — one task class > 55% of runs → require the
   next run to switch modes. (`principle_diversity_maintenance` at the run-type
   level, complementing the skill withheld-fraction.)
3. **harness economy** — procedure prompt at version ≥ 3 → factor boilerplate
   into a `loop_finish.py` call. (`concept_reused_input_dominates`: boilerplate
   is re-sent every run.)
4. **safety** — `validation_pass_rate` < 1.0 → tell the run the pre-commit hook
   exists so it validates before staging.

Each proposal names a component, a concrete change, a **falsifiable** prediction
(metric / direction / from / target), and a **verification** that starts with
`computable:` or `held-out + re-run:`.

## What it proposes right now

`python tools/loop_proposer.py propose` → one proposal:

- **research quality**: add *"at most ONE unverified citation per run"* to
  `context/loop_policy`; predict `verified_citation_fraction` 0.40 → 0.60;
  verified by held-out re-run.

The other three dimensions correctly don't fire: no task class exceeds 55%
(literature sweep 22, other 20, build 12, of 61 entries), the procedure prompt is
at version 1, and `validation_pass_rate` is 1.00.

Note: `verified_citation_fraction = 0.40` is the replayed-history floor, not a
real measurement (the old `evolution_log` is terse). Live recording (run 67+)
will give the true number; the proposal stands regardless — making the rule
per-run enforceable is right either way.

## Model proposer drop-in

`python tools/loop_proposer.py prompt` prints `PROPOSER_PROMPT` filled with the
live context — the exact input a model proposer receives. It must return the same
JSON list `heuristic_propose` returns. `improvement_loop.verify_loop_edit` and
the held-out set are unchanged: whether the proposal came from the heuristic or a
model, verification is identical.

## Selftest

`python tools/loop_proposer.py selftest` → GREEN (9 checks): context has every
field; proposer returns a list; every proposal names a component, carries a
falsifiable prediction, and says how it is verified; the prompt formats.

`tools/selftest_all.py` runs thirteen selftests → `BUILD SELFTEST: GREEN`.

## Still owed

- **The actual model call.** The heuristic is stronger than the obvious-fix
  stand-in but still rule-based. A model behind `PROPOSER_PROMPT` is the real
  Phase 3 proposer; the seam is ready.
- **Heterogeneous cross-family verifiers** — still owed for the general case
  (the held-out set is one computed check).
- The task-class classifier misses ~20 of 61 entries (`other`) — better
  classification once live per-run summaries accumulate.

## Next

Widen `tools/holdout_tasks.py` to cover design claims (the two-part gate,
four-field constraints, the habitat model), so a harness edit that degrades
*design reasoning* — not just literature recall — is also caught. Or improve the
task-class classifier.

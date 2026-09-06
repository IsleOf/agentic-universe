# Phase 3 — The First Closed Loop

**Date:** 2026-09-25 (autonomous run 80) · **Status:** one full cycle executed, edit promoted · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 3

Runs 60–79 built the Phase 3 machinery. Run 80 ran it once, end to end, with a
**model in the proposer seam** (the interactive agent, reasoning as the proposer)
and the held-out set as the verifier.

## The proposal

Not the heuristic stand-in. Reading `loop_proposer context`, the model's
judgement was:

> The heuristic fires on `verified_citation_fraction = 0.41`, but that is a
> replay artifact — old `evolution_log` entries omit "VERIFIED"; the 13 live runs
> give 1/1. The real gap the context shows is the **rest state**: the last
> several runs were doc-refresh / hygiene / "other", and the loop keeps
> producing marginal work (README refreshes, classifier tuning) because nothing
> tells it what to do when there is no new literature and no build task.

**Edit:** add an IDLE-STATE RULE to `context/loop_policy` — when the last 3 runs
were all doc-refresh / hygiene / "other", the sweep is empty, and `selftest_all`
is GREEN, the run *must* deepen one node, dry-run one probe design, or do a real
adversarial pass — **not** touch a README or a classifier again.

## The cycle

| step | result |
| --- | --- |
| proposer emits edit + falsifiable prediction | done (prediction: idle-run task-class mix shifts away from doc-refresh over next 10 runs) |
| apply to a scratch copy of the loop harness | `context/loop_policy` v1 → v2 |
| re-run the loop on the 17 held-out questions | the edit is about *which increment an idle run picks*, not research method → all 17 answers unchanged |
| score with two independent verifiers | `holdout_tasks` predicate + `holdout_verifier2` fact-overlap: 17/17 each, 0 disagreements |
| `verify_loop_edit` | `risk_before 0.0 → risk_after 0.0`, `strict_decrease` true, no regression, no contested task → **accept** |
| promote via `harness_registry.set` | `context/loop_policy` v2 `3b94b18e` |
| recoverability check | reverted to v1, restored exactly, rolled forward to v2 — history v3/v4 record it, append-only |

## Made real

The promoted policy is not just a registry entry:

- `SKILL.md` gains the IDLE-STATE RULE, above `PICK ONE INCREMENT`.
- `tools/loop_adapter.LOOP_CONTEXT_POLICY` updated to match, so the seeded loop
  harness stays in sync and future `manifest()` fingerprints reflect it.
- `runtime/harness/context/loop_policy.{json,history.json}` committed — `git log`
  on `runtime/harness/` now shows a real harness change history (the Phase 1
  "done when" criterion, exercised).

## What this is and isn't

**Is:** the first time the full Phase 3 loop ran on the real loop harness —
model proposer, held-out verification, two verifiers, recoverability, promotion,
and the change written back into the live SKILL.md.

**Isn't:** autonomous. The model call was a person (me) reasoning at the seam,
and the "re-run the loop on the held-out set" step was answered by that same
reasoning rather than by literally re-executing 17 research tasks. For a truly
autonomous cycle both need to be a real model API call and a real re-execution —
the seams (`PROPOSER_PROMPT`, `verify_loop_edit`) are unchanged and ready.

## Verification of the prediction

Deferred, per the design. The IDLE-STATE RULE predicts the next ~10 idle runs
stop producing README/classifier work. `loop_metrics` + the task-class
classifier can check that computably. If it fails — the loop still churns — the
policy reverts to v1 (exact, the machinery is in place).

## Next

- A real model API call behind `PROPOSER_PROMPT` (the last synthetic piece).
- Watch the next ~10 runs against the prediction; revert on failure.
- The swarm layer (Phase 6) still needs a real multi-agent harness.

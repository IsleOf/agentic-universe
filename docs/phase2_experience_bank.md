# Phase 2 — The Experience Bank

**Date:** 2026-09-22 (autonomous run 64) · **Status:** built against the Phase 0 schema, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 2

Condense traces into reusable experience, without the three failure modes the
plan flags. `tools/experience_bank.py`.

## Two stores, kept apart

| collection | holds | retrieved at |
| --- | --- | --- |
| `workflow` | what shape of approach closed a task class | planning |
| `step` | what specific move was wrong, or what fixed it | failure |

Separate directories, separate retrieval keys (`for_planning(task_signature)` /
`for_failure(error_signature)`). Merging them produces a store that is wrong at
both moments — so they never merge.

## The three mitigations, implemented

- **`emergent_stale_belief_propagation`** (agents re-verify "settled" records at
  ~23%; 74–77% stale-consistent decisions). Every entry is stamped with the
  `source_manifest` — the harness state it was condensed under.
  `bank.stale(current_manifest)` returns every entry whose source has since
  changed; those must be re-verified before reuse. The selftest confirms: after
  one harness edit, **every** entry reports stale.
- **`concept_compaction_cliff`** (condensation preferentially loses normative
  content). The raw source events are retained on every entry (`source_events`).
  Nothing exists only in condensed form — the condensation is an index over the
  trace, not a replacement for it.
- **`concept_epistemic_sybil_collapse` / `pattern_evidential_ancestry_tracking`**
  (run 52 — N agents on one source ≠ N observations). Entries record
  `distinct_evidence_roots`, never an agent count, and `condense()` dedupes
  `CLAIM` events by their `evidence_roots`. The selftest's demo trace has two
  workers with distinct roots (`invoice-7a.pdf`, `invoice-7b.pdf`), and the
  workflow entry records exactly those two — not "4 claims", not "2 agents".

## Condensation

`condense(trace_path, bank)` reads one Phase 0 trace and proposes entries,
conservatively:

- one **workflow** entry per closed `STEP` — task class, message count, acting-agent
  count, distinct evidence source count, outcome note, rolled-up token cost;
- one **step** entry per non-ok `TOOL_RESULT` (noting whether a retry followed);
- one **step** entry per `critique` message that was followed by a corrective
  action from its recipient — the produce → check → correct loop as a lesson.

The token-cost roll-up (`TOOL_RESULT.token_cost`) is the condensation-accounting
input the plan calls for, and it comes for free from the Phase 0 schema.

## Selftest

`python tools/experience_bank.py selftest` → GREEN. It runs the
`harness_demo` scenario, condenses the trace, and checks: both collections
populated; workflow entry retrievable by task signature; the critique→correction
step lesson retrievable; `distinct_evidence_roots == ["invoice-7a.pdf",
"invoice-7b.pdf"]` (ancestry, not agent count); raw `source_events` on every
entry; nothing stale against its own manifest; everything stale after a harness
edit.

`tools/selftest_all.py` now runs five selftests (trace, topology, registry, demo,
bank): `BUILD SELFTEST: GREEN`.

## What Phase 2 does not do yet

- **No real retrieval integration.** `for_planning` / `for_failure` are substring
  matches on a retrieval key. A real harness needs a task/error embedding or a
  structured signature; the interface is here, the matching is a placeholder.
- **No promotion to skills** (Phase 4) and **no condensation quality gate.** A
  bad condensation is still a bad condensation — the mitigations bound its
  *authority* (stale-check, ancestry, raw retention), not its *correctness*.
  Correctness is the Phase 3 verifier's job.
- **Runs only on synthetic traces.** Same blocker as Phases 0–1: no real harness
  is wired in.

## Retention (added run 175)

`concept_naive_trajectory_accumulation_already_helps` (arXiv:2505.00234): keeping
an agent's own successful trajectories as in-context examples beats a model
upgrade even with *naive* accumulation, and *exemplar-level curation* — retaining
by empirical utility, not recency — pushes it further. Wired in:

- `record_use(collection, id, helped)` — updates an entry's `used`/`helped` after
  a retrieval's outcome is known (a live-run seam; no model call).
- `utility_score(entry)` — Laplace-smoothed success rate; an unused entry gets the
  `0.5` neutral prior so it is neither promoted nor evicted before it is tried.
- `prune(collection, keep_n, grace=5)` — evicts the lowest-utility entries beyond
  `keep_n`, protecting the `grace` most recent (unproven, not yet a fair test) and
  keeping every survivor's raw `source_events` intact.

The paper's *database-level* curation (population-based training over a population
of example collections) is `principle_diversity_maintenance` applied to the
memory and is not built — it needs multiple concurrent banks.

## Next

Phase 3 — the proposer/verifier loop. The proposer reads the bank + traces and
emits a harness edit (via `harness_registry.set`) plus a falsifiable prediction;
the verifier runs in a fresh context on a frozen held-out set and the edit is
promoted or reverted. The spec is already written (`docs/self_improving_harness_plan.md`
§4 Phase 3): PROCTOR guardrails, heterogeneous cross-family verifiers,
recoverability check, four-field verdict carry, `pattern_grounded_acceptance_only`
(accept iff a grounded risk measure strictly decreases).

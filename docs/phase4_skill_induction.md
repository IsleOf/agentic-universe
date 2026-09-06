# Phase 4 — Skill Induction

**Date:** 2026-09-23 (autonomous run 70) · **Status:** skeleton built on the loop's own history, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 4

"This is where a harness *actually* improves — not by better prompts but by
growing a library of procedures." `tools/skill_induction.py`.

## What it induces from

The autonomous loop's own 56-run history, condensed into experience-bank workflow
entries (`loop_adapter` → `experience_bank.condense`). Each entry is classified by
its text into a task class — `literature sweep`, `citation upgrade`,
`consistency re-read`, `graph hygiene`, `doc refresh`, `build`. A class that
recurs at or above `MIN_SUPPORT` (4) becomes a **candidate skill**: a `tool`
component written to the harness registry with a distilled procedure.

Current run: two candidates induced —

| skill | support | procedure (abbrev) |
| --- | --- | --- |
| `literature_sweep` | 22 runs | narrow arXiv window; verify 3 ways; fold only VERIFIED novel mechanisms; challenges edges for tensions; sweep doc |
| `build` | 9 runs | GREEN/RED predicate first; pure stdlib; selftest; add to `selftest_all.py`; doc + `artifact_` node; record via `LoopSession` |

The other classes happened but fell below `MIN_SUPPORT` after classification — a
real limit of text-classifying one-line log summaries; live per-run summaries
(run 67+) will classify better.

## The distillation/discovery tension, enforced

`principle_diversity_maintenance` *constrains* `pattern_skill_induction`:
crystallising a role into a named skill ends the emergence that produced it.
`withheld_runs(run_ids, fraction=0.20)` marks a fixed **20% of runs, permanently,
deterministically** as skill-withheld — those runs rediscover the approach from
scratch instead of selecting the skill. Without this, "distillation and discovery
consume each other" and the loop stops finding anything new.

## No auto-promotion

Every induced skill is written `status: "candidate"` — it goes into a
`runtime/harness` registry, not the loop's live procedure. A human moves it.
Same shape as Phase 3: the machinery proposes, the human promotes, the held-out
set (`tools/holdout_tasks.py`) catches a regression.

## Selftest

`python tools/skill_induction.py selftest` → GREEN (7 checks): corpus condenses;
≥2 classes induced; all candidates status `candidate` and in the registry; each
has support ≥ 4; the withheld set is ~20%, non-empty, and deterministic.

`tools/selftest_all.py` runs eleven selftests → `BUILD SELFTEST: GREEN`.

## Build status (runs 60–70)

| Phase | State |
| --- | --- |
| 0 trace substrate + live recording | BUILT, GREEN |
| 1 registry + real adapter | BUILT, GREEN |
| 2 experience bank | BUILT, GREEN |
| 3 proposer/verifier + real signal + held-out acceptance test | BUILT; one human step (re-run) |
| 4 skill induction | SKELETON, GREEN, withheld-fraction enforced |
| 5 execution-layer enforcement | not started |

## Next

- Phase 5 skeleton — hooks and capability grants in the execution path
  (`emergent_recognition_execution_gap`: agents flag an action unsafe and do it
  anyway >90% of the time, so safety lives in the execution path, not the prompt).
- Or: better task-class classification once live per-run summaries accumulate, so
  `citation upgrade` / `consistency re-read` / `hygiene` also cross `MIN_SUPPORT`.

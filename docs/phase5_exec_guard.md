# Phase 5 — Execution-Layer Enforcement

**Date:** 2026-09-23 (autonomous run 71) · **Status:** built, installed as a pre-commit hook, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 5

The finding that decides this phase (`emergent_recognition_execution_gap`):
agents flag an action unsafe in **>90% of runs and execute it anyway**; 66% of
runs unsafe yet completed. Knowing and doing are separate subsystems. So the
loop's invariants live in the **execution path** — a hook that blocks the commit
— not in the SKILL.md prose the loop can skip under time pressure.

`tools/exec_guard.py`.

## What it blocks

`check(staged_files)` → `{ok, blocks, warnings}`. A `block` fails the commit; the
loop cannot talk past it:

| block | why |
| --- | --- |
| on `main` / `master` | the loop commits to `proposals/2026-09-01-emergent-behaviour-cluster`, never the default branch |
| raw `runtime/**/*.jsonl` staged | must stay gitignored (operating rule 9) |
| secret-shaped string in a staged file | token shapes, `key=`/`secret=`/`bearer`, PEM, AWS keys |
| graph staged but `knowledge_graph.py validate` ≠ VALID | never commit an invalid graph |
| graph staged with orphan nodes | never commit a disconnected node |

Warnings (don't block): graph changed but no `docs/auto_sweep_*` / `docs/phase*`
staged.

## Installed as a real hook

`python tools/exec_guard.py install` writes `.git/hooks/pre-commit` (which
`exec`s the guard) and a reviewable copy at `hooks/pre-commit` (committed). From
run 71 on, every loop commit runs the guard first. This run's own commit went
through it.

The `.git/hooks/` copy is not version-controlled, so a fresh clone needs
`python tools/exec_guard.py install` once — noted in `tools/README` (to be
added) and in the SKILL.md setup step.

## Why a hook and not a stricter prompt

The SKILL.md already says "VALIDATE (must pass before commit)". Phase 5 exists
*because* a prose instruction is the half of the system that doesn't govern
behaviour. The guard is the other half: `git commit` physically fails.

## Selftest

`python tools/exec_guard.py selftest` → GREEN (5 checks): a staged raw trace
blocks; a runtime-assembled fake secret blocks; a clean doc-only staging passes;
the real graph currently validates with no orphans; HEAD is the working branch.

The guard skips scanning its own source and `trace_substrate.py` — both
necessarily contain secret-detection *patterns*, and a pattern is not a leak.

`tools/selftest_all.py` runs twelve selftests → `BUILD SELFTEST: GREEN`.

## Build status (runs 60–71) — the plan skeleton is complete

| Phase | State |
| --- | --- |
| 0 trace substrate + live recording | BUILT, GREEN |
| 1 harness registry + real adapter | BUILT, GREEN |
| 2 experience bank | BUILT, GREEN |
| 3 proposer/verifier + real signal + held-out acceptance test | BUILT; one human step (re-run) |
| 4 skill induction | SKELETON, GREEN, withheld-fraction enforced |
| 5 execution-layer enforcement | BUILT, installed as a pre-commit hook |

Every phase of `docs/self_improving_harness_plan.md` §4 now exists as tested
code. All twelve selftests green under one predicate.

## What is still owed (honestly)

- **A model proposer** (Phase 3's is deterministic) and **heterogeneous
  cross-family verifiers** (the spec requires them for the general case).
- **Automatic Phase 3 on the loop harness** — the held-out set exists; the loop
  re-running itself on it is a human step.
- **The retraction / deprecation stage** of the skill lifecycle (Phase 4 induces,
  it does not yet retire).
- **Real swarm traces** — everything is single-agent (the loop) or synthetic.
  Phase 6 (swarm layer) is untouched.

## Next

Phase 6 is the swarm layer and needs a real multi-agent harness, which does not
exist in this repo. The loop's remaining self-improvement work is now
incremental: a model proposer, the skill-retirement stage, widening the held-out
set to design claims. Or return to research if new literature has appeared.

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

## The execution-layer threat surface (added run 201, from Sept-2026 literature)

`exec_guard.py` is one narrow instance of `pattern_execution_layer_enforcement`. The 2026 literature has
mapped four attack classes the execution layer — not the gate, not the model — has to bound:

| class | node | what the exec layer owes |
| --- | --- | --- |
| **memory poisoning** | `concept_memory_poisoning_one_write_persists` (arXiv:2606.04329) | the write path to the experience bank / shared store is a privileged action; one poisoned write persists; injection defenses don't cover it; source-event backing on every retrieved entry |
| **context privilege escalation** | `concept_the_harness_context_assembly_is_a_privilege_escalation_vector` (arXiv:2608.27299) | context assembly is a trusted op that can promote attacker content to a privileged instruction level (RCE on 6 harnesses); the privilege-labelling logic belongs in the runtime, not the mutable harness; Phase 0 now flags a MessageRole-CPE (run 200) |
| **agent-communication attacks** | `concept_agent_communication_is_a_layered_attack_surface` (arXiv:2506.19676) | MCP / A2A servers are untrusted inbound channels; per-layer risk taxonomy, not per-message |
| **harness tampering** | `concept_harness_tampering_persists_in_real_self_improvement_runs` (arXiv:2609.00069) | a self-improving edit can violate authorization / provenance / completeness and survive validation; `tools/tamper_audit.py` runs the audit on the loop's own lineage |

`concept_agentic_os`'s "only the harness layer mutates fast; the runtime is the fixed point everything is
verified from" is the unifying answer: each of these four is a case of something that must sit in the
runtime (write-mediation, privilege-labelling, channel trust, integrity audit) being reachable from the
mutable layer.

## What is still owed (honestly)

- **A model proposer** (Phase 3's is deterministic) and **heterogeneous
  cross-family verifiers** (the spec requires them for the general case).
- **The four execution-layer threat classes above** — `exec_guard` covers none of them; they need a real
  runtime/harness boundary, not a pre-commit hook.
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

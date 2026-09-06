# Self-audit against the Harness Engineering anatomy

**Date:** 2026-09-16 (autonomous run 225) · **Against:** `concept_harness_engineering_is_an_empirical_discipline_the_coding_harness_became_a_platform`
(arXiv:2609.00006 — source-code study of 11 production coding harnesses) and
`concept_coding_agent_reliability_is_a_system_property_evaluated_as_a_dependency_chain` (arXiv:2608.13867 —
the 206-record reliability monograph).

This is a consistency pass (IDLE-STATE RULE clause c), not new research. It checks the project's own
toolchain against the empirical picture of what production harnesses actually look like.

## The seven canonical subsystems → project tools

The harness-anatomy paper maps seven canonical subsystems; the project's own decomposition
(`concept_bottleneck_is_the_model_harness_coupling`, six runtime responsibilities) lines up with it:

| subsystem (anatomy) | project responsibility | where it lives in `tools/` |
| --- | --- | --- |
| **the loop** | control | `loop_session.LoopSession` (wraps a run), `loop_adapter` |
| **tools / actions** | action | not modelled directly — the loop's increments *are* the actions; `exec_guard` bounds them |
| **context management** | context | `context/loop_policy` component (registry), `experience_bank` (retrieval), `loop_metrics.trace_legibility` |
| **state / session** | state | `harness_registry` version chains, `loop_session` run records (`runtime/observations/loop_runs/`) |
| **safety controls** | verification | `exec_guard` (pre-commit hook), `improvement_loop.verify_loop_edit` (6-check gate + `paired_eprocess`), `tamper_audit` |
| **orchestration** | — | not built — single-agent (the loop); Phase 6 is untouched; `probe_orchestration_value` is the design probe |
| **extension surfaces** | — | `skill_induction` (Phase 4 skeleton), the scheduled-task `SKILL.md` |
| observation (project's 6th) | observation | `trace_substrate.Recorder`, `topology_recover` |

**Gap surfaced:** the project has no explicit *action/tool* subsystem — increments are executed directly by
the loop with `exec_guard` as the only boundary. That is fine for a research loop but is the subsystem a
real harness invests most in. Noted, not a blocker.

## The four headline empirical findings → project status

| finding (arXiv:2609.00006, ~4M LOC, 11 harnesses) | project |
| --- | --- |
| **no runtime imports a general-purpose agentic framework** | ✅ `tools/` is pure stdlib, no dependencies (`tools/README.md` line 3) — the mainstream choice, not a shortcut |
| **none retrieves code with vector embeddings; deterministic retrieval only** | ✅ `experience_bank` retrieval is substring/key match; `topology_recover` is deterministic role recovery; no embeddings anywhere |
| **SKILL.md skills lead MCP in adoption (9/11 vs 8/11)** | ✅ the 6-hourly loop runs from `C:\Users\PC\.claude\scheduled-tasks\agentic-universe-research-loop\SKILL.md`; no MCP dependency |
| **behavioural policy migrating from prompt prose to configuration** | ✅ `context/loop_policy` is a JSON config component (`read_first` / `pin` / `compress` / `do_not` / `rules`), kept in sync with `loop_adapter.LOOP_CONTEXT_POLICY`; `emergent_constraint_weakening_at_handoffs` is the reason |

The longitudinal finding — *convergence becoming imitation* — is the one caution: a research graph that
keeps folding "the field converged on X" is itself part of that convergence. `pattern_structural_decoupling`
is the counterweight, and `docs/what_would_make_this_wrong.md` §4 tracks diversity erosion.

## The monograph's dependency chain → project

`concept_coding_agent_reliability_is_a_system_property_evaluated_as_a_dependency_chain`: weaknesses in task
construction / execution / retrieval / state / verification / observability can invalidate downstream
conclusions. The project's held-out set has patched three of these already — search contamination (run
166), format-repair scoring (run 194), category masking (run 116) — and the paired e-process (run 220)
addresses the multiple-testing weakness in the verification link. The **observability** link was the one unpatched dependency — **closed run 226**: `loop_metrics.status_line`
renders the key signals into a one-line health glance (`OK` / `WATCH` / `STOP`), `loop_session._write_summary`
stamps it into every `run-<N>.json` as `status_line`, and `python tools/loop_metrics.py status` prints the
latest. Example: `run 226 OK · VALID · graph +0n/+1e · cites 0v/0 · idle-streak 0 · legible 1.00 · verified-frac 0.79`.

## Verdict

The project's build choices are **mainstream, not idiosyncratic** — every one of the four headline
findings validates a choice already made. The two real gaps are the two subsystems the project has never
claimed to build: an action/tool layer and orchestration (Phase 6). Both are known and documented.

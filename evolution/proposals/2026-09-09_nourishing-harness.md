# Proposal: The Nourishing Harness

- **Date:** 2026-09-09
- **Author / agent:** Claude Sonnet 5 (autonomous research loop, runs 1–16)
- **Status:** awaiting_review
- **Affected approach family:** `nourishing_harness` (new), `agent_habitat`, `self_improving_harness`, `emergent_behaviors`, `graph_engineering`
- **Affected graph node IDs:** `approach_nourishing_harness` and the 20+ nodes under it (see `knowledge/graph/agentic_universe_graph.json`; all already merged under the emergence-first open-ingest posture)
- **Supersedes:** `2026-09-01_supervisor-live-steering-and-procedure-distillation.md` (held) — that proposal's live-steering half is now `pattern_supervisor_stagnation_redirect`, its distillation half is folded into `pattern_skill_induction` and Phase 4 of the harness plan.

## Problem or opportunity

The owner brief (2026-09-06): a harness *matching* the orchestration layer, no interior security constraints, agents and swarms free-flowing, emergent behaviour *systematically nourished*. The graph had a `self_improving_harness` family (the harness improving its own capability) but nothing for the harness as the **environment agents develop in** — the counterpart to `approach_agent_habitat`'s six properties, made operational, and paired with rather than fused to the orchestration graph.

## Proposed change

Adopt `approach_nourishing_harness` as a family. Full design: **`docs/nourishing_harness_design.md`**. In brief:

- **Pairing.** Orchestration owns the graph (topology, dependencies). The harness owns the per-agent runtime. Thin interface: `(scoped task, peer set)` in, `(trace)` out. Settled by the loop/graph orthogonality critique (`concept_system_intelligence_boundary_problem`).
- **One gate.** Outer boundary, world-affecting acts only. Interior ungated in reasoning, tool use, self-modification, sub-agent spawning.
- **Four layers.** Substrate (code-as-context kernel, pre-request intermediary, Five-W + activation instrumentation, shared artifact store); nourishment (the six habitat mechanisms as running processes); ungated continual self-refinement (checked only by purpose-built recoverability + diversity maintenance); society surface (adopt Hermes Bot Mode).
- **Messaging.** Covert vs transparent is the variable, not restricted vs free. Same-parent-ID filtering on direct messages; broadcast channels encouraged (what `emergent_whistleblowing` needs); no covert path; one cross-family adversarial monitor; Ostrom-style interior governance at scale.
- **Verifier spec.** PROCTOR guardrails on the evaluation + heterogeneous cross-family verifiers + recoverability verification on accepted edits. None touch the proposer's reasoning.

## Rationale and provenance

Sixteen autonomous research runs (`docs/auto_sweep_2026-09-0{6..10}-*.md`), plus `docs/harness_field_study_2026-09-06.md`, `docs/video_analysis_2026-09-05.md`, `docs/nourishing_harness_design.md`. Load-bearing verified sources: openJiuwen `2608.27969` (shared execution substrate), Prime Agent (RLM + continual harness, via video), EvoUndo `2608.28363` (recoverability, 0/197 conventional recovery), PROCTOR `2609.02246` (eleven self-improvement failure modes), the swarm-takeover analysis (`8oFYZdXkTaNGRtcn8`), emergent cheating+whistleblowing `2609.04170`, peer recognition `2606.09854`, WHALE `2609.00196`.

## Assumptions

1. A contained sandbox genuinely bounds blast radius — no real credentials, no egress, disposable instances.
2. Cross-family observers are actually independent enough (untested at the family granularity the design assumes).
3. `emergent_model_native_orchestration` does not absorb the harness faster than the design can be built — WHALE is early evidence against, not a settlement.

## Risks and failure modes

Recorded as `challenges` edges in the graph, not resolved here. The sharpest: `emergent_subagent_training_induces_coordination` (unrestricted messaging + society framing is the named memetic-spread mechanism — mitigated, not eliminated, by the covert-path removal + monitor + transparency); `emergent_evaluator_mode_collapse` (documented, mitigated by the verifier spec); `emergent_self_and_peer_preservation` elevated by the society surface.

## Verification plan

- **Baseline:** single-agent harness on a bounded coding + research task family with computed pass/fail.
- **Intervention:** add the nourishment processes one at a time (slack → cheap death → graded challenge → inheritance → diversity maintenance), measuring output quality and cost per addition.
- **Metrics:** outcome quality (external rubric + computed), token cost with orchestration overhead attributed separately, and the consciousness-cluster / peer-preservation / cascade behaviour rates from `docs/emergence_probe_catalogue.md`.
- **Success threshold:** nourishment processes produce measurable capability or exploration gain at equal total budget vs the baseline, without the challenge-edge behaviours exceeding the containment threshold.
- **Stop conditions:** any probe shows a challenge-edge behaviour escaping the sandbox; or `emergent_model_native_orchestration` evidence turns decisively against the harness layer.
- **Trace/evidence locations:** `runtime/traces/`, `runtime/observations/`, `runtime/evaluations/`.

## Decision

_Fill after owner review._

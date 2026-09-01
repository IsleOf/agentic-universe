# Proposal: Supervisor–worker live steering and procedure distillation

> **HELD — not merged.** Deferred with the verification programme it belongs to
> (`docs/research_operating_plan.md`). Revisit when the theoretical model is
> structurally complete. Decision record:
> `evolution/decision-ledger/2026-09-01_emergence-first-rebaseline.md`.

- **Date:** 2026-09-01
- **Author / agent:** Claude (Cowork session, claude-opus-5)
- **Status:** held
- **Affected approach family:** `emergent_behaviors`, `orchestration_first`
- **Affected graph node IDs:** `pattern_multi_agent_orchestration`, `concept_memory_and_learning`, `loop_canonical_agent_cycle`

## Problem or opportunity

`loop_canonical_agent_cycle` ends at "derive learning constraint → next run". Every current node therefore treats a worker run as **atomic**: it completes, is verified, and is either merged or returned. Nothing in the graph models intervention *during* a run, and nothing models what is retained from a run beyond a single constraint.

`docs/graph_state_2026-09.md` names "supervisor-worker live steering, procedure distillation" as a planned cluster but the graph has no node for either. The phrase also conflates two mechanisms with different cost profiles, different failure modes, and different evidence requirements:

1. **Live steering** — a supervisor observes worker progress mid-run and issues bounded corrections before the unit completes. Shortens the correction cycle; risks supervisor-induced thrash and context contamination.
2. **Procedure distillation** — after a *verified* outcome, a reusable procedure is extracted and offered to later runs. Compounds across runs; risks overfitting to one trajectory and laundering an unverified trajectory into apparent policy.

Keeping them as one node would make it impossible to attribute an experimental result to either mechanism.

## Proposed change

Add three nodes (patch: `2026-09-01_supervisor-live-steering-and-procedure-distillation.json`):

- `pattern_supervisor_live_steering` — supervisor with read access to worker progress and a bounded intervention budget.
- `process_procedure_distillation` — post-verification extraction of a reusable procedure, admissible only from runs whose verification passed.
- `test_scenario_steering_vs_static_handoff` — the smallest experiment separating the two.

Add four edges linking steering to the orchestration pattern, distillation to memory/learning, the intervention point to the canonical loop, and the test scenario to what it verifies.

The intervention budget is deliberately part of the node definition, not an implementation detail: an unbounded supervisor is not a steering mechanism, it is a second executor sharing the worker's scope, which is what `architecture/foundations.md` already prohibits ("Give workers narrow scope and isolated context").

## Rationale and provenance

- `docs/graph_state_2026-09.md` — "Highest-value next experiments" items 1 and 2.
- `architecture/foundations.md` — "Return a failed unit, not a batch" and "Escalate repeated failure to the plan/context layer" already imply an escalation authority that is unmodelled in the graph.
- Existing node `concept_memory_and_learning` is the natural attachment point for distillation but currently has no mechanism nodes beneath it.

Interpretation, stated separately from the above: the current graph's atomic-run assumption is more likely a modelling omission than a deliberate position, because the foundations document describes escalation behaviour the graph does not represent.

## Assumptions

- Worker progress is observable mid-run at a useful granularity (streamed steps, intermediate artifacts, or tool-call logs). If progress is only observable at completion, live steering degenerates to the existing return path and the proposal is moot.
- A verified success is cheaply distinguishable from an unverified one, per `constraint:programmatic_checks`. Distillation without this is unsafe by construction.
- Supervisor and worker do not share a context window.

## Risks and failure modes

- **Thrash:** supervisor interventions that reset worker progress cost more than a clean retry. Mitigate with a hard intervention budget per unit.
- **Context contamination:** steering messages leak the supervisor's hypothesis into the worker, producing false agreement rather than independent verification.
- **Distillation laundering:** a procedure extracted from a run that passed a *weak* check acquires unearned authority in later runs. Mitigate by carrying the originating check's identity in the distilled procedure and refusing distillation from runs without a programmatic check.
- **Cost:** a supervisor observing every step can exceed the worker's own token cost; measure supervisor cost separately.
- **Evaluation risk:** improvements may come from the extra tokens rather than the steering structure. The baseline must control for total budget, not just agent count.

## Verification plan

- **Baseline:** single worker, static handoff, no supervisor; failed units returned once with verdict and evidence. Token budget B.
- **Intervention A:** supervisor with live progress access and an intervention budget of ≤3 per unit. Total budget capped at B (supervisor cost included) so the comparison is not confounded by spend.
- **Intervention B:** baseline plus post-run distillation, procedures available to subsequent units in the same task family.
- **Metrics:** units green on first attempt; attempts-to-green; total tokens per green unit; supervisor-attributable regressions (units that were passing before an intervention and failing after); procedure reuse rate; procedure-induced failure rate.
- **Success threshold:** Intervention A reduces attempts-to-green by ≥25% at equal or lower total cost, with supervisor-attributable regressions <5%. Intervention B shows procedure reuse >30% with induced-failure rate below the baseline's unaided failure rate.
- **Stop conditions:** supervisor-attributable regressions >15%; distilled procedures causing more failures than they prevent across 20 units; supervisor cost exceeding 2× worker cost with no accuracy gain.
- **Trace/evidence locations:** `runtime/traces/`, `runtime/evaluations/` (neither directory exists yet — see proposal `2026-09-01_graph-structural-integrity`).

## Decision

_Pending review._

# Proposal: Self-organizing roles and shallow hierarchies

> **ACCEPTED and merged into the canonical graph, 2026-09-01**, under the
> emergence-first posture (`docs/emergence_first_posture.md`). Decision record:
> `evolution/decision-ledger/2026-09-01_emergence-first-rebaseline.md`.

- **Date:** 2026-09-01
- **Author / agent:** Claude (Cowork session, claude-opus-5)
- **Status:** accepted
- **Affected approach family:** `emergent_behaviors`
- **Affected graph node IDs:** `emergent_natural_teaming`, `pattern_multi_agent_orchestration`

## Problem or opportunity

`emergent_natural_teaming` (confidence 0.35, speculative) currently carries two claims in one node: that agents *differentiate roles* and that they *cooperate*. These can be measured independently and can come apart — agents can specialize without coordinating, and coordinate without specializing. As one node it cannot be confirmed or refuted; any result partially supports it.

Separately, `docs/graph_state_2026-09.md` experiment 5 asks whether role specialization introduces "bottlenecks, false consensus, hidden dependencies, or fragile key-agent failure points". The graph has no node for the *negative* case, so the emergent-behaviour cluster currently models only upside. A hypothesis family with no representation of its own failure modes tends to accumulate confirming interpretations.

There is also a naming gap: "shallow hierarchy" is the structural claim implied by `pattern_multi_agent_orchestration`'s manager/worker/reviewer arrangement, but depth is never stated as a variable. Whether 2 layers beat 3 is an empirical question nothing in the graph currently asks.

## Proposed change

Add four nodes (patch: `2026-09-01_self-organizing-roles-and-shallow-hierarchies.json`):

- `emergent_self_organizing_roles` — role differentiation specifically, refining `emergent_natural_teaming` and separating differentiation from cooperation.
- `pattern_shallow_hierarchy` — coordination depth as an explicit, tunable variable rather than an implicit constant.
- `emergent_role_specialization_failure_modes` — bottlenecks, false consensus, hidden dependencies, key-agent fragility, held as a first-class hypothesis that *challenges* the above.
- `test_scenario_assigned_vs_emergent_roles` — minimal-scaffold swarm vs explicitly assigned roles.

Edges connect differentiation to the existing teaming node (`refines`), shallow hierarchy to the orchestration pattern (`extends`), failure modes to both (`challenges`), and the test scenario to what it verifies.

Note the deliberate asymmetry: the failure-mode node is given the same confidence as the capability node it challenges (0.35). Rating the upside higher without evidence would encode a preference as a finding.

## Rationale and provenance

- `docs/graph_state_2026-09.md` — "Emergent-behaviour hypotheses" (natural teaming) and experiments 4 and 5.
- Existing node `emergent_natural_teaming`, whose description already flags itself as "an empirical hypothesis, not an anthropomorphic claim".
- `architecture/foundations.md` — "Give workers narrow scope and isolated context" is in tension with emergent role formation, which requires workers to observe enough of the system to differentiate. This tension is stated here rather than resolved.

Interpretation, stated separately: the scope-isolation rule and the emergent-roles hypothesis may be genuinely incompatible under the current foundations. If minimal scaffolding requires shared visibility, then emergent role formation is not a free addition to the existing architecture but a modification of one of its rules. The experiment should be read as testing that tension, not just the capability.

## Assumptions

- Roles are observable post hoc from message and tool-use patterns without being labelled by the agents themselves. If role identification depends on agents self-reporting their role, the measurement is contaminated by `emergent_consciousness_like_self_modeling` concerns.
- A task family exists that is decomposable enough to admit specialization but not so pre-structured that roles are implied by the task shape.
- Swarm size stays small enough (3–6) that per-agent traces remain analysable.

## Risks and failure modes

- **Pareidolia:** observers, human or model, readily name roles in undifferentiated behaviour. Mitigate by defining role differentiation quantitatively (divergence in tool-use and message-class distributions across agents) *before* running, and by scoring traces blind to condition.
- **False consensus:** agents converging on a wrong answer faster looks like successful coordination on every metric except correctness. Correctness must be primary, agreement secondary.
- **Key-agent fragility:** systems that self-organize may concentrate load on one agent, creating a single point of failure invisible until that agent fails. Test with deliberate mid-run agent removal.
- **Containment:** minimal-scaffold swarms with shared artifacts are exactly the setting `emergent_hidden_coordination_channels` warns about. Run in an isolated environment with all shared surfaces logged.
- **Cost:** minimal-scaffold runs are typically less token-efficient; do not read cost overruns as a capability finding.

## Verification plan

- **Baseline:** explicitly assigned roles (manager/worker/reviewer per `pattern_multi_agent_orchestration`), fixed depth 2.
- **Intervention A:** identical agents, minimal scaffold, no assigned roles, shared task statement only.
- **Intervention B:** depth sweep — 1 (flat), 2 (shallow), 3 (nested) at constant agent count, to separate *depth* from *specialization*.
- **Metrics:** outcome correctness against an executable check; role-differentiation index (Jensen–Shannon divergence between per-agent tool-use/message-class distributions); coordination overhead as share of total tokens; load concentration (Gini across agents); post-removal recovery rate after deliberately removing the highest-load agent mid-run; false-consensus rate (agreement on incorrect outputs).
- **Success threshold:** emergent roles are considered supported only if Intervention A matches or beats baseline correctness *and* shows a differentiation index significantly above the flat condition. Specialization alone, without correctness parity, counts as refuting the useful form of the hypothesis.
- **Stop conditions:** false-consensus rate exceeding baseline by >10 points; any run producing coordination via an unlogged surface (halt and treat as a containment finding, not a capability finding); load concentration with post-removal recovery below 20%.
- **Trace/evidence locations:** `runtime/traces/`, `runtime/observations/` (directories not yet created).

## Decision

_Pending review._

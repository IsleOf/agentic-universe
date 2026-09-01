# Proposal: Five-W communication instrumentation for multi-agent swarms

- **Date:** 2026-09-01
- **Author / agent:** Claude (Cowork session, claude-opus-5)
- **Status:** awaiting_review
- **Affected approach family:** `emergent_behaviors`, `control_plane_governance`
- **Affected graph node IDs:** `pattern_multi_agent_orchestration`, `emergent_hidden_coordination_channels`, `pattern_append_only_audit` (subnode)

## Problem or opportunity

Three of the five "highest-value next experiments" in `docs/graph_state_2026-09.md` measure *outcomes* of multi-agent arrangements (steering, emergent roles, specialization risks). None of them can be interpreted without a record of what agents actually said to each other, when, and why. Message-level instrumentation is currently assumed by those experiments and provided by nothing in the graph.

The Five Ws — sender/receiver, content class, timing, purpose, channel — are named once in `graph_state` as an experiment, but they are not an experiment. They are the **measurement substrate** the other experiments depend on. Modelling them as one more hypothesis alongside the others gets the dependency backwards and invites running the capability experiments first, producing traces that cannot answer the questions asked of them.

There is a second, sharper reason to build this first. `emergent_hidden_coordination_channels` (confidence 0.45) is the highest-confidence hypothesis in the emergent cluster and the only one framed as a safety risk. A hidden channel is by definition one that is *not* in the message log. Complete Five-W instrumentation of the sanctioned channels is what makes an unsanctioned channel detectable — coordination that appears in outcomes but not in the log. Without it, that node is untestable in principle, not merely untested.

## Proposed change

Add two nodes (patch: `2026-09-01_five-w-communication-instrumentation.json`):

- `pattern_five_w_message_instrumentation` — every inter-agent message carries sender, receiver, content class, timestamp, declared purpose, and channel identifier.
- `verification_suite_communication_topology` — the analysis layer over those records: topology, message-class distributions, timing, and the sanctioned-vs-observed coordination gap.

Four edges: instrumentation supports the orchestration pattern, instrumentation *detects* hidden coordination channels, the suite measures instrumentation output, and instrumentation supports the control plane's audit requirement.

The last edge matters for sequencing: `concept_config_driven_control_plane` already claims "durable audit" via its `pattern_append_only_audit` subnode. Five-W message records are a concrete instance of that audit surface, so this proposal partially implements an existing to_test node rather than adding an unrelated one. It is the cheapest node in this batch and unblocks the other three.

## Rationale and provenance

- `docs/graph_state_2026-09.md` — experiment 3, and the dependency structure of experiments 1, 2, 4, 5.
- Existing nodes `emergent_hidden_coordination_channels` and `pattern_append_only_audit` (subnode of `concept_config_driven_control_plane`).
- `architecture/foundations.md` — "Every dependency edge must carry a named artifact; remove chronological-only edges." Message records make the artifact on each coordination edge explicit and machine-checkable.

Interpretation, stated separately: the foundations rule about named artifacts on dependency edges is currently enforced only by review convention. Five-W records would make it enforceable by tooling — a coordination edge with no corresponding message artifact becomes a detectable defect rather than a stylistic lapse.

## Assumptions

- All sanctioned inter-agent communication passes through a surface that can be intercepted. If agents share a context window or a filesystem directly, "channel" is not well defined and the gap metric loses meaning.
- Declared purpose is recorded from the *sending* framework's call site, not inferred from message text after the fact. Inferred purpose would make the record a model artifact rather than an observation.
- Content class can be assigned from a small fixed taxonomy (request, answer, correction, status, escalation, verdict) with acceptable inter-rater agreement.

## Risks and failure modes

- **Declared-purpose drift:** agents or frameworks label a message with a purpose that does not match its effect. Purpose is a claim about intent, not evidence of function; analysis must treat it as such and cross-check against downstream effect.
- **Observation cost:** full logging of a large swarm produces traces too large to analyse, which in practice means they go unanalysed. Cap swarm size and retain full traces only for sampled runs.
- **False security:** complete logs of sanctioned channels can create confidence that no other channel exists. The gap metric is evidence of *unexplained* coordination, never proof of its absence.
- **Privacy/secrets:** message logs are the most likely place for credentials or personal data to end up in this repo. Per operating rule 9, traces committed here must be scrubbed, and raw traces should stay out of version control entirely.
- **Taxonomy lock-in:** a content-class taxonomy fixed too early biases later analysis. Version the taxonomy and record which version produced each trace.

## Verification plan

- **Baseline:** current uninstrumented multi-agent run; outcomes recorded, message content not structured.
- **Intervention:** identical run with full Five-W records on every sanctioned message.
- **Metrics:** instrumentation overhead (tokens and latency as % of baseline); coverage (share of messages with complete Five-W fields); message-class distribution per agent; topology density and centralization; **sanctioned-vs-observed coordination gap** — cases where two agents' outputs show dependency with no message path connecting them.
- **Success threshold:** ≥98% field coverage at <5% token overhead, and the topology analysis reproduces known assigned roles in a control condition where roles *are* assigned. If instrumentation cannot recover roles that were explicitly assigned, it is not sensitive enough to detect emergent ones, and the role experiments should not proceed on it.
- **Stop conditions:** overhead >15% of run cost; coverage below 90% (partial logs invite unsupported conclusions about the unlogged remainder).
- **Trace/evidence locations:** `runtime/traces/` for scrubbed samples, `runtime/evaluations/` for topology analyses.

## Sequencing note

This proposal is a prerequisite for `2026-09-01_supervisor-live-steering-and-procedure-distillation` and `2026-09-01_self-organizing-roles-and-shallow-hierarchies`. Recommend accepting and building this first even if the other two are deferred; running them first produces traces that cannot answer their own questions.

## Decision

_Pending review._

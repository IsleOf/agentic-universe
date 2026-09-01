# Proposal: Evidence substrate, baseline comparison, and a promotion gate

> **HELD — not merged.** Deferred with the verification programme it belongs to
> (`docs/research_operating_plan.md`). Revisit when the theoretical model is
> structurally complete. Decision record:
> `evolution/decision-ledger/2026-09-01_emergence-first-rebaseline.md`.

- **Date:** 2026-09-01
- **Author / agent:** Claude (Cowork session, claude-opus-5)
- **Status:** held
- **Affected approach family:** `control_plane_governance`, `orchestration_first`
- **Affected graph node IDs:** all 11 nodes currently at `status: stable_theory`; `process_change_proposal`; `approach_orchestration_first`

## Problem or opportunity

This is the largest contradiction currently in the repository, and it is a governance issue rather than a research one.

`docs/graph_state_2026-09.md` states the evidence standard: *"Promote a node only after evidence is reproducible, attributable, and relevant to the stated domain."* The handover adds operating rule 6: *"Do not treat agent outputs, chat statements, or model self-reports as verified facts by default."*

Measured against the current graph:

- **11 of 19 nodes** carry `status: stable_theory`, and 11 carry `verification_state: partially_validated`.
- **1 of 19 nodes** has a `derived_from` field (`concept_config_driven_control_plane`, citing two Hackernoon articles).
- **0 of 19 nodes** have `evidence_links`. The field is defined in the schema, required by handover rule 5, and used nowhere.

So eleven nodes are marked *partially validated* with no recorded attribution of what validated them. On the standard the project has already written down, none of those eleven qualify for their current status. The most likely reading is that `stable_theory` is being used to mean "I am fairly confident in this" rather than "this survived a test" — which is precisely the conflation operating rule 6 exists to prevent.

Confidence values compound the problem. Values from 0.2 to 0.8 appear with no rubric anchoring them, so 0.72 and 0.75 are not distinguishable claims. Numeric confidence without a rubric reads as precision the evidence does not support.

Separately, `graph_state` experiment 1 — single capable agent with deterministic tools vs a manager-worker-reviewer harness — is the load-bearing test for the entire `orchestration_first` family, which sits at confidence 0.75. It has no node.

## Proposed change

Add three nodes (patch: `2026-09-01_evidence-substrate-and-promotion-gate.json`):

- `principle_evidence_before_promotion` — a status may only be raised when a named, replayable evidence artifact is linked. Absent that, the node stays `speculative` or `to_test` regardless of how plausible it seems.
- `verification_suite_single_vs_multi_agent_baseline` — experiment 1, made a first-class node.
- `approach_comparison_single_agent_vs_orchestrated` — the comparison result slot, so a future finding has a defined home and cannot be absorbed silently into prose.

Plus `add_edges` connecting the principle to the proposal process it constrains, and the baseline suite to the approach family it tests.

**Deliberately not included in the patch:** any `update_nodes` entry demoting the eleven `stable_theory` nodes. That would be a large, contentious change to canonical knowledge and it is the owner's call, not an agent's. Three options, for the owner to choose:

1. **Demote to `to_test`** until evidence is attached. Most consistent with the written standard; makes the graph look less settled than it feels.
2. **Keep status, add an explicit `evidence_basis: authorial_judgment`** field to the schema, distinguishing "reasoned position" from "tested finding" without pretending either is the other.
3. **Retroactively attach `derived_from`** to the conversation archives in `conversations/raw/` that produced each node, acknowledging these are source material rather than validation.

Option 2 is the recommendation: it is honest about what the eleven nodes are, requires no demotion, and makes the distinction machine-readable. Option 3 is worth doing regardless of which is chosen, since provenance is currently missing entirely.

## Rationale and provenance

- `docs/graph_state_2026-09.md` — "Evidence standards" section; experiment 1.
- `docs/claude_desktop_handover.md` — operating rules 4, 5, 6; "Definition of done".
- `knowledge/graph/agentic_universe_graph.json` — field-level counts above, obtained by direct inspection of the canonical file at commit `ef4ed3e`.
- `architecture/foundations.md` — "Absence of an error is not proof of correctness."

The counts are observations. The inference that `stable_theory` is being used as a confidence synonym is interpretation, and the owner is better placed than I am to say whether that is what happened.

## Assumptions

- The eleven nodes were authored as reasoned positions rather than as claims of empirical validation. If any of them *do* have evidence behind them that simply was not linked, option 3 resolves it and this proposal overstates the problem.
- A rubric with 4–5 anchored bands is more useful than continuous confidence values. Continuous values invite false precision at the second decimal.
- The project wants the graph to be auditable by someone who was not in the originating conversations. If it is primarily a personal thinking aid, the standard can be relaxed deliberately — but then the written standard should be relaxed to match, rather than left aspirational.

## Risks and failure modes

- **Bureaucratic drag:** a promotion gate can make the graph tedious to extend, pushing real thinking outside it. Mitigate by keeping `speculative` cheap to add — the gate applies only to *raising* status.
- **Demotion churn:** option 1 would mark most of the graph unvalidated at once, which may misrepresent genuinely well-founded architectural reasoning as flimsy.
- **Rubric gaming:** once bands are defined, there is pressure to write evidence that clears a band rather than evidence that settles a question.
- **Baseline underpowered:** a single bounded task cannot support a general claim about multi-agent value. The comparison node must record task family and refuse to generalize beyond it.
- **Baseline strength:** the single-agent arm must be a genuinely strong baseline with good deterministic tools. A weak baseline would manufacture support for the orchestration family, which is the outcome the family's own confidence rating already leans toward.

## Verification plan

- **Baseline:** one capable agent with deterministic tools (search, execution, validation) on a bounded task family with an executable check.
- **Intervention:** manager-worker-reviewer harness per `pattern_multi_agent_orchestration`, same task family, **same total token budget**.
- **Metrics:** correctness against the executable check; total cost per correct outcome; wall-clock latency; retry count; policy violations; recovery quality after an injected failure.
- **Success threshold:** the orchestrated arm must beat the single-agent baseline on correctness *at equal or lower cost* to justify `approach_orchestration_first` remaining above 0.6 confidence. Matching correctness at higher cost is a negative result for the family and should be recorded as such.
- **Stop conditions:** baseline arm found to be under-tooled (halt, strengthen, restart — a weak baseline invalidates the comparison); task family too easy for either arm to fail.
- **Trace/evidence locations:** `runtime/evaluations/`, with the comparison result written to `approach_comparison_single_agent_vs_orchestrated`.

## Decision

_Pending review. The three options for the eleven `stable_theory` nodes need an explicit choice; the patch itself is safe to accept independently of that decision._

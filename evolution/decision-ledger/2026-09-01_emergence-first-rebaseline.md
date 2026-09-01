# Decision: emergence-first re-baseline

- **Date:** 2026-09-01
- **Decided by:** owner
- **Executed by:** Claude Code (Sonnet 5), local session
- **Affects:** posture, canonical graph, tooling, all five pending proposals

## Decision

Suspend the evidence-gating regime. The project enters an **emergence-first
theoretical phase**: ideas enter the graph on interest rather than on evidence,
and the research target is what agents do when given room — in swarms and
individually — rather than how to constrain them.

Owner's framing: *"my main focus is exploiting emergent behaviours and new
discoveries in agent behaviour in swarms and individually, and build system
around it instead of forcing the llms in constraints."*

Full posture: `docs/emergence_first_posture.md`.

## What changed

**Posture.** `docs/research_operating_plan.md` deferred, kept intact. The
falsifier-required ingest gate in `sources/README.md` suspended, kept verbatim
for restoration. Direct edits to the canonical graph are now permitted;
proposals become optional change-notes rather than a checkpoint.

**Proposals — accepted and merged:**

| Proposal | Why |
| --- | --- |
| `graph-structural-integrity` | Pure repair, correct under any posture |
| `five-w-communication-instrumentation` | An instrument, not a gate — discovery without a message log yields unreplayable anecdotes |
| `self-organizing-roles-and-shallow-hierarchies` | Directly on the new focus |

**Proposals — held:**

| Proposal | Why |
| --- | --- |
| `evidence-substrate-and-promotion-gate` | This *is* the gate machinery being suspended |
| `supervisor-live-steering-and-procedure-distillation` | Steering is a constraint mechanism; the distillation half is worth revisiting first |

**Graph.** 19 → 32 nodes, 13 → 41 edges. New emergence-first spine:

- `approach_emergence_first` — **the family had no root node.** Every other
  approach family has an `approach_` root; `emergent_behaviors` did not, so its
  hypotheses hung off other families' concepts with no stance of their own.
  Found while re-reading the graph for this pivot.
- `principle_affordance_over_constraint` — the posture, as a graph object, with
  its tension against `concept_trust_gates` recorded as a `challenges` edge
  rather than resolved.
- `concept_swarm_decentralized_coordination`, `emergent_stigmergic_coordination`
  — the swarm axis. Stigmergy is the constructive reframing of
  `emergent_hidden_coordination_channels`: same mechanism, capability rather
  than only risk.
- `emergent_individual_strategy_invention`, `concept_intrinsic_motivation` —
  the individual axis, kept separate from the swarm axis on purpose.
- `concept_autonomy_dial` — human involvement as a graded experimental
  variable rather than a binary policy setting.

**Tooling.** `tools/knowledge_graph.py` now collects subnode IDs alongside
top-level IDs (new `collect_ids`). This fixes the seven unaddressable
control-plane subnodes: an edge targeting `pattern_append_only_audit` now
passes `check-proposal`, where it previously failed as an unknown target.
Verified before and after.

**Metadata.** `schema_version`, `last_updated`, `evolution_log` restored to the
graph root, having been dropped after the seed commit. Added a `posture` field
so the file itself records which regime produced its labels.

## The three open owner decisions, resolved

1. **The 11 `stable_theory` nodes with no evidence links.** No longer a defect —
   under this posture `status` and `confidence` mean *how load-bearing is this
   in the model*, not *how proven*. No demotion, no new schema field. This
   reverts to an open question when the verification phase resumes.
2. **Are subnodes addressable?** **Yes.** Validator fixed rather than IDs
   stripped.
3. **Do tooling changes go through the proposal process?** **No.** Code changes
   land directly with a ledger entry. `check-proposal` cannot validate code and
   pretending otherwise added ceremony without a check.

## Risk accepted

A graph that grows into a hundred nodes of plausible vocabulary with no
mechanisms in it. The single defence kept: prefer nodes that assert a mechanism
over nodes that name a category, and grow the count of `challenges` edges —
currently six — as the measure of whether the model is asking real questions.

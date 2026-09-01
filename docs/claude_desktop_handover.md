# Agentic Universe — Claude Desktop Handover

## Purpose

Agentic Universe is a GitHub-backed, evolving knowledge base and design workspace for building reliable agentic systems. It records concepts, architectures, workflows, experiments, runtime evidence, and governance decisions so new agents can continue the work without relying on chat history.

The repository is the durable source of truth. Treat it as a curated system model, not a scratchpad.

## Start here

Read these files in order before proposing work:

1. `README.md` if present
2. `architecture/foundations.md`
3. `knowledge/graph/agentic_universe_schema.json`
4. `knowledge/graph/agentic_universe_graph.json`
5. `docs/graph_state_2026-09.md`
6. `evolution/proposals/README.md`
7. Recent files in `evolution/proposals/`, `evolution/decision-ledger/`, and `runtime/` if present

## Repository map

- `knowledge/graph/agentic_universe_graph.json` — canonical, curated knowledge graph
- `knowledge/graph/agentic_universe_schema.json` — evolving JSON Schema for graph nodes and edges
- `architecture/` — stable architecture notes and conceptual foundations
- `conversations/raw/` — preserved chat transcripts or archives; source material, not canonical truth
- `conversations/summaries/` — structured summaries of preserved conversations
- `conversations/extracted/` — claims and artifacts extracted from conversation sources
- `evolution/proposals/` — reviewable proposed graph, architecture, or process changes
- `evolution/decision-ledger/` — accepted/rejected decisions and rationale
- `runtime/observations/` — raw observations from agent runs
- `runtime/evaluations/` — evaluation results and comparisons
- `runtime/traces/` — replayable run traces
- `runtime/reward-ledger/` — durable learning/reward evidence, if adopted
- `tools/knowledge_graph.py` — graph validation, summary, and safe proposal checking utility

## Operating rules

1. Do not overwrite or casually rewrite the canonical graph.
2. Read the schema before creating nodes or edges.
3. Convert new ideas into a proposal first, especially if they are speculative or source-derived.
4. Mark uncertain claims with `status: speculative` or `to_test` and `verification_state: needs_empirical_validation`.
5. Preserve provenance in `derived_from`, and connect evidence with `evidence_links` when available.
6. Do not treat agent outputs, chat statements, or model self-reports as verified facts by default.
7. Keep irreversible actions outside the graph behind explicit policy/approval controls.
8. Prefer small, reviewable commits with clear commit messages.
9. Never commit credentials, API keys, cookies, browser profiles, personal data, or raw secrets.

## Standard workflow

1. Inspect the current graph and supporting documents.
2. State the exact problem, node cluster, or architecture decision being addressed.
3. Create a proposal in `evolution/proposals/` using the supplied templates.
4. Validate a graph patch against the current canonical graph:

```bash
python tools/knowledge_graph.py validate
python tools/knowledge_graph.py check-proposal evolution/proposals/<proposal-file>.json
```

5. Summarize expected benefits, assumptions, risks, and the smallest viable experiment.
6. Ask the human owner for approval before merging a proposal into the canonical graph.
7. After approval, apply the patch, validate again, update the decision ledger/changelog, and commit.

## Graph semantics

The graph supports multiple approach families in one file. Use `approach_family` for the broad school of thought and `branch_key` for a more specific line of inquiry.

Current approach families include:

- `control_plane_governance`
- `orchestration_first`
- `agent_os_desktop`
- `marketplace_workflow`
- `emergent_behaviors`

Useful node metadata:

- `status`: epistemic/project maturity, such as `speculative`, `to_test`, `in_experiment`, `stable_theory`, `verified`, `controversial`, or `deprecated`
- `verification_state`: evidence state, such as `needs_empirical_validation`, `validated_in_sandbox`, `validated_in_production`, `refuted`, or `inconclusive`
- `confidence`: bounded numeric confidence from 0 to 1
- `derived_from`: source references
- `evidence_links`: graph IDs, file paths, or stable references to supporting/challenging evidence

## Current priority themes

- Governed control planes for multi-agent systems
- Canonical agent loops, memory, evaluation, and learning
- Desktop/browser agent operating surfaces with explicit capability boundaries
- Bounded business and marketplace workflows
- Emergent behavior research: live self-improvement, self-organizing roles, communication topologies, coordination, and safety failure modes

## Definition of done

A useful contribution is complete when it has: a clear artifact, provenance, a status and verification state, explicit links to affected graph nodes, a validation result, and a proposal/decision record when it changes canonical knowledge.

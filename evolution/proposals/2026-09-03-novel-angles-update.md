# Proposal: Novel angles & experiments 2026 update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: cost‑utility alignment, real‑time caps/anomaly detection, schema governance, HITL UX/fatigue, agent identity/federation, temporal logic/runtime verification, physical/edge/digital twins, red‑team/forensics, privacy/residency/lineage, RAG precision/drift, meta‑learning, multi‑modal limits, marketplace dynamics.

## Motivation

The broadest search pass confirmed twelve infrastructure‑level opportunity primitives that should be treated
as first‑class in Agentic Universe: cost‑utility control, schema governance, HITL UX, agent identity/trust,
formal verification, physical/edge, red‑team, privacy/lineage, RAG governance, meta‑learning, multi‑modal,
and marketplace dynamics. This commit adds a synthesis note and extends the graph patch with
the corresponding nodes and edges.

## What this commit adds

1. `knowledge/notes/novel-angles-experiments-2026.md` — design rules + candidate experiments.
2. `evolution/proposals/2026-09-03-novel-angles-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 1 cost node: `pattern-cost-utility-control`.
- 1 schema node: `pattern-schema-governance`.
- 1 UX node: `pattern-hitl-ux-fatigue`.
- 1 identity node: `pattern-agent-identity-federation`.
- 1 formal node: `pattern-runtime-verification`.
- 1 physical node: `pattern-physical-edge-agents`.
- 1 red‑team node: `pattern-red-team-forensics`.
- 1 privacy node: `pattern-privacy-lineage`.
- Edges link these to existing patterns (`pattern-progressive-skill-disclosure`, `pattern-dynamic-tool-injection`, `pattern-layered-agent-memory`, `pattern-massive-parallel-swarm`, `pattern-multi-gateway-fleet`) and to projects (`proj-hermes-agent`, `proj-google-adk`, `proj-openai-agents-sdk`, `proj-mastra`, `proj-kimi-k2-6`).

## Caveats

- Same connector limitation: generic node shape; validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`.
- Dedupe nodes if earlier patches already added them.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, landscape, solidifying, protocol/governance, structural primitives, attack surface, this one) via
   `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run 1–2 candidate experiments (cost‑utility pilot + schema governance test).

# Proposal: Next‑frontier angles 2026 update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: A2A negotiation, multi‑tenant agent management, durable execution/checkpoint‑merge, agent marketplaces/reputation, Gemini agentic video understanding, federated learning + agents, agent‑native CI/CD, edge/robot orchestration.

## Motivation

The broadest search pass confirmed eight infrastructure‑level opportunity primitives that should be treated
as first‑class in Agentic Universe: negotiation/SLAs, multi‑tenant control, durable execution, marketplace/reputation,
multi‑modal verification, privacy‑preserving learning, agent‑native CI/CD, and edge/robot orchestration. This commit adds a synthesis note and extends the graph patch with
the corresponding nodes and edges.

## What this commit adds

1. `knowledge/notes/next-frontier-angles-2026.md` — design rules + candidate experiments.
2. `evolution/proposals/2026-09-03-next-frontier-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 1 negotiation node: `pattern-agent-negotiation-slas`.
- 1 multi‑tenant node: `pattern-multi-tenant-control`.
- 1 durable execution node: `pattern-durable-execution`.
- 1 marketplace node: `pattern-marketplace-reputation`.
- 1 multi‑modal node: `pattern-multi-modal-verification`.
- 1 privacy‑learning node: `pattern-privacy-preserving-learning`.
- 1 CI/CD node: `pattern-agent-native-cicd`.
- Edges link these to existing patterns (`pattern-progressive-skill-disclosure`, `pattern-dynamic-tool-injection`, `pattern-layered-agent-memory`, `pattern-massive-parallel-swarm`, `pattern-multi-gateway-fleet`) and to projects (`proj-hermes-agent`, `proj-google-adk`, `proj-openai-agents-sdk`, `proj-mastra`, `proj-kimi-k2-6`).

## Caveats

- Same connector limitation: generic node shape; validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`.
- Dedupe nodes if earlier patches already added them.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, landscape, solidifying, protocol/governance, structural primitives, attack surface, novel angles, this one) via
   `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run 1–2 candidate experiments (A2A negotiation pilot + durable execution MVP).

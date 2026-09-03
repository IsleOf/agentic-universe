# Proposal: Structural primitives 2026 update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: A2A/MCP specs & foundation moves, Forrester AEGIS + "Stop Means Stop", OpenAI/Azure deprecations, LHTB benchmark, Kimi K2.6 Agent Swarm, SkillsInjector/MUSE‑Autoskill/ADK 2.0, Hermes v0.21.0 fleet.

## Motivation

The broadest search pass confirmed seven infrastructure‑level primitives that should be treated
as first‑class in Agentic Universe: two‑protocol stack (MCP+A2A), HITL enforcement, vendor
deprecations, long‑horizon benchmarks, massive parallel swarms, progressive skill disclosure,
and fleet control planes. This commit adds a synthesis note and extends the graph patch with
the corresponding nodes and edges.

## What this commit adds

1. `knowledge/notes/structural-primitives-2026.md` — design rules + candidate experiments.
2. `evolution/proposals/2026-09-03-structural-primitives-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 2 protocol nodes: `protocol-a2a`, `protocol-mcp` (if not already added by the protocol/governance patch).
- 1 benchmark node: `benchmark-lhtb`.
- 2 deprecation markers: `deprecation-openai-assistants-2026-08-26`, `deprecation-openai-agent-builder-evals-2026-11-30`.
- 3 pattern nodes: `pattern-progressive-skill-disclosure`, `pattern-parallel-swarm-reconciliation`, `pattern-fleet-gateway-registry`.
- Edges link these to existing patterns (`pattern-dynamic-tool-injection`, `pattern-layered-agent-memory`, `pattern-massive-parallel-swarm`, `pattern-multi-gateway-fleet`) and to projects (`proj-google-adk`, `proj-hermes-agent`, `proj-kimi-k2-6`).

## Caveats

- Same connector limitation: generic node shape; validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`.
- Dedupe `protocol-a2a`, `protocol-mcp`, `benchmark-lhtb`, and deprecations if earlier patches already added them.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, landscape, solidifying, protocol/governance, this one) via
   `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run 1–2 candidate experiments (two‑protocol pilot + LHTB stress test).

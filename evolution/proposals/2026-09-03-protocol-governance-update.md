# Proposal: Protocol + governance + deprecations update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: A2A/MCP foundation moves (Aug 2026), Forrester AEGIS/CSA guidance, Microsoft MCP guidance, OpenAI/Azure Assistants sunset (Aug 26, 2026), Google ADK 2.0, long‑horizon harness/compaction papers.

## Motivation

The broader search confirmed structural shifts at the protocol/governance layer: two‑protocol
stack (MCP vertical, A2A horizontal), binding HITL gate expectations, major vendor
deprecations (OpenAI/Azure Assistants), and explicit long‑horizon harness/compaction
primitives. This commit adds a synthesis note and extends the graph patch with protocol,
governance, and deprecation nodes.

## What this commit adds

1. `knowledge/notes/protocol-governance-deprecations-2026.md` — design rules + candidate
   experiments.
2. `evolution/proposals/2026-09-03-protocol-governance-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 2 protocol nodes: `protocol-a2a`, `protocol-mcp`
- 1 platform node: `proj-google-adk`
- 3 governance/pattern nodes: `pattern-hitl-approval-gates`, `pattern-progressive-skill-disclosure`, `pattern-compaction-as-primitive`
- 2 deprecation markers: `deprecation-openai-assistants-2026-08-26`, `deprecation-azure-assistants-2026-08-26`
- 1 benchmark node: `benchmark-lhtb`
- Edges link these to existing patterns (`pattern-cyclic-graph-orchestration`, `pattern-dynamic-tool-injection`, `pattern-layered-agent-memory`, `pattern-multi-gateway-fleet`) and to projects (`proj-hermes-agent`, `proj-agent-zero`, `proj-opencode`, `proj-pi`).

## Caveats

- Same connector limitation: generic node shape; validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`.
- Dedupe `proj-hermes-agent` if earlier patches were applied.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, landscape, solidifying, this one) via
   `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run 1–2 candidate experiments (two‑protocol pilot + HITL gate audit).

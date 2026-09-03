# Proposal: Attack surface & supply‑chain 2026 update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: SkillBloat token‑amplification, OWASP Agentic Skills Top 10, GitHub MCP allowlists, CSA trust‑boundary flaw, AOS/runtime split, SKILL.state compaction risks, Hermes v0.21.0 fleet, OpenAI/ADK/Mastra shifts.

## Motivation

The broadest search pass confirmed five infrastructure‑level threat primitives that should be treated
as first‑class in Agentic Universe: skills as executable code, MCP servers as governed dependencies,
AOS/runtime split, compaction safety, and fleet control planes. This commit adds a synthesis note
and extends the graph patch with the corresponding nodes and edges.

## What this commit adds

1. `knowledge/notes/attack-surface-supply-chain-2026.md` — design rules + candidate experiments.
2. `evolution/proposals/2026-09-03-attack-surface-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 1 pattern node: `pattern-skill-allowlist-registry`.
- 1 governance node: `governance-mcp-allowlist`.
- 1 runtime node: `runtime-aos-split`.
- 1 compaction node: `pattern-compaction-safety`.
- 1 fleet node: `pattern-fleet-control-plane`.
- Edges link these to existing patterns (`pattern-progressive-skill-disclosure`, `pattern-dynamic-tool-injection`, `pattern-layered-agent-memory`, `pattern-massive-parallel-swarm`, `pattern-multi-gateway-fleet`) and to projects (`proj-hermes-agent`, `proj-google-adk`, `proj-openai-agents-sdk`, `proj-mastra`).

## Caveats

- Same connector limitation: generic node shape; validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`.
- Dedupe nodes if earlier patches already added them.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, landscape, solidifying, protocol/governance, structural primitives, this one) via
   `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run 1–2 candidate experiments (skill allowlist pilot + compaction safety test).

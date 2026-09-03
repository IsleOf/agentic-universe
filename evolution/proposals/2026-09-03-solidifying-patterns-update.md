# Proposal: Solidifying patterns 2026 update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: arXiv (AgeMem 2601.01885, CMA 2601.09913, SkillsInjector 2605.29794, SelfOrg/ICLR 2026), Kimi K2.6 docs, LangGraph guides, Hermes v0.21.0, Agent Zero v2.11, Codex CLI SKILL.state.

## Motivation

The last search pass confirmed seven patterns that are deepening as models get stronger:
minimal-scaffolding emergence, unified/continuum memory, dynamic tool/skill injection,
deterministic cyclic orchestration, massive parallel sub-agent routing, harness-level
resilience (repair + compaction), and fleet control planes. This commit adds a synthesis
note and extends the graph patch with the new research nodes and edges.

## What this commit adds

1. `knowledge/notes/solidifying-patterns-2026.md` — design rules + candidate experiments.
2. `evolution/proposals/2026-09-03-solidifying-patterns-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 4 new research nodes:
  - `paper-agentic-memory` (AgeMem, arXiv 2601.01885)
  - `paper-continuum-memory` (CMA, arXiv 2601.09913)
  - `paper-skills-injector` (SkillsInjector, arXiv 2605.29794)
  - `paper-selforg-iclr-2026` (Stochastic Self-Organization, ICLR 2026)
- Edges link these to existing patterns (`pattern-layered-agent-memory`,
  `pattern-dynamic-tool-injection`, `pattern-mission-not-roles`, `pattern-cyclic-graph-orchestration`,
  `pattern-massive-parallel-swarm`, `pattern-context-doctor-repair`, `pattern-multi-gateway-fleet`).

## Caveats

- Same connector limitation: generic node shape; validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`.
- Dedupe `proj-hermes-agent` if earlier patches were applied.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, landscape, this one) via
   `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run 1–2 candidate experiments (memory schema compaction + dynamic tool loader).

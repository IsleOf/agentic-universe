# Proposal: Emergent-behavior research + harness space scan (Sept 2026)

- Date: 2026-09-03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: arXiv/OpenReview/MDPI/alphaxiv (emergence), GitHub releases + official project
  blogs (harness scan)

## Motivation

Two additions requested by the owner:
1. Current research on emergent agent/swarm behavior, framed as *exploitable* qualities
   (mission-not-roles, persona+ToM steering, pressure-field coordination, horizon
   amplification, heterogeneous collectives, evolutionary societies) with concrete
   candidate experiments.
2. A harness-space scan: Hermes v0.21.0 Pantheon, OpenCode v1.18.27 (repo moved to
   anomalyco), Agent Zero v2.11 (Context Doctor), Pi (repo moved to earendil-works,
   ~95k stars, engine behind OpenClaw).

## What this commit adds

1. `knowledge/notes/emergent-swarm-behavior-scan-2026-09.md` — 6 exploitable phenomena +
   constraints/risks + 5 candidate experiments.
2. `knowledge/notes/harness-space-scan-2026-09.md` — per-project changes + 6 converging
   trends.
3. `evolution/proposals/2026-09-03-emergence-harness-patch.json` — graph patch.

## Proposed graph changes

- 8 research nodes: `paper-pressure-field-coordination`, `paper-emergent-coordination-tdmi`,
  `paper-drop-the-hierarchy`, `paper-horizon-amplification-swarm`,
  `paper-heterogeneous-collectives`, `paper-evolving-agent-societies`, `paper-swarmbench`,
  `survey-mas-orchestration-2026`
- 10 new pattern nodes: `pattern-mission-not-roles`, `pattern-persona-tom-steering`,
  `pattern-pressure-field-coordination`, `pattern-horizon-amplification`,
  `pattern-heterogeneous-collective-memory`, `pattern-cron-memory-continuity`,
  `pattern-monitor-mode-llm-skip`, `pattern-agent-peer-comms`, `pattern-live-subagent-steering`,
  `pattern-context-doctor-repair`, `pattern-minimal-harness`
- 3 new project nodes: `proj-opencode`, `proj-agent-zero`, `proj-pi`
  (`proj-hermes-agent` already exists from the ECC patch)
- Edges link papers→patterns (supports), projects→patterns (implements), and connect to
  existing ECC nodes (extends / contrasts-with / relates-to).

## Caveats

- Same connector limitation as the ECC patch: generic node shape, validate against
  `knowledge/graph/agentic_universe_schema.json` before applying with
  `tools/knowledge_graph.py`; dedupe `proj-hermes-agent` if the ECC patch was applied.
- The MIPT "14%" figure and TDMI steering results are single-paper findings; the
  heterogeneous-collective report is self-published (scaffolded emergence, no ablations
  yet). Treat as hypotheses for the candidate experiments, not settled fact.

## Next steps

1. Apply both pending patches (ECC + this one) via `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Pick 1–2 candidate experiments (suggest: mission-vs-roles A/B + stigmergy prototype —
   both cheap on existing infra).

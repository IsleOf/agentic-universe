# Proposal: 2026‑09 harness/swarm landscape patterns update

- Date: 2026‑09‑03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Sources: community write‑ups (Sept 2026), official releases (Hermes v0.21.0, Agent Zero
v2.11, OpenCode v1.18.27, Pi), cross‑checks against arXiv/MDPI.

## Motivation

The owner's pasted landscape text contains several high‑signal patterns (dynamic tool
injection, long‑horizon state + compaction, cyclic graph orchestration, massive parallel
sub‑agent routing, containerized worker pools, harness‑boundary repair, fleet control
plane, minimalism pole). Some project/version claims need verification before being
canonical. This commit adds a synthesis note and extends the graph patch with the new
patterns, while flagging unverified claims.

## What this commit adds

1. `knowledge/notes/2026-09-harness-swarm-landscape.md` — synthesis + patterns to steal +
claims to verify + cross‑links to existing notes.
2. `evolution/proposals/2026-09-03-landscape-patterns-patch.json` — graph patch extending
the earlier emergence/harness patch with 5 new pattern nodes and edges.

## Proposed graph changes (delta)

- 5 new pattern nodes:
  - `pattern-dynamic-tool-injection`
  - `pattern-cyclic-graph-orchestration`
  - `pattern-massive-parallel-swarm`
  - `pattern-containerized-agent-workers`
  - `pattern-multi-gateway-fleet`
- Edges link these to existing nodes (`pattern-layered-agent-memory`, `pattern-hooks-enforcement`,
`proj-hermes-agent`, `proj-agent-zero`, `proj-pi`, `pattern-pressure-field-coordination`,
`pattern-horizon-amplification`, `pattern-agent-peer-comms`).
- Add a "claims to verify" marker node or keep as prose in the landscape note; prefer prose
for now to avoid polluting the graph with unverified entities.

## Caveats

- Same connector limitation: generic node shape; validate against
`knowledge/graph/agentic_universe_schema.json` before applying with
`tools/knowledge_graph.py`.
- Dedupe `proj-hermes-agent` if the ECC patch was already applied.
- Do not add VVAH/Glasswing, Swarms v15 "Akira", Microsoft ".AsHarnessAgent()", or
agent‑swarm.dev as canonical nodes until primary sources are confirmed.

## Next steps

1. Apply all pending patches (ECC, emergence/harness, this one) via `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Pick 1–2 cheap experiments (dynamic tool loader prototype + cyclic graph pilot on a
compliance‑sensitive workflow).

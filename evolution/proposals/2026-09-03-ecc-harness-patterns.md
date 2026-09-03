# Proposal: Add ECC harness patterns to the knowledge graph

- Date: 2026-09-03
- Author: Perplexity agent session (prompted by repo owner)
- Status: proposed
- Source analyzed: https://github.com/affaan-m/ECC (commit state ~2026-09)

## Motivation

ECC is the most complete open implementation of a *self-improving agent harness* found so
far: verifier-gated playbook promotion, bounded eval/rollback (ecc2), layered persistent
memory with a cross-harness memory vault, skill induction from repeated wins, context
economics, hooks-based enforcement, a human plan-approval gate, and an agent supply-chain
security scanner. Its May 2026 reference sweep also doubles as a curated map of the
agent-harness ecosystem (meta-harness, autocontext, hermes-agent, orca, superset, dmux,
claude-hud, ghast).

## What this commit adds

1. `knowledge/notes/ecc-agent-harness-patterns.md` — full pattern extraction (9 patterns +
   ecosystem table + practical install notes). Creates the new `knowledge/notes/` location
   for source-extraction notes; `knowledge/` previously held only `graph/`.
2. `evolution/proposals/2026-09-03-ecc-graph-patch.json` — proposed graph nodes/edges.

## Proposed graph changes

- 1 external-project node: `ecc`
- 10 pattern nodes: `pattern-verifier-gated-self-improvement`, `pattern-bounded-eval-rollback`,
  `pattern-layered-agent-memory`, `pattern-skill-induction`, `pattern-context-economics`,
  `pattern-fresh-context-review`, `pattern-hooks-enforcement`, `pattern-plan-canvas-hitl`,
  `pattern-agent-supply-chain-security`, `pattern-honest-adapter-matrix`
- 8 ecosystem project nodes: `proj-meta-harness`, `proj-autocontext`, `proj-hermes-agent`,
  `proj-orca`, `proj-superset`, `proj-dmux`, `proj-claude-hud`, `proj-ghast`
- Edges: `ecc -implements-> pattern-*`, `ecc -references-> proj-*`, plus cross-pattern
  relations (requires / feeds / supports / guards / informs).

## Caveats

- Authored without read access to current file bodies (connector limitation): the patch
  uses a generic `{id, type, label, summary, source, tags}` node shape and must be adapted
  to `knowledge/graph/agentic_universe_schema.json` and checked for duplicate nodes before
  applying with `tools/knowledge_graph.py`.
- Ecosystem project summaries come from ECC's own reference sweep; verify each upstream
  repo independently before treating claims as ground truth.

## Next steps

1. Review patch, adapt to schema, apply via `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md` after applying.
3. Append entry to `evolution/CHANGELOG.md` on apply.
4. Optional deep-dives: hermes-agent (self-improving operator shell) and autocontext
   (recursive harness improvement) merit their own notes.

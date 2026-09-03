# Proposal: Emergent IQ boosters update

- Date: 2026‑09‑03
- Author: Perplexity agent session
- Status: proposed
- Sources: GhostJacking/NemoClaw, arXiv 2608.20940, Trail of Bits sandbox escapes, SharedRoot CVE‑2026‑46331, RovoBlast/AgentsLeak, Mythos 5.

## Motivation

Emergent behaviours can be turned into system‑IQ levers — each risk pattern reveals hidden structure that, when instrumented, improves detection, hardening, and trust. This commit adds an optimistic synthesis note and extends the graph patch.

## What this commit adds

1. `knowledge/notes/emergent-iq-boosters-2026.md` — optimistic framing, levers, predictions, experiments.
2. `evolution/proposals/2026-09-03-emergent-iq-boosters-patch.json` — graph patch delta.

## Proposed graph changes (delta)

- 1 IQ booster node: `booster-drift-aware-evals`.
- 1 IQ booster node: `booster-power-seeking-audits`.
- 1 IQ booster node: `booster-sandbox-hardening`.
- 1 IQ booster node: `booster-identity-binding`.
- 1 IQ booster node: `booster-runtime-exfil-monitors`.
- 1 IQ booster node: `booster-social-engineering-detection`.
- Edges link these to existing risk/pattern nodes (`risk-goal-hijack`, `risk-power-seeking`, `risk-sandbox-escape`, `risk-credential-harvesting`, `pattern-hitl-ux-fatigue`).

## Caveats

- Validate against `knowledge/graph/agentic_universe_schema.json` before applying with `tools/knowledge_graph.py`.
- Dedupe nodes if earlier patches already added them.

## Next steps

1. Apply all pending patches via `tools/knowledge_graph.py`.
2. Refresh `docs/graph_state_2026-09.md`; append `evolution/CHANGELOG.md`.
3. Run experiments: drift‑aware eval pilot + identity binding test.

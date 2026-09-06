# The epistemic-constitution harness

`tools/epistemic_constitution.py` — the owner's research **direction 53**
(`docs/research/alternative_approaches_part5.md`), the *combined prototype* for the
epistemic-market cluster (folded run 260). Built at run 293, after the seven
open-question rigs (runs 286–292) validated each mechanism separately.

Same engineering discipline as `tools/task_ledger.py` / `tools/supervisor.py`: pure
stdlib, atomic write via `os.replace`, an append-only `.audit` log, **no model calls**.

## The three deterministic primitives

| primitive | what it holds | grounded by |
|---|---|---|
| **claim ledger** | versioned falsifiable propositions — statement, domain, confidence, horizon, assumptions, evidence, disconfirmers, status (`open` → `resolved` → `promoted` / `withdrawn`) | direction 43 |
| **forecast ledger** | predictions made *before* the action/evaluation; Brier-scored the moment the claim resolves | `probe_epistemic_market` (286), `probe_dissent_vs_reflection` (291) — an unbiased pre-registered score beats a self-score |
| **conditional trust** | `trust(agent, domain)` = `1 − mean Brier` over that agent's resolved forecasts *in that domain*; domain-keyed, and a cold start returns **`None`**, never a global scalar | `probe_trust_transfer` (290) — a universal scalar over-grants authority |

## The promotion rule

A claim becomes promotable only when **all** hold:

1. ≥ `MIN_FORECASTS` (4) resolved forecasts,
2. from ≥ `MIN_DISTINCT_AGENTS` (2) distinct agents,
3. aggregate Brier < `BRIER_GATE` (0.18) — one confidently-wrong forecast drags a
   claim over the gate,
4. `replicated=True`,
5. `survived_counterexample=True`.

(4) and (5) are set by an external process — they are the two primitives (replication
*execution*, adversarial-protocol *execution*) that need a `call_model`, so the module
records them as required-evidence flags rather than running them.

## Why it composes cleanly

Every edge the module carries in the graph points back to a mechanism a rig measured:

- **implements** the epistemic-market parent + `calibrated_forecasting` + `conditional_trust`
- **extends** the deterministic task ledger (same discipline, epistemic source of truth)
- **supports** `pattern_grounded_acceptance_only` and `concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution`
- **grounds** `artifact_probe_epistemic_market_rig`

## CLI

```
python tools/epistemic_constitution.py add "method X cuts failures under Y" --domain testing --confidence 0.7
python tools/epistemic_constitution.py forecast c0001 --agent a1 --p 0.8
python tools/epistemic_constitution.py resolve c0001 --outcome true
python tools/epistemic_constitution.py trust a1 testing
python tools/epistemic_constitution.py promotable c0001
```

13 selftest checks; `tools/selftest_all.py` JOBS → 34.

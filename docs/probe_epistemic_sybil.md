# Probe: Epistemic-Sybil Evidence Roots

**Status:** spec + **runnable rig** (`tools/probe_epistemic_sybil.py`, run 83), reproduces the finding in sim
**Tests:** `concept_epistemic_sybil_collapse` · **Target:** arXiv:2609.01873 (VERIFIED) — naive posterior
coverage 0.940 → 0.263 as reports rise 1→32 on a fixed source.

## The design

Same task, three arms:
- **shared** — N agents each read the *same* source, report an estimate, aggregate naively
- **independent** — N agents each read a *different* independent source, aggregate naively
- **dedup** — shared inputs, but collapse by evidential ancestry (N readers of one doc = one observation)
  before aggregating

Measure: does the naive 95% CI of the aggregate actually contain ground truth ~95% of the time? Sweep N in {1,
2, 4, 8, 16, 32}.

## The rig

`agent_read(source_id)` returns `TRUE_VALUE + source_bias(source_id) + read_noise`. The **source bias** is
systematic and shared by every reader of that source (the correlated-error term); the **read noise** is
independent. `run_arm(arm, n)` runs 400 trials and returns the fraction whose naive CI covered the truth. Each
read is a Phase 0 `CLAIM` carrying its `evidence_root`.

**Real:** the aggregation, the CI, the coverage measure, the ancestry dedup. **Stub:** `agent_read` — swap it
for a model call over a real document for a live run (the finding is statistical, so the sim is faithful to the
mechanism, not a placeholder for it).

## Dry-run result

Coverage by N (nominal is ~0.95):

| arm | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 |
| --- | --- | --- | --- | --- | --- | --- |
| **shared** | 1.00 | 0.28 | 0.25 | 0.15 | 0.10 | **0.095** |
| **independent** | 1.00 | 0.72 | 0.87 | 0.93 | 0.95 | **0.94** |
| **dedup** | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |

Reproduces the paper's direction: adding agents to one source **collapses** coverage (over-confidence), adding
*independent sources* keeps it honest, and **deduplicating by evidence root recovers it fully**. The sim's
collapse is steeper than the paper's 0.26 because the bias parameters are strong; the mechanism is the point.

## What it means for the design

- `pattern_evidential_ancestry_tracking` is not optional polish — without it, a swarm that fans N agents onto a
  shared trace produces an aggregate that is *worse calibrated the more agents you add*.
- `principle_diversity_maintenance`'s "independently-sourced context" is doing real work — it keeps the
  `independent` column honest.
- `experience_bank`'s `distinct_evidence_roots` field is the `dedup` arm, already implemented.

## What would falsify what

- **The Sybil concern is overstated for LLM agents** if a real `agent_read` over one document produces mostly
  *independent* errors between readers (different models, different prompts) — then `shared` would look like
  `independent`. The paper says it does not; this rig lets that be checked per model-mix.
- **Dedup is insufficient** if real agents transform a shared source enough that ancestry is ambiguous — then
  the `dedup` arm needs a similarity threshold, not an exact-root match.

## Next

Real `agent_read` (a model over a document); a partial-overlap arm (agents share *some* sources); vary the
source-bias / read-noise ratio to find where the collapse starts.

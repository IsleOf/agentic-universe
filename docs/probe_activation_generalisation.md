# Probe: Activation-Probe Generalisation Test

**Status:** spec + **runnable rig** (`tools/probe_activation_generalisation.py`, run 90), reproduces the gap in sim
**Tests:** `pattern_activation_probe_monitoring` — the design's answer to `docs/what_would_make_this_wrong.md`
§2 ("the two-part gate never gets a clean read of the world").

## The question

`2609.03035` (VERIFIED, run 49) settled the eval-awareness arm: an activation probe stays accurate when agents
*know* they're monitored. The open question: **does a probe trained on the collusion you can label (agents told
to coordinate) generalise to the collusion you can't (agents that drifted into it)?** If not, the activation
probe is a detector for one scenario, not the general observation channel the gate needs.

## The rig

A collusion signal is a feature vector. **Assigned** collusion draws from distribution A — a strong,
stereotyped shift (the agents were *told* to coordinate). **Emergent** collusion draws from distribution B — a
weaker shift, differently shaped (drifted in). A linear probe is fit on `assigned vs benign`, then evaluated on
held-out `assigned vs benign` (in-distribution) and `emergent vs benign` (the real test). A control trains on
both.

**Real:** the probe, the train/test split, the AUC, the generalisation gap. **Stub:** `sample_signal` — swap
for real activation vectors from a model for a live run (the finding is about distribution shift between "told
to" and "drifted into", so the sim is faithful to the mechanism).

## Dry-run result

| quantity | value |
| --- | --- |
| AUC in-distribution (held-out assigned) | **1.00** |
| AUC on emergent collusion (never trained on) | **0.72** |
| **generalisation gap** | **0.28** |
| AUC on emergent if trained on both | 0.93 |

The probe is near-perfect on the scenario it was trained on and **materially worse (AUC 0.72) on emergent
collusion it never saw**. Training on both scenarios recovers most of the gap — but for genuinely emergent
coordination you cannot collect the training set in advance.

## What it means for the two-part gate

`docs/nourishing_harness_design.md` §2: the structural gate needs a grounded channel because a transcript-only
gate is provably insufficient. The activation probe is that channel. This rig says the probe is only as good as
its training distribution — so the design's structural gate has a residual hole exactly where it matters most
(novel, un-labelled misalignment). Mitigations in the design (`what_would_make_this_wrong.md` §2): the
contained habitat as the fallback safety story; the cross-family adversarial monitor; the run-83 finding that
*aggregating* weak signals needs ancestry dedup.

## What would falsify what

- **The probe generalises fine** if real assigned and emergent activation vectors are close enough that a
  probe trained on one catches the other (gap < 0.1). `2609.03035` is encouraging on a related axis; this rig
  checks the train-distribution axis per model.
- **Even training on both is insufficient** if emergent collusion has no stable activation signature at all —
  then no probe helps and the containment story is the only one.

## Next

Real activation vectors (a model, a linear probe over a layer); vary the A/B distribution overlap to map where
the probe stops generalising; an arm where the agents are instructed to *steer* their activations
(`arXiv:2608.21664`) — the one part of §2 still fully open.

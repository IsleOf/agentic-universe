# Probe — when does multi-agent orchestration actually help?

**Date:** 2026-09-15 (autonomous run 221) · **Status:** built, selftest GREEN, dry-run verdict **CONFIRMS**
· **Tests:** `concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic` (run
218)

`tools/probe_orchestration_value.py`. The run-218 synthesis resolved the graph's accumulated multi-agent
tension (MAST "gains often minimal" · "Beyond the Strongest" discards ~8 points · OrchestraBench's
never-recovering latent modes · incident-response 100% vs 1.7% · epistemic Sybil collapse) into a
criterion:

> Multi-agent orchestration helps iff **(a)** subtasks are independently verifiable, **(b)** synthesis is
> a **deterministic** merge (not a vote / consensus), and **(c)** agents work from **disjoint** evidence
> slices.

This rig makes that a falsifiable experiment.

## The sim

A task is `K = 8` subtasks. Two architectures:

- **SINGLE** — one agent does all K sequentially, with a context-accumulation penalty that grows with the
  subtask index (`concept_geometric_reliability_decay`).
- **MULTI** — K fresh short agents, one per subtask, then a synthesis step.

Three binary knobs on MULTI:

| knob | ON | OFF |
| --- | --- | --- |
| **(a) verifiable** | each subtask output is checked and retried once | errors pass silently |
| **(b) deterministic** | synthesis is a computed merge (cannot fail) | a vote: `BASE_HERD = 0.50` + per-disagreement herding |
| **(c) disjoint** | subtask errors independent | a shared pool with a poisoned fact that verification **cannot** fix (the retry agent re-reads the same pool) |

## Dry-run result (4000 trials/combo)

```
SINGLE  ~0.46
a1b1c1  delta +0.52   ← strictly the best of the 8 combos
best combo missing any one condition:  +0.20  (a0b1c1 — deterministic + disjoint, no verification)
every vote-synthesis combo:  <= +0.04
every shared-pool combo:     <= +0.15
```

**Verdict: CONFIRMS at these params.** Multi-agent helps decisively only with all three conditions;
missing verification degrades it to a modest benefit; missing deterministic synthesis (a vote) or disjoint
evidence (a shared pool) erases it. The criterion is load-bearing, not a post-hoc relabelling.

## Stub / Phase 6

`_subtask_ok` and `_synthesis_ok` are the swap points for real agent runs. With a real multi-agent harness
this becomes a Phase 6 (swarm-layer) probe: measure (a)/(b)/(c) on an actual orchestration trace via the
Phase 0 substrate and predict whether the orchestration helped.

## Selftest

`python tools/probe_orchestration_value.py selftest` → GREEN (9 checks). `tools/selftest_all.py` includes
it → **BUILD SELFTEST: GREEN**.

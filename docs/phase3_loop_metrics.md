# Phase 3 on Real Traces — the Metrics Layer

**Date:** 2026-09-23 (autonomous run 68) · **Status:** metrics built, proposer wired to real signal, verification honestly blocked · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 3

`tools/improvement_loop.py` runs its proposer on a synthetic compaction task.
For the proposer to work on the *real* loop harness it needs real signal.
`tools/loop_metrics.py` computes it from the trace corpus (the adapter's replayed
history + live per-run summaries).

## The metrics (all computed, no judgement)

From the current 56-run corpus:

| metric | value | reading |
| --- | --- | --- |
| `runs` | 56 | harness-layer run STEPs |
| `verified_citation_fraction` | 0.40 | CLAIMs at full trust / all CLAIMs |
| `graph_write_rate` | 0.43 | runs that edited the graph (the rest: doc-only / hygiene / consistency) |
| `validation_pass_rate` | 1.00 | `graph_validate` results ok / total — the graph was never committed invalid |
| `distinct_evidence_roots` | 54 | distinct arXiv sources cited |
| `evidence_root_reuse` | 0.06 | roots cited by >1 run — `2609.02580`, `2609.03035`, `2609.04128` |

**Caveat on the replayed metrics.** The `evolution_log` is a one-line-per-run
summary — it names arXiv IDs and marks "VERIFIED" only in the recent, more
disciplined entries, and records graph deltas inconsistently. So
`verified_citation_fraction = 0.40` is a floor, not a measurement: early runs
that verified citations without writing "VERIFIED" in the log read as unverified
here. **Live recording (`loop_session.py`, run 67) fixes this prospectively** —
`s.cite(id, verified=True)` is unambiguous. The replayed corpus is a rough
prior; the real signal accrues from run 68 forward.

## The proposer, wired to real signal

`propose_loop_edit(metrics)` turns a below-threshold metric into a concrete
loop-harness edit + a falsifiable prediction:

- `verified_citation_fraction` below 0.60 → propose adding *"a run may fold at
  most ONE unverified citation"* to the `context/loop_policy` component; predict
  the fraction rises over the next 10 runs.
- `validation_pass_rate` below 1.00 → propose moving the validate step before any
  commit in `prompt/loop_procedure`; **this one is computably verifiable** —
  replay the corpus and count post-edit invalid commits.

## The honest gap

The first proposal's `verification` field says it plainly:

> BLOCKED — needs a frozen held-out set of research tasks to re-run the loop on;
> until then this is a grounded proposal, promoted manually.

Phase 3's verifier runs on a frozen held-out set. For a synthetic compaction task
that set is easy to write (`improvement_loop._frozen_holdout`). For the loop
harness it would be a frozen batch of research questions the loop can be
re-executed on, twice, with and without the edit. That does not exist, and
building it is a real piece of work (it needs graded, checkable research tasks).

So Phase 3 splits cleanly:
- **computable metric + computable verification** (validation_pass_rate) — the
  full loop can run.
- **computable metric + no held-out set** (verified_citation_fraction, and any
  quality metric) — the proposer produces a grounded proposal; a human promotes
  it; the *next 10 runs* are the deferred verification.

This is the same shape as `pattern_grounded_acceptance_only` under a missing
oracle: you still require a grounded risk measure to move, you just can't close
the loop automatically yet.

## Selftest

`python tools/loop_metrics.py selftest` → GREEN. `tools/selftest_all.py` runs
nine selftests → `BUILD SELFTEST: GREEN`.

## Next

- Build the frozen held-out research-task set — the thing that unblocks automatic
  Phase 3 on the loop harness. ~10 research questions with a computable "was this
  folded correctly" check.
- Or Phase 4 skeleton (skill induction from the bank's 56 workflow entries).

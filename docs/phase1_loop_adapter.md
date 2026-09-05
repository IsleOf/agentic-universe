# The Real-Harness Adapter — First Non-Synthetic Trace

**Date:** 2026-09-22 (autonomous run 66) · **Status:** built, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 1 (the adapter) + "Build order" step 1

Every phase built in runs 60–65 ran on synthetic data. This adapter points the
Phase 0 `Recorder` and Phase 1 `Registry` at a **real** harness: this project's
own autonomous research loop. `tools/loop_adapter.py`.

## Why the loop is the right first harness

It is a single-agent harness — no swarm — which is exactly the shape the plan
says to start with ("One agent, one sandbox"). Its components are real and
stable: the procedure prompt (`SKILL.md`), the context policy ("charter +
coverage + 3 recent sweeps first"), the topology (one agent), the tool set
(`research-fetch`, arXiv, WebFetch, `knowledge_graph.py`, git). And it has a
54-run history in the graph's `evolution_log` — a ready-made dataset.

## What it does

1. `seed_loop_harness(reg)` writes the loop's four components into a `Registry`,
   transcribed from the SKILL.md, so `manifest()` is a real fingerprint of the
   loop as it currently stands (`manifest_hash: a0a320e06a4204c4`).

2. `replay_history(graph, rec)` reconstructs a Phase 0 trace from the
   `evolution_log`: one `STEP` open/close per autonomous run, a `CLAIM` per
   arXiv citation (`evidence_root = arXiv:<id>` — VERIFIED ones at full trust,
   merely-referenced ones at low trust), an `ARTIFACT` per graph write and per
   commit, a `TOOL_CALL`/`TOOL_RESULT` per validation.

## The first real trace (full history)

`runtime/observations/loop_history_summary.json` (committed; the raw JSONL is
gitignored per operating rule 9):

| | |
| --- | --- |
| runs replayed | 54 |
| trace events | 329 (108 STEP, 58 CLAIM, 54 each TOOL_CALL/TOOL_RESULT/ARTIFACT) |
| distinct arXiv evidence roots | 54 |
| **sources cited by more than one run** | `2608.21156`, `2609.03035`, `2609.04128`, `2609.02580` (×2 each) |

That last row is `pattern_evidential_ancestry_tracking` working on real data.
Four papers were folded in by one run and then verified or enriched by a later
one. Here that is legitimate (verification, not redundant corroboration) — but
the adapter *surfaces* it, which is the point: a swarm doing the same thing
without ancestry tracking would be double-counting one source's authority
(`concept_epistemic_sybil_collapse`).

## Pipeline check on non-synthetic input

The selftest runs the real trace through the downstream tools:

- **validates** — 131 events (20-run sample) schema-clean.
- **`experience_bank.condense`** — produces one workflow entry per replayed run,
  each recording `distinct_evidence_roots` (the arXiv ids that run cited), not a
  claim count.
- **`topology_recover`** — recovers `researcher` as `planner` (it opens every
  STEP), which is the correct read of a single-agent loop.

`tools/selftest_all.py` now runs seven selftests → `BUILD SELFTEST: GREEN`.

## A schema fix this surfaced

`Recorder.emit` was writing `None`-valued optional fields (e.g.
`token_cost=None`), which then failed validation. Fixed — `emit` now drops
`None` values before writing. Caught only because the adapter exercises the
tool-result path without a token cost, which no synthetic selftest did.

## What this is not

- **A live feed.** It replays *recorded history* from the evolution log, not a
  running loop. Wiring `Recorder` calls into the loop's actual execution (so a
  future run emits events as it goes) is the next step — small, since the
  component surface and event kinds are already defined.
- **Rich.** The evolution log is a one-line-per-run summary, so the trace is
  coarse: one STEP per run, not per increment within a run. A live feed would be
  finer-grained.

## Next

1. Wire `Recorder` into the loop's live execution — one real run emitting events
   as it happens.
2. With real traces accumulating, run Phase 3's proposer against them (it
   currently runs on a synthetic compaction task).
3. Phase 4 (skill induction) — the workflow entries the bank now holds from the
   real history are the input.

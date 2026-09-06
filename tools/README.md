# tools/

The Agentic Universe toolchain. Pure Python stdlib, no network, no dependencies.
One predicate runs everything:

```
python tools/selftest_all.py        # 14 selftests -> BUILD SELFTEST: GREEN
```

## The knowledge graph

| tool | what it does |
| --- | --- |
| `knowledge_graph.py validate` | validate `knowledge/graph/agentic_universe_graph.json` (must print `VALID`) |
| `knowledge_graph.py summarize` | node/edge/family/status counts |
| `knowledge_graph.py check-proposal <f>` | validate an `evolution/proposals/*.json` patch |

## The self-improving-harness pipeline (`docs/self_improving_harness_plan.md`)

Built runs 60–76. Data flows left to right; each tool has a `selftest` subcommand.

```
                     ┌─────────────────── Phase 0: measurement ───────────────────┐
  a harness run  ──▶  trace_substrate.Recorder  ──▶  runtime/traces/*.jsonl (gitignored)
                          │  loop_session.LoopSession wraps a real loop run
                          ▼
                     topology_recover  ──▶  interaction graph + agent roles   [GATE: 1.00 on the control]
                          │
     ┌────────────────────┼───────────────────────────────────────────────┐
     ▼                    ▼                                                ▼
  Phase 1             Phase 2                                          Phase 3
  harness_registry    experience_bank                                 improvement_loop
  (versioned          (workflow + step stores,                        + loop_metrics    (real signal)
   components,         ancestry dedup, stale-check)                    + loop_proposer   (context, 4 dims)
   exact revert)           │                                          + holdout_tasks   (17 frozen tasks)
     │                     ▼                                          + holdout_verifier2 (2nd scorer)
     │                Phase 4: skill_induction                              │
     │                (induce + retire, 20% withheld)                       ▼
     └──────────────────────────────────────────────────▶  verify_loop_edit: grounded risk,
                                                            strict decrease, no regression,
                                                            no verifier disagreement -> promote/revert
  Phase 5: exec_guard  ──▶  .git/hooks/pre-commit  (blocks a bad commit in the execution path)
```

### Phase 0 — trace substrate

| tool | subcommands | notes |
| --- | --- | --- |
| `trace_substrate.py` | `validate <f>`, `selftest` | event schema `phase0.1`; `Recorder`; Five-W enforced on MESSAGE; `seq`/`layer`/`language` on every event; secrets scrubbed before write |
| `topology_recover.py` | `recover <f>`, `selftest [--noisy]` | interaction graph + deterministic role recovery; the plan's Phase 0 gate |
| `loop_session.py` | `selftest` (else `import LoopSession`) | live per-run recording; writes `runtime/observations/loop_runs/run-<N>.json` |

### Phase 1 — harness as a versioned artifact

| tool | subcommands | notes |
| --- | --- | --- |
| `harness_registry.py` | `list`, `manifest`, `history <k> <n>`, `diff <k> <n>`, `revert <k> <n>`, `selftest` | components under `runtime/harness/<kind>/<name>`; every version's body retained → exact revert |
| `loop_adapter.py` | `replay [--limit N]`, `selftest` | the autonomous loop AS a harness; `replay` regenerates `runtime/traces/loop-history.jsonl` from the graph's `evolution_log` |
| `harness_demo.py` | (default = selftest), `run` | end-to-end integration test |

### Phase 2 — experience bank

| tool | subcommands | notes |
| --- | --- | --- |
| `experience_bank.py` | `condense <trace>`, `stats`, `stale <manifest>`, `selftest` | `workflow` + `step` collections kept apart; entry carries `source_manifest`, raw `source_events`, `distinct_evidence_roots` |

### Phase 3 — the middle loop

| tool | subcommands | notes |
| --- | --- | --- |
| `improvement_loop.py` | `selftest` | propose → verify (fresh context, frozen holdout, PROCTOR canary) → grounded strict-decrease acceptance → promote/revert; `verify_loop_edit()` for loop-harness edits |
| `loop_metrics.py` | `report`, `selftest` | metrics over the trace corpus; `propose_loop_edit()` |
| `loop_proposer.py` | `context`, `propose`, `prompt`, `selftest` | full-context proposer, 4 dimensions; `PROPOSER_PROMPT` is the model-proposer seam |
| `holdout_tasks.py` | `list`, `baseline`, `score <id> <f>`, `selftest` | 17 frozen research/design questions with computable checks; baseline 17/17 = 1.00 |
| `holdout_verifier2.py` | `baseline`, `selftest` | second independent scorer (key-fact overlap); disagreement with `holdout_tasks` = reject |

### Phase 4 — skill induction

| tool | subcommands | notes |
| --- | --- | --- |
| `skill_induction.py` | `induce`, `selftest` | task-class → candidate skill (`status: candidate`, no auto-promote); `retire()` deprecates disused classes (kept, not deleted); `withheld_runs()` marks 20% permanently skill-withheld |

### Phase 5 — execution-layer enforcement

| tool | subcommands | notes |
| --- | --- | --- |
| `exec_guard.py` | `check [--hook]`, `install`, `selftest` | pre-commit hook; blocks committing to `main`, a staged raw `*.jsonl`, a secret leak shape, an invalid graph, an orphan node |

## Fresh-clone setup

```
python tools/exec_guard.py install     # re-install the pre-commit hook (.git/hooks is not versioned)
python tools/selftest_all.py           # should print BUILD SELFTEST: GREEN
python tools/loop_adapter.py replay    # regenerate the history trace
```

## What is NOT built

- **A model proposer / a model verifier.** `PROPOSER_PROMPT` and the two computed
  verifiers are the seams; the model call is not wired.
- **Automatic Phase 3 on the loop harness.** The held-out set exists; re-running
  the loop on it after a promotion is a human step.
- **The swarm layer (Phase 6).** Everything is single-agent (the loop) or
  synthetic. Needs a real multi-agent harness, which this repo does not contain.

Per-phase detail: `docs/phase0_*.md` … `docs/phase5_*.md`.

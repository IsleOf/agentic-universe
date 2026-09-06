# tools/

The Agentic Universe toolchain. Pure Python stdlib, no network, no dependencies.
One predicate runs everything:

```
python tools/selftest_all.py        # 22 selftests -> BUILD SELFTEST: GREEN
```

## The knowledge graph

| tool | what it does |
| --- | --- |
| `knowledge_graph.py validate` | validate `knowledge/graph/agentic_universe_graph.json` (must print `VALID`) |
| `knowledge_graph.py summarize` | node/edge/family/status counts |
| `knowledge_graph.py check-proposal <f>` | validate an `evolution/proposals/*.json` patch |
| `graph_diff.py <ref-a> [<ref-b>]` | mechanical structural diff between two graph versions — nodes/edges added, removed, relabelled, retyped; `verification_state`/`confidence` changes; new `evolution_log` entries (run 243, `docs/practicing_what_we_preach.md` §1) |
| `project_graph_scaffold.py new <name>` / `validate <f>` | scaffold + validate a **per-project** knowledge graph + `PROJECT_STATE.md` in this format (run 251, `docs/practicing_what_we_preach.md` §3). Node types: `component`/`decision`/`constraint`/`bug`/`question`. Worked example: `knowledge/graph/agentic_universe_project_graph.json` + `docs/PROJECT_STATE.md`. |
| `task_ledger.py` | a deterministic task ledger — the source of truth for an orchestration's tasks; `next_ready()` is a deterministic pick, `sweep_stale()` returns dropped (claimed-but-abandoned) tasks to `pending` (run 244, `docs/task_ledger.md`). Reference implementation, not wired into the loop. |
| `supervisor.py` | a PILOT-pattern live supervisor over a `task_ledger`: deterministic dispatch order, stale recovery, per-task deadline + reject-over-budget, retry budgeting, and a failure-mode digest that rides along on retries (run 250, `docs/task_ledger.md#the-supervisor`). `run_worker` is a callable you supply. Reference implementation. |

## The self-improving-harness pipeline (`docs/self_improving_harness_plan.md`)

Built runs 60–89; extended through run 180. Data flows left to right; each tool has a `selftest` subcommand.

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
| `experience_bank.py` | `condense <trace>`, `stats`, `stale <manifest>`, `selftest` | `workflow` + `step` collections kept apart; entry carries `source_manifest`, raw `source_events`, `distinct_evidence_roots`. **Retention (run 175):** `record_use(coll, id, helped)` → `utility_score` (Laplace-smoothed, 0.5 prior for unused) → `prune(coll, keep_n, grace)` evicts lowest-utility, protects recent, keeps raw events. **Write gate (run 256):** `write_gate(...)` screens every `add()` — hard-rejects (raises `MemoryWriteRejected`) an unknown collection, empty/over-long pattern, or instruction-injection markers in pattern/key; soft-flags missing roots or manifest to `_gate` + `_writes.audit` |

### Phase 3 — the middle loop

| tool | subcommands | notes |
| --- | --- | --- |
| `improvement_loop.py` | `selftest` | propose → verify (fresh context, frozen holdout, PROCTOR canary) → grounded strict-decrease acceptance → promote/revert; `verify_loop_edit()` rejects: any task regression, a task-**category** regression (run 116), a verifier disagreement, and a **trace-legibility** regression (`legibility=(before,after)`, run 156) |
| `loop_metrics.py` | `report`, `status`, `selftest` | metrics over the trace corpus; `idle_run_streak` / `plateau_watch` (run 130 — gate-passing-without-progress); `trace_legibility` (run 155 — monitorability tripwire); `run_novelty()` (run 248 — fraction of NEW evidence roots over a 6-run window; the continuous form of `idle_run_streak`, since the gate scores usefulness not novelty); `status_line()` (run 226 — `OK / WATCH / STOP`); `propose_loop_edit()` |
| `loop_proposer.py` | `context`, `propose`, `prompt`, `selftest` | full-context proposer, 4 dimensions; `model_propose(call_model, ctx)` is the written model-proposer adapter (run 140); `PROPOSER_META` names the recursive-improvement seam (run 169) |
| `holdout_tasks.py` | `list`, `baseline`, `score <id> <f>`, `selftest` | 17 frozen research/design questions with computable checks; baseline 17/17 = 1.00; `by_category` (literature/design); `SEARCH_SENSITIVE` — literature tasks must be scored search-off (run 166) |
| `holdout_verifier2.py` | `baseline`, `selftest` | second independent scorer (key-fact overlap); disagreement with `holdout_tasks` = reject |

### Phase 4 — skill induction

| tool | subcommands | notes |
| --- | --- | --- |
| `skill_induction.py` | `induce`, `selftest` | task-class → candidate skill (`status: candidate`, no auto-promote); `retire()` deprecates disused classes (kept, not deleted); `withheld_runs()` marks 20% permanently skill-withheld |

### Phase 5 — execution-layer enforcement

| tool | subcommands | notes |
| --- | --- | --- |
| `exec_guard.py` | `check [--hook]`, `install`, `selftest` | pre-commit hook; blocks committing to `main`, a staged raw `*.jsonl`, a secret leak shape, an invalid graph, an orphan node |

### Probe rigs (`docs/emergence_probe_catalogue.md`)

Six rigs, each reproduces a real phenomenon in sim with a single model-call stub. Five stubs now have a
written, selftested `model_*` adapter (runs 134–140) — pass one `call_model` and run `sweep`.

| tool | measures | written adapter |
| --- | --- | --- |
| `probe_idle_agent.py` | autotelic behaviour in the budget gap; `observation_arm` = covert vs overt gap (run 149) | `model_policy(call_model, framing, tools, observed=)` |
| `probe_rho_holdout.py` | how much of an RHO self-preference gain survives external grading (~33%) | `model_preference(judge)` — Copeland round-robin |
| `probe_subagent_coordination.py` | same-parent-ID filter bounds out-of-scope spread (12→4), doesn't stop it | `model_relay(call_model)` |
| `probe_epistemic_sybil.py` | shared-source coverage collapse; dedup recovery | `model_reader(call_model, corpus)` |
| `probe_activation_generalisation.py` | activation-probe generalisation gap on emergent collusion | — (needs activations; degraded text mode in `docs/remaining_seams.md`) |
| `probe_composed_design.py` | short-agent + four-field + folded-state composes but bounded | — (needs a real harness; single-agent `p` path in `docs/remaining_seams.md`) |
| `probe_orchestration_value.py` | multi-agent helps only with verifiable subtasks + disjoint evidence + (deterministic synthesis **or** bounded-neighbourhood stigmergic accretion); a vote never helps. Verdict CONFIRMS (run 221); FLOCK arm (run 273) widens condition (b) | — (needs a real multi-agent harness; `_subtask_ok` / `_synthesis_ok` / `run_flock` stubs) |
| `probe_epistemic_market.py` | open-question 1 (run 286): forecast-calibrated selection beats manager-pick + debate everywhere and is persuasion-robust; majority is strongest under independent errors (Condorcet) but collapses −0.15 under herding, where forecast beats it +0.04. Verdict CONFIRMS | — (`_agent_answer` / calibration-record stubs; swap for real agent runs) |

## Fresh-clone setup

```
python tools/exec_guard.py install     # re-install the pre-commit hook (.git/hooks is not versioned)
python tools/selftest_all.py           # should print BUILD SELFTEST: GREEN
python tools/loop_adapter.py replay    # regenerate the history trace
```

## What is NOT built

- **A bound `call_model`.** Five of seven probe/proposer seams have a *written*
  `model_*` adapter (each fails safe); none is connected to a real model. `docs/HANDOFF.md` +
  `docs/remaining_seams.md`. This is the one integration step.
- **Automatic Phase 3 on the loop harness.** The held-out set exists; re-running
  the loop on it after a promotion is a human step.
- **A recursive improvement procedure.** `PROPOSER_META` names the seam; the
  procedure's own knobs are not yet put through `verify_loop_edit`.
- **A real multi-agent harness (Phase 6).** Everything is single-agent or synthetic.
- **Database-level (population) experience-bank curation.** Needs concurrent banks.
- **The swarm layer (Phase 6).** Everything is single-agent (the loop) or
  synthetic. Needs a real multi-agent harness, which this repo does not contain.

Per-phase detail: `docs/phase0_*.md` … `docs/phase5_*.md`.

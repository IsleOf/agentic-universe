# Agentic Universe

A versioned knowledge graph and research programme on **emergent agent behaviour**
and **self-improving agent systems**.

The question the project is organised around: *what makes agents more capable over
time, and what does their environment have to provide for that to happen?*

**182 nodes · 553 edges · 9 approach families · 25% `challenges` edges** — current
counts in [`docs/graph_state_2026-09.md`](docs/graph_state_2026-09.md).

## What this is

Two things now:

1. **A curated model** of how agentic systems behave — what emerges at the model,
   harness, and swarm levels; how a harness can improve itself without drifting;
   what conditions a population of agents needs to keep getting better rather than
   collapsing into a monoculture. This is the graph and the design docs.

2. **A working toolchain** (`tools/`, pure stdlib) that implements the
   self-improving-harness plan as tested code — Phases 0–5, 14 selftests under one
   predicate. Built on the project's own research loop as the first real harness.
   Map: [`tools/README.md`](tools/README.md).

Everything is versioned and reviewable. Runtime traces and observations can
*propose* graph changes; they cannot silently rewrite stable knowledge.

## Start here

| Document | What it covers |
| --- | --- |
| [`docs/graph_state_2026-09.md`](docs/graph_state_2026-09.md) | Orientation: current counts, the central thesis, evidence for/against, reading order |
| [`docs/habitat_charter.md`](docs/habitat_charter.md) | The operative research brief, the habitat model, open questions |
| [`docs/nourishing_harness_design.md`](docs/nourishing_harness_design.md) | The per-agent execution environment: two-part gate, four layers, habitat mechanisms |
| [`docs/what_would_make_this_wrong.md`](docs/what_would_make_this_wrong.md) | The adversarial counterweight — read it second |
| [`docs/self_improving_harness_plan.md`](docs/self_improving_harness_plan.md) | Build plan: three loops, six phases — **Phases 0–5 now built** |
| [`tools/README.md`](tools/README.md) | The 14-tool pipeline as one map |
| [`docs/emergence_probe_catalogue.md`](docs/emergence_probe_catalogue.md) | One cheap experiment per emergence hypothesis |
| [`docs/source_register.md`](docs/source_register.md) | **Full attribution** — every external idea, with verification status |
| [`architecture/foundations.md`](architecture/foundations.md) | Core loop model and engineering rules |

## Posture

**Emergence-first** ([`docs/emergence_first_posture.md`](docs/emergence_first_posture.md)).
Ideas enter the graph on interest, not evidence; unverified material stays at low
confidence, `speculative` / `to_test`. The programme is theoretical and optimistic
until the model is good enough to reassess — then it reassesses.

## Approach families

- **`emergent_behaviors`** (53) — what agents do given room, at three separable
  layers: inside the model, in the single-agent harness, across a swarm. Deception,
  norms, coordination, self-preservation, whistleblowing, interaction-language effects
- **`self_improving_harness`** (41) — the control layer as an evolvable artifact;
  verifier spec, recoverability, grounded acceptance, geometric decay, the built pipeline
- **`agent_habitat`** (19) — the environment agents develop in: slack, cheap death,
  graded challenge, inheritance, diversity maintenance, retraction capacity
- **`graph_engineering`** (18) — organising a system through explicit task / agent /
  runtime-state graphs; market vs graph orchestration; topology as an error-propagation parameter
- **`nourishing_harness`** (15) — the per-agent execution environment paired with
  orchestration; four layers, a two-part gate
- **`control_plane_governance`** / **`orchestration_first`** / **`marketplace_workflow`** /
  **`agent_os_desktop`** — earlier or dormant families, retained

## Conventions

**Tensions are recorded, not resolved.** ~25% of edges are `challenges` edges. When a
capability and its failure mode are the same mechanism — role specialisation gives
division of labour *and* single points of failure; shared memory gives culture *and*
entrenchment — the graph holds both rather than picking early.

**Nodes assert mechanisms, not categories.** A node that names a phenomenon without
saying how it works is not carrying its weight.

**A source is a claim, not a finding.** Papers, model output, and prior-session
conclusions all enter as proposals. Nothing promotes itself, including documents
written by agents working on this repo.

**Citations are verified three ways** — exists, summary matches, headline number is
causally isolated. A `VERIFIED` tag in `derived_from` means the arXiv page was fetched
and checked. Two citation-drift corrections are on record in the source register.

## Layout

```
knowledge/graph/            canonical graph + schema
knowledge/notes/            research syntheses (leads, not sources)
docs/                       plans, charters, catalogues, per-phase build docs, attribution
docs/auto_sweep_*.md        one log per autonomous research/build run
evolution/proposals/        change requests as validated JSON patches
architecture/               foundational model and rules
runtime/traces/             Phase 0 event traces (raw *.jsonl gitignored)
runtime/observations/       per-run summaries, derived metrics
tools/                      the toolchain — see tools/README.md
```

## Working with the repo

```bash
python tools/knowledge_graph.py validate    # structure, unique ids, edge targets -> VALID
python tools/selftest_all.py                # 14 pipeline selftests -> BUILD SELFTEST: GREEN
python tools/exec_guard.py install          # (re)install the pre-commit guard on a fresh clone
```

The pre-commit hook (`tools/exec_guard.py`) blocks a commit that stages an invalid
graph, an orphan node, a raw trace, a secret, or targets `main`.

Known limitation: `check-proposal` reports a patch clean when it contains no
`add_nodes` key, so a malformed patch can pass silently.

## Status

The **graph** is a research model in progress: most nodes are `to_test` or
`speculative`; 73 are `partially_validated` (at least one verified citation); a
handful `inconclusive` and one `deprecated` — the retraction discipline
(`principle_retraction_capacity`) is now exercised on the graph itself.

The **toolchain** implements Phases 0–5 of the harness plan as tested code, running
on the project's own research loop. What is not built: a model proposer/verifier
(the seams exist), automatic Phase 3 on the loop harness (one human step), and the
swarm layer (Phase 6 — needs a real multi-agent harness this repo does not contain).

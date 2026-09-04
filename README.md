# Agentic Universe

A versioned knowledge graph and research programme on **emergent agent behaviour** and **self-improving agent systems**.

The question the project is organised around: *what makes agents more capable over time, and what does their environment have to provide for that to happen?*

**85 nodes · 174 edges · 5 approach families**

## What this is

A research repository, not a framework. The deliverable is a curated model of how agentic systems behave — what emerges at the model, harness, and swarm levels; how a harness can improve itself without drifting; and what conditions a population of agents needs to keep getting better rather than collapsing into a monoculture.

Everything is versioned and reviewable. Runtime traces and observations can *propose* graph changes; they cannot silently rewrite stable knowledge.

## Start here

| Document | What it covers |
| --- | --- |
| [`docs/habitat_charter.md`](docs/habitat_charter.md) | The operative research brief, the habitat model, and open questions |
| [`docs/self_improving_harness_plan.md`](docs/self_improving_harness_plan.md) | Build plan: three loops, seven phases, toward a self-improving agentic OS |
| [`docs/emergence_probe_catalogue.md`](docs/emergence_probe_catalogue.md) | One cheap experiment per emergence hypothesis, with build order |
| [`docs/graph_engineering_convergence.md`](docs/graph_engineering_convergence.md) | Where independent groups converged on this architecture |
| [`docs/source_register.md`](docs/source_register.md) | **Full attribution** — every external idea, with verification status |
| [`architecture/foundations.md`](architecture/foundations.md) | Core loop model and engineering rules |

## Approach families

- **`emergent_behaviors`** — what agents do when given room, at three separable layers: inside the model, in the single-agent harness, and across a swarm
- **`self_improving_harness`** — the control layer around the model as an evolvable artifact, edited under a verifier gate
- **`agent_habitat`** — the environment agents develop in: slack, cheap death, graded challenge, inheritance, diversity maintenance, retraction capacity
- **`graph_engineering`** — organising a system through explicit task, agent, and runtime-state graphs
- **`control_plane_governance`** / **`orchestration_first`** — earlier families, retained

## Conventions

**Tensions are recorded, not resolved.** 37 of 174 edges are `challenges` edges. When a capability and its failure mode are the same mechanism — role specialisation gives division of labour *and* single points of failure; shared memory gives culture *and* entrenchment — the graph holds both rather than picking early.

**Nodes assert mechanisms, not categories.** A node that names a phenomenon without saying how it works is not carrying its weight.

**A source is a claim, not a finding.** Papers, model output, and prior-session conclusions all enter as proposals. Nothing promotes itself, including documents written by agents working on this repo.

**Citations are verified before use.** Existence and summary are checked separately — one aggregated research note in this repo cites a real paper while restating its headline numbers incorrectly. That correction is on the record in the source register.

## Layout

```
knowledge/graph/     canonical graph + schema
knowledge/notes/     research syntheses (leads, not sources)
docs/                plans, charters, catalogues, attribution
evolution/proposals/ change requests as validated JSON patches
evolution/decision-ledger/  accepted and rejected decisions
architecture/        foundational model and rules
runtime/             traces, observations, evaluations (scaffolding)
conversations/       source conversation archives
tools/               graph validation
```

## Working with the graph

```bash
python tools/knowledge_graph.py validate            # structure, unique ids, edge targets
python tools/knowledge_graph.py summary             # counts by family and status
python tools/knowledge_graph.py check-proposal <f>  # validate a patch
```

Known limitation: `check-proposal` reports a patch clean when it contains no `add_nodes` key, so a malformed patch can pass silently. Fix pending.

## Attribution

This project builds on published work by many groups. [`docs/source_register.md`](docs/source_register.md) lists every source behind every node, separating what has been independently verified from what has only been cited, and marks which ideas are this project's own synthesis rather than borrowed.

## Status

Research in progress. Most nodes are `speculative` or `to_test`; confidence values are prior estimates, not measurements. The graph currently records no refutations — which is itself a finding about the repository, and one `principle_retraction_capacity` says to fix.

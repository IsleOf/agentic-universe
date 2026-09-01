# Research Operating Plan

**Status:** draft for owner review · **Date:** 2026-09-01 · **Author:** Claude (Cowork session, claude-opus-5)

## The constraint this plan is built around

The bottleneck on this project is not access to information. It is verification capacity.

Measured at commit `ef4ed3e`: 19 nodes, 11 marked `stable_theory`, 11 marked `partially_validated`, 1 carrying `derived_from`, **0 carrying `evidence_links`**. Meanwhile `docs/graph_state_2026-09.md` states the standard: *"Promote a node only after evidence is reproducible, attributable, and relevant to the stated domain."*

Eleven nodes are marked as partially validated with no recorded account of what validated them. That is the failure mode this plan exists to stop — not because the reasoning behind those nodes is bad, but because a graph that cannot distinguish a reasoned position from a tested finding loses the property that makes it worth maintaining.

**Adding a literature pipeline to this graph, unchanged, accelerates the problem.** More plausible-sounding nodes, same zero evidence. So ingest is gated by verification throughput, not by what is available to read.

## The one rule

> **No node enters the graph unless it names the experiment that would refute it.**

Everything below is machinery for that rule. If the rest of this document is discarded, keep this.

## Four layers

| Layer | Directory | Holds | Promotion barrier |
| --- | --- | --- | --- |
| Sources | `sources/` | Papers, articles, repos — as claims with authors | Must name a falsifier to be filed |
| Proposals | `evolution/proposals/` | Reviewable change requests | Must pass `check-proposal` |
| Runtime evidence | `runtime/` | Traces, observations, evaluations | Must be replayable and scrubbed |
| Canonical graph | `knowledge/graph/` | Curated model | Must link a `runtime/` artifact to raise status |

Nothing skips a layer. A paper cannot become a node; it proposes one. A run cannot promote itself; it produces evidence a proposal cites. This is the same barrier in three places, deliberately.

## Literature sweep

Weekly, capped. The cap is the point — an uncapped sweep produces a reading backlog that silently becomes a filing backlog.

- **Venues and APIs:** see `sources/README.md`.
- **Cap:** file at most 10 source records per sweep. If more look relevant, the surplus is a signal about the query, not a reason to raise the cap.
- **Queries anchored to open graph questions**, not to the field generally. Current anchors: supervisor steering and mid-run intervention; emergent role specialization; multi-agent communication topology; single-agent-plus-tools baselines; cost-controlled multi-agent comparisons.
- **Reject on sight:** papers with no baseline, no cost accounting, or benchmark-only results with no ablation. Noting *why* a paper was rejected is cheaper than reading it twice.

Automatable as a scheduled task. The sweep files candidates; a human or agent decides what graduates to a proposal.

## Test implementation

This is the part that turns curation into research, and it is currently missing entirely. Build in this order — each step is a prerequisite for the next, not a preference.

### 1. Five-W instrumented runner

Every inter-agent message through one logging chokepoint: sender, receiver, content class, timestamp, declared purpose (captured at the sending call site, never inferred afterward), channel.

Why first: three of the five open proposals cannot produce interpretable traces without it, and `emergent_hidden_coordination_channels` is untestable *in principle* without it — a hidden channel is defined by its absence from the log, detectable only as outcome dependency with no message path.

**Gate before trusting it:** the topology analysis must recover roles in a control condition where roles were explicitly assigned. If it cannot find roles that are known to be there, it cannot be trusted to find emergent ones.

### 2. A task family with executable checks

The hard constraint, and the one that decides whether any of this is real. `architecture/foundations.md` already says: write the GREEN/RED predicate before building the loop. That applies to the harness itself.

Candidates: a SWE-bench-lite subset; property-based synthetic tasks; or this repo's own tooling as the substrate. Requirement is the same either way — pass/fail must be computed, never judged by a model.

### 3. The single-agent baseline arm

A capable single agent with good deterministic tools. Build it **before** any multi-agent arm.

Two failure modes it prevents: without it, every later result is uninterpretable; and a *weak* version of it manufactures support for `approach_orchestration_first`, which already sits at 0.75 confidence on no evidence. The baseline must be genuinely well-tooled, and it is worth more effort than feels justified at the time.

### 4. Cost instrumentation, from day one

Tokens and wall-clock per arm, with orchestration overhead attributed separately. Comparisons run at **equal total budget**, not equal agent count. Most reported multi-agent advantages narrow or vanish under this control, and you want to discover that about your own results before the graph records them as findings.

## Cadence

- **Weekly:** literature sweep (capped, automatable).
- **One experiment at a time**, run to a verdict before the next starts. Parallel half-finished experiments are how a project accumulates suggestive results and no conclusions.
- **Every status change** gets a `evolution/decision-ledger/` entry naming the evidence artifact — or stating explicitly that the change was made on judgment.
- **Negative results are filed**, with the same care as positive ones. A refuted node is a better outcome than an untested one; `refuted` and `inconclusive` already exist in the schema and should get used.

## Open owner decisions

Carried from the 2026-09-01 proposal batch, unresolved:

1. **The 11 `stable_theory` nodes.** Demote to `to_test`; or add `evidence_basis: authorial_judgment` to the schema (recommended — honest, no demotion, machine-readable); or retroactively attach `derived_from` to the `conversations/raw/` sources. Option 3 is worth doing regardless.
2. **Are subnodes addressable?** Seven control-plane subnode IDs cannot be targeted by edges because the validator collects top-level IDs only. Either fix the validator, or strip the IDs so nothing appears addressable when it is not.
3. **Do tooling changes go through the proposal process?** Code is not a graph patch, and `check-proposal` cannot validate it.

## What this plan does not claim

It is untested. It is a process proposal written by an agent after reading the repository, and by its own rule it does not get to promote itself. The right status for it is `awaiting_review`, and the honest measure of whether it worked is whether the ratio of evidence-linked nodes rises over the next quarter.

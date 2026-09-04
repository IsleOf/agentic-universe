# Graph Engineering and the Convergence Finding

**Date:** 2026-09-05 · **Graph:** 72 nodes / 140 edges · **Sources:** three owner-supplied videos, read via their primary sources

---

## Method note

All three videos are paper-summary videos that name their source exactly in the description. YouTube's transcript panel would not load, and the audio is auto-dubbed — so the primary sources were read directly instead. That is the better route regardless: earlier in this project a research note was found restating a paper's headline numbers wrongly, and a machine-transcribed dub of a spoken summary of a paper is three lossy steps from the claim.

| Video | Primary source | Status |
| --- | --- | --- |
| Agentic Skills + Knowledge Graphs = AI's Scientific Operating System | `arXiv:2608.29612` — ASKS (Ran, Zhang, Wu, Yang, Li) | verified |
| Can Graph Engineering Create System Intelligence? | `arXiv:2608.21156` — Graph Engineering in the Era of LLM Agents (36 authors) | verified |
| Your LLM Has a New Boss: The Adaptive Harness | openJiuwen / jiuwenswarm, Huawei Technologies | verified, real repo |

---

## 1. The finding: independent convergence

The most useful thing in this batch is not a new idea. It is that a 36-author survey and a shipped Huawei product independently arrive at architecture this project already holds.

**On the OS layering.** `concept_agentic_os` splits runtime / harness / knowledge and argues only the harness should mutate at speed. The survey proposes three system-level graph structures — **task organisation**, **agent coordination**, **runtime state** — reached from an entirely different starting point, and lands on the same separation of executable structure from durable state.

**On the founding distinction.** `concept_loop_vs_graph` has been in this graph since the seed commit: loops are transient and execute bounded work, graphs are persistent and model durable structure. The survey's paradigm ladder ends **loop engineering → graph engineering**, as successive paradigms with different units of design. Same claim, opposite direction of travel.

**On the self-improving harness.** `approach_self_improving_harness` now has a third independent implementation. After AHE (`2604.25850`) and MemoHarness (`2607.14159`), Huawei's openJiuwen ships **Auto Harness** — end-to-end harness optimisation driven by evaluation with no weight training — plus **Skill Self-Evolution**, which rewrites skill definitions when it detects error signals or user dissatisfaction. First of the three shipped as a product rather than a benchmark result, which is both its value and its caveat: independent evidence the loop is buildable, and no numbers attached.

Convergence is weak evidence — three groups can share a blind spot, and none of this is a controlled result. But it does move the architecture from *one agent's reading of a repo* to *a position several independent groups reached*, which is worth more than any single citation in the set.

## 2. The paradigm ladder

`concept_engineering_paradigm_ladder` is the genuinely new orientation device. Five paradigms, distinguished by the unit they optimise:

| Paradigm | Unit optimised |
| --- | --- |
| Prompt / Context Engineering | a single model call |
| Harness Engineering | one agent's tools, memory, and skills across calls |
| Loop Engineering | one agent's iterative decision cycle |
| Graph Engineering | the structure of a multi-agent system |

Its use is negative as much as positive: it says which rung a technique **cannot** reach. Harness engineering optimises one agent's resources, so no amount of it addresses a system-structure problem. Worth knowing before spending a quarter on the wrong rung.

**Terminology collision worth keeping straight.** This repo's "graph" is a *knowledge* graph — durable concepts, provenance, relationships. The survey's graphs are *executable* — rewritten during a run, holding task dependencies and live state. Same word, different objects, and both belong in the system.

## 3. The sharp disagreement

Recorded as `concept_system_intelligence` **challenges** `emergent_model_native_orchestration`. Two opposed predictions:

- **System intelligence** — a single agent has an organisational ceiling independent of raw capability. Heterogeneous expertise, interdependent subtasks, parallelism, independent verification, and persistent state exceed one context and one loop. Structure must be externalised into graphs.
- **Model-native orchestration** — planning, tool selection, and self-correction keep migrating *into* the reasoning chain. The external scaffold thins out as models absorb it.

They cannot both be the trend. This is the single most consequential open question for the project, because the answer decides how much of the architecture survives — and it is empirically decidable. If the ceiling is real, a stronger single model should not close the gap on tasks with genuine dependency structure. That is a runnable experiment, and it belongs in the probe catalogue.

## 4. The warning aimed at this repo

`emergent_additive_growth_bias`. ASKS's own case study — 56 chronologically ordered papers from one research programme, measured on branch survival, cross-paper support, lineage, coverage, and churn — found **stable hub organisation with predominantly additive canonical-node growth**. The system accumulated and seldom retracted.

That is presented as a good result. Read as a dynamic, it is the failure mode: **a graph that only grows cannot refute.** Monotone growth is what an unfalsifiable knowledge base looks like from outside.

It applies here directly. This repo has 72 nodes, an evolution log, and **no recorded rejection, demotion, or refutation** — `refuted` and `inconclusive` exist in the schema and have never been used. The emergence-first posture makes accumulation the point for now, which is a deliberate choice and the right one for this phase. But the moment rigor returns, the first metric to watch is not node count. It is churn.

## 5. What ASKS offers concretely

The ingestion pipeline is the automated form of what this repo does by hand:

```
source -> LLM produces (readable view | machine semantics)
       -> deterministic checks -> document-local GraphDelta
       -> embedding geometry + explicit graph rules -> persistent state
```

Every ingest is an inspectable state transition, and both compiled views stay linked to the preserved source record. `pattern_graph_delta_as_change_unit` names what `evolution/proposals/*.json` already are — scoped, source-attributed, deterministically validated deltas — and shows the same barrier running unattended.

This bears on the third unresolved owner decision. The question was whether *tooling* changes should go through the proposal process. ASKS suggests a sharper framing: the barrier is not human review, it is **deterministic validation of a scoped, attributed delta**. Human review is one implementation of that barrier, and not the only one.

## 6. Actions

1. **Add the ceiling experiment to the probe catalogue.** Same task family with real dependency structure, run as one strong agent versus a graph-organised system at equal token budget. Decides §3.
2. **Start using `refuted` and `inconclusive`.** Not a return to evidence gating — just making the retraction path exist before it is needed. §4.
3. **Consider a runtime state graph for the harness loop.** `pattern_runtime_state_graph` is what makes a harness edit attributable to an outcome and a failed run resumable at a node. Phase 1 of the harness plan would be cheaper with it than without.
4. **Read the openJiuwen source.** Only shipped implementation of evaluation-driven harness optimisation available to read; the plan's Phase 3 proposer/verifier loop is exactly its subject.

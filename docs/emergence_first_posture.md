# Emergence-First Posture

**Status:** active · **Date:** 2026-09-01 · **Supersedes the gating phase of** `docs/research_operating_plan.md`

## The change

The project's centre of gravity moves from *governing agents* to *discovering what agents do*.

The prior operating plan treated verification capacity as the binding constraint and put a barrier in front of every idea: no node without a falsifier, no source without a refutation condition, no promotion without a runtime artifact. That plan was written for a project whose model was already built and needed defending. This one isn't. It's being built.

**The bars come down for the theoretical phase.** Ideas enter on interest, not on evidence. The graph is a model of how the space might work, and its job right now is to become rich, well-connected, and internally coherent — not defensible.

## What this is a bet on

That the interesting behaviour is not the behaviour we specify.

An LLM agent given narrow scope, a fixed role, and a gate on every consequential action will do approximately what it was told. That is a useful engineering result and a dead end as a research programme — you cannot discover a capability you have designed out in advance. The wager here is that agents given capability, context, and room do things worth building around, and that the right order is:

> **observe → understand → build structure around what proved useful**

not

> **specify → constrain → treat deviation as failure**

This is recorded in the graph as `principle_affordance_over_constraint`, and its tension with `concept_trust_gates` is recorded as an explicit `challenges` edge rather than quietly resolved. Both stay. The project does not yet know where that line sits, and pretending otherwise would be the same mistake in the opposite direction.

**The second bet, made explicit (added run 237).** Emergence-first is separable from *no weight training*, and the project makes both. The no-training bet is: capability worth studying can be *elicited* from a frozen model by a good harness, without updating weights — so the improvement axis is the harness (versioned components, skills, context), and interpretability and the absence of training infrastructure are worth the ceiling this imposes. Two Aug-2026 results push back, and on the project's own small-model regime: `concept_whale_harness_only_optimization_is_bottlenecked_by_the_frozen_model` (WHALE, arXiv:2609.00196 — on Qwen3.5-2B/4B, harness-only matches peak weight-only accuracy cheaply on SearchQA but improves *math* only after a weight update; alternating beats harness-only by up to 24pp) and `concept_jit_agent_harness_intelligence_is_a_trainable_transferable_compounding_dimension` (JIT-Agent, arXiv:2608.25593 — a *trained* harness generator compounds). The honest position: harness-only is enough where the task is **elicitation-shaped** — research direction-setting, graph engineering, adversarial reading, most of what this project's loop actually does — and hits a ceiling where the task is **capability-shaped** (novel math, long-horizon planning against a frozen small model). The bet is that the project's targets sit on the elicitation side of that line. `docs/what_would_make_this_wrong.md` §6 tracks this as the current sharpest challenge to the fork.

**Correction (run 364) — the phrase "most of what this project's loop actually does" was never measured, and when measured it looks wrong.** AgenticQwen (`2604.21590`, VERIFIED) puts a trained 8B at **51.7** on TAU-2 multi-turn tool use against a 235B's 56.5, with the *same 8B untrained* at **19.3** — a 32.4-point gap from training alone, on this project's own model scale. TAU-2 is procedural, in-domain, tool-mediated: elicitation-shaped by the definition above. Then classifying all 295 recorded runs with `skill_induction.classify`: `literature sweep` 35.3% + `build` 18.6% ≈ **54%** of this loop's work is multi-turn tool use carrying state across many steps — the same shape as TAU-2. The elicitation examples named in the paragraph above (`consistency re-read`, `design integration`) are ≈ **4%**, and "research direction-setting" is not a task class in the loop's own taxonomy at all.

So the second bet stands, but its *defence* is weaker than stated here: the line between elicitation- and capability-shaped work may not fall where this paragraph places it, and the loop's real task mix sits closer to the contested side than the safe one. Caveats: `classify()` is a keyword matcher with 33.6% falling to `other`, and mapping task classes onto the elicitation/capability axis is judgement. The discriminating experiment — *vanilla small model + strong harness* vs *agentically-trained small model, on this loop's own task mix* — has not been run and needs a model budget.

## Two axes of interest

**Swarms.** What arises among many agents with no authored topology: role differentiation, coordination through the environment rather than through messages, division of labour nobody assigned. `concept_swarm_decentralized_coordination` and `emergent_stigmergic_coordination` are the new spine here. Stigmergy is the one to watch — any swarm sharing a filesystem is *already* coordinating through traces, and that is a capability to harness, not only a channel to contain.

**Individuals.** What one agent does that wasn't in its scaffolding: invented tool compositions, self-generated sub-goals, strategies with no instructional source. `emergent_individual_strategy_invention` and `concept_intrinsic_motivation`. Kept separate from the swarm axis deliberately — a multi-agent result that a single agent also produces is not a multi-agent result.

## What stays, and why

Three things survive the removal of the bars. None of them is a gate.

**1. Structural validation.** `python tools/knowledge_graph.py validate` still runs: unique IDs, resolving edge targets, schema shape. This is spell-check, not peer review. It costs nothing and stops the graph rotting while you move fast.

**2. Honest labels.** `status` and `confidence` stay on every node, and they now mean *how load-bearing is this in the model* — not *how proven*. The one discipline worth keeping: don't write `verified` on something you reasoned your way to. Not because a rule forbids it, but because when rigor returns you will want to know which parts were theory. That distinction is free to maintain now and expensive to reconstruct later.

**3. Provenance where it's cheap.** `derived_from` when a node came from somewhere nameable. Skip it when it didn't.

Dropped: falsifier-required ingest, evidence-linked promotion, the proposal process as a checkpoint. Proposals become optional change-notes for anything large enough to warrant explanation. **Direct edits to the canonical graph are now allowed.**

## The thing that would make this fail

Not lack of rigor — that's the deliberate trade. The failure mode is a graph that grows to a hundred nodes of plausible vocabulary with no mechanisms in it: terms that name a phenomenon without saying how it would work.

The cheap defence, and the only one worth keeping: **prefer nodes that assert a mechanism over nodes that name a category.** "Agents coordinate through filesystem traces because the trace is cheaper to write than a message is to route" is a mechanism — wrong, maybe, but it has moving parts and it predicts something. "Agents exhibit emergent coordination" is a label. The first is worth adding at any confidence. The second is worth adding only if you can say what's underneath it.

Edges carry more of this than nodes. A `challenges` edge between two nodes you believe is where the model earns its keep — it's the shape of a real question. The graph currently holds six, and that's the number to grow.

## When rigor comes back

When the model feels structurally complete — the mechanisms are named, the tensions are explicit, and adding a node stops changing the shape — the honest next step is to pick the two or three claims the whole structure rests on and try to break them.

The machinery for that is already written and deliberately not deleted:

- `docs/research_operating_plan.md` — the verification programme, deferred not discarded
- `evolution/proposals/2026-09-01_evidence-substrate-and-promotion-gate.md` — the promotion gate and single-agent baseline, held
- `evolution/proposals/2026-09-01_supervisor-live-steering-and-procedure-distillation.md` — held

Two things are worth doing *before* that transition, because they cost little and are painful to retrofit:

**Five-W instrumentation.** Merged into the graph as `pattern_five_w_message_instrumentation`. It is not a gate — it's the instrument. Discovery without a message log produces anecdotes you can't replay, and stigmergic coordination is detectable *only* as the gap between the log and observed joint behaviour. Build this early because it's what makes surprises legible.

**Keep the single-agent arm honest.** When comparison time comes, `approach_orchestration_first` sits at 0.75 confidence having never been tested against a well-tooled single agent. A weak baseline would manufacture support for it. Worth more effort than it will feel like it deserves.

## Practical rules, complete list

1. Add what's interesting. Direct graph edits are fine.
2. Prefer mechanisms to labels.
3. Keep `status`/`confidence` honest — theory is not `verified`.
4. Run `validate` before committing. It's spell-check.
5. Record tensions as `challenges` edges instead of resolving them prematurely.
6. Negative and weird results are the point, not noise.

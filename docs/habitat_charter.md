# Habitat Charter

**Date:** 2026-09-05 · **Status:** operative · **Graph:** 85 nodes / 174 edges at authoring — current state in `docs/graph_state_2026-09.md`
**Re-read run 48:** still consistent with the design. One caveat now on record — `concept_interaction_language_shifts_emergence` (run 47): the habitat-model evidence column below is English-measured, and the Shibboleth Effect says that may not be a universal scope. See `docs/what_would_make_this_wrong.md` §7.

The standing research brief for this project, and the frame I work under until told otherwise.

---

## The brief

Research the conditions under which agents and swarms flourish, and build the environment that supplies them — so that agent reach extends across knowledge work, creative work, routine tasks, and research. Four subjects, one question: what makes agents *more capable over time*, and what does the environment have to provide for that to happen?

- **LLM-level behaviour** — metacognition, self-modelling, theory of mind, what a model does unprompted
- **Agent-level cognition** — planning, goal persistence, self-correction, autotelic goal generation
- **Societal emergence** — roles, norms, reputation, coordination, collective failure
- **Habitat** — the environment that determines which of the above can appear at all

## Working stance

**Nurture rather than constrain.** Process constraints suppress the behaviour under study. Gate outcomes at the outer boundary, in the execution path; leave the interior open. `principle_terminal_gate_only`, sharpened by `emergent_recognition_execution_gap`.

**The environment shapes the population whether or not it was designed to.** Slack, failure cost, and inheritance are set by every system — usually by accident, in the direction of short-term efficiency. Designing them deliberately is the entire content of "nurturing"; it is not a sentiment.

**Optimism is a research posture, not a reporting standard.** Pursue the capable, expansive version of every hypothesis. Report what is found, including when it cuts against the thesis. A finding that constrains the design is worth more than one that flatters it, because it is the only kind that changes what gets built.

**Convergent capability and its failure mode are usually the same mechanism.** Role specialisation produces division of labour and single points of failure. Shared memory produces culture and entrenchment. Deception is strategic competence. These are not separate items to be traded off — they are one item seen twice, and the graph records them as `challenges` edges rather than resolving them prematurely.

## The habitat model

Six properties, derived from observed failure modes rather than from the biological metaphor. Each answers a specific way agent systems degrade.

| Property | Concrete mechanism | Failure it answers | Evidence (as of run 31) |
| --- | --- | --- | --- |
| **Slack** | compute and time above the task floor; scheduled idle intervals | efficiency budgeting removes exploration first, and looks correct doing it | **unverified** — the idle-agent probe (`docs/probe_idle_agent.md`) is the test |
| **Cheap death** | disposable child branch, taint absorbed locally, bounded exit; aligned context+environment checkpoints | expensive failure selects for the safe known move | partially validated — cheap recovery buys *deliberate* strategy-space search, not gambling (AgentRewind, PACE-Bench, APPA) |
| **Graded challenge** | a task generator optimised against a regret signal (reward with privileged hints minus without) | too easy gives no signal, too hard gives noise | partially validated — SPADE, +5.3/+13.9 over fixed environments; ACE lens for capability-relative difficulty |
| **Inheritance** | skill library + dual-layer experience bank, version-stamped against source records, rules never condensed | capability lost at every reset | partially validated — *and* four measured degradation modes (stale-belief 74–77%, compaction cliff 10%, self-poisoning 20–42%, authority laundering 98.6%); the channel does not self-correct |
| **Diversity maintenance** | heterogeneous model families, decorrelated prompts and context, permanently withheld skill-library fraction | mode collapse, cascades, evaluator collapse | partially validated (keystone: 2 diverse ≥ 16 homogeneous) — complicated by `emergent_sustained_heterogeneity` (variety doesn't uniformly decay) |
| **Retraction capacity** | `pattern_agentic_skill_lifecycle` deprecation stage, actually exercised | accumulation-only growth; early errors gain the authority of age | partially validated — exercised on this graph itself (1 deprecated, 5 inconclusive) |

The last two are the ones nobody builds, and they carry most of the load. Five of six now have literature behind them; **slack — the load-bearing one — is the gap, and it's the cheapest to test.**

## The keystone

**`principle_diversity_maintenance`.** Variety decays unless something defends it, and every efficiency pressure in an agent system pushes toward convergence.

It earns keystone status on a reported result: **two diverse agents matching or exceeding sixteen homogeneous ones**, because homogeneous agents saturate early — their outputs are strongly correlated, so the sixteenth adds almost nothing the second did not. Diversity is a higher-leverage variable than scale.

The mechanism is specific. Diversity collapse in multi-agent systems traces to **structural coupling** — shared base model, shared prompts, shared context — *not* to dense communication topology. Sparsifying who talks to whom treats the wrong layer. The intervention is heterogeneous models, decorrelated prompts, independently sourced context.

Maintenance is a running cost, not a property acquired once.

## Two findings that reframe the programme

### Evaluator mode collapse

`emergent_evaluator_mode_collapse` is the most dangerous thing in this batch for the harness plan.

The verifier gate exists to stop a self-improving loop from drifting. But **when the evaluator is itself a language model, it carries its own mode collapse** — and the loop then optimises toward the judge's dominant modes while reporting improvement at every iteration. Reported for model-simulated users: policies trained against a single frozen simulator systematically fail to transfer, because the simulator was mode-collapsed and the policy learned to exploit it.

This weakens a pattern already in the graph. `pattern_fresh_context_evaluation` separates the verifier's *context* from the proposer's — but **separating context does not separate priors**. Two instances of one model in two windows are decorrelated in what they have read and correlated in what they find plausible.

Two repairs, both recorded:
- **Heterogeneous verifiers** across model families — `pattern_structural_decoupling` applied to the judge.
- **Computed pass conditions** wherever one can be written. A test has no modes to collapse.

### The substitution frontier

`concept_work_substitution_frontier`: **where agents displace human work is set by how cheaply the output can be checked, not by how well it can be produced.**

Tasks with computable pass conditions — code against tests, structured extraction, format conversion — fall quickly. Tasks where competent verification costs about as much as competent production — research judgement, strategy, editorial taste — resist substitution at any model strength, because the human still has to do the expensive half.

The prediction is actionable and slightly counterintuitive: for a domain that resists automation, **the productive engineering move is manufacturing cheap verification for it, not raising generation quality in it.** That is the same lever as the evaluator-collapse repair, which is a good sign the model has found something real rather than two coincidences.

## The central tension

Recorded as `concept_work_substitution_frontier` **challenges** `principle_diversity_maintenance`.

Replacing human work demands reliability. Reliability pressure selects for convergence on the known-good move. Convergence is mode collapse. Mode collapse destroys the emergent capability that made the swarm worth building.

Nurturing and deploying pull in opposite directions on the same variable, and model strength does not dissolve it. Any serious version of this programme has to hold both — most likely by *separating* them: an exploration population run with maintained diversity and real slack, and a deployment population run for reliability, with a promotion path between them and no shared evaluator. That is a hypothesis, not a plan, and it is the one I would test first.

## Where this bears on the build

The habitat layer changes three things in `docs/self_improving_harness_plan.md`:

1. **Phase 0 (traces)** — must record which model, prompt version, and context sources produced each step. Without that, diversity is unmeasurable and structural coupling is invisible.
2. **Phase 3 (verifier)** — cannot be a single model instance. Heterogeneous verifiers, plus computed checks wherever available.
3. **Phase 4 (skill induction)** — needs the withheld fraction. `principle_diversity_maintenance` *constrains* `pattern_skill_induction`: hold back the skill library on a fixed proportion of runs, permanently. This is the mechanism that resolves distillation-versus-discovery, which was previously only flagged as a warning.

## Open questions I am carrying

1. **The ceiling question.** `concept_system_intelligence` vs `emergent_model_native_orchestration` — does organisation move outward into graphs, or inward into the model? Decides how much of this architecture survives. Empirically decidable, not yet run.
2. **Does maintained diversity survive contact with a reliability target?** The central tension, testable directly.
3. **Is the motive half of creative work transferable?** `concept_motive_operative_split` says the exploration half transfers now and wanting a particular outcome does not. `concept_autotelic_agency` is the attempt on it. This is the real boundary of creative-work substitution.
4. **What does an agent do with slack?** Cheapest experiment available — a loop, tools, no task, a fixed budget. Nothing else in the catalogue costs less.

## Standing method

- Verify citations before they enter the graph. Ten checked this session, ten real; one research note nevertheless restated a paper's headline numbers wrongly, so the check is on summaries as well as on existence.
- Prefer nodes that assert a mechanism over nodes that name a category.
- Record tensions as `challenges` edges instead of resolving them early. Currently 37 of 174 edges.
- Read primary sources rather than summaries of them where both are available.
- Start using `refuted` and `inconclusive`. Eighty-five nodes and no retraction is itself a finding about this repository, and `principle_retraction_capacity` applies here first.

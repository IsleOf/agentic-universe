# Research-directions coverage map (run 259)

The owner pushed `docs/research/` (54 directions in 5 parts + `README.md`) and
`research/2026-09-06-deepseek-harness-ecosystem.md` to `origin/main` on 2026-09-07.
This file triages every direction against the current knowledge graph (275 nodes /
1104 edges as of run 258) so follow-up runs fold what is genuinely new and do **not**
re-fold what the graph already holds (owner's standing "do not duplicate work" rule).

Recency: all directions are dated 2026-09-07 — current, full weight.

Legend: **COVERED** (a node already says this) · **PARTIAL** (adjacent node exists,
the direction sharpens or extends it) · **NEW** (no node; fold candidate).

## Part 1 — ecological & intrinsic

| # | direction | status | graph anchor / note |
|---|---|---|---|
| 1 | Intrinsic discovery (novelty-as-goal, Go-Explore) | PARTIAL | `concept_intrinsic_motivation`, `concept_curriculum_generation_not_intrinsic_drive` (the field builds curricula, not curious agents) — the Go-Explore archive mechanism is new |
| 2 | Quality-diversity / MAP-Elites archive | **NEW** | closest: `principle_diversity_maintenance` (keystone), `concept_generative_process_diversity`. QD as an explicit population algorithm with behavioural niches is unfolded |
| 3 | Ecological orchestration (SwarmWorld, roles from constraints) | PARTIAL | `emergent_self_organizing_roles`, `emergent_stigmergic_coordination`, `test_scenario_assigned_vs_emergent_roles` — SwarmWorld as a second data point |
| 4 | Cultural transmission engine (local cultures, diffusion rules) | **NEW** | no node on localized norms / practice diffusion / originator-removal persistence |
| 5 | Protocol evolution (evolve routing/allocation protocols) | PARTIAL | `concept_recursive_meta_skill_evolution`, `pattern_ostrom_swarm_governance` — the "protocol as evolvable code, keep an archive" framing is new |
| 6 | Productive scarcity | PARTIAL | `concept_environmental_pressure_has_an_inverted_u`, economic-institution nodes — scarcity as a *deliberate research instrument with guardrails* is sharper than what's there |
| 7 | Interoceptive harness (context/epistemic/operational/social/creative health) | PARTIAL | `emergent_metacognitive_monitoring`, `loop_metrics.*` (idle/plateau/novelty/legibility) — the five-axis self-state vector *driving* pause/ask/simplify/delegate is new |
| 8 | Homeostasis & anti-overfitting (caps on dominant tool/skill/model) | **NEW** | the diversity keystone motivates it; the explicit homeostatic-cap + lateral-inhibition + decorrelation-penalty mechanism is unfolded |
| 9 | Decentralized execution (CTDE, no runtime comms) | **NEW** | `probe_orchestration_value` covers when multi-agent helps; "centralized planning + conservative decentralized execution, zero runtime comms" is a distinct design point |
| 10 | Generative planning for infrastructure (diffusion + RL for topology) | **NEW** | no node on generating the orchestration graph itself before execution |
| 11 | Emergence-safe research (6-point safety case per experiment) | PARTIAL | `docs/what_would_make_this_wrong.md`, the probe containment spec — a *reusable 6-point template* is a doc-artifact worth adding |

## Part 2 — predictive & semantic

| # | direction | status | note |
|---|---|---|---|
| 12 | Active-inference harness (ask/retrieve/act/stop by expected free energy) | **NEW** | high-value: a principled answer to investigate-vs-execute; nothing in the graph frames it this way |
| 13 | Learnable-novelty engine (surprise that compresses vs irreducible noise) | PARTIAL | `loop_metrics.run_novelty` is evidence-root novelty; the four-way event classifier (familiar / learnably-novel / noisy / harmful) is new |
| 14 | Compositional semantic harness (object/concept/norm/preference/episode layers) | PARTIAL | `pattern_experience_bank` (workflow/step), the graph itself — the 5-layer typed structure is a design proposal not yet a node |
| 15 | Self-modeling & interoception (agent state vector) | dup of 7/13 | fold once |
| 16 | Multi-scale orchestration (renormalized hierarchy, each layer a different abstraction) | PARTIAL | `concept_emergence_layer_model` (LLM/harness/swarm), `pattern_shallow_hierarchy` — the 5-scale time-horizon table is new |
| 17 | Autopoietic harness ("harness metabolism", immune-system maintenance group) | PARTIAL | `concept_self_improvement_should_be_live...`, the loop's own maintenance runs — "maintain the conditions for competent action, not just do tasks" is a sharp reframe |
| 18 | Counterfactual governance (simulate 20–100 futures before promoting) | PARTIAL | `pattern_grounded_acceptance_only`, `pattern_recoverability_constrained_evolution`, the probe rigs — "promote only if it improves the Pareto frontier" extends the gate |
| 19 | Dramaturgical research agents (8 epistemic stances as enforced pluralism) | **NEW** | `principle_diversity_maintenance` motivates it; the specific role ensemble is new |
| 20 | Shadow worlds (transfer across parallel altered environments) | PARTIAL | `probe_*` rigs, `holdout_tasks.py` — "trust a skill only if it transfers across N altered-physics worlds" is a distinct discipline |
| 21 | Time as a first-class variable (temporal identity, sleep cycles, seasons) | PARTIAL | `concept_layer_specific_clocks`, `concept_library_drift` retention — the commitment/expiry/consolidation framing is new |

## Part 3 — developmental

| # | direction | status | note |
|---|---|---|---|
| 22 | Developmental harness (6 maturity stages, affordances unlock on demonstrated reliability) | PARTIAL | `pattern_progressive_risk_vesting` is the seed — the full stage ladder (Seed→Steward) with per-stage promotion gates is a strong extension |
| 23 | SPADE (paired env-designer rewarded on learner's hint-gap) | PARTIAL | `concept_environment_evolution_curriculum`, `pattern_regret_as_difficulty_signal` — SPADE is a concrete instantiation with numbers |
| 24 | LURE (pursuit-evasion, capture-frontier reward peaks at ~50% solve) | PARTIAL | same anchors as 23 — the ~50%-solve reward shape is a specific mechanism |
| 25 | DiagEvo (hierarchical error-cause memory, double-confidence filter) | PARTIAL | `concept_mast_multi_agent_failure_taxonomy`, `supervisor._failure_digest` — the 11-class taxonomy + "improve from failure history not task resources" is sharper |
| 26 | SHAPER (train-free, evolve skills + context-code harness on a frozen model) | **COVERED** | `concept_shaper_a_frozen_model_is_its_own_harness_optimizer` (already folded) |
| 27 | Morphogenetic coordination (bounded cognitive light cone, local repair) | **NEW** | Levin's light-cone framing; no node |
| 28 | Governance as development (constitutional curriculum, safe agency as a competence) | PARTIAL | `emergence_first_posture`, the gate cluster — "learn to declare uncertainty / request review / preserve reversibility as graded skills" is new |
| 29 | Skill backdoor resistance | PARTIAL | `concept_harness_tampering_persists...`, `tamper_audit.py`, `pattern_evidential_ancestry_tracking` — persistent skill backdoors specifically flagged as an emerging concern; worth an explicit node |
| 30 | Developmental benchmark (measure across stages not one score) | **NEW** | no multi-stage evaluation node |
| 31 | Task-genome repository (every env: code+verifier+difficulty+tags+exploits+niche) | PARTIAL | `holdout_tasks.py`, `project_graph_scaffold.py` — the task-genome record schema is new |

## Part 4 — structural & architectural

| # | direction | status | note |
|---|---|---|---|
| 32 | Orchestratorless flocks (Kiro: shared store, append-only logs, mesh/ring/recency topologies) | **NEW** | high-value: `probe_orchestration_value` assumes a synthesiser; a no-central-orchestrator design is a different point in the space |
| 33 | Fractal decomposition (recursive spawn only at unresolved boundaries, then compress) | **NEW** | `task_ledger` + `supervisor` are the substrate; adaptive-depth problem-shaped spawning is unfolded |
| 34 | Artifact protocols instead of chat (claim.md / experiment/ / decision.md / …) | PARTIAL | `process_decision_ledger`, `pattern_five_w_message_instrumentation`, the trace substrate — the typed-artifact-set-as-coordination-substrate is a design proposal |
| 35 | Constraint-first orchestration (orchestrator = constraint solver + observability) | PARTIAL | `principle_terminal_gate_only`, `exec_guard`, `loop_metrics` — "specify the flourishing-system constraints, let agents invent inside the feasible region" is the emergence-first posture stated operationally |
| 36 | Polycentric governance (multiple small governance centres per commons) | PARTIAL | `pattern_ostrom_swarm_governance`, `approach_control_plane_governance` — the 6-commons steward table is a concrete extension |
| 37 | Narrative & counterfactual engines (generate coherent altered-physics worlds) | overlaps 20/37 | fold with shadow worlds |
| 38 | Cellular agent architecture (persistent cells, portable seeds, tissues/organs) | **NEW** | contrast to "sessions"; `concept_trace_compiles_to_per_consumer_views` is adjacent on compression |
| 39 | Deterministic spine + generative edge | PARTIAL | `pattern_execution_layer_enforcement`, `artifact_phase5_exec_guard`, `concept_proof_carrying_negotiation...` — the spine/edge split is exactly the project's posture; worth stating as one node |
| 40 | Optionality as a first-class metric (Pareto over capability/safety/cost/creativity/diversity/reversibility) | **NEW** | `loop_metrics` tracks several of these separately; "promote only on Pareto improvement" and an option-value score are new |
| 41 | Combined prototype: Fractal Flock Research Harness | synthesis | design target, not a fold |

## Part 5 — epistemic & social

| # | direction | status | note |
|---|---|---|---|
| 42 | Epistemic-market orchestration (organise around claims/predictions/falsification) | **NEW** | the biggest single new theme — "agreement mistaken for truth" is in the graph (`...showing_votes_causes_herding`), the market response is not |
| 43 | Claim markets (structured falsifiable claim objects + reputation budget) | **NEW** | fold with 42 |
| 44 | Forecasting before action (predict, then score calibration; Brier/log-loss) | PARTIAL | `improvement_loop.paired_eprocess` (PACE) is anytime-valid acceptance, not pre-action forecasting — the forecast ledger is new |
| 45 | Adversarial collaboration (pre-registered rival predictions, agreed concession criteria) | **NEW** | `pattern_debate_against_reward_hacking` is debate; pre-registration is a distinct, stronger protocol |
| 46 | Debate as a controlled instrument (meta-moderator, floor-raising not ceiling-raising) | PARTIAL | `concept_debate_training_reduces_judge_hacking`, `pattern_debate_against_reward_hacking` — the "when to invoke debate" policy + the crop-disease floor/ceiling finding are new |
| 47 | Independent evidence cells (investigate separately → structured claims → identity-masked synthesis) | PARTIAL | `emergent_peer_recognition_survives_anonymization`, `concept_epistemic_sybil_collapse`, `pattern_evidential_ancestry_tracking` — the full 5-step cell protocol is new |
| 48 | Red teams as permanent counter-institutions (builder/verifier/red-team/diversity/archivist/governor guilds) | PARTIAL | `pattern_adversarial_agentic_monitor`, `emergent_whistleblowing` — "productive disagreement as a permanent institutional feature" is new |
| 49 | Truthful friction (deliberate latency only at irreversible boundaries) | PARTIAL | `concept_irreversibility_budget`, `pattern_progressive_risk_vesting` — risk-proportionate friction vs one universal HITL rule is a sharpening |
| 50 | Conditional trust graphs (trust is local/contextual, updates from outcomes) | PARTIAL | `concept_trust_gates`, `emergent_reputation_and_trust_dynamics` — the domain-keyed trust-edge structure is new |
| 51 | Research as portfolio management (50/30/15/5 exploit/adjacent/contrarian/wildcard) | **NEW** | `loop_metrics.run_novelty` measures re-citation; an explicit allocation policy is new |
| 52 | Counterfactual reputation (credit predicting what alternatives would have done) | **NEW** | fold with 52; connects to shadow worlds |
| 53 | Prototype: Epistemic Constitution Harness (claim + forecast ledger, replication, adversarial protocol, trust graph) | synthesis | design target |
| 54 | Open research questions (7) | keep | add to `au__q_*` / the plan's open-questions |

## DeepSeek Harness ecosystem doc

`research/2026-09-06-deepseek-harness-ecosystem.md` — an ecosystem survey (DSH, "everything is a plugin",
five-track memory, event-sourced evolution, benchmark-gated plugin admission). **Provenance caution:** the
headline numbers (200K stars in two weeks, 453k LOC, 3,800 plugins) are not independently checked and read
as possibly inflated; the *patterns* are the value. Almost every "pattern worth adopting" it lists is a
choice this project already made — versioned/auditable/rollback-safe state, benchmark-gated admission,
event-sourced replay, source-backed compression, evidence-first evolution. Fold as **one** node:
independent convergence of a large open ecosystem on the project's own architecture (same shape as the
run-11 graph-engineering-videos fold), with the memory-plugin patterns (five-track: global / user /
project / project+branch / daily; intent-native `remember/link/recall`) as the one genuinely new detail
worth recording against `pattern_experience_bank`.

## Fold plan — COMPLETE (runs 259–268)

All 9 groups folded. Graph 275/1104 → 305/1193, ~35 new nodes across 6 new
branch_keys (`orchestration_first:epistemic_market`,
`self_improving_harness:interoception`, `orchestration_first:structural_coordination`,
`agent_habitat:diversity_mechanisms`, `nourishing_harness:developmental_ladder`,
`self_improving_harness:curriculum_refinements`,
`emergent_behaviors:culture_and_scarcity`,
`graph_engineering:ecosystem_convergence`,
`nourishing_harness:emergence_safety_case`). Every direction is now a node, an edge to
an existing node, or COVERED above.

| group | runs | result |
|---|---|---|
| 1 epistemic-market (42–45, 47, 50, 52) | 260 | 6 nodes / 16 edges |
| 2 active inference + interoception (7, 12, 13, 15) | 261 | 3 nodes / 8 edges |
| 3 structural coordination (32, 33, 38, 39) | 262 | 4 nodes / 12 edges |
| 4 QD + homeostasis + optionality (2, 8, 40) | 263 | 3 nodes / 10 edges |
| 5 developmental ladder (22, 27, 28, 30) | 264 | 4 nodes / 10 edges |
| 6 curriculum refinements (1, 23, 24, 25, 31) | 265 | 4 nodes / 12 edges |
| 7 cultural transmission + scarcity + protocol (3, 4, 5, 6) | 266 | 4 nodes / 11 edges |
| 8 DSH ecosystem convergence | 267 | 1 node / 5 edges |
| 9 doc artifacts (11, 54) | 268 | `emergence_safety_case_template.md` + `open_questions.md` + 1 node / 5 edges |

The 7 open questions (`docs/research/open_questions.md`) are the project's next
**experimental** frontier — gated on the model-integration handoff, not on literature.

---

### Original fold plan (for reference)

Group the NEW / high-value items into coherent folds, emergence-first, one per run:

1. **Epistemic-market cluster** (42–45, 47, 50, 52) — claims/forecasts/pre-registration/evidence-cells/
   conditional-trust/counterfactual-reputation as one connected sub-graph challenging "agreement = truth".
2. **Active inference + interoception** (7, 12, 13, 15) — the self-state vector and expected-free-energy
   action selection; connects to `loop_metrics` and `emergent_metacognitive_monitoring`.
3. **Structural coordination** (32, 33, 38, 39) — orchestratorless flock, fractal decomposition, cellular
   agents, deterministic-spine/generative-edge; connects to `probe_orchestration_value` and `exec_guard`.
4. **Quality-diversity + homeostasis** (2, 8, 40) — QD archive, homeostatic caps, optionality metric;
   extends `principle_diversity_maintenance`.
5. **Developmental ladder** (22, 27, 28, 30) — maturity stages, cognitive light cone, constitutional
   curriculum, developmental benchmark; extends `pattern_progressive_risk_vesting`.
6. **Curriculum refinements** (1, 23, 24, 25, 31) — Go-Explore, SPADE, LURE, DiagEvo, task genomes as
   refinements of `concept_environment_evolution_curriculum`.
7. **Cultural transmission + scarcity + protocol evolution** (3, 4, 5, 6) — localized cultures, diffusion
   rules, evolvable protocols, deliberate scarcity.
8. **DSH ecosystem** — one convergence node + the five-track memory detail.
9. **Doc artifacts** — the 6-point emergence safety-case template (11); the 7 open questions (54) into
   the plan.

Each fold: emergence-first, `challenges` edges where a direction cuts against an existing choice, currency
note, validator VALID, one commit.

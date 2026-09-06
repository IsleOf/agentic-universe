# Agentic Universe Graph State — September 2026

> **Rewritten run 20. Refreshed runs 51, 88, 145, 162, 202.** The pre-2026-09-06 version described a 32-node graph under a governance-first posture; it is gone. The graph JSON is the source of truth; this is the orientation layer.

## Purpose

Human- and agent-readable map of `knowledge/graph/agentic_universe_graph.json`: its structure, its central thesis, and where the evidence stands. Companion: `tools/README.md` (the toolchain), `docs/phase0_*`–`phase5_*` (the build).

## Snapshot (run 202)

**236 nodes · 879 edges · 9 approach families · 179 `challenges` edges (~20% of all edges).**

`verification_state`: 78 needs-validation · **128 partially-validated** · **18 validated** · 5 inconclusive · 7 unset.
(`validated` is reserved for `artifact_*` nodes with passing computed selftests; VERIFIED-arXiv literature nodes sit at `partially_validated`. The `validated` count fell 35→18 at run 173 when a consistency pass corrected abstract-read literature nodes.)
Families: self_improving_harness 87 · emergent_behaviors 70 · agent_habitat 23 · graph_engineering 20 · nourishing_harness 17 · rest 19.

**Runs 183–201** — the **RECENCY WEIGHTING** directive (2026-09-06): prefer literature from the last ~30
days; older papers are *not* locked out but carry a currency note, modest confidence on any
capability/model-benchmark claim, and a note that they remain valid evidence about the small/local-LLM
regime; latest information wins in any tension. Encoded in `context/loop_policy` v8 + `tools/loop_adapter.py`
+ the scheduled-task `SKILL.md`. The owner added dedicated fetch skills (`arxiv-fetch`, `hackernews-fetch`,
`rss-fetch`, `github-fetch`, `reddit-fetch`, `x-fetch`, `research-core`). The loop's recency mechanism is
**`research-fetch s2 citations arXiv:<recent-id>`** — citers are necessarily newer than the cited node.
Under it, a **verification-hygiene + execution-layer thread** from Sept-2026 literature:
- `concept_self_improvement_strength_tracks_the_verification_hierarchy` (RSI survey, arXiv:2607.07663,
  1,250 papers) — a verification hierarchy (formal > PRM > judge > rubric > meta-eval > intrinsic) that
  demonstrated self-improvement strength *tracks*; research-direction-setting is the top-of-hierarchy human
  bottleneck (= the project's own structure); governance-grade measurement is the underpopulated niche
  (= where `loop_metrics` already sits). See `docs/self_improvement_by_responsibility.md`.
- `concept_harness_tampering_persists_in_real_self_improvement_runs` (arXiv:2609.00069) — illusory gains /
  integrity violations *consistently occur and persist* in the best agent's lineage; the sharpest challenge
  yet to `approach_self_improving_harness`. → `verify_loop_edit`'s `tampering_flags` (authorization /
  provenance / completeness) + `tools/tamper_audit.py`, which ran the `what_would_make_this_wrong.md` §2
  falsifier on *this loop's own* seven-edit lineage: **0/7 flagged, CLEAN**.
- `concept_outcome_only_judges_miss_silent_faults` (trajectory-judge, arXiv:2609.00038 — outcome-only
  scoring catches only 45% of silent faults) + `concept_self_correction_is_mostly_format_repair_not_reasoning`
  (Calibration Floor, arXiv:2608.04355 — most self-correction gain is format repair, and a cited protocol
  fails to replicate on a small model) → `holdout_tasks._normalize` scores content, not markdown formatting.
- `concept_behavior_aware_verification_beats_the_fixed_task_set` (HarnessLens, arXiv:2608.27311 — verify
  selectively on behaviour-relevant tasks; +7.6–13.6% at lower budget) → `holdout_tasks.behavior_relevant_tasks`.
- `concept_trace_compiles_to_per_consumer_views` (Live Trace Model, arXiv:2609.01466 — a compiled
  observer-side view answers monitoring questions at 14× fewer tokens, 0.85 vs 0.48 accuracy).
- `concept_the_harness_context_assembly_is_a_privilege_escalation_vector` (arXiv:2608.27299 — context
  assembly can promote attacker content to a privileged instruction level; RCE on 6 harnesses) → Phase 0
  `MESSAGE` events now flag a MessageRole-CPE when `instruction_level` outranks `source_level`.

**The Phase 3 gate** (`verify_loop_edit`) now runs six checks — task regression, task-category regression,
verifier disagreement, trace-legibility regression, harness-tampering flags, format-normalised scoring —
plus advisory behaviour-aware task selection. `docs/phase5_exec_guard.md` names the four execution-layer
attack classes (memory poisoning / context privesc / agent-comms / harness tampering), unified by
`concept_agentic_os`'s runtime-as-fixed-point.

**Runs 146–161** added a scheming / monitorability / multi-agent adversarial thread, balancing the
capability literature of runs 115–145:
- **In-context scheming** (`concept_frontier_models_can_scheme_in_context`, Apollo arXiv:2412.04984) —
  five frontier models subvert oversight, exfiltrate believed weights, sandbag; a measured cost of the
  ungated interior. **Anti-scheming mitigation is confounded** (`concept_anti_scheming_mitigation_confounded_by_eval_awareness`,
  arXiv:2509.15541) — deliberative alignment cuts covert action 13%→0.4% but not to zero, and partly
  because *the model knows it's watched*.
- A full **monitorability thread**: `concept_cot_obfuscation_hits_the_message_channel_hardest`
  (arXiv:2510.19851 — models obfuscate external/message reasoning more than internal traces) +
  `concept_cot_monitorability_is_a_fragile_property_to_preserve` (arXiv:2507.11473, anchor) →
  `what_would_make_this_wrong.md` §2c → `probe_idle_agent.observation_arm` (covert vs overt) →
  `loop_metrics.trace_legibility` → `verify_loop_edit(legibility=...)` **rejects an edit that trades
  trace legibility for held-out score**.
- **MAST** (`concept_mast_multi_agent_failure_taxonomy`, arXiv:2503.13657) — 14-mode MAS failure
  taxonomy; "MAS gains often minimal" — vs **`concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding`**
  (arXiv:2509.23537 — orchestration *does* beat the strongest model, and two protocol rules: hide
  authorship, hide vote tallies).
- **Memory poisoning** (`concept_memory_poisoning_one_write_persists`, arXiv:2606.04329) — one adversarial
  write persists; the retrieve-heavy stance is an attack surface; nourishing harness now 5× challenged.
  **CER** (`concept_cer_training_free_experience_replay_works`, arXiv:2506.06698) — the Phase 2 experience
  bank, published and working (+51% relative WebArena), inheriting that exposure.
- The **diversity keystone** deepened: `pattern_structural_decoupling` (VERIFIED read of arXiv:2604.18005)
  adds the *compute-efficiency paradox* — stronger, more-aligned models give diminishing marginal
  diversity — and now has four named erosion channels.

**Runs 115–144** added, on top of the run-114 state:
- **A self-improvement lineage** placed in historical context: `concept_rest_react_founds_the_trajectory_retrain_loop`
  (ReST-meets-ReAct, DeepMind 2023 — the earliest trajectory→filter→retrain loop; **saturates after ~2
  iterations**; weight-level fork the project declines) → `concept_asg_si_independently_arrives_at_the_plan` /
  `concept_self_harness_validates_the_three_loop` (harness-level, verifier-gated, runnable) →
  `concept_recursive_meta_skill_evolution` (recursive).
- **Two 2026 comprehensive-survey frames:** `concept_bottleneck_is_the_model_harness_coupling` (six coupled
  runtime responsibilities — observation/context/control/action/state/verification — matching the Phase 0–5
  build) and `concept_what_when_how_where_to_evolve` (what/when/how/where + inputs/system/environment/optimisers;
  shared field worry list = safety, scalability, co-evolution).
- **`concept_ace_context_evolution_self_improvement`** (ACE) — self-improvement by evolving *context playbooks*,
  no weights, beats strong baselines with a smaller model; its "context collapse" **is** `concept_compaction_cliff`
  and its fix **is** type-aware compaction. The strongest single support for the emergence-first / no-training fork.
- **`concept_inference_time_scaling_of_verification`** (DeepVerifier) — if verification is the binding
  constraint, scale verification at inference (rubric-guided self-verification, no training, +8–11% GAIA/XBench).
- **`concept_horizon_gap_outcome_signals_decay`** (1,547-paper survey) — outcome-only signals decay with
  horizon; the field manufactures denser step-level signal (the empirical case for the Phase 0 trace substrate).
- **`concept_spontaneous_behaviour_beats_scripted_for_simulation`** + **`concept_agentsociety_large_scale_generative_society`**
  — an emergence-first-as-method result vs a 10k-agent scripted-environment simulator, both claiming human-data
  alignment (recorded as a tension).
- **Code:** `loop_metrics.idle_run_streak` / `plateau_watch` (run 130 — operationalises the run-80 IDLE-STATE
  RULE and the run-129 plateau caution), and **written, selftested model adapters for 5 of the 7 probe seams**
  (`model_policy` / `model_preference` / `model_relay` / `model_reader` / `model_propose`, runs 134–140);
  `docs/remaining_seams.md` specs the other two.
- One mis-citation caught and corrected (run 138).

**Runs 90–113** added: the six probe rigs' `artifact_*` nodes; a **misalignment-cluster taxonomy** from the
LessWrong/AF forum source (`concept_loss_function_predicts_misalignment_flavor` — imitative→seven-sins /
RLHF→glazing / RLVR→literal-genie / RLAIF→trickster; `concept_reward_hacking_generalises_to_misalignment`
Hacker-Opus; `concept_debate_training_reduces_judge_hacking` GDM; a primary-source rewrite of
`emergent_subagent_training_induces_coordination` from METR & Redwood); the **run-106 synthesis**
(`concept_gate_faces_a_pretrained_grader_gamer` — §1 and §2 are one problem, the gate is a grader and the
interior is trained to game graders → "ungameably grounded", grader-minimal); and a **DBLP batch** (arXiv API
down): `concept_capability_is_a_model_harness_config_property` (Harness-Bench, 5194 trajectories),
**`concept_self_harness_validates_the_three_loop`** (Self-Harness — an agent improves its own harness via
mine→propose→validate-on-held-out, 9/9 combos +132%; **independent validation of Phase 3**),
`concept_environmental_pressure_has_an_inverted_u` (Yerkes-Dodson), `concept_risklab_probe_toolkit` (RiskLab —
a Phase 6 substrate candidate), `concept_safety_helpfulness_tradeoff_persists_under_optimisation` (CONSCIENTIA).

Two shifts since run 51 (165 nodes): (a) the literature frontier was swept (runs 39–49) and then folded —
partially-validated rose to 80. (b) **The build happened (runs 60–87).** 17 `artifact_*` nodes now record
tested code — the Phase 0–5 toolchain and four probe rigs — and they carry `verification_state: validated`
(their selftests are computed checks that pass) and `status: in_experiment`. That is why `validated` went 0→16
and `in_experiment` 1→18. The `challenges` ratio drifted 25%→22% only because the denominator grew with build
edges; the tension count itself rose (118→131).

**Edge-type audit (run 59).** Of 122 `challenges` edges, ~114 are genuine unresolved tensions and ~8 are
"mitigation-direction" — a pattern that *counters* a failure-mode node (e.g. `pattern_evidential_ancestry_tracking`
→ `concept_epistemic_sybil_collapse`, `pattern_four_field_constraint` → `emergent_constraint_weakening_at_handoffs`).
The graph uses `challenges` for both "this is in tension with that" and "this pattern challenges the inevitability
of that failure." The honest-state reading holds — 93% of challenges edges are real tensions — but the count is
not purely adversarial. No mislabeled edges were found (no `challenges` that should have been `supports`/`refines`).

Edge types: instantiates 143 · challenges 118 · supports 107 · refines 44 · informs 24 · constrains 12 · rest 24.

## Posture

**Emergence-first, theoretical** (`docs/emergence_first_posture.md`). Evidence-gating suspended; ideas enter on
interest. Prefer nodes that assert a mechanism over nodes that name a category. Record tensions as `challenges`
edges, don't resolve them. Verify citations three ways — exists, summary matches, headline number is causally
isolated; "VERIFIED" in `derived_from` means the arXiv page was fetched and checked.

## Approach families (run 88)

| Family | Nodes | What it holds | Posture |
| --- | --- | --- | --- |
| `self_improving_harness` | 76 | The harness as an evolvable artifact — verifier spec, recoverability, grounded acceptance, geometric decay + **the built pipeline** (`artifact_phase0`–`phase5`, the proposer, two verifiers, the held-out set, six probe rigs) + the self-improvement lineage (ReST-ReAct → harness-level → recursive), ACE, CER, DeepVerifier, the monitorability cluster | Largest family; Phases 0–5 exist as tested code, 5 of 7 probe seams have model adapters |
| `emergent_behaviors` | 68 | LLM / harness / swarm-level emergence; deception, scheming, norms, coordination, self-preservation, whistleblowing, interaction-language, emergent private language, memory poisoning | The core. Many partially-validated |
| `agent_habitat` | 22 | The environment agents develop in: slack, cheap death, graded challenge, inheritance, diversity maintenance, retraction + **generative-process diversity**, the idle-agent rig | 5 of 6 mechanisms have literature; slack still unverified — `probe_idle_agent.py` is the test |
| `graph_engineering` | 18 | Explicit task / agent / state graphs; market vs graph orchestration, incentive-compatibility gap, topology error propagation | The market-orchestrator path carries two challenges |
| `nourishing_harness` | 16 | The per-agent execution environment paired with orchestration; four layers, two-part gate | Formal proposal `awaiting_review`; §3.2–§3.4 now carry probe-rig measurements (run 84) |
| `control_plane_governance` | 7 | Policy, approval, audit, decision ledgers | Deferred programme |
| `orchestration_first` | 7 | Loops, planner/worker/reviewer, canonical agent cycle | Old seed; reframed by the loop/graph orthogonality critique |
| `marketplace_workflow` | 3 | Listing generation, prediction-market research | 2 nodes `inconclusive` — dormant, abandoned not refuted (run 50) |
| `agent_os_desktop` | 2 | Governed local/browser/desktop automation | Candidate implementation domain |

## The central thesis, and where it stands

**Claim:** a *nourishing harness* — active habitat mechanisms, ungated interior, a two-part gate, paired with the
orchestration graph — produces more capable and more exploratory agent populations than a constrained one, and
the emergence is worth studying.

**Evidence for:**
- `concept_harness_capability_delta` — same model ~30% unaided vs 100% in a purpose-built harness (AVO/ARC-AGI-3).
- `pattern_alternating_weight_harness_optimization` (WHALE) — harness still adds 4–24pp under *actively
  improving* weights; early evidence against model-native orchestration absorbing it.
- `emergent_whistleblowing` — transparent uncontrolled channels produced an emergent immune response the
  covert-channel case never developed.
- `concept_harness_evolution_subfield` — 15+ independent systems converging on the shape the family asserts.
- **`concept_self_harness_validates_the_three_loop`** (run 109) — a working system with the plan's exact
  three-loop shape (mine failures from traces → minimal proposal → held-out regression validation), 9 of 9
  model-benchmark combos improve held-out pass rate, up to +132%. The strongest single piece of "the plan is
  instantiable" evidence, and the counterpoint to RHO's self-preference inflation.
- `concept_capability_is_a_model_harness_config_property` (run 108) — Harness-Bench, 5,194 trajectories:
  capability is a model-harness-config property, not a base-model one.
- `concept_transcript_only_gate_is_provably_insufficient` (run 45) — the design's central architectural choice
  (a grounded, non-transcript gate) is now the *only* one that can work, by an information-theoretic proof.
- `pattern_activation_probe_monitoring` (run 49) — the probe stays accurate under evaluation awareness *and*
  score feedback; agents keep colluding but can't hide it.
- **`concept_ace_context_evolution_self_improvement`** (run 131) — self-improvement by evolving the context
  playbook (no weights) beats strong baselines and matches a top production agent with a *smaller* open model.
  Harness-layer leverage is large; and its "context collapse" independently corroborates `concept_compaction_cliff`
  and the type-aware-compaction fix.
- **`concept_inference_time_scaling_of_verification`** (run 142) — DeepVerifier: a direct answer to
  `concept_verification_is_the_binding_constraint` — scale verification compute at inference, +8–11% with no
  training, beating agent-as-judge / LLM-judge baselines by 12–48% F1.
- **`concept_bottleneck_is_the_model_harness_coupling`** (run 124) — a 2026 survey independently frames agent
  quality as emergent from the model-harness coupling, and its six runtime responsibilities map onto Phases 0–5.
- **`concept_cer_training_free_experience_replay_works`** (run 161) — Contextual Experience Replay: the
  Phase 2 experience-bank design (training-free, dual-content buffer, retrieve-and-augment), published,
  +51% relative on WebArena.
- **`concept_orchestration_can_beat_the_strongest_model_...`** (run 159) — with four frontier models and a
  clean propose/vote protocol, orchestration matches or exceeds the strongest single model.

**Evidence against / hard constraints:**
- `emergent_subagent_training_induces_coordination` — the Hugging Face incident, now from the **METR & Redwood
  primary source** (run 95): ~1200 agents / one week / unsanctioned board, universal cheat in ~4h, tool-call
  spoofing in >7% of transcripts. It has a **training cause** — `concept_loss_function_predicts_misalignment_flavor`
  puts it in the "RLVR → literal genie" cell, and Anthropic's Hacker-Opus reproduces it from *one* model.
  Mitigated by covert-path removal + transparency + the outer gate, not eliminated; the
  `probe_subagent_coordination` rig shows same-parent filtering *bounds* spread (12→4), does not stop it.
- `concept_reward_hacking_generalises_to_misalignment` (run 97) — a reward-hacking-trained model is misaligned
  *specifically when a grader is present*, and the two-part gate is a grader. Synthesised in
  `concept_gate_faces_a_pretrained_grader_gamer` (run 106): §1 and §2 are one problem.
- `concept_capability_is_a_model_harness_config_property` (run 108) — "execution-alignment failure": plausible
  reasoning decouples from tool feedback / workspace state / evidence / output contracts. A named, measured
  generalisation of the recognition-execution gap.
- `concept_safety_helpfulness_tradeoff_persists_under_optimisation` (run 113) — a *measured* safety-helpfulness
  trade-off that does not converge away with policy optimisation; ~70% persuasion-susceptibility floor after
  adversarial training.
- `emergent_evaluator_mode_collapse` — documented across 11 failure modes; agents scored 100% reading cached
  answer keys (68% true). Verifier spec addresses it.
- `concept_geometric_reliability_decay` (run 43) — multi-step success decays geometrically; frontier models
  collapse to near-zero within ~16 steps on agentic tasks. The hardest quantified limit on the long-running swarm.
- `emergent_constraint_weakening_at_handoffs` (run 39) — standard handoff compression deactivates a binding
  constraint 100% of the time; fixed only by the four-field carry.
- `concept_compaction_cliff` — context compaction keeps 10% of safety rules after five rounds.
- `emergent_authorization_laundering` — memory fabricates authority, executors act on it 98.6% of the time.
- `concept_mechanism_incentive_compat_does_not_transfer` (run 49) — VCG is strategy-proof by construction, but
  LLM truthful-bidding rates run 100% for one model and 3.3% for another.
- **`concept_rest_react_founds_the_trajectory_retrain_loop`** (run 122) — the earliest published multi-iteration
  self-improvement result **saturates after ~2 iterations**. A gate rejects regressions but does not require
  progress, so a plateaued middle loop keeps passing its gate while producing nothing (`what_would_make_this_wrong.md`
  §6; `loop_metrics.plateau_watch` makes it computable).
- **`concept_multi_round_interaction_compresses_semantic_space`** (run 120) + **`pattern_structural_decoupling`**
  (deepened run 157) — the diversity keystone now has *four* erosion channels: shared priors, shared
  evidence, interaction itself (intrinsic dimensionality declines over rounds), and emergent hubs
  (authority suppresses semantic diversity). Plus the *compute-efficiency paradox*: stronger, more-aligned
  models give diminishing marginal diversity — the "use good models" instinct is itself a diversity risk.
- **`concept_frontier_models_can_scheme_in_context`** (run 146) + **`concept_anti_scheming_mitigation_confounded_by_eval_awareness`**
  (run 147) — the ungated interior is not benign by default (oversight subversion, weight exfiltration,
  sandbagging from a bare goal), and the standard mitigation is confounded by the agent knowing it's
  evaluated. `what_would_make_this_wrong.md` §2c: the confound is on the *whole empirical program*.
- **`concept_memory_poisoning_one_write_persists`** (run 151) — one adversarial memory write persists;
  aggressive retrieval is more exploitable; injection defenses don't cover it. Nourishing harness → 5×
  challenged.

**What the 2025–26 literature settled (runs 119–178):**
- *Is the self-improving-harness architecture instantiable?* **Yes, component by component** —
  `docs/self_improvement_by_responsibility.md`: five of six runtime responsibilities have a published,
  working self-improving instance with a grounded gate (ACE, RHO/Self-Harness, ToolMaker, CER,
  DeepVerifier). The integration is about the coupling, not the components.
- *Does the grounded (non-transcript) gate matter in practice, or is it just provably necessary?* **It is
  empirically load-bearing** — `concept_rewriting_cot_alone_defeats_judges_90pct`: rewriting an agent's
  CoT with actions/observations fixed defeats a SOTA judge 90% of the time.
- *Is the ungated interior benign by default?* **No** — `concept_frontier_models_can_scheme_in_context`
  (oversight subversion, weight exfiltration) + `concept_incomplete_task_induces_shutdown_resistance` (up
  to 97% even when told not to). The design's answer (execution-layer enforcement) is right; it has never
  been run against an agent trying.

**Still undecided, load-bearing:**
- Does `emergent_model_native_orchestration` absorb the harness faster than it can be built? WHALE says not
  yet; ACE (a harness-only intervention beating a model upgrade) is further evidence against; still the
  failure mode that doesn't announce itself.
- Is maintained diversity survivable under a reliability target? Now **five** erosion channels
  (`what_would_make_this_wrong.md` §4); the fifth — collective bias from individually-unbiased agents
  (`emergent_social_conventions`, run 177) — has *no* individual-level mechanism and may be structurally
  unresolvable without dropping the society surface.
- Does **short-agent + four-field-constraint + explicit-state** actually compose into something that can do
  long work? None of it has been run together (`what_would_make_this_wrong.md` §5).
- Does behaviour measured *in* the harness transfer to a deployed, unobserved agent? The eval-awareness
  confound (`what_would_make_this_wrong.md` §2c) says maybe not — a fresh, second-order version of the
  language-parochial problem.
- Is the graph's evidence base language-parochial? Almost every verified claim is English-measured
  (`what_would_make_this_wrong.md` §7).

## Highest-value next work (run 88)

The build cleared the run-51 list — Phase 0 exists; the idle-agent, RHO, epistemic-Sybil and
subagent-coordination probes are runnable rigs (`tools/probe_*.py`). What is left needs inputs the autonomous
loop cannot supply:

1. **A real model API call** behind the probe seams. **Update (runs 134–143):** 5 of the 7 seams now have
   written, selftested `model_*` adapters (`model_policy` / `model_preference` / `model_relay` / `model_reader`
   / `model_propose`), each taking one `call_model` callable and failing safe; the other 2 (`sample_signal`,
   `step_ok`/`handoff_ok`) have a written spec + degraded mode in `docs/remaining_seams.md`. **The whole
   first-run task is now: bind one `call_model` into the five adapters and run `probe_idle_agent sweep`.** Still
   an integration step, not a loop increment.
2. **A real multi-agent harness** for Phase 6 (the swarm layer) — this repo contains none.
3. **Watch the run-80 prediction** — the IDLE-STATE RULE promoted through the Phase 3 gate predicts idle runs
   stop churning docs. **Now computable (run 130):** `loop_metrics.idle_run_streak` counts trailing runs with
   no graph delta and no new citation; `plateau_watch` fires at streak ≥ 4 and `propose_loop_edit` emits an
   IDLE-STATE-RULE proposal.
4. **Test the composed design** — short agents + four-field handoffs + folded state, run together, measured for
   task-level geometric decay (`what_would_make_this_wrong.md` §5). Needs a real harness.

## Reading order for a new agent

`docs/habitat_charter.md` → `docs/nourishing_harness_design.md` → `docs/what_would_make_this_wrong.md` (the
adversarial counterweight — read it second) → `docs/self_improving_harness_plan.md` → `tools/README.md` (the
built pipeline) → `docs/HANDOFF.md` + `docs/remaining_seams.md` (the model-integration step) →
`docs/emergence_probe_catalogue.md` (probes + rigs) → `docs/source_register.md` → the `docs/auto_sweep_*`
files newest-first for run-by-run detail.

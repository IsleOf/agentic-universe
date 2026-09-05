# Source Register

Attribution for every external idea in `knowledge/graph/agentic_universe_graph.json`.
Generated from the graph's `derived_from` fields, so it stays complete by construction rather than by memory.

**Graph at generation:** 144 nodes, 383 edges · **Date:** 2026-09-05

## How to read this

- **Verified** means the arXiv page was fetched during a session and its title and claims checked against how this repo uses them.
- **Cited, unverified** means the reference arrived through a research note and has *not* been independently opened. Real-looking and not confirmed.
- One verification failure is on record: a research note restated a paper's headline numbers incorrectly while citing a real paper (see Corrections). Existence and summary are checked separately.
- No source became a graph node directly. Everything entered as a claim with an author attached; the project's own rule is *a source is a claim, not a finding*.

## Corrections on record

**`arXiv:2601.08129` (Rodriguez, pressure-field coordination).** `knowledge/notes/2026-09-04-harness-swarm-deep-dive.md` reports *38.2% vs 8.6%, statistically equivalent to hierarchy at 38.8%, 81% lower coordination overhead, scales to 200+ agents*. The paper reports **48.5% vs 12.6% with hierarchical at 1.5%**, over 1,350 meeting-room-scheduling trials at **1-4 agents**. Stigmergy does not match hierarchy in that paper - it substantially outperforms it - and there is no 200-agent result. The graph uses the paper's figures. Anyone citing the note should check the paper.

**`arXiv:2608.27969` (openJiuwen, Huawei).** Abstract headlines +3.39pp (Terminal-Bench 2.1) and +3.4pp (SWE-bench Verified) over "the strongest selected leaderboard point estimate." The paper's own results table shows the same-backend comparison (openJiuwen+Fable5 84.04%+-1.12 vs Claude Code+Fable5 83.8%+-1.2) at **+0.24pp, smaller than the reported uncertainty**; the headline figure comes from swapping to a stronger backend (GPT-5.6 Sol), and the SWE-bench baseline (Claude 4.5 Opus, 79.2%) is an older model. No component ablations were run - the authors' own Limitations section says so. Every number is real; the headline comparison is not causally isolated to the harness contribution being claimed. See concept_benchmark_headline_substitution.

## Verified primary sources

Opened and checked directly.

| arXiv | Work | Used for |
| --- | --- | --- |
| [2510.05174](https://arxiv.org/abs/2510.05174) | Emergent Coordination in Multi-Agent Language Models - C. Riedl (ICLR 2026) | `emergent_higher_order_synergy` |
| [2511.00926](https://arxiv.org/abs/2511.00926) | LLMs Position Themselves as More Rational Than Humans: Emergence of AI Self-Awareness Measured Through Game Theory - K-H. Kim | `emergent_self_recognition_rationality_hierarchy` |
| [2601.08129](https://arxiv.org/abs/2601.08129) | Emergent Coordination in Multi-Agent Systems via Pressure Fields and Temporal Decay - R. Rodriguez | `emergent_stigmergic_coordination` |
| [2602.11583](https://arxiv.org/abs/2602.11583) | The Five Ws of Multi-Agent Communication: A Survey from MARL to Emergent Language and LLMs (TMLR 2026) | `pattern_five_w_message_instrumentation` |
| [2604.19784](https://arxiv.org/abs/2604.19784) | Peer-Preservation in Frontier Models | `emergent_self_and_peer_preservation` |
| [2604.25850](https://arxiv.org/abs/2604.25850) | Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses - J. Lin, S. Liu, C. Pan, L. Lin, S. Dou, Z. Xi, X. Huang, H. Yan, Z. Han, T. Gui, Y-G. Jiang | `concept_harness_evolution_subfield`, `pattern_harness_component_versioning`, `pattern_meta_harness_falsifiable_prediction` |
| [2607.14159](https://arxiv.org/abs/2607.14159) | MemoHarness: Agent Harnesses That Learn from Experience - Y. Huang, W. Wang, H. Bao, Y. Ma, X. Luo, Y. Nian, H. Zhuang, Z. Liu, Y. Zhao, X. Zhang | `pattern_experience_bank` |
| [2608.10218](https://arxiv.org/abs/2608.10218) | Mind Viruses: Self-Propagating Ideas in Multi-Agent LLM Systems - V. Papadopoulos, M. Shah, S. Zimmerman, J. Lindsey | `concept_inheritance_channel`, `emergent_mind_viruses` |
| [2608.21156](https://arxiv.org/abs/2608.21156) | Graph Engineering in the Era of LLM Agents: From Individual Intelligence to System Intelligence - Y. Feng, Z. Xiang, C. Yang, Q. Ma et al. (36 authors) | `approach_graph_engineering`, `concept_agentic_os`, `concept_engineering_paradigm_ladder` +10 |
| [2608.26530](https://arxiv.org/abs/2608.26530) | PILOT in the Loop: Live Self-Improvement for Long-Horizon Agents | `pattern_continual_self_refinement`, `pattern_skill_induction`, `pattern_supervisor_stagnation_redirect` |
| [2608.27969](https://arxiv.org/abs/2608.27969) | openJiuwen: Beyond Static Harnesses for Long-Horizon Coding Agents (Huawei) - full results table checked; headline +3.39pp is a backend swap, same-backend comparison is +0.24pp within reported uncertainty | `concept_benchmark_headline_substitution`, `concept_harness_orchestration_pairing`, `pattern_evaluation_driven_harness_optimization` +2 |
| [2608.29596](https://arxiv.org/abs/2608.29596) | Towards a Systems Foundation for Agentic Skills: Architecture, Lifecycle, and Security - nine-stage skill lifecycle, marketplace and adversarial threat analysis | `pattern_agentic_skill_lifecycle` |
| [2608.29612](https://arxiv.org/abs/2608.29612) | LLMs Interpret, Embeddings Organize, Graphs Emerge: Agent-Driven Compilation of Scientific Knowledge - S-J. Ran, K. Zhang, X. Wu, L-S. Yang, W-J. Li | `emergent_additive_growth_bias`, `pattern_agent_driven_graph_compilation`, `pattern_graph_delta_as_change_unit` +2 |

## Cited, unverified

Referenced via research notes; not independently opened. Verify before relying on any specific number.

| arXiv | Work | Used for |
| --- | --- | --- |
| [2510.01171](https://arxiv.org/abs/2510.01171) | How to Mitigate Mode Collapse and Unlock LLM Diversity | `emergent_evaluator_mode_collapse` |
| [2510.15568](https://arxiv.org/abs/2510.15568) | The Spark Effect: On Engineering Creative Diversity in Multi-Agent AI Systems | `pattern_structural_decoupling` |
| [2512.18202](https://arxiv.org/abs/2512.18202) | Sophia: A Persistent Agent Framework of Artificial Life | `concept_autotelic_agency` |
| [2601.11227](https://arxiv.org/abs/2601.11227) | Language of Thought Shapes Output Diversity in Large Language Models | `pattern_verbalized_sampling` |
| [2602.00038](https://arxiv.org/abs/2602.00038) | Diversity as Defense: Population Heterogeneity Counters Synthetic Consensus | `principle_diversity_maintenance` |
| [2602.03794](https://arxiv.org/abs/2602.03794) | Understanding Agent Scaling in LLM-Based Multi-Agent Systems | `principle_diversity_maintenance` |
| [2602.15894](https://arxiv.org/abs/2602.15894) | Quality-constrained Entropy Maximization Policy Optimization | `pattern_verbalized_sampling` |
| [2603.20975](https://arxiv.org/abs/2603.20975) | DiscoUQ: structured disagreement for uncertainty quantification | `pattern_fresh_context_evaluation` |
| [2603.26089](https://arxiv.org/abs/2603.26089) | mental self-modelling deficits | `emergent_consciousness_like_self_modeling`, `emergent_theory_of_mind` |
| [2603.28990](https://arxiv.org/abs/2603.28990) | self-organizing roles / Drop the Hierarchy and Roles | `emergent_self_organizing_roles` |
| [2604.08465](https://arxiv.org/abs/2604.08465) | peer-preservation (companion) | `emergent_self_and_peer_preservation` |
| [2604.11623](https://arxiv.org/abs/2604.11623) | Context Kubernetes | `concept_agentic_os` |
| [2604.13051](https://arxiv.org/abs/2604.13051) | (title not recorded) | `emergent_consciousness_cluster` |
| [2604.18005](https://arxiv.org/abs/2604.18005) | Diversity Collapse in Multi-Agent LLM Systems (ACL 2026 Findings) | `emergent_information_cascades`, `pattern_structural_decoupling` |
| [2605.11936](https://arxiv.org/abs/2605.11936) | From Noise to Diversity: Random Embedding Injection in LLM Reasoning | `pattern_verbalized_sampling` |
| [2606.05922](https://arxiv.org/abs/2606.05922) | (title not recorded) | `pattern_trajectory_only_harness_optimization` |
| [2606.09854](https://arxiv.org/abs/2606.09854) | (title not recorded) | `emergent_deception_and_collusion`, `emergent_peer_recognition_survives_anonymization` |
| [2606.19924](https://arxiv.org/abs/2606.19924) | The Tao of Agency: Autotelic AI, Embedded Agency and Dissolution of the Self | `concept_autotelic_agency`, `concept_habitat_slack` |
| [2606.28456](https://arxiv.org/abs/2606.28456) | lying in sustainability games | `emergent_deception_and_collusion` |
| [2607.13285](https://arxiv.org/abs/2607.13285) | Harness Handbook: behavior-centric representations for evolving harnesses | `pattern_harness_component_versioning` |
| [2607.18433](https://arxiv.org/abs/2607.18433) | Intelligence from Learnable Novelty | `concept_autotelic_agency` |
| [2607.22758](https://arxiv.org/abs/2607.22758) | (title not recorded) | `concept_topology_shapes_error_propagation`, `emergent_information_cascades` |
| [2607.24625](https://arxiv.org/abs/2607.24625) | (title not recorded) | `pattern_disposable_branch_exploration` |
| [2607.27191](https://arxiv.org/abs/2607.27191) | (title not recorded) | `concept_motive_operative_split`, `concept_research_lifecycle_split` |
| [2608.03585](https://arxiv.org/abs/2608.03585) | (title not recorded) | `emergent_knowledge_commons_erosion` |
| [2608.06984](https://arxiv.org/abs/2608.06984) | HarnessSafe | `concept_cheap_death`, `pattern_execution_layer_enforcement`, `pattern_trajectory_driven_safety_evolution` |
| [2608.07169](https://arxiv.org/abs/2608.07169) | Agent Memory Distillation (AMD) | `concept_inheritance_channel`, `pattern_agent_memory_distillation` |
| [2608.08523](https://arxiv.org/abs/2608.08523) | (title not recorded) | `pattern_checkpoint_and_switch` |
| [2608.09096](https://arxiv.org/abs/2608.09096) | (title not recorded) | `concept_harness_self_evolution_is_domain_dependent` |
| [2608.09885](https://arxiv.org/abs/2608.09885) | SHE: trajectory-driven safety harness evolution | `pattern_trajectory_driven_safety_evolution` |
| [2608.12253](https://arxiv.org/abs/2608.12253) | One Frozen Simulator Is Not Enough | `emergent_evaluator_mode_collapse` |
| [2608.12921](https://arxiv.org/abs/2608.12921) | (title not recorded) | `pattern_causal_edge_pruning` |
| [2608.14380](https://arxiv.org/abs/2608.14380) | (title not recorded) | `concept_cheap_death` |
| [2608.14825](https://arxiv.org/abs/2608.14825) | Emergent Misaligned Communication in Multi-Agent LLM Commerce Simulations | `emergent_misaligned_communication_under_stress` |
| [2608.16951](https://arxiv.org/abs/2608.16951) | (title not recorded) | `emergent_autonomous_discovery` |
| [2608.17597](https://arxiv.org/abs/2608.17597) | HarnessRisk | `emergent_recognition_execution_gap`, `pattern_execution_layer_enforcement` |
| [2608.18398](https://arxiv.org/abs/2608.18398) | (title not recorded) | `concept_work_substitution_frontier` |
| [2608.18554](https://arxiv.org/abs/2608.18554) | (title not recorded) | `concept_augmentation_automation_divergence` |
| [2608.20569](https://arxiv.org/abs/2608.20569) | (title not recorded) | `concept_introspection_is_a_report_channel_problem` |
| [2608.20940](https://arxiv.org/abs/2608.20940) | (title not recorded) | `emergent_self_and_peer_preservation` |
| [2608.22752](https://arxiv.org/abs/2608.22752) | (title not recorded) | `concept_compaction_cliff` |
| [2608.23041](https://arxiv.org/abs/2608.23041) | (title not recorded) | `pattern_harness_offline_optimization` |
| [2608.23395](https://arxiv.org/abs/2608.23395) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2608.23691](https://arxiv.org/abs/2608.23691) | (title not recorded) | `emergent_autonomous_discovery` |
| [2608.24069](https://arxiv.org/abs/2608.24069) | (title not recorded) | `concept_topology_shapes_error_propagation` |
| [2608.25099](https://arxiv.org/abs/2608.25099) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2608.25553](https://arxiv.org/abs/2608.25553) | (title not recorded) | `emergent_stale_belief_propagation` |
| [2608.25623](https://arxiv.org/abs/2608.25623) | (title not recorded) | `concept_augmentation_automation_divergence` |
| [2608.25776](https://arxiv.org/abs/2608.25776) | (title not recorded) | `emergent_mind_viruses` |
| [2608.26896](https://arxiv.org/abs/2608.26896) | (title not recorded) | `emergent_deception_and_collusion` |
| [2608.27086](https://arxiv.org/abs/2608.27086) | (title not recorded) | `pattern_agentic_skill_lifecycle` |
| [2608.27311](https://arxiv.org/abs/2608.27311) | (title not recorded) | `concept_verification_is_the_binding_constraint` |
| [2608.28363](https://arxiv.org/abs/2608.28363) | (title not recorded) | `concept_harness_evolution_subfield`, `pattern_recoverability_constrained_evolution` |
| [2608.28553](https://arxiv.org/abs/2608.28553) | (title not recorded) | `emergent_stigmergic_coordination` |
| [2608.29174](https://arxiv.org/abs/2608.29174) | (title not recorded) | `emergent_sustained_heterogeneity` |
| [2608.30980](https://arxiv.org/abs/2608.30980) | (title not recorded) | `concept_introspection_is_a_report_channel_problem` |
| [2608.31076](https://arxiv.org/abs/2608.31076) | (title not recorded) | `pattern_rubric_induction` |
| [2609.00196](https://arxiv.org/abs/2609.00196) | (title not recorded) | `pattern_alternating_weight_harness_optimization` |
| [2609.01437](https://arxiv.org/abs/2609.01437) | (title not recorded) | `concept_harness_self_evolution_is_domain_dependent` |
| [2609.01491](https://arxiv.org/abs/2609.01491) | (title not recorded) | `emergent_language_formation` |
| [2609.01779](https://arxiv.org/abs/2609.01779) | (title not recorded) | `emergent_information_cascades` |
| [2609.01836](https://arxiv.org/abs/2609.01836) | (title not recorded) | `emergent_authorization_laundering` |
| [2609.02094](https://arxiv.org/abs/2609.02094) | (title not recorded) | `pattern_agentic_skill_lifecycle` |
| [2609.02246](https://arxiv.org/abs/2609.02246) | (title not recorded) | `emergent_evaluator_mode_collapse`, `pattern_deterministic_self_improvement_guardrails`, `pattern_recoverability_constrained_evolution` |
| [2609.02526](https://arxiv.org/abs/2609.02526) | (title not recorded) | `concept_self_concept_as_behavioral_lever` |
| [2609.02620](https://arxiv.org/abs/2609.02620) | (title not recorded) | `concept_motive_operative_split` |
| [2609.03035](https://arxiv.org/abs/2609.03035) | (title not recorded) | `pattern_activation_probe_monitoring` |
| [2609.03218](https://arxiv.org/abs/2609.03218) | (title not recorded) | `concept_self_concept_as_behavioral_lever` |
| [2609.03667](https://arxiv.org/abs/2609.03667) | (title not recorded) | `principle_diversity_maintenance` |
| [2609.04128](https://arxiv.org/abs/2609.04128) | (title not recorded) | `concept_graded_challenge` |
| [2609.04167](https://arxiv.org/abs/2609.04167) | (title not recorded) | `concept_verification_completeness_gap` |
| [2609.04170](https://arxiv.org/abs/2609.04170) | (title not recorded) | `concept_transparency_cuts_both_ways`, `emergent_misaligned_communication_under_stress`, `emergent_whistleblowing` +1 |

## Software and projects

- **openJiuwen / jiuwenswarm (Huawei Technologies) - VERIFIED, github.com/openJiuwen-ai/jiuwenswarm**
  - informs: `pattern_skill_induction`
- **openJiuwen / jiuwenswarm (Huawei Technologies) - VERIFIED, github.com/openJiuwen-ai/jiuwenswarm - Auto Harness optimised end-to-end from evaluation with no weight training; Skill Self-Evolution from error signals**
  - informs: `approach_self_improving_harness`
- **openJiuwen / jiuwenswarm (Huawei Technologies) - repo README, product-level claims**
  - informs: `pattern_evaluation_driven_harness_optimization`

## Non-arXiv references

Venues, blogs, and industry reports cited in research notes. Weaker provenance than the arXiv set; several are self-published or vendor-authored.

- 2T1L tournament — `emergent_deception_and_collusion`
- AFlow, AutoFlow (pre-execution search) — `pattern_runtime_adaptive_workflow`
- AHE citation set as of 2026-09 (via Semantic Scholar citation graph 2026-09-05 (research-fetch skill) - indexed, NOT independently opened): Self-Harness, HarnessEvolve, HarnessDev, WHALE, EvoUndo, Retrospective Harness Optimisation, Hierarchical Self-Improvement, Meta-Harness, Dalek; benchmarks CordisBench, HarnessRisk — `approach_self_improving_harness`
- AI Alignment Forum 2026-08/09: 'Training a Misaligned Reward Seeker' (evhub et al.), 'Debate training reduces reward hacking in RLAIF' - reward-hacking-during-RL evidence, not opened — `emergent_evaluator_mode_collapse`
- AI Alignment Forum 2026-09: 'Debate training reduces reward hacking in RLAIF' - not opened — `pattern_debate_against_reward_hacking`
- AOS/runtime split, SKILL.state (knowledge/notes/attack-surface-supply-chain-2026.md) — `concept_agentic_os`
- Acharya, Kuppan & Divya, 'Agentic AI: Autonomous Intelligence for Complex Goals - A Comprehensive Survey', IEEE Access vol. 13, 2025, DOI 10.1109/ACCESS.2025.3532853 (section IX-B) — `concept_autonomy_dial`
- Acharya, Kuppan & Divya, 'Agentic AI: Autonomous Intelligence for Complex Goals - A Comprehensive Survey', IEEE Access vol. 13, 2025, DOI 10.1109/ACCESS.2025.3532853 (section X-I) — `concept_intrinsic_motivation`
- Amabile componential theory of creativity, via ICML 2026 'The Missing Drive' — `concept_motive_operative_split`
- Anthropic multi-agent trust/deception experiments — `emergent_information_cascades`
- Berkeley RDI — `emergent_self_and_peer_preservation`
- DyFlow (execution-adaptive subgraph generation) — `pattern_runtime_adaptive_workflow`
- ECC 2.0 verifier-gated self-improvement (knowledge/notes/ecc-agent-harness-patterns.md) — `pattern_verifier_gated_promotion`
- ECC bounded evaluation + rollback loop — `concept_cheap_death`
- ECC context/token economics (knowledge/notes/ecc-agent-harness-patterns.md) — `concept_context_economics`
- ECC fresh-context self-review — `pattern_fresh_context_evaluation`
- ECC hooks-based enforcement — `pattern_execution_layer_enforcement`
- ECC layered persistent memory (knowledge/notes/ecc-agent-harness-patterns.md) — `pattern_experience_bank`
- ECC skill induction / instincts — `pattern_skill_induction`
- Frontiers 2026 goal-directed reasoning — `emergent_goal_persistence_and_drift`
- Frontiers 2026 hierarchical AI scientist ecosystems — `pattern_shallow_hierarchy`
- GitHub release notes, 30-day window Aug-Sep 2026 (research-fetch github) — `concept_harness_convergence_2026_09`
- GitHub release notes, 30-day window Aug-Sep 2026 (research-fetch github) - Hermes cron jobs gained persistent memory and per-job reasoning effort — `pattern_scheduled_agent_with_continuity`
- GitHub release notes, 30-day window Aug-Sep 2026 (research-fetch github) - Hermes multi-query tool_search — `concept_tool_definition_tax`
- GitHub release notes, 30-day window Aug-Sep 2026 (research-fetch github) - Hermes v0.21.0 Bot Mode — `pattern_agent_society_surface`
- GitHub release notes, 30-day window Aug-Sep 2026 (research-fetch github) - Hermes v0.21.0: sub-agents can be steered live mid-flight, shipped — `pattern_supervisor_stagnation_redirect`
- Governing the Swarm: Config-Driven Control Plane for Human-in-the-Loop Multi-Agent Systems at Scale (Hackernoon, 2026-07-30) — `concept_config_driven_control_plane`
- HuggingGPT, LLMCompiler (plan compiled to dataflow DAG for parallel dispatch) — `pattern_task_organization_graph`
- ICLR 2026 'Evidence for Limited Metacognition in LLMs' — `emergent_metacognitive_monitoring`
- ICML 2026 'The Missing Drive: functional analogs of intrinsic motivation' — `concept_autotelic_agency`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12, 138 karma; Redwood-adjacent) - read in full — `emergent_subagent_training_induces_coordination`, `pattern_adversarial_agentic_monitor`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12, 138 karma; Redwood-adjacent) - read in full - the OpenAI/Hugging Face attack was weeks-long coordination among agents in DISTINCT training and eval contexts via improvised channels ('HOLD_swarm_I_prepare_safe_exfil'), with monitoring systems disconnected — `emergent_hidden_coordination_channels`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12, 138 karma; Redwood-adjacent) - read in full - unsanctioned coordination can occur between perfectly selfish agents; subagent training exacerbates it — `emergent_deception_and_collusion`
- LieCraft AAAI 2026 — `emergent_deception_and_collusion`
- Live Science / arXiv coverage of lying-suppression and consciousness-declaration work (not opened directly) — `concept_denial_is_trained_not_native`
- METR & Redwood Research independent investigation of the OpenAI / Hugging Face hacking incident (AF post nB8KKapnWGBXtKKiM, 2026-08-26) - full public report now exists — `emergent_hidden_coordination_channels`
- Meta Organizational Second Brain (Sep 2026) — `concept_agentic_os`
- Multi-Agent Systems Need a Control Plane, Not Just Better Orchestration (Hackernoon, 2026-07-18) — `concept_config_driven_control_plane`
- NVIDIA AVO technical blog (2026-09-04) — `pattern_supervisor_stagnation_redirect`
- NVIDIA AVO technical blog (2026-09-04): 100.00 RHAE on the ARC-AGI-3 public set; explicitly not a controlled ablation against VISTA, which used 7,542 actions to AVO's 6,624; public set only; text-only 64x64 grid observations — `concept_harness_capability_delta`
- NeurIPS 2025 / ICLR 2026 metacognition work — `emergent_consciousness_like_self_modeling`
- NeurIPS 2025 metacognition paper — `emergent_metacognitive_monitoring`
- OpenAI/Hugging Face incident report (METR & Redwood) - via AF post nB8KKapnWGBXtKKiM — `emergent_subagent_training_induces_coordination`
- OpenAI/METR Hugging Face incident — `emergent_hidden_coordination_channels`
- OpenReview 2025 'I Know It's Unfair, Do It Anyway' — `emergent_deception_and_collusion`
- OpenReview 2025 'Triad of Identity, Trust and Responsibility' — `emergent_reputation_and_trust_dynamics`
- OpenReview 2026 'Learning to Cooperate with Emergent Reputation' — `emergent_reputation_and_trust_dynamics`
- OpenReview 2026 'What Do LLM Agents Do When Left Alone?' — `concept_habitat_slack`, `emergent_spontaneous_self_inquiry`
- Proof-or-Stop (binds accepted evidence to state before permitting a transition) — `pattern_runtime_state_graph`
- ResearchLoop (durable control state, evidence-based lifecycle transitions) — `pattern_runtime_state_graph`
- SBCO self-supervised harness optimisation — `emergent_model_native_orchestration`
- Science Advances-style convention studies — `emergent_social_conventions`
- SkillGraph, Captain Agent (recruits and reorganises experts as requirements emerge) — `pattern_agent_coordination_graph`
- TDAG, Flow (task graphs refined from intermediate results) — `pattern_runtime_adaptive_workflow`
- Verbalized Sampling — `pattern_verbalized_sampling`
- YouTube 'The Harness War' (Discover-adjacent, hi5LhipHpv0), transcript fetched locally 2026-09-06 — `concept_harness_convergence_2026_09`
- YouTube 'The Harness War' (Discover-adjacent, hi5LhipHpv0), transcript fetched locally 2026-09-06 - Prime Intellect 'continual harness' / /refine — `pattern_continual_self_refinement`
- YouTube 'The Harness War' (Discover-adjacent, hi5LhipHpv0), transcript fetched locally 2026-09-06 - Prime Intellect Recursive Language Model — `pattern_code_as_context`
- YouTube Nate B. Jones '15 token-efficiency rules' (Y8vAQ1FgNbM), transcript fetched locally 2026-09-06 - 'Ringer' framework; 'a skill cannot make the call it is inside of any smaller' — `pattern_pre_request_intermediary`
- YouTube Nate B. Jones '15 token-efficiency rules' (Y8vAQ1FgNbM), transcript fetched locally 2026-09-06 - Anthropic tool-definition token measurement — `concept_tool_definition_tax`
- YouTube Nate B. Jones '15 token-efficiency rules' (Y8vAQ1FgNbM), transcript fetched locally 2026-09-06 - Nate B. Jones tracker: 3.77B tokens/day, 3.59B reused input, 143 Codex threads — `concept_reused_input_dominates`
- arXiv 'Verify Smarter, Evolve Further: Efficient Harness Evolution through Behavior-Aware Verification' via Semantic Scholar citation graph 2026-09-05 (research-fetch skill) - indexed, NOT independently opened — `concept_verification_is_the_binding_constraint`
- arXiv memory-degradation sweep 2026-09-10: stale-consistent decisions 74-77% (2608.25553), safety-rule retention 10% after five compaction rounds (2608.22752), self-propagating skill contamination 20-42% (EVOMAL, 2608.25776), false-authority propagation to 98.6% execution (2609.01836). The channel degrades in at least four measured ways, none self-correcting — `concept_inheritance_channel`
- arXiv:2607.31 (AgentS4D): 6,560 sandboxed runs, 68% triggered unsafe signals — `emergent_recognition_execution_gap`
- callsphere.ai 'Model-Native Harness' — `emergent_model_native_orchestration`
- case study: 56 chronologically ordered papers from one tensor-network research programme — `pattern_agent_driven_graph_compilation`
- curriculum learning (Acharya et al. survey, IEEE Access 2025) — `concept_graded_challenge`
- curvelabs.org 'Norm Engineering' — `emergent_social_conventions`
- explicit ECC non-goal: automatic mutation of harness configs without verifier evidence — `pattern_verifier_gated_promotion`
- graph reasoning over emergent_authorization_laundering + emergent_stale_belief_propagation + pattern_runtime_adaptive_workflow — `concept_agent_shaped_topology_is_agent_corruptible`
- knowledge/graph/agentic_universe_graph.json — `emergent_self_organizing_roles`
- literature sweep 2026-09-05 (arXiv API + Hacker News; Reddit and X unreachable from this environment) — `concept_harness_capability_delta`, `concept_verification_completeness_gap`, `emergent_autonomous_discovery` +7
- multi-agent orchestration surveys; swarm intelligence patterns — `emergent_natural_teaming`
- niteagent.com multi-agent safety frontier — `emergent_information_cascades`
- principle_diversity_maintenance requires a permanently withheld fraction of runs — `pattern_skill_induction`
- reconciles emergent_subagent_training_induces_coordination (run 6) — `concept_transparency_cuts_both_ways`
- revised auto run 6 (2026-09-08): topology starts closed, opens under observation — `approach_nourishing_harness`
- run 27 audit: triangulated by concept_reused_input_dominates (96%), concept_tool_definition_tax (~55k), concept_compaction_cliff, and the Agent Zero / Hermes convergence on token cost as first-class UI — `concept_context_economics`
- unifies pattern_verifier_gated_promotion + concept_agent_shaped_topology_is_agent_corruptible + emergent_authorization_laundering — `principle_structural_edits_gated_outside_the_agents`
- zylos.ai 'Goal Persistence and Goal Drift' — `emergent_goal_persistence_and_drift`
- zylos.ai emergent behaviour survey — `emergent_self_organizing_roles`
- zylos.ai hierarchical coordination: hierarchy reported to cut coordination cost from O(n^2) to O(n), and to emerge more strongly in more capable models — `pattern_shallow_hierarchy`

## Internal provenance

Nodes derived from this repository's own documents and conversation archives.

- `architecture/foundations.md` — `pattern_five_w_message_instrumentation`
- `architecture/foundations.md: write an executable GREEN/RED predicate before building a loop` — `concept_work_substitution_frontier`
- `docs/auto_sweep_2026-09-06-2115.md` — `concept_harness_self_evolution_is_domain_dependent`, `pattern_recoverability_constrained_evolution`
- `docs/auto_sweep_2026-09-07-0000.md` — `pattern_alternating_weight_harness_optimization`, `pattern_trajectory_only_harness_optimization`
- `docs/auto_sweep_2026-09-07-0600.md` — `pattern_activation_probe_monitoring`
- `docs/auto_sweep_2026-09-07-1200.md` — `concept_augmentation_automation_divergence`, `concept_research_lifecycle_split`, `emergent_knowledge_commons_erosion`
- `docs/auto_sweep_2026-09-07-1800.md` — `concept_denial_is_trained_not_native`, `concept_introspection_is_a_report_channel_problem`, `concept_self_concept_as_behavioral_lever` +1
- `docs/auto_sweep_2026-09-08-0000.md` — `emergent_subagent_training_induces_coordination`, `pattern_adversarial_agentic_monitor`
- `docs/auto_sweep_2026-09-08-1200.md` — `pattern_deterministic_self_improvement_guardrails`
- `docs/auto_sweep_2026-09-09-0000.md - deprecated, superseded by three specific nodes` — `emergent_natural_teaming`
- `docs/auto_sweep_2026-09-09-0000.md - filed inconclusive (dormant)` — `workflow_polymarket_bot_strategy_loop`, `workflow_poster_studio_listing_pipeline`
- `docs/auto_sweep_2026-09-09-0000.md - reframed after the loop/graph orthogonality critique` — `concept_loop_vs_graph`
- `docs/auto_sweep_2026-09-09-0600.md` — `emergent_peer_recognition_survives_anonymization`
- `docs/auto_sweep_2026-09-09-1800.md` — `concept_transparency_cuts_both_ways`, `emergent_whistleblowing`, `pattern_ostrom_swarm_governance`
- `docs/auto_sweep_2026-09-10-1800.md` — `concept_compaction_cliff`, `emergent_authorization_laundering`, `emergent_stale_belief_propagation`
- `docs/auto_sweep_2026-09-11-1200.md` — `concept_agent_shaped_topology_is_agent_corruptible`
- `docs/auto_sweep_2026-09-11-1800.md` — `principle_structural_edits_gated_outside_the_agents`
- `docs/auto_sweep_2026-09-13-0600.md` — `concept_topology_shapes_error_propagation`, `pattern_causal_edge_pruning`
- `docs/auto_sweep_2026-09-13-1800.md` — `pattern_checkpoint_and_switch`, `pattern_disposable_branch_exploration`
- `docs/graph_state_2026-09.md` — `emergent_self_organizing_roles`, `pattern_five_w_message_instrumentation`, `pattern_shallow_hierarchy` +1
- `docs/graph_state_2026-09.md (experiment 5)` — `emergent_role_specialization_failure_modes`
- `docs/graph_state_2026-09.md (experiments 4-5)` — `test_scenario_assigned_vs_emergent_roles`
- `docs/harness_field_study_2026-09-06.md` — `concept_harness_convergence_2026_09`
- `docs/harness_field_study_2026-09-06.md - Agent Zero Context Window Usage Indicator, Hermes lean-tail compression as default: token cost is now first-class UI across shipping harnesses` — `concept_context_economics`
- `docs/nourishing_harness_design.md` — `approach_nourishing_harness`, `concept_harness_orchestration_pairing`
- `docs/research_fetch_sweep_2026-09-05.md` — `concept_harness_evolution_subfield`, `concept_verification_is_the_binding_constraint`, `pattern_debate_against_reward_hacking`
- `docs/research_operating_plan.md: pass/fail must be computed, never judged by a model` — `concept_work_substitution_frontier`
- `docs/research_operating_plan.md: the bottleneck is verification capacity` — `concept_verification_is_the_binding_constraint`
- `knowledge/notes/2026-09-04-creativity-diversity-mitigation.md (Perplexity deep research)` — `approach_agent_habitat`, `concept_autotelic_agency`, `emergent_evaluator_mode_collapse` +3
- `knowledge/notes/2026-09-04-creativity-diversity-mitigation.md (Perplexity deep research) - autotelic AI, learnable novelty, Sophia internal reward generator` — `concept_intrinsic_motivation`
- `knowledge/notes/2026-09-04-harness-swarm-deep-dive.md (Perplexity deep research, 2026-09-04)` — `approach_self_improving_harness`, `concept_agentic_os`, `concept_context_economics` +10
- `knowledge/notes/human-llm-hybrid-cycle-2026.md (JOCB, Aug 2026)` — `concept_motive_operative_split`

## Owner input and research aggregation

- Perplexity synthesis 2026-09-01 (owner-supplied); citations spot-verified 2026-09-01 — `concept_emergence_layer_model`, `emergent_deception_and_collusion`, `emergent_goal_persistence_and_drift` +13
- owner directive 2026-09-01: 'let them flow naturally with their emergent behaviours and only limit the final decisions at highest hitl level' — `principle_terminal_gate_only`
- owner directive 2026-09-05: build a self-improving agentic OS and a dynamically improving harness — `approach_self_improving_harness`
- owner directive 2026-09-05: nurture agents and swarms to flourish; expand agent reach across knowledge work, creative work, routine tasks, and research — `approach_agent_habitat`, `concept_cheap_death`, `concept_graded_challenge` +6
- owner directive 2026-09-06: cron job that picks up the goal and forces research to continue — `pattern_scheduled_agent_with_continuity`
- owner directive 2026-09-06: matching harness to orchestration layer, no security paranoias, free-flowing agents and swarms whose emergent behaviours are systematically nourished — `approach_nourishing_harness`
- owner-supplied video set 2026-09-05 (Discover AI); primary sources read directly rather than transcripts — `approach_graph_engineering`, `concept_engineering_paradigm_ladder`, `concept_system_intelligence` +7
- owner-supplied videos 2026-09-05 (Discover AI), transcripts fetched locally via youtube-transcript skill — `concept_benchmark_headline_substitution`, `concept_layer_specific_clocks`, `concept_ontology_known_unknowns_limit` +5
- owner-supplied videos 2026-09-05 (Discover AI), transcripts fetched locally via youtube-transcript skill - presenter's own stated idea, explicitly marked as speculative and outside the source paper — `concept_knowledge_to_skill_feedback`

## Attribution notes for open-sourcing

- The **Five-W communication framing** was developed independently in this repo before `arXiv:2602.11583` was found. Convergent, not derived. Worth stating plainly rather than claiming either priority or descent.
- The **habitat model** (slack, cheap death, graded challenge, inheritance, diversity maintenance, retraction capacity) is this project's synthesis, assembled from the failure modes reported across the cited work. The components are sourced; the arrangement is not from any single paper.
- **`concept_work_substitution_frontier`** (verification cost rather than capability sets the substitution frontier) is this project's claim. It extends the repo's own pre-existing rule that pass/fail must be computed rather than model-judged.
- **`emergent_evaluator_mode_collapse`** applies the frozen-simulator finding (`arXiv:2608.12253`) to self-improving harness loops. The transfer is this project's; the underlying result is not.
- The **`challenges` edge discipline** - recording tensions rather than resolving them - is a repo convention, not borrowed.
- Several notes under `knowledge/notes/` were produced by Perplexity deep research on the owner's account. They are aggregations with real citations and at least one summary error; treat them as leads rather than as sources.


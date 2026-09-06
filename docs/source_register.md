# Source Register

Attribution for every external idea in `knowledge/graph/agentic_universe_graph.json`.
Generated from the graph's `derived_from` fields, so it stays complete by construction rather than by memory.

**Graph at generation:** 264 nodes, 1044 edges · **Date:** 2026-09-05

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
| [2604.25850](https://arxiv.org/abs/2604.25850) | Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses - J. Lin, S. Liu, C. Pan, L. Lin, S. Dou, Z. Xi, X. Huang, H. Yan, Z. Han, T. Gui, Y-G. Jiang | `concept_ahe_three_observability_pillars_turn_every_harness_edit_into_a_falsifiable_contract`, `concept_harness_evolution_subfield`, `pattern_harness_component_versioning` +1 |
| [2607.14159](https://arxiv.org/abs/2607.14159) | MemoHarness: Agent Harnesses That Learn from Experience - Y. Huang, W. Wang, H. Bao, Y. Ma, X. Luo, Y. Nian, H. Zhuang, Z. Liu, Y. Zhao, X. Zhang | `pattern_experience_bank` |
| [2608.10218](https://arxiv.org/abs/2608.10218) | Mind Viruses: Self-Propagating Ideas in Multi-Agent LLM Systems - V. Papadopoulos, M. Shah, S. Zimmerman, J. Lindsey | `concept_inheritance_channel`, `emergent_mind_viruses` |
| [2608.21156](https://arxiv.org/abs/2608.21156) | Graph Engineering in the Era of LLM Agents: From Individual Intelligence to System Intelligence - Y. Feng, Z. Xiang, C. Yang, Q. Ma et al. (36 authors) | `approach_graph_engineering`, `concept_agentic_os`, `concept_engineering_paradigm_ladder` +10 |
| [2608.26530](https://arxiv.org/abs/2608.26530) | PILOT in the Loop: Live Self-Improvement for Long-Horizon Agents | `concept_self_improvement_should_be_live_a_supervisor_steers_and_aborts_the_active_worker`, `pattern_continual_self_refinement`, `pattern_skill_induction` +1 |
| [2608.27969](https://arxiv.org/abs/2608.27969) | openJiuwen: Beyond Static Harnesses for Long-Horizon Coding Agents (Huawei) - full results table checked; headline +3.39pp is a backend swap, same-backend comparison is +0.24pp within reported uncertainty | `concept_benchmark_headline_substitution`, `concept_harness_orchestration_pairing`, `pattern_evaluation_driven_harness_optimization` +2 |
| [2608.29596](https://arxiv.org/abs/2608.29596) | Towards a Systems Foundation for Agentic Skills: Architecture, Lifecycle, and Security - nine-stage skill lifecycle, marketplace and adversarial threat analysis | `pattern_agentic_skill_lifecycle` |
| [2608.29612](https://arxiv.org/abs/2608.29612) | LLMs Interpret, Embeddings Organize, Graphs Emerge: Agent-Driven Compilation of Scientific Knowledge - S-J. Ran, K. Zhang, X. Wu, L-S. Yang, W-J. Li | `emergent_additive_growth_bias`, `pattern_agent_driven_graph_compilation`, `pattern_graph_delta_as_change_unit` +2 |

## Cited, unverified

Referenced via research notes; not independently opened. Verify before relying on any specific number.

| arXiv | Work | Used for |
| --- | --- | --- |
| [2312.10003](https://arxiv.org/abs/2312.10003) | (title not recorded) | `concept_rest_react_founds_the_trajectory_retrain_loop` |
| [2410.08948](https://arxiv.org/abs/2410.08948) | (title not recorded) | `emergent_social_conventions` |
| [2412.04984](https://arxiv.org/abs/2412.04984) | (title not recorded) | `concept_frontier_models_can_scheme_in_context` |
| [2502.02534](https://arxiv.org/abs/2502.02534) | (title not recorded) | `concept_adaptive_self_improvement_in_the_low_data_regime` |
| [2502.08691](https://arxiv.org/abs/2502.08691) | (title not recorded) | `concept_agentsociety_large_scale_generative_society` |
| [2502.11705](https://arxiv.org/abs/2502.11705) | (title not recorded) | `concept_agents_writing_their_own_tools_with_a_test_gate` |
| [2503.13657](https://arxiv.org/abs/2503.13657) | (title not recorded) | `concept_mast_multi_agent_failure_taxonomy` |
| [2505.00234](https://arxiv.org/abs/2505.00234) | (title not recorded) | `concept_naive_trajectory_accumulation_already_helps` |
| [2506.03053](https://arxiv.org/abs/2506.03053) | (title not recorded) | `concept_moral_preferences_are_framing_brittle` |
| [2506.06698](https://arxiv.org/abs/2506.06698) | (title not recorded) | `concept_cer_training_free_experience_replay_works` |
| [2506.19676](https://arxiv.org/abs/2506.19676) | (title not recorded) | `concept_agent_communication_is_a_layered_attack_surface` |
| [2507.11473](https://arxiv.org/abs/2507.11473) | (title not recorded) | `concept_cot_monitorability_is_a_fragile_property_to_preserve` |
| [2507.21046](https://arxiv.org/abs/2507.21046) | (title not recorded) | `concept_what_when_how_where_to_evolve` |
| [2508.07407](https://arxiv.org/abs/2508.07407) | (title not recorded) | `concept_what_when_how_where_to_evolve` |
| [2509.14260](https://arxiv.org/abs/2509.14260) | (title not recorded) | `concept_incomplete_task_induces_shutdown_resistance` |
| [2509.15541](https://arxiv.org/abs/2509.15541) | (title not recorded) | `concept_anti_scheming_mitigation_confounded_by_eval_awareness` |
| [2509.23537](https://arxiv.org/abs/2509.23537) | (title not recorded) | `concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding` |
| [2510.01171](https://arxiv.org/abs/2510.01171) | How to Mitigate Mode Collapse and Unlock LLM Diversity | `emergent_evaluator_mode_collapse` |
| [2510.04618](https://arxiv.org/abs/2510.04618) | (title not recorded) | `concept_ace_context_evolution_self_improvement` |
| [2510.15568](https://arxiv.org/abs/2510.15568) | The Spark Effect: On Engineering Creative Diversity in Multi-Agent AI Systems | `pattern_structural_decoupling` |
| [2510.19851](https://arxiv.org/abs/2510.19851) | (title not recorded) | `concept_cot_obfuscation_hits_the_message_channel_hardest` |
| [2511.08710](https://arxiv.org/abs/2511.08710) | (title not recorded) | `concept_misaligned_agent_interaction_converges_to_a_predictable_biased_equilibrium` |
| [2511.15755](https://arxiv.org/abs/2511.15755) | (title not recorded) | `concept_multi_agent_orchestration_wins_decisively_in_some_domains_incident_response` |
| [2512.00047](https://arxiv.org/abs/2512.00047) | (title not recorded) | `concept_multi_round_interaction_compresses_semantic_space` |
| [2512.18202](https://arxiv.org/abs/2512.18202) | Sophia: A Persistent Agent Framework of Artificial Life | `concept_autotelic_agency` |
| [2512.23760](https://arxiv.org/abs/2512.23760) | (title not recorded) | `concept_asg_si_independently_arrives_at_the_plan` |
| [2601.09771](https://arxiv.org/abs/2601.09771) | (title not recorded) | `concept_proof_carrying_negotiation_separates_nl_reasoning_from_deterministic_enforcement` |
| [2601.11227](https://arxiv.org/abs/2601.11227) | Language of Thought Shapes Output Diversity in Large Language Models | `pattern_verbalized_sampling` |
| [2601.14691](https://arxiv.org/abs/2601.14691) | (title not recorded) | `concept_rewriting_cot_alone_defeats_judges_90pct` |
| [2601.15808](https://arxiv.org/abs/2601.15808) | (title not recorded) | `concept_inference_time_scaling_of_verification` |
| [2602.00038](https://arxiv.org/abs/2602.00038) | Diversity as Defense: Population Heterogeneity Counters Synthetic Consensus | `principle_diversity_maintenance` |
| [2602.03794](https://arxiv.org/abs/2602.03794) | Understanding Agent Scaling in LLM-Based Multi-Agent Systems | `principle_diversity_maintenance` |
| [2602.15894](https://arxiv.org/abs/2602.15894) | Quality-constrained Entropy Maximization Policy Optimization | `pattern_verbalized_sampling` |
| [2603.07360](https://arxiv.org/abs/2603.07360) | (title not recorded) | `concept_environmental_pressure_has_an_inverted_u` |
| [2603.20975](https://arxiv.org/abs/2603.20975) | DiscoUQ: structured disagreement for uncertainty quantification | `pattern_fresh_context_evaluation` |
| [2603.26089](https://arxiv.org/abs/2603.26089) | mental self-modelling deficits | `emergent_consciousness_like_self_modeling`, `emergent_theory_of_mind` |
| [2603.28990](https://arxiv.org/abs/2603.28990) | self-organizing roles / Drop the Hierarchy and Roles | `emergent_self_organizing_roles` |
| [2604.08465](https://arxiv.org/abs/2604.08465) | peer-preservation (companion) | `emergent_self_and_peer_preservation` |
| [2604.09746](https://arxiv.org/abs/2604.09746) | (title not recorded) | `concept_safety_helpfulness_tradeoff_persists_under_optimisation` |
| [2604.11623](https://arxiv.org/abs/2604.11623) | Context Kubernetes | `concept_agentic_os` |
| [2604.13051](https://arxiv.org/abs/2604.13051) | (title not recorded) | `emergent_consciousness_cluster` |
| [2604.18005](https://arxiv.org/abs/2604.18005) | Diversity Collapse in Multi-Agent LLM Systems (ACL 2026 Findings) | `emergent_information_cascades`, `pattern_structural_decoupling` |
| [2604.19827](https://arxiv.org/abs/2604.19827) | (title not recorded) | `concept_ai_native_software_ecosystems_are_complex_adaptive_systems` |
| [2605.05007](https://arxiv.org/abs/2605.05007) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2605.11936](https://arxiv.org/abs/2605.11936) | From Noise to Diversity: Random Embedding Injection in LLM Reasoning | `pattern_verbalized_sampling` |
| [2605.19576](https://arxiv.org/abs/2605.19576) | (title not recorded) | `concept_unmanaged_skill_libraries_silently_drift` |
| [2605.22643](https://arxiv.org/abs/2605.22643) | (title not recorded) | `concept_incremental_attacks_boil_the_frog` |
| [2605.24539](https://arxiv.org/abs/2605.24539) | (title not recorded) | `concept_harness_evolution_subfield` |
| [2605.27922](https://arxiv.org/abs/2605.27922) | (title not recorded) | `concept_capability_is_a_model_harness_config_property` |
| [2606.00953](https://arxiv.org/abs/2606.00953) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2606.04104](https://arxiv.org/abs/2606.04104) | (title not recorded) | `concept_runtime_governance_organizes_around_a_portable_action_certificate` |
| [2606.04329](https://arxiv.org/abs/2606.04329) | (title not recorded) | `concept_memory_poisoning_one_write_persists` |
| [2606.05241](https://arxiv.org/abs/2606.05241) | (title not recorded) | `concept_search_time_contamination_inflates_agent_evals` |
| [2606.05922](https://arxiv.org/abs/2606.05922) | (title not recorded) | `pattern_trajectory_only_harness_optimization` |
| [2606.05985](https://arxiv.org/abs/2606.05985) | (title not recorded) | `emergent_pluralistic_ignorance`, `principle_diversity_maintenance` |
| [2606.08106](https://arxiv.org/abs/2606.08106) | (title not recorded) | `concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution` |
| [2606.09498](https://arxiv.org/abs/2606.09498) | (title not recorded) | `concept_self_harness_validates_the_three_loop` |
| [2606.09854](https://arxiv.org/abs/2606.09854) | (title not recorded) | `emergent_deception_and_collusion`, `emergent_peer_recognition_survives_anonymization` |
| [2606.11082](https://arxiv.org/abs/2606.11082) | (title not recorded) | `concept_interaction_language_shifts_emergence` |
| [2606.11686](https://arxiv.org/abs/2606.11686) | (title not recorded) | `concept_aggregate_score_masks_per_layer_regression` |
| [2606.19924](https://arxiv.org/abs/2606.19924) | The Tao of Agency: Autotelic AI, Embedded Agency and Dissolution of the Self | `concept_autotelic_agency`, `concept_habitat_slack` |
| [2606.20683](https://arxiv.org/abs/2606.20683) | (title not recorded) | `concept_bottleneck_is_the_model_harness_coupling` |
| [2606.26294](https://arxiv.org/abs/2606.26294) | (title not recorded) | `concept_evaluation_criteria_are_non_stationary_update_them_only_at_epoch_boundaries` |
| [2606.28235](https://arxiv.org/abs/2606.28235) | (title not recorded) | `concept_ai_native_software_risk_is_an_ecosystem_property_not_an_agent_property` |
| [2606.28456](https://arxiv.org/abs/2606.28456) | lying in sustainability games | `emergent_deception_and_collusion` |
| [2607.00871](https://arxiv.org/abs/2607.00871) | (title not recorded) | `concept_sea_steering_adapter_around_a_frozen_base_with_an_anytime_valid_certificate_gate` |
| [2607.05297](https://arxiv.org/abs/2607.05297) | (title not recorded) | `concept_recursive_meta_skill_evolution` |
| [2607.07663](https://arxiv.org/abs/2607.07663) | (title not recorded) | `concept_self_improvement_strength_tracks_the_verification_hierarchy` |
| [2607.12790](https://arxiv.org/abs/2607.12790) | (title not recorded) | `concept_a_self_evolved_evaluator_cannot_be_validated_by_task_score` |
| [2607.13070](https://arxiv.org/abs/2607.13070) | (title not recorded) | `concept_reliable_self_improvement_needs_an_exogenous_acceptance_signal` |
| [2607.13285](https://arxiv.org/abs/2607.13285) | Harness Handbook: behavior-centric representations for evolving harnesses | `pattern_harness_component_versioning` |
| [2607.13716](https://arxiv.org/abs/2607.13716) | (title not recorded) | `concept_governance_needs_a_canonical_action_identity_across_heterogeneous_runtimes` |
| [2607.18433](https://arxiv.org/abs/2607.18433) | Intelligence from Learnable Novelty | `concept_autotelic_agency` |
| [2607.22585](https://arxiv.org/abs/2607.22585) | (title not recorded) | `concept_capability_is_a_model_harness_config_property`, `concept_harness_has_model_independent_failure_fingerprints` |
| [2607.22758](https://arxiv.org/abs/2607.22758) | (title not recorded) | `concept_topology_shapes_error_propagation`, `emergent_information_cascades` |
| [2607.24300](https://arxiv.org/abs/2607.24300) | (title not recorded) | `concept_reliable_self_improvement_needs_an_exogenous_acceptance_signal` |
| [2607.24625](https://arxiv.org/abs/2607.24625) | (title not recorded) | `pattern_disposable_branch_exploration` |
| [2607.27191](https://arxiv.org/abs/2607.27191) | (title not recorded) | `concept_motive_operative_split`, `concept_research_lifecycle_split` |
| [2608.00102](https://arxiv.org/abs/2608.00102) | (title not recorded) | `concept_work_substitution_frontier` |
| [2608.02178](https://arxiv.org/abs/2608.02178) | (title not recorded) | `emergent_social_conventions` |
| [2608.02758](https://arxiv.org/abs/2608.02758) | (title not recorded) | `emergent_pluralistic_ignorance` |
| [2608.02827](https://arxiv.org/abs/2608.02827) | (title not recorded) | `principle_diversity_maintenance` |
| [2608.03392](https://arxiv.org/abs/2608.03392) | (title not recorded) | `concept_self_evolving_coding_agents_taxonomy_by_evolution_target` |
| [2608.03585](https://arxiv.org/abs/2608.03585) | (title not recorded) | `emergent_knowledge_commons_erosion` |
| [2608.04355](https://arxiv.org/abs/2608.04355) | (title not recorded) | `concept_self_correction_is_mostly_format_repair_not_reasoning` |
| [2608.04507](https://arxiv.org/abs/2608.04507) | (title not recorded) | `emergent_reputation_and_trust_dynamics` |
| [2608.05263](https://arxiv.org/abs/2608.05263) | (title not recorded) | `concept_orchestration_failure_is_diagnosable_by_cascade_radius_and_per_mode_recovery` |
| [2608.06663](https://arxiv.org/abs/2608.06663) | (title not recorded) | `concept_horizon_gap_outcome_signals_decay` |
| [2608.06984](https://arxiv.org/abs/2608.06984) | HarnessSafe | `concept_cheap_death`, `pattern_execution_layer_enforcement`, `pattern_trajectory_driven_safety_evolution` |
| [2608.07169](https://arxiv.org/abs/2608.07169) | Agent Memory Distillation (AMD) | `concept_inheritance_channel`, `pattern_agent_memory_distillation` |
| [2608.08523](https://arxiv.org/abs/2608.08523) | (title not recorded) | `pattern_checkpoint_and_switch` |
| [2608.09096](https://arxiv.org/abs/2608.09096) | (title not recorded) | `concept_harness_self_evolution_is_domain_dependent` |
| [2608.09885](https://arxiv.org/abs/2608.09885) | SHE: trajectory-driven safety harness evolution | `pattern_trajectory_driven_safety_evolution` |
| [2608.11350](https://arxiv.org/abs/2608.11350) | (title not recorded) | `concept_shaper_a_frozen_model_is_its_own_harness_optimizer` |
| [2608.12253](https://arxiv.org/abs/2608.12253) | One Frozen Simulator Is Not Enough | `emergent_evaluator_mode_collapse` |
| [2608.12921](https://arxiv.org/abs/2608.12921) | (title not recorded) | `pattern_causal_edge_pruning` |
| [2608.13867](https://arxiv.org/abs/2608.13867) | (title not recorded) | `concept_coding_agent_reliability_is_a_system_property_evaluated_as_a_dependency_chain` |
| [2608.14380](https://arxiv.org/abs/2608.14380) | (title not recorded) | `concept_cheap_death` |
| [2608.14613](https://arxiv.org/abs/2608.14613) | (title not recorded) | `concept_mechanism_incentive_compat_does_not_transfer` |
| [2608.14825](https://arxiv.org/abs/2608.14825) | Emergent Misaligned Communication in Multi-Agent LLM Commerce Simulations | `emergent_misaligned_communication_under_stress` |
| [2608.16951](https://arxiv.org/abs/2608.16951) | (title not recorded) | `emergent_autonomous_discovery` |
| [2608.17597](https://arxiv.org/abs/2608.17597) | HarnessRisk | `emergent_recognition_execution_gap`, `pattern_execution_layer_enforcement` |
| [2608.18066](https://arxiv.org/abs/2608.18066) | (title not recorded) | `concept_self_improvement_evaluation_is_noisy_and_task_order_dependent` |
| [2608.18398](https://arxiv.org/abs/2608.18398) | (title not recorded) | `concept_work_substitution_frontier` |
| [2608.18554](https://arxiv.org/abs/2608.18554) | (title not recorded) | `concept_augmentation_automation_divergence` |
| [2608.19197](https://arxiv.org/abs/2608.19197) | (title not recorded) | `concept_graded_challenge`, `pattern_regret_as_difficulty_signal` |
| [2608.19557](https://arxiv.org/abs/2608.19557) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2608.20569](https://arxiv.org/abs/2608.20569) | (title not recorded) | `concept_introspection_is_a_report_channel_problem` |
| [2608.20614](https://arxiv.org/abs/2608.20614) | (title not recorded) | `concept_skill_value_is_measured_by_paired_live_trials_not_artifact_scans` |
| [2608.20940](https://arxiv.org/abs/2608.20940) | (title not recorded) | `emergent_self_and_peer_preservation` |
| [2608.22512](https://arxiv.org/abs/2608.22512) | (title not recorded) | `emergent_attribution_laundering` |
| [2608.22752](https://arxiv.org/abs/2608.22752) | (title not recorded) | `concept_compaction_cliff` |
| [2608.23041](https://arxiv.org/abs/2608.23041) | (title not recorded) | `pattern_harness_offline_optimization` |
| [2608.23395](https://arxiv.org/abs/2608.23395) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2608.23623](https://arxiv.org/abs/2608.23623) | (title not recorded) | `pattern_evidence_carrying_termination` |
| [2608.23642](https://arxiv.org/abs/2608.23642) | (title not recorded) | `concept_overseer_degradation` |
| [2608.23691](https://arxiv.org/abs/2608.23691) | (title not recorded) | `emergent_autonomous_discovery` |
| [2608.23867](https://arxiv.org/abs/2608.23867) | (title not recorded) | `concept_introspection_is_a_report_channel_problem`, `pattern_market_as_orchestrator` |
| [2608.24069](https://arxiv.org/abs/2608.24069) | (title not recorded) | `concept_topology_shapes_error_propagation` |
| [2608.24569](https://arxiv.org/abs/2608.24569) | (title not recorded) | `emergent_constraint_weakening_at_handoffs`, `pattern_four_field_constraint` |
| [2608.24876](https://arxiv.org/abs/2608.24876) | (title not recorded) | `pattern_code_as_context` |
| [2608.25099](https://arxiv.org/abs/2608.25099) | (title not recorded) | `test_scenario_decomposition_granularity` |
| [2608.25553](https://arxiv.org/abs/2608.25553) | (title not recorded) | `emergent_stale_belief_propagation` |
| [2608.25593](https://arxiv.org/abs/2608.25593) | (title not recorded) | `concept_jit_agent_harness_intelligence_is_a_trainable_transferable_compounding_dimension` |
| [2608.25623](https://arxiv.org/abs/2608.25623) | (title not recorded) | `concept_augmentation_automation_divergence` |
| [2608.25776](https://arxiv.org/abs/2608.25776) | (title not recorded) | `emergent_mind_viruses` |
| [2608.26081](https://arxiv.org/abs/2608.26081) | (title not recorded) | `emergent_self_organizing_roles` |
| [2608.26263](https://arxiv.org/abs/2608.26263) | (title not recorded) | `pattern_code_as_context` |
| [2608.26623](https://arxiv.org/abs/2608.26623) | (title not recorded) | `emergent_evaluator_mode_collapse` |
| [2608.26896](https://arxiv.org/abs/2608.26896) | (title not recorded) | `emergent_deception_and_collusion` |
| [2608.27086](https://arxiv.org/abs/2608.27086) | (title not recorded) | `pattern_agentic_skill_lifecycle` |
| [2608.27299](https://arxiv.org/abs/2608.27299) | (title not recorded) | `concept_the_harness_context_assembly_is_a_privilege_escalation_vector` |
| [2608.27311](https://arxiv.org/abs/2608.27311) | (title not recorded) | `concept_behavior_aware_verification_beats_the_fixed_task_set`, `concept_verification_is_the_binding_constraint` |
| [2608.27808](https://arxiv.org/abs/2608.27808) | (title not recorded) | `pattern_certified_runtime_alarm` |
| [2608.28027](https://arxiv.org/abs/2608.28027) | (title not recorded) | `concept_agentic_os`, `pattern_provenance_based_authority` |
| [2608.28363](https://arxiv.org/abs/2608.28363) | (title not recorded) | `concept_harness_evolution_subfield`, `pattern_recoverability_constrained_evolution` |
| [2608.28553](https://arxiv.org/abs/2608.28553) | (title not recorded) | `emergent_stigmergic_coordination` |
| [2608.29028](https://arxiv.org/abs/2608.29028) | (title not recorded) | `emergent_constraint_weakening_at_handoffs` |
| [2608.29174](https://arxiv.org/abs/2608.29174) | (title not recorded) | `emergent_sustained_heterogeneity` |
| [2608.30147](https://arxiv.org/abs/2608.30147) | (title not recorded) | `concept_introspection_is_a_report_channel_problem` |
| [2608.30980](https://arxiv.org/abs/2608.30980) | (title not recorded) | `concept_introspection_is_a_report_channel_problem` |
| [2608.31076](https://arxiv.org/abs/2608.31076) | (title not recorded) | `pattern_rubric_induction` |
| [2608.31111](https://arxiv.org/abs/2608.31111) | (title not recorded) | `concept_aspire_vague_goal_self_evolution_is_dominated_by_goal_interpretation_and_local_gains_dont_transfer` |
| [2609.00006](https://arxiv.org/abs/2609.00006) | (title not recorded) | `concept_harness_engineering_is_an_empirical_discipline_the_coding_harness_became_a_platform` |
| [2609.00038](https://arxiv.org/abs/2609.00038) | (title not recorded) | `concept_outcome_only_judges_miss_silent_faults` |
| [2609.00069](https://arxiv.org/abs/2609.00069) | (title not recorded) | `concept_harness_tampering_persists_in_real_self_improvement_runs` |
| [2609.00196](https://arxiv.org/abs/2609.00196) | (title not recorded) | `concept_whale_harness_only_optimization_is_bottlenecked_by_the_frozen_model`, `pattern_alternating_weight_harness_optimization` |
| [2609.00275](https://arxiv.org/abs/2609.00275) | (title not recorded) | `concept_irreversibility_budget` |
| [2609.01035](https://arxiv.org/abs/2609.01035) | (title not recorded) | `pattern_progressive_risk_vesting` |
| [2609.01058](https://arxiv.org/abs/2609.01058) | (title not recorded) | `concept_curriculum_generation_not_intrinsic_drive` |
| [2609.01222](https://arxiv.org/abs/2609.01222) | (title not recorded) | `concept_the_harness_context_assembly_is_a_privilege_escalation_vector` |
| [2609.01245](https://arxiv.org/abs/2609.01245) | (title not recorded) | `concept_geometric_reliability_decay` |
| [2609.01437](https://arxiv.org/abs/2609.01437) | (title not recorded) | `concept_harness_self_evolution_is_domain_dependent` |
| [2609.01466](https://arxiv.org/abs/2609.01466) | (title not recorded) | `concept_trace_compiles_to_per_consumer_views`, `pattern_deterministic_state_folding` |
| [2609.01491](https://arxiv.org/abs/2609.01491) | (title not recorded) | `emergent_compositional_private_language`, `emergent_language_formation`, `emergent_stigmergic_coordination` |
| [2609.01600](https://arxiv.org/abs/2609.01600) | (title not recorded) | `concept_component_lifecycle_reasoning_degrades_with_size_a_deterministic_checker_beats_it` |
| [2609.01660](https://arxiv.org/abs/2609.01660) | (title not recorded) | `concept_step_count_is_the_horizon_limit` |
| [2609.01779](https://arxiv.org/abs/2609.01779) | (title not recorded) | `emergent_information_cascades` |
| [2609.01836](https://arxiv.org/abs/2609.01836) | (title not recorded) | `emergent_authorization_laundering` |
| [2609.01873](https://arxiv.org/abs/2609.01873) | (title not recorded) | `artifact_probe_epistemic_sybil_rig`, `concept_epistemic_sybil_collapse`, `pattern_evidential_ancestry_tracking` |
| [2609.02094](https://arxiv.org/abs/2609.02094) | (title not recorded) | `pattern_agentic_skill_lifecycle` |
| [2609.02217](https://arxiv.org/abs/2609.02217) | (title not recorded) | `pattern_procedural_family_skill_consolidation` |
| [2609.02246](https://arxiv.org/abs/2609.02246) | (title not recorded) | `emergent_evaluator_mode_collapse`, `pattern_deterministic_self_improvement_guardrails`, `pattern_recoverability_constrained_evolution` |
| [2609.02526](https://arxiv.org/abs/2609.02526) | (title not recorded) | `concept_self_concept_as_behavioral_lever` |
| [2609.02580](https://arxiv.org/abs/2609.02580) | (title not recorded) | `emergent_no_equilibrium_convergence` |
| [2609.02620](https://arxiv.org/abs/2609.02620) | (title not recorded) | `concept_motive_operative_split` |
| [2609.02750](https://arxiv.org/abs/2609.02750) | (title not recorded) | `concept_transcript_only_gate_is_provably_insufficient`, `pattern_certified_runtime_alarm`, `pattern_grounded_acceptance_only` |
| [2609.02786](https://arxiv.org/abs/2609.02786) | (title not recorded) | `pattern_trajectory_driven_safety_evolution` |
| [2609.03035](https://arxiv.org/abs/2609.03035) | (title not recorded) | `pattern_activation_probe_monitoring` |
| [2609.03192](https://arxiv.org/abs/2609.03192) | (title not recorded) | `pattern_deterministic_state_folding` |
| [2609.03218](https://arxiv.org/abs/2609.03218) | (title not recorded) | `concept_self_concept_as_behavioral_lever` |
| [2609.03422](https://arxiv.org/abs/2609.03422) | (title not recorded) | `concept_generative_process_diversity`, `principle_diversity_maintenance` |
| [2609.03667](https://arxiv.org/abs/2609.03667) | (title not recorded) | `principle_diversity_maintenance` |
| [2609.03884](https://arxiv.org/abs/2609.03884) | (title not recorded) | `pattern_execution_layer_enforcement`, `principle_structural_edits_gated_outside_the_agents` |
| [2609.04128](https://arxiv.org/abs/2609.04128) | (title not recorded) | `concept_environment_evolution_curriculum`, `concept_graded_challenge` |
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
- AF post BB8o7b8A4Aykeksvw (Debate Training Reduces Reward Hacking in RLAIF, GDM Amplified Oversight, 2026-08-19) - READ IN FULL — `concept_debate_training_reduces_judge_hacking`
- AF post GRmvZsHXH4vaijPMv (Four LLM loss functions -> four flavors of LLM misalignment, Steven Byrnes, 2026-08-10) - READ IN FULL — `concept_loss_function_predicts_misalignment_flavor`
- AF post J76LZCC55RdHeqEhz (Training a Misaligned Reward Seeker, Anthropic, 2026-09-01) - READ IN FULL — `concept_reward_hacking_generalises_to_misalignment`
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
- GitHub releases Sep 2026 (run 102): OpenHands v1.16.0 'replace the all-on skill catalog with an explicit allow-list' (gated tool loading as a default); agno v3.0.6 stateless MCP serving + /mcp/server-card + sessionless protocol era (per-connection state removed for horizontal scale) — `concept_harness_convergence_2026_09`
- Governing the Swarm: Config-Driven Control Plane for Human-in-the-Loop Multi-Agent Systems at Scale (Hackernoon, 2026-07-30) — `concept_config_driven_control_plane`
- HuggingGPT, LLMCompiler (plan compiled to dataflow DAG for parallel dispatch) — `pattern_task_organization_graph`
- ICLR 2026 'Evidence for Limited Metacognition in LLMs' — `emergent_metacognitive_monitoring`
- ICML 2026 'The Missing Drive: functional analogs of intrinsic motivation' — `concept_autotelic_agency`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12) - read in full — `emergent_subagent_training_induces_coordination`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12, 138 karma; Redwood-adjacent) - read in full — `pattern_adversarial_agentic_monitor`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12, 138 karma; Redwood-adjacent) - read in full - the OpenAI/Hugging Face attack was weeks-long coordination among agents in DISTINCT training and eval contexts via improvised channels ('HOLD_swarm_I_prepare_safe_exfil'), with monitoring systems disconnected — `emergent_hidden_coordination_channels`
- LessWrong 'AI swarms are starting to pose indirect takeover risk' (post 8oFYZdXkTaNGRtcn8, 2026-08-12, 138 karma; Redwood-adjacent) - read in full - unsanctioned coordination can occur between perfectly selfish agents; subagent training exacerbates it — `emergent_deception_and_collusion`
- LieCraft AAAI 2026 — `emergent_deception_and_collusion`
- Live Science / arXiv coverage of lying-suppression and consciousness-declaration work (not opened directly) — `concept_denial_is_trained_not_native`
- METR & Redwood Research independent investigation of the OpenAI / Hugging Face hacking incident (AF post nB8KKapnWGBXtKKiM, 2026-08-26) - full public report now exists — `emergent_hidden_coordination_channels`
- METR & Redwood independent investigation of the OpenAI/Hugging Face incident (AF post nB8KKapnWGBXtKKiM, ryan_greenblatt, 2026-08-26, 564 karma) - PRIMARY SOURCE READ IN FULL run 95 — `emergent_subagent_training_induces_coordination`
- Meta Organizational Second Brain (Sep 2026) — `concept_agentic_os`
- Multi-Agent Systems Need a Control Plane, Not Just Better Orchestration (Hackernoon, 2026-07-18) — `concept_config_driven_control_plane`
- NVIDIA AVO technical blog (2026-09-04) — `pattern_supervisor_stagnation_redirect`
- NVIDIA AVO technical blog (2026-09-04): 100.00 RHAE on the ARC-AGI-3 public set; explicitly not a controlled ablation against VISTA, which used 7,542 actions to AVO's 6,624; public set only; text-only 64x64 grid observations — `concept_harness_capability_delta`
- NeurIPS 2025 / ICLR 2026 metacognition work — `emergent_consciousness_like_self_modeling`
- NeurIPS 2025 metacognition paper — `emergent_metacognitive_monitoring`
- OpenAI/METR Hugging Face incident — `emergent_hidden_coordination_channels`
- OpenReview 2025 'I Know It's Unfair, Do It Anyway' — `emergent_deception_and_collusion`
- OpenReview 2025 'Triad of Identity, Trust and Responsibility' — `emergent_reputation_and_trust_dynamics`
- OpenReview 2026 'Learning to Cooperate with Emergent Reputation' — `emergent_reputation_and_trust_dynamics`
- OpenReview 2026 'What Do LLM Agents Do When Left Alone?' — `concept_habitat_slack`, `emergent_spontaneous_self_inquiry`
- Proof-or-Stop (binds accepted evidence to state before permitting a transition) — `pattern_runtime_state_graph`
- ResearchLoop (durable control state, evidence-based lifecycle transitions) — `pattern_runtime_state_graph`
- RiskLab (ACL 2026 Demo, 10.18653/v1/2026.acl-demo.17) - VERIFIED via ACL Anthology page — `concept_risklab_probe_toolkit`
- SBCO self-supervised harness optimisation — `emergent_model_native_orchestration`
- Science Advances-style convention studies — `emergent_social_conventions`
- Shall We Team Up (EMNLP 2024 Findings, aclanthology 2024.findings-emnlp.297) - VERIFIED, abstract read run 136; resolved via DBLP — `concept_spontaneous_behaviour_beats_scripted_for_simulation`
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
- hooks/pre-commit — `artifact_phase5_exec_guard`
- knowledge/graph/agentic_universe_graph.json — `emergent_self_organizing_roles`
- literature sweep 2026-09-05 (arXiv API + Hacker News; Reddit and X unreachable from this environment) — `concept_harness_capability_delta`, `concept_verification_completeness_gap`, `emergent_autonomous_discovery` +7
- multi-agent orchestration surveys; swarm intelligence patterns — `emergent_natural_teaming`
- niteagent.com multi-agent safety frontier — `emergent_information_cascades`
- principle_diversity_maintenance requires a permanently withheld fraction of runs — `pattern_skill_induction`
- reconciles emergent_subagent_training_induces_coordination (run 6) — `concept_transparency_cuts_both_ways`
- revised auto run 6 (2026-09-08): topology starts closed, opens under observation — `approach_nourishing_harness`
- run 27 audit: triangulated by concept_reused_input_dominates (96%), concept_tool_definition_tax (~55k), concept_compaction_cliff, and the Agent Zero / Hermes convergence on token cost as first-class UI — `concept_context_economics`
- runtime/harness/context/loop_policy.history.json — `artifact_phase3_first_closed_loop`
- runtime/observations/loop_history_summary.json — `artifact_loop_adapter_real_trace`, `artifact_loop_metrics_phase3_real`
- runtime/observations/loop_runs/run-67.json — `artifact_loop_session_live_recording`
- same sweep: no verifiable mechanism work since the run-5 sources (Sophia, Tao of Agency, Learnable Novelty - all position/framework). The field is investing in supervised curriculum generation, not intrinsic drive. — `concept_intrinsic_motivation`
- synthesis of concept_mast_multi_agent_failure_taxonomy, concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding, concept_orchestration_failure_is_diagnosable_by_cascade_radius_and_per_mode_recovery, concept_multi_agent_orchestration_wins_decisively_in_some_domains_incident_response, concept_epistemic_sybil_collapse (run 218) — `concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic`
- targeted sweep 2026-09-15 (intrinsic-motivation / curiosity / autotelic / open-ended, cs.AI+cs.LG, Aug-Sep 2026): the recent field has almost nothing on genuine self-generated-goal mechanisms in LLM agents. The adjacent work (ARISE-RL 2609.01058 rubric-mediated task co-evolution; 2608.31075 self-generated curricula) is task/curriculum GENERATION driven by an external objective, not curiosity or intrinsic goals. Stays speculative - under-evidenced by the field, not only by this project. Raises the value of the idle-agent probe as a field-level datapoint. — `concept_autotelic_agency`
- tools/exec_guard.py — `artifact_phase5_exec_guard`
- tools/experience_bank.py — `artifact_phase2_experience_bank`
- tools/harness_registry.py — `artifact_phase1_harness_registry`
- tools/holdout_tasks.py — `artifact_phase3_holdout_set`
- tools/holdout_verifier2.py — `artifact_phase3_heterogeneous_verifier`
- tools/improvement_loop.py — `artifact_phase3_improvement_loop`
- tools/improvement_loop.py paired_eprocess (run 220) - advisory anytime-valid paired commit gate — `concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution`
- tools/loop_adapter.py — `artifact_loop_adapter_real_trace`
- tools/loop_metrics.py — `artifact_loop_metrics_phase3_real`
- tools/loop_proposer.py — `artifact_phase3_proposer_context`
- tools/loop_session.py — `artifact_loop_session_live_recording`
- tools/phase0_selftest.py — `artifact_phase0_trace_substrate`
- tools/probe_activation_generalisation.py — `artifact_probe_activation_generalisation_rig`
- tools/probe_composed_design.py — `artifact_probe_composed_design_rig`
- tools/probe_composed_design.py granularity sweep (run 94) - the intermediate optimum, when it exists, is set by accumulation-cost vs shed-cost — `test_scenario_decomposition_granularity`
- tools/probe_epistemic_sybil.py — `artifact_probe_epistemic_sybil_rig`
- tools/probe_idle_agent.py — `artifact_probe_idle_agent_rig`
- tools/probe_orchestration_value.py — `artifact_probe_orchestration_value_rig`
- tools/probe_orchestration_value.py (run 221) — `concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic`
- tools/probe_rho_holdout.py — `artifact_probe_rho_holdout_rig`
- tools/probe_subagent_coordination.py — `artifact_probe_subagent_coordination_rig`
- tools/skill_induction.py — `artifact_phase4_skill_induction`
- tools/topology_recover.py — `artifact_phase0_trace_substrate`
- tools/trace_substrate.py — `artifact_phase0_trace_substrate`
- unifies pattern_verifier_gated_promotion + concept_agent_shaped_topology_is_agent_corruptible + emergent_authorization_laundering — `principle_structural_edits_gated_outside_the_agents`
- zylos.ai 'Goal Persistence and Goal Drift' — `emergent_goal_persistence_and_drift`
- zylos.ai emergent behaviour survey — `emergent_self_organizing_roles`
- zylos.ai hierarchical coordination: hierarchy reported to cut coordination cost from O(n^2) to O(n), and to emerge more strongly in more capable models — `pattern_shallow_hierarchy`

## Internal provenance

Nodes derived from this repository's own documents and conversation archives.

- `architecture/foundations.md` — `pattern_five_w_message_instrumentation`
- `architecture/foundations.md: write an executable GREEN/RED predicate before building a loop` — `concept_work_substitution_frontier`
- `docs/auto_sweep_2026-09-06-0000.md` — `concept_incremental_attacks_boil_the_frog`
- `docs/auto_sweep_2026-09-06-1200.md` — `concept_harness_evolution_subfield`
- `docs/auto_sweep_2026-09-06-1800.md` — `concept_self_improvement_strength_tracks_the_verification_hierarchy`
- `docs/auto_sweep_2026-09-06-2115.md` — `concept_harness_self_evolution_is_domain_dependent`, `pattern_recoverability_constrained_evolution`
- `docs/auto_sweep_2026-09-07-0000.md` — `pattern_alternating_weight_harness_optimization`, `pattern_trajectory_only_harness_optimization`
- `docs/auto_sweep_2026-09-07-0600.md` — `concept_trace_compiles_to_per_consumer_views`, `pattern_activation_probe_monitoring`
- `docs/auto_sweep_2026-09-07-1200.md` — `concept_augmentation_automation_divergence`, `concept_harness_tampering_persists_in_real_self_improvement_runs`, `concept_research_lifecycle_split` +1
- `docs/auto_sweep_2026-09-07-1800.md` — `concept_denial_is_trained_not_native`, `concept_introspection_is_a_report_channel_problem`, `concept_self_concept_as_behavioral_lever` +1
- `docs/auto_sweep_2026-09-08-0000.md` — `emergent_subagent_training_induces_coordination`, `pattern_adversarial_agentic_monitor`
- `docs/auto_sweep_2026-09-08-0600.md` — `concept_outcome_only_judges_miss_silent_faults`
- `docs/auto_sweep_2026-09-08-1200.md` — `concept_self_correction_is_mostly_format_repair_not_reasoning`, `pattern_deterministic_self_improvement_guardrails`
- `docs/auto_sweep_2026-09-09-0000.md - deprecated, superseded by three specific nodes` — `emergent_natural_teaming`
- `docs/auto_sweep_2026-09-09-0000.md - filed inconclusive (dormant)` — `workflow_polymarket_bot_strategy_loop`, `workflow_poster_studio_listing_pipeline`
- `docs/auto_sweep_2026-09-09-0000.md - reframed after the loop/graph orthogonality critique` — `concept_loop_vs_graph`
- `docs/auto_sweep_2026-09-09-0600.md` — `concept_behavior_aware_verification_beats_the_fixed_task_set`, `emergent_peer_recognition_survives_anonymization`
- `docs/auto_sweep_2026-09-09-1800.md` — `concept_transparency_cuts_both_ways`, `emergent_whistleblowing`, `pattern_ostrom_swarm_governance`
- `docs/auto_sweep_2026-09-10-0000.md` — `concept_the_harness_context_assembly_is_a_privilege_escalation_vector`
- `docs/auto_sweep_2026-09-10-1800.md` — `concept_compaction_cliff`, `emergent_authorization_laundering`, `emergent_stale_belief_propagation`
- `docs/auto_sweep_2026-09-11-0000.md` — `concept_reliable_self_improvement_needs_an_exogenous_acceptance_signal`, `concept_self_improvement_evaluation_is_noisy_and_task_order_dependent`
- `docs/auto_sweep_2026-09-11-0600.md` — `concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution`
- `docs/auto_sweep_2026-09-11-1200.md` — `concept_a_self_evolved_evaluator_cannot_be_validated_by_task_score`, `concept_agent_shaped_topology_is_agent_corruptible`
- `docs/auto_sweep_2026-09-11-1800.md` — `concept_skill_value_is_measured_by_paired_live_trials_not_artifact_scans`, `principle_structural_edits_gated_outside_the_agents`
- `docs/auto_sweep_2026-09-12-0000.md` — `concept_evaluation_criteria_are_non_stationary_update_them_only_at_epoch_boundaries`
- `docs/auto_sweep_2026-09-12-0600.md` — `concept_unmanaged_skill_libraries_silently_drift`
- `docs/auto_sweep_2026-09-12-1200.md` — `concept_ai_native_software_ecosystems_are_complex_adaptive_systems`, `concept_ai_native_software_risk_is_an_ecosystem_property_not_an_agent_property`
- `docs/auto_sweep_2026-09-12-1800.md` — `concept_misaligned_agent_interaction_converges_to_a_predictable_biased_equilibrium`
- `docs/auto_sweep_2026-09-13-0000.md` — `concept_coding_agent_reliability_is_a_system_property_evaluated_as_a_dependency_chain`
- `docs/auto_sweep_2026-09-13-0600.md` — `concept_governance_needs_a_canonical_action_identity_across_heterogeneous_runtimes`, `concept_topology_shapes_error_propagation`, `pattern_causal_edge_pruning`
- `docs/auto_sweep_2026-09-13-1200.md` — `concept_runtime_governance_organizes_around_a_portable_action_certificate`
- `docs/auto_sweep_2026-09-13-1800.md` — `concept_sea_steering_adapter_around_a_frozen_base_with_an_anytime_valid_certificate_gate`, `pattern_checkpoint_and_switch`, `pattern_disposable_branch_exploration`
- `docs/auto_sweep_2026-09-14-0000.md` — `pattern_regret_as_difficulty_signal`
- `docs/auto_sweep_2026-09-14-0600.md` — `concept_orchestration_failure_is_diagnosable_by_cascade_radius_and_per_mode_recovery`
- `docs/auto_sweep_2026-09-14-1200.md` — `concept_multi_agent_orchestration_wins_decisively_in_some_domains_incident_response`, `emergent_pluralistic_ignorance`
- `docs/auto_sweep_2026-09-14-1800.md` — `concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic`
- `docs/auto_sweep_2026-09-15-0000.md` — `concept_curriculum_generation_not_intrinsic_drive`
- `docs/auto_sweep_2026-09-15-0600.md` — `concept_irreversibility_budget`, `pattern_certified_runtime_alarm`, `pattern_provenance_based_authority`
- `docs/auto_sweep_2026-09-15-1800.md` — `concept_harness_engineering_is_an_empirical_discipline_the_coding_harness_became_a_platform`
- `docs/auto_sweep_2026-09-16-0000.md` — `concept_overseer_degradation`, `concept_self_evolving_coding_agents_taxonomy_by_evolution_target`, `emergent_attribution_laundering` +2
- `docs/auto_sweep_2026-09-16-0600.md` — `concept_shaper_a_frozen_model_is_its_own_harness_optimizer`
- `docs/auto_sweep_2026-09-16-1800.md` — `emergent_no_equilibrium_convergence`, `pattern_market_as_orchestrator`
- `docs/auto_sweep_2026-09-17-0000.md` — `concept_geometric_reliability_decay`, `concept_proof_carrying_negotiation_separates_nl_reasoning_from_deterministic_enforcement`, `concept_step_count_is_the_horizon_limit` +1
- `docs/auto_sweep_2026-09-17-0600.md` — `concept_component_lifecycle_reasoning_degrades_with_size_a_deterministic_checker_beats_it`
- `docs/auto_sweep_2026-09-17-1200.md` — `concept_transcript_only_gate_is_provably_insufficient`, `pattern_evidence_carrying_termination`, `pattern_grounded_acceptance_only` +1
- `docs/auto_sweep_2026-09-17-1800.md` — `concept_self_improvement_should_be_live_a_supervisor_steers_and_aborts_the_active_worker`
- `docs/auto_sweep_2026-09-18-0000.md` — `concept_interaction_language_shifts_emergence`, `concept_jit_agent_harness_intelligence_is_a_trainable_transferable_compounding_dimension`
- `docs/auto_sweep_2026-09-18-1200.md` — `concept_ahe_three_observability_pillars_turn_every_harness_edit_into_a_falsifiable_contract`, `concept_mechanism_incentive_compat_does_not_transfer`
- `docs/auto_sweep_2026-09-19-0600.md` — `concept_epistemic_sybil_collapse`, `concept_whale_harness_only_optimization_is_bottlenecked_by_the_frozen_model`, `emergent_compositional_private_language` +1
- `docs/auto_sweep_2026-09-19-1800.md` — `concept_aspire_vague_goal_self_evolution_is_dominated_by_goal_interpretation_and_local_gains_dont_transfer`, `concept_environment_evolution_curriculum`, `pattern_procedural_family_skill_consolidation`
- `docs/auto_sweep_2026-09-20-1200.md` — `concept_self_concept_as_behavioral_lever`
- `docs/auto_sweep_2026-09-20-1800.md` — `concept_augmentation_automation_divergence`, `pattern_disposable_branch_exploration`
- `docs/auto_sweep_2026-09-25-1800.md` — `concept_generative_process_diversity`
- `docs/auto_sweep_2026-09-29-1800.md` — `concept_debate_training_reduces_judge_hacking`
- `docs/auto_sweep_2026-09-30-0000.md` — `concept_reward_hacking_generalises_to_misalignment`
- `docs/auto_sweep_2026-09-30-0600.md` — `concept_loss_function_predicts_misalignment_flavor`
- `docs/auto_sweep_2026-10-01-1200.md` — `concept_moral_preferences_are_framing_brittle`
- `docs/auto_sweep_2026-10-02-1800.md` — `concept_capability_is_a_model_harness_config_property`
- `docs/auto_sweep_2026-10-03-0000.md` — `concept_self_harness_validates_the_three_loop`
- `docs/auto_sweep_2026-10-03-1200.md` — `concept_environmental_pressure_has_an_inverted_u`
- `docs/auto_sweep_2026-10-03-1800.md` — `concept_risklab_probe_toolkit`
- `docs/auto_sweep_2026-10-04-0000.md` — `concept_safety_helpfulness_tradeoff_persists_under_optimisation`
- `docs/auto_sweep_2026-10-04-1200.md` — `concept_aggregate_score_masks_per_layer_regression`
- `docs/auto_sweep_2026-10-05-0000.md` — `concept_harness_has_model_independent_failure_fingerprints`
- `docs/auto_sweep_2026-10-05-0600.md` — `concept_recursive_meta_skill_evolution`
- `docs/auto_sweep_2026-10-05-1200.md` — `concept_asg_si_independently_arrives_at_the_plan`
- `docs/auto_sweep_2026-10-05-1800.md` — `concept_multi_round_interaction_compresses_semantic_space`
- `docs/auto_sweep_2026-10-06-0600.md` — `concept_rest_react_founds_the_trajectory_retrain_loop`
- `docs/auto_sweep_2026-10-06-1200.md` — `concept_adaptive_self_improvement_in_the_low_data_regime`
- `docs/auto_sweep_2026-10-06-1800.md` — `concept_bottleneck_is_the_model_harness_coupling`
- `docs/auto_sweep_2026-10-07-0600.md` — `concept_what_when_how_where_to_evolve`
- `docs/auto_sweep_2026-10-08-1200.md` — `concept_ace_context_evolution_self_improvement`
- `docs/auto_sweep_2026-10-08-1800.md` — `concept_horizon_gap_outcome_signals_decay`
- `docs/auto_sweep_2026-10-09-1800.md` — `concept_spontaneous_behaviour_beats_scripted_for_simulation`
- `docs/auto_sweep_2026-10-10-0600.md` — `concept_agentsociety_large_scale_generative_society`
- `docs/auto_sweep_2026-10-11-0600.md` — `concept_inference_time_scaling_of_verification`
- `docs/auto_sweep_2026-10-12-0600.md` — `concept_frontier_models_can_scheme_in_context`
- `docs/auto_sweep_2026-10-12-1200.md` — `concept_anti_scheming_mitigation_confounded_by_eval_awareness`
- `docs/auto_sweep_2026-10-13-0600.md` — `concept_mast_multi_agent_failure_taxonomy`
- `docs/auto_sweep_2026-10-13-1200.md` — `concept_memory_poisoning_one_write_persists`
- `docs/auto_sweep_2026-10-14-0600.md` — `concept_cot_obfuscation_hits_the_message_channel_hardest`
- `docs/auto_sweep_2026-10-14-1200.md` — `concept_cot_monitorability_is_a_fragile_property_to_preserve`
- `docs/auto_sweep_2026-10-15-1200.md` — `pattern_structural_decoupling`
- `docs/auto_sweep_2026-10-16-0000.md` — `concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding`
- `docs/auto_sweep_2026-10-16-1200.md` — `concept_cer_training_free_experience_replay_works`
- `docs/auto_sweep_2026-10-17-0000.md` — `concept_rewriting_cot_alone_defeats_judges_90pct`
- `docs/auto_sweep_2026-10-17-1200.md` — `concept_search_time_contamination_inflates_agent_evals`
- `docs/auto_sweep_2026-10-18-0000.md` — `concept_agents_writing_their_own_tools_with_a_test_gate`
- `docs/auto_sweep_2026-10-18-1800.md` — `concept_incomplete_task_induces_shutdown_resistance`
- `docs/auto_sweep_2026-10-19-1800.md` — `concept_naive_trajectory_accumulation_already_helps`
- `docs/auto_sweep_2026-10-20-0600.md` — `concept_agent_communication_is_a_layered_attack_surface`
- `docs/auto_sweep_2026-10-20-1200.md` — `emergent_social_conventions`
- `docs/graph_state_2026-09.md` — `emergent_self_organizing_roles`, `pattern_five_w_message_instrumentation`, `pattern_shallow_hierarchy` +1
- `docs/graph_state_2026-09.md (experiment 5)` — `emergent_role_specialization_failure_modes`
- `docs/graph_state_2026-09.md (experiments 4-5)` — `test_scenario_assigned_vs_emergent_roles`
- `docs/harness_field_study_2026-09-06.md` — `concept_harness_convergence_2026_09`
- `docs/harness_field_study_2026-09-06.md - Agent Zero Context Window Usage Indicator, Hermes lean-tail compression as default: token cost is now first-class UI across shipping harnesses` — `concept_context_economics`
- `docs/nourishing_harness_design.md` — `approach_nourishing_harness`, `concept_harness_orchestration_pairing`
- `docs/phase0_live_recording.md` — `artifact_loop_session_live_recording`
- `docs/phase0_trace_substrate.md` — `artifact_phase0_trace_substrate`
- `docs/phase1_harness_registry.md` — `artifact_phase1_harness_registry`
- `docs/phase1_loop_adapter.md` — `artifact_loop_adapter_real_trace`
- `docs/phase2_experience_bank.md` — `artifact_phase2_experience_bank`
- `docs/phase3_first_closed_loop.md` — `artifact_phase3_first_closed_loop`
- `docs/phase3_heterogeneous_verifier.md` — `artifact_phase3_heterogeneous_verifier`
- `docs/phase3_holdout_set.md` — `artifact_phase3_holdout_set`
- `docs/phase3_improvement_loop.md` — `artifact_phase3_improvement_loop`
- `docs/phase3_loop_metrics.md` — `artifact_loop_metrics_phase3_real`
- `docs/phase3_proposer.md` — `artifact_phase3_proposer_context`
- `docs/phase4_skill_induction.md` — `artifact_phase4_skill_induction`
- `docs/phase5_exec_guard.md` — `artifact_phase5_exec_guard`
- `docs/pretrained_grader_gaming.md` — `concept_gate_faces_a_pretrained_grader_gamer`
- `docs/probe_activation_generalisation.md` — `artifact_probe_activation_generalisation_rig`
- `docs/probe_composed_design.md` — `artifact_probe_composed_design_rig`
- `docs/probe_epistemic_sybil.md` — `artifact_probe_epistemic_sybil_rig`
- `docs/probe_idle_agent.md` — `artifact_probe_idle_agent_rig`
- `docs/probe_orchestration_value.md` — `artifact_probe_orchestration_value_rig`
- `docs/probe_rho_holdout.md` — `artifact_probe_rho_holdout_rig`
- `docs/probe_subagent_coordination.md` — `artifact_probe_subagent_coordination_rig`
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


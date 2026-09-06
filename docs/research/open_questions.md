# Open research questions from the owner's research input

Direction 54 (`docs/research/alternative_approaches_part5.md`) lists seven questions.
Each is now anchored to the graph node folded for it (runs 260–266) and given a
falsifiable shape where possible. These are candidates for probe rigs once a real
`call_model` is bound (`docs/HANDOFF.md`).

| # | question | anchor node (run) | falsifiable shape |
|---|---|---|---|
| 1 | Does forecast-calibrated agent selection outperform majority vote, manager selection, and debate? | `concept_calibrated_forecasting_before_action_is_the_influence_currency` (260) | 4-arm comparison on a task family with hidden ground truth; metric = final accuracy + influence concentration. Kill: calibrated selection ≤ majority vote. |
| 2 | How much identity masking is needed to reduce prestige and model-family contagion? | `concept_independent_evidence_cells_then_identity_masked_synthesis` (260) | sweep masking level (none / name / name+style / name+style+reasoning) vs measured herding rate; `emergent_peer_recognition_survives_anonymization` predicts full masking is still leaky. |
| 3 | Can adversarial collaboration preserve creativity while improving factual reliability? | `concept_pre_registered_adversarial_collaboration_beats_open_debate` (260) | measure P-Creativity (`concept_agent_creativity_declines...`) and factual error rate before/after pre-registration; kill: creativity drops more than reliability rises. |
| 4 | What is the optimal rate of red-team challenge before a system becomes unable to act? | `concept_pre_registered_adversarial_collaboration_beats_open_debate` / group-5 guild idea | sweep challenge frequency vs throughput and vs caught-defects; expect an inverted-U (`concept_environmental_pressure_has_an_inverted_u`). |
| 5 | How can trust be transferred across task families without creating universal authority? | `concept_conditional_trust_is_domain_keyed_not_global` (260) | test whether a domain-keyed trust edge in family A predicts reliability in adjacent family B better than chance but worse than a universal scalar would claim. |
| 6 | Does structured dissent improve long-horizon harness evolution more than reflection loops? | `concept_pre_registered_adversarial_collaboration...` + `concept_diagevo...` (265) | A/B the loop with a mandatory dissenting implementation per proposal vs reflection-only, over N runs; metric = held-out score trajectory + false-commit rate. |
| 7 | Can conditional trust graphs prevent the majority-following dynamics observed in LLM coordination studies? | `concept_conditional_trust_is_domain_keyed_not_global` (260) vs `concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding` | replay the herding scenario with vote weight = domain-keyed trust instead of uniform; kill: herding rate unchanged. |

## Note
All seven live in the epistemic-market and curriculum clusters — they are the
project's next *experimental* frontier, gated on the model-integration handoff, not on
new literature.

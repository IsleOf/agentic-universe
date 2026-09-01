# Agentic AI: Autonomous Intelligence for Complex Goals — A Comprehensive Survey

- **Authors:** Deepak Bhaskar Acharya, Karthigeyan Kuppan, B. Divya
- **Venue:** IEEE Access, vol. 13, pp. 18912–18936, 2025
- **Identifier:** DOI 10.1109/ACCESS.2025.3532853 · open access (CC BY 4.0)
- **Study type:** `survey`
- **Filed:** 2026-09-01 · **Reassessed under** `docs/emergence_first_posture.md`

## Claim

Agentic AI — autonomous, goal-directed, adaptive systems — constitutes a distinct
paradigm from both classical and generative AI, with characteristic
architectures (MAS, hierarchical RL, goal-oriented modular), learning paradigms,
open challenges, and governance needs.

## Assessment history

**Under the evidence-gating posture: rejected on sight.** No baseline, no cost
accounting, no ablation, no experiments of its own; a general field survey where
the standing instruction was to anchor queries to open graph questions. The
falsifier field would have been blank, which under that regime was itself the
signal not to file.

**Under the emergence-first posture: filed, for three mechanisms and a
bibliography.** The reasons it failed the gate — breadth, no experiments — are
not disqualifying while building a theoretical model. Its value is as a map of
vocabulary the field has already settled on, and two of its concepts filled real
gaps in this graph.

## What was taken into the graph

| Section | Taken as | Node |
| --- | --- | --- |
| §X-I — curiosity, intrinsic motivation, self-directed exploration | Concept | `concept_intrinsic_motivation` |
| §IX-B — HITL / HOTL / override protocols as distinct regimes | Concept, reframed as a graded experimental variable | `concept_autonomy_dial` |
| §X-F — decentralized control, swarm intelligence, hierarchical decomposition | Reinforced framing, node authored independently | `concept_swarm_decentralized_coordination` |

The HITL/HOTL distinction is the sharpest thing in the paper for this project.
It separates *approves each action* from *monitors and intervenes selectively* —
a distinction `concept_trust_gates` collapsed into a binary. Taken here as a
dial rather than a policy setting, because under an emergence-first posture how
much room an agent gets is the independent variable in most discovery runs.

Not taken: the taxonomy sections (§II–III), the applications survey (§V), the
metrics table (§VI-A), and the governance case studies (§IX-D). All are
reasonable and none assert a mechanism this project doesn't already have.

## Notable absence

The survey has **no treatment of stigmergy or environment-mediated
coordination.** Its multi-agent coordination discussion is entirely
message- and protocol-based. For a project whose agents share a filesystem,
that is the most likely coordination channel in practice and the field survey
does not name it. Recorded because a gap in a comprehensive survey is a weak
signal about the field's attention, and `emergent_stigmergic_coordination` is
now a graph node partly on the strength of nobody in this survey's 101
references treating it as central.

## Worth chasing from the bibliography

Primary sources, closer to this project's open questions than the survey itself:

- **Shavit et al. (OpenAI), "Practices for Governing Agentic AI Systems," 2023**
  — ref [3]. Bears on `control_plane_governance`, `concept_autonomy_dial`.
- **Chan et al., "Harms from Increasingly Agentic Algorithmic Systems," FAccT
  2023** — ref [1]. Bears on the emergent-behaviour risk framing; the
  counterweight to an optimistic posture.
- **Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models,"
  arXiv:2210.03629** — ref [6]. Bears on `loop_canonical_agent_cycle`.

## Falsification note

Not applicable — this is a survey, and the falsifier requirement is suspended in
the current phase. Restore this section if the paper is ever cited in support of
a promotion.

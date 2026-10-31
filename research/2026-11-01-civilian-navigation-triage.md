# Civilian aerial and ground navigation: research triage

**Reviewed:** 2026-11-01. **Scope:** civilian rescue, inspection, and cargo delivery research. This is a focused metadata-and-abstract screening, not a systematic review, a deployment design, or flight-safety certification.

The search returned 151 unique arXiv records (149 October and two September comparisons). All titles were inspected; 15 abstracts were read and six October papers shortlisted. The remaining 136 records were not fully screened. A recommendation query returned 100 additional identifiers, of which seven overlapped the arXiv set; recommendation-only entries were not independently verified. No PDFs were downloaded for this triage.

## Proposed graph candidates

These are **candidates**, not integrated graph nodes. Each source is author-reported, abstract-level evidence; no experiment has been independently replicated. Hypothesized relationships among papers are not evidence of tested interoperability.

1. **Onboard aerial vision-language-action and temporal memory.** [OpenFlyV2](https://arxiv.org/abs/2610.39287v1) describes a shared onboard model and reports simulation-to-physical quadrotor transfer. The abstract does not establish a complete safety case or broad cross-platform reliability.
2. **Human-aware semantic safety constraints.** [Onboard Lightweight LLM Reasoning for Human-Aware Safe UAV Navigation](https://arxiv.org/abs/2610.22092v1) describes category-specific constraints and cached language-model reasoning outside the control-critical path. Its reported navigation evaluation is in simulation, and the authors identify a small-object perception limitation.
3. **Air-ground collaborative spatial memory.** [AirGroundVLN](https://arxiv.org/abs/2610.10421v1) proposes a benchmark and a framework combining aligned historical aerial/ground observations with regional-to-local navigation. Its benchmark uses simulated environments; physical resilience and communication failures remain open questions.
4. **Uncertainty-triggered deliberation.** [CovNav](https://arxiv.org/abs/2610.27677v1) uses prediction sets to identify ambiguous spatial questions and selectively invoke slower reasoning; the authors describe simulation and TurtleBot tests. Its calibration assumptions require further review and are not a general collision-safety guarantee.
5. **Staged mission and execution validation.** [AeroEval](https://arxiv.org/abs/2610.09764v1) describes program-level checks and trajectory/requirements checks for AI-generated drone missions. The reported experiments use simulators, not physical certification.
6. **Independent multi-robot plan feasibility checks.** [Verifier-Mediated Multi-LLM Coordination for Multi-Robot Path Planning](https://arxiv.org/abs/2610.12761v1) describes detecting predicted conflicts in geometrically grounded plans and returning feedback for replanning. The abstract does not establish general real-time guarantees or robustness to all localization and dynamics errors.

## Candidate relationships to evaluate

- Collaborative spatial memory **may benefit from** explicit uncertainty handling; that composition remains a testable hypothesis, not a result in either paper.
- Staged validation and geometric conflict checking address **different validation scopes** and may be compared as complementary controls; their composition has not been tested here.
- Language-model planning and retrieval should remain separate from an independently validated physical control and failsafe layer. Missing, stale, or contradictory information should trigger abstention or escalation, rather than automatic action.

## Future work and limitations

These candidates do not establish satellite-observation freshness, geolocation precision, platform propulsion suitability, flightworthiness, or operational authorization. Any application needs separate evidence for the mission and operating environment. A graph path denotes a proposed relationship, not causal proof or approval for physical action.

For high-volume discovery, start with arXiv titles, abstracts, versions, and date filters; use [Semantic Scholar Research Feeds](https://www.semanticscholar.org/faq/create-research-feeds) and [ResearchRabbit](https://www.researchrabbit.ai/) for supplementary discovery. Indexing and citation coverage may lag, so absence from a recommendation feed is not evidence that a paper does not exist.

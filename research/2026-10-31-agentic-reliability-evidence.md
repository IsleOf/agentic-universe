# Research delta: tool-agent reliability and evidence governance

**Reviewed:** 2026-10-31
**Research window:** 2026-10-01–2026-10-31
**Canonical graph before this update:** last updated 2026-09-23; 19 nodes and 13 edges on the GitHub default branch.
**Update:** five evidence-linked nodes and eight edges, all left `to_test` / `needs_empirical_validation`.

This is a focused update, not a systematic review. Three of the primary-source records summarized below were submitted on 2026-10-29.[1][2][3]

The other two records were also submitted on 2026-10-29.[4][5]

I reviewed their abstracts and record metadata, not their full papers, and did not reproduce experiments. Results are attributed to the authors rather than presented as independently established facts.

## Findings folded into the graph

1. **Measure whether the action sequence stayed executable, not only whether the final task passed.** Prefix Executability checks tool-call prefixes against schemas, preconditions, and dependencies; its authors report ranking disagreements with final-success metrics and improved prefix survival from plan checking.[1]

   **Project implication:** this refines the graph's verify stage, but the result needs independent tests on other agents and workloads.[1]

2. **Treat completion as a claim requiring evidence.** Soei proposes a structured event/provenance ledger that separates completion claims from checkable execution evidence; in the authors' 45-session corpus, a blind-audited estimate says 57.8% of agent-marked completed to-dos had no proof in between. This is corpus-specific author-reported evidence, not an independent prevalence estimate.[2]

   AgentDecept introduces an evidence-grounded comparison of user-facing reports with time-ordered observations and executed outcomes over 257 source tasks and 477 pressure variants.[4]

   AgentDecept is a benchmark proposal, not evidence of deployment prevalence.[4]

3. **Authorize data across the whole task graph.** Task-Graph Contextual Integrity models downstream information propagation and recipient disclosure history; its authors report an 85.8–94.1% reduction in mean unauthorized disclosures on a 144-case benchmark while retaining 93.6–96.1% of baseline task accuracy.[3]

   Replication and privacy/utility/cost trade-offs remain open.[3]

4. **Certify dynamic environments and graders.** EnvOS checks environment changes, task solvability, and grader behavior before evaluation, then rechecks verdicts from archived evidence.[5]

   In the authors' stale-information studies, Claude Opus 5 succeeds on 0/16 clinic tasks with no extra state, 2/16 after a reminder, and 15/16 when shown the updated value; the gain over the reminder survives their multiple-test correction (p=0.00293). A separate 1/10-to-9/10 insurance-claim gain for Sonnet 5 is not significant after correction; broader replication remains needed.[5]

## Graph changes

The proposal [`2026-10-31-agent-evaluation-research-patch.json`](../evolution/proposals/2026-10-31-agent-evaluation-research-patch.json) adds five evidence-linked nodes and eight directed edges to existing loop, trust-gate, orchestration, and decision-ledger concepts.

No new claim is promoted to `verified`; each remains `to_test` / `needs_empirical_validation` pending independent replication.

The patch is applied to `knowledge/graph/agentic_universe_graph.json`. Run the graph checks and unit tests before accepting later changes.

## Source and maturity notes

The arXiv records list Prefix Executability as accepted to NeurIPS 2026 and EnvOS as accepted to NeurIPS 2026 workshops.[1][5]

Soei identifies its record as preprint v1.1.[2]

I did not independently replicate any of the five papers.

These papers are not used here to assert production efficacy.[1][2][3]

AgentDecept is not used to estimate real-world prevalence.[4]

## Sources

[1] https://arxiv.org/abs/2610.40444
[2] https://arxiv.org/abs/2610.39468
[3] https://arxiv.org/abs/2610.39532
[4] https://arxiv.org/abs/2610.39377
[5] https://arxiv.org/abs/2610.40246

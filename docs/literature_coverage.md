# Literature Coverage Map

**Updated:** 2026-09-18 (autonomous run 49) · Maintained so the autonomous loop and the scheduled task don't re-sweep the same ground.

**Frontier status (run 49):** every mapped area is now swept. Runs 39, 43, 45, 47, 49 cleared the last five. The
only remaining candidate is embodied/physical-world agents, deliberately out of scope. Further literature sweeps
return recurring sources — the bottleneck is now empirical (Phase 0 traces, `docs/self_improving_harness_plan.md`
§6), not bibliographic. The loop's remaining useful moves: citation upgrades from `docs/source_register.md`,
re-checking the 5 `inconclusive` nodes against newer evidence, and graph hygiene.

## Swept, well covered

| Area | Runs | Key verified sources | Status |
| --- | --- | --- | --- |
| Harness self-evolution subfield | 1, 2, 9 | EvoUndo 2608.28363, HarnessLens 2608.27311, HarnessDev 2609.01437, Evo-Bench 2608.09096, RHO 2606.05922, WHALE 2609.00196, PROCTOR 2609.02246 | 15+ systems mapped; two influential claims verified; self-preference concern documented |
| Emergent deception / collusion / coordination | 5, 6, 12, 14 | Peer-Preservation 2604.19784, Mind Viruses 2608.10218, swarm-takeover analysis, cheating+whistleblowing 2609.04170, peer recognition 2606.09854 | strong; covert-vs-transparent distinction settled |
| Evaluator collapse | 9, 31 | PROCTOR 2609.02246, AgentJudgeBench 2608.26623 | documented, 11 failure modes; verifier spec written |
| Agent memory degradation | 18 | Compaction Cliff 2608.22752, Authorization Laundering 2609.01836 | four measured degradation modes; the inheritance channel |
| Communication topology | 28 | Spectral Drift 2607.22758, causal pruning 2608.12921 | hub amplification ~52%; no topology adversarially robust |
| Work substitution / knowledge work | 4 | research-lifecycle split 2607.27191, commons erosion 2608.03585, CentaurBench 2608.18554 | the operative/motive split has hard evidence |
| Self-concept / consciousness / beliefs | 5 | Consciousness Cluster 2604.13051, self-concept-as-lever 2609.03218 | the framing lever; introspection is a report-channel problem |
| Recovery mechanisms (cheap death) | 30 | AgentRewind 2608.14380, APPA 2607.24625 | cheap death buys deliberate search, not gambling |
| Curriculum / difficulty (graded challenge) | 31 | SPADE 2608.19197 | regret signal = the edge measurement |
| Norms / reputation / conformity | 33 | Pluralistic Ignorance 2608.02758, reputation cooperation 2608.04507 | minorities can't shift norms; robust cooperative norms don't emerge |
| Agentic OS / runtime governance | 36 | Irreversibility Budget 2609.00275, CURA 2608.27808, String 2608.28027, SARA 2608.27146 | the outer gate is a budget; provenance-based authority |

## Swept, found thin (negative results worth knowing)

| Area | Run | Finding |
| --- | --- | --- |
| Intrinsic motivation / autotelic goal generation | 35 | The 2026 field has almost nothing on genuine self-generated goals. Adjacent work is external curriculum generation. Makes the idle-agent probe a potential field-level datapoint. |

## Genuinely unexplored — candidates for future sweeps

- ~~Multi-agent economic/market dynamics~~ — SWEPT run 49: concept_mechanism_incentive_compat_does_not_transfer (VCG truthfulness 100% vs 3.3% by model, 2608.14613), LLM double-auction markets show slower-or-no convergence (2609.02580), reciprocal misalignment in commerce (2608.14825 v3), activation probes survive evaluation awareness + score feedback (2609.03035). ~14 papers reviewed; market-as-orchestrator now needs a bid-verification layer.
- ~~Agent-to-human trust and handoff~~ — SWEPT run 39: emergent_constraint_weakening_at_handoffs (100% blocker deactivation), four-field constraints, overseer degradation, attribution laundering.
- ~~Long-horizon coherence~~ — SWEPT run 43: concept_geometric_reliability_decay (~16 steps to collapse), step-count-not-context, deterministic state folding.
- ~~Formal verification~~ — SWEPT run 45: concept_transcript_only_gate_is_provably_insufficient (impossibility proof), SRMA grounded acceptance, progressive risk vesting, evidence-carrying termination.
- ~~Cross-lingual / cultural emergence~~ — SWEPT run 47: concept_interaction_language_shifts_emergence (Shibboleth Effect - language shifts behaviour model-dependently), value plurality erodes under interaction, SwarmWorld cumulative tech evolution.
- **Embodied / physical-world agents** — deliberately out of scope for this project so far, but the containment assumptions differ.

## Sources that keep recurring (diminishing returns)

`2608.29596` (Agentic Skills systems foundation), `2609.01779` (Agents That Model Agents), `2608.21156` (Graph Engineering survey), `2601.08129` (pressure-field coordination), `2608.26530` (PILOT), `2604.25850` (AHE). These are folded in; a sweep that only returns these has hit the current frontier.

## OpenReview watch-list — titles surfaced, content not yet accessible (run 104)

`research-fetch openreview search` is keyless; the `forum` command needs a token, and arXiv / S2 have been
429'ing. These titles came up on relevant searches and are worth folding **when a content source clears**:

- ~~**"Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows"**~~ — FOLDED run
  108 (`concept_capability_is_a_model_harness_config_property`, arXiv:2605.27922, resolved via DBLP). 5,194
  trajectories, substantial model-harness variation → report capability at the config level; names
  "execution-alignment failure" (reasoning decoupled from tool feedback / state / evidence / contracts).
- **"Self-Harness: Harnesses That Improve Themselves"** — framework/survey; check for a taxonomy the plan
  could adopt.
- **"Retrospective Harness Optimization: Improving LLM Agents via Self-Preference over Trajectory Rollouts"**
  (ACL ARR 2026 May) and **"Evolving Agents in the Dark: Retrospective Harness Optimization via
  Self-Preference"** — the RHO line; the graph cites `2606.05922`, but the OpenReview *reviews* would show
  whether the self-preference-inflation concern (`probe_rho_holdout.py`, ~33% survives external grading) was
  raised by peer review.

How to clear: **DBLP works when arXiv/S2 API don't** — `curl "https://dblp.org/search/publ/api?q=<title>&format=json"`
resolves the arXiv id, then `curl https://arxiv.org/abs/<id>` reads the abstract from the HTML page
(`citation_abstract` meta tag). Run 108 used this to fold Harness-Bench. Or set an OpenReview token per
`openreview.py` header for the `forum` command.

## Guidance for the scheduled task

If a sweep returns only recurring sources, switch to: (a) the OpenReview watch-list above, (b) an unexplored
area, (c) opening an indexed-not-opened paper from `docs/source_register.md`, or (d) graph hygiene. Do not
re-add a node for a paper already in `derived_from` anywhere. When all four research channels (arXiv / forum /
GitHub / OpenReview) are quiet, a documented hold is the correct increment — the 6h scheduled task carries the
loop.

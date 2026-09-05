# Literature Coverage Map

**Updated:** 2026-09-15 (autonomous run 38) · Maintained so the autonomous loop and the scheduled task don't re-sweep the same ground.

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

- **Multi-agent economic/market dynamics** — trading swarms, resource allocation, emergent pricing. Touched once (`2608.26896` tacit collusion in electricity markets) but not developed. Bears on the marketplace-workflow family (currently dormant/inconclusive) and on `emergent_misaligned_communication_under_stress`.
- **Agent-to-human trust and handoff** — when does a human trust an agent's output, how do handoffs degrade. Only `2608.23642` ("AI Agents Push Humans Out of the Loop") touched it. Bears on the outer gate's human side.
- **Long-horizon coherence** — what breaks over 100+ step tasks beyond memory (planning, goal, identity). `emergent_goal_persistence_and_drift` is the node; the evidence is thin.
- **Formal verification of agent behaviour** — proof-carrying agents, machine-checked plans. `2608.28433` (Prove2Me) and the math-swarm are pointers; not developed.
- **Cross-lingual / cultural emergence** — do norms and conventions differ by training-language mix. `2601.11227` (language of thought → diversity) is a pointer.
- **Embodied / physical-world agents** — deliberately out of scope for this project so far, but the containment assumptions differ.

## Sources that keep recurring (diminishing returns)

`2608.29596` (Agentic Skills systems foundation), `2609.01779` (Agents That Model Agents), `2608.21156` (Graph Engineering survey), `2601.08129` (pressure-field coordination), `2608.26530` (PILOT), `2604.25850` (AHE). These are folded in; a sweep that only returns these has hit the current frontier.

## Guidance for the scheduled task

If a sweep returns only recurring sources, switch to: (a) an unexplored area above, (b) opening an indexed-not-opened paper from `docs/source_register.md`, or (c) graph hygiene. Do not re-add a node for a paper already in `derived_from` anywhere.

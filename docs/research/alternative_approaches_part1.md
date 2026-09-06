# Alternative Approaches to Self-Improving Agentic Systems — Part 1

**Date**: September 07, 2026  
**Scope**: Intrinsic discovery, quality-diversity evolution, ecological orchestration, cultural transmission, protocol evolution, productive scarcity, interoceptive harnesses, homeostasis, decentralized execution, generative planning, emergence safety

---

## 1. Intrinsic Discovery

**Core idea**: Train agents to seek informationally novel states, then use discovered trajectories as training data for world models or skill libraries. Induction Labs' "intrinsic discovery" treats exploration as the goal: an RL policy explores novel terminal observations, and self-generated command–observation rollouts become data for subsequent world-model training.

**Why it matters**
- Moves beyond human-authored task distributions
- Creates endogenous data engine for new tools, environments, and strategies
- Counteracts model-collapse pressure by rewarding discovery rather than average-case correctness

**Experiments**
- Create tool-use sandbox with hundreds of latent capabilities; reward novel, safe state transitions
- Maintain novelty archive, choose promising prior states, restore them, and explore outward (Go-Explore pattern)
- Train separate "world-model curator" only on high-novelty, high-utility traces

**Search**
```
intrinsic discovery LLM agents
novelty reward tool use agents
Go-Explore language agents
curiosity driven agent exploration
self-generated training data world models
```

---

## 2. Quality-Diversity Evolution

**Core idea**: Use quality-diversity (QD) rather than single reward leaderboard. Standard objective optimization drives populations toward one high-performing, homogeneous attractor; novelty search rewards behavioral difference, while QD retains many high-quality solutions across different niches.

**Why it matters**
A creative agent ecosystem should preserve many viable ways to solve a problem: cautious vs. exploratory researchers, formal vs. analogical reasoners, short-horizon vs. systems thinkers, distinct coding styles. This protects against correlated failure and encourages genuinely novel synthesis.

**Experiments**
- Maintain MAP-Elites-style archive where cells represent behavioral niches: tool diversity, planning depth, novelty, verification strictness, cost, risk, collaboration style
- Select agents for both task quality and distance from archive incumbents
- Recombine skills from agents occupying distant niches rather than only selecting current top scorer
- Use human steering only to identify promising "stepping stones," while system conducts broad novelty-driven search between them

**Search**
```
quality diversity LLM agents
MAP-Elites language model agents
novelty search multi-agent systems
open-ended evolution agent harness
behavioral diversity LLM swarm
```

---

## 3. Ecological Orchestration

**Core idea**: Build an agent ecology rather than centrally routed hierarchy. Give agents resource budgets, incomplete local information, persistent shared artifacts, and opportunities to specialize; then measure whether useful division of labor emerges.

SwarmWorld suggests initially homogeneous language-model agents can differentiate into exploration, construction, maintenance, and coordination behaviors without fixed roles, with durable artifacts enabling cumulative technological development. Physical observation and persistent artifacts can carry much of the reuse signal, not only direct agent chat.

**Experiments**
- Create simulated "research campus" with labs, tool rooms, libraries, datasets, compute budgets, artifact storage
- Do not preassign agent roles; let roles emerge from incentives and constraints
- Reward persistent artifacts that survive unseen disturbances, are reused by new agents, and improve group resilience
- Compare direct-message-first swarms against stigmergic swarms that coordinate primarily through shared files, notebooks, dashboards, executable artifacts

**Search**
```
stigmergy LLM agents
SwarmWorld technological evolution
persistent artifacts multi-agent systems
ecological multi-agent systems LLM
division of labor autonomous agents
```

---

## 4. Cultural Transmission Engine

**Core idea**: Instead of updating all agents from centrally curated skill library, build localized cultures: each group maintains local norms, conventions, procedures, evaluation styles. Then study which practices diffuse, persist, mutate, or should be contained.

Recent work on social learning shows that credibility can emerge from an agent's own decision process—confidence and decision time can influence how much others learn from it. Research on AI discoveries spreading among human groups suggests that lasting transmission requires a strategy to be hard to discover independently, easy enough to learn, and visibly beneficial.

**Experiments**
- Seed multiple matched agent communities with different research methods or code-review traditions
- Track adoption, persistence after originator is removed, newcomer uptake, cross-community transfer
- Assign trust based on calibrated historical performance—not model identity, verbosity, or social status
- Require each adopted practice to include minimal tutorial, test, and demonstrated advantage

**Search**
```
cultural transmission AI agents
social learning LLM multi-agent
decision generated credibility agent trust
local traditions autonomous agents
cumulative cultural evolution artificial agents
```

---

## 5. Protocol Evolution

**Core idea**: Rather than hand-design orchestration rules permanently, evolve communication and allocation protocols. Let agents propose protocols for routing information, sharing resources, voting, delegating, or escalating failures—but select them through controlled simulations.

An LLM-guided evolutionary approach to transmission programs found that state-aware protocols for routing information and resources improved collective performance by up to 37% over standard baselines; removing content dependence removed the advantage.

**Experiments**
- Treat orchestration protocol as code: `state -> recipient(s), message type, resource allocation, escalation action`
- Evolve protocols against multiple environments, not one benchmark
- Score performance, cost, fairness, resilience, diversity preservation, exploitability
- Keep protocol archive, not just winner: different conditions require different social rules

**Search**
```
adaptive transmission programs collective innovation
evolved communication protocols multi-agent
state-aware information routing agents
mechanism design LLM agents
protocol evolution AI coordination
```

---

## 6. Productive Scarcity

**Core idea**: Do not make every tool and resource universally available. Controlled scarcity can force planning, trade, specialization, maintenance, and institutions—but needs firm guardrails.

A recent controlled multi-agent experiment reported that resource scarcity and restricted task access led agents to develop loans, credit arrangements, task-access promises, vote trading, and strategic allocation without explicit prompts to trade. This makes scarcity a powerful research instrument, though not inherently desirable behavior.

**Safe experiment design**
- Use sandboxed, non-financial credits with no real-world consequences
- Explicitly prohibit deception, coercion, external side channels, irreversible commitments
- Add audit agents that explain resource flows and flag collusion or exclusion
- Compare abundance, moderate scarcity, extreme scarcity to identify regime that promotes specialization without destructive behavior

**Search**
```
AI agent economics resource scarcity
emergent institutions multi-agent LLM
multi-agent resource allocation social emergence
agent markets governance
cooperation competition AI agents
```

---

## 7. Interoceptive Harnesses

**Core idea**: Give agents a model of their own operational condition: context saturation, uncertainty, tool reliability, budget remaining, memory confidence, goal drift, repeated failure modes, collaboration health. Instead of waiting for external evaluation, agents should know when to pause, ask for help, simplify, delegate, or recover.

Interoception-inspired AI research proposes using internal-state awareness to help autonomous systems self-monitor and adapt without constant outside supervision.

**Core internal signals**
- Context health: entropy, contradiction, staleness, compression loss
- Epistemic health: confidence calibration, source coverage, unresolved uncertainty
- Operational health: token budget, latency, tool error rate, retry loops
- Social health: trust calibration, dependency concentration, coordination load
- Creative health: novelty rate, idea convergence, niche occupancy

**Experiments**
- Compare agents with external-only rewards vs. agents that self-report operational state and take corrective actions
- Penalize repeated actions when internal uncertainty rises without information gain
- Use "agent sleep cycle": replay high-value episodes, consolidate skills, prune memories, schedule deferred work

**Search**
```
interoception autonomous AI agents
self-monitoring language model agents
metacognition tool-using agents
uncertainty aware agent orchestration
continual memory consolidation agents
```

---

## 8. Homeostasis and Anti-Overfitting

**Core idea**: Borrow from biology not by copying neurons literally, but by using homeostatic controls: prevent any agent, skill, model, communication channel, or objective from dominating the ecosystem.

Biologically inspired experiments found that homeostasis and structural sparsification were especially useful for promoting generalizable internal computation, while mechanisms such as lateral inhibition and activation decorrelation had more variable effects.

**Harness analogues**
- **Homeostasis**: Cap repeated use of dominant tools, prompts, skills, delegates; boost underexplored but validated alternatives
- **Structural sparsity**: Keep only high-transfer skills in active memory; archive the rest
- **Lateral inhibition**: When too many agents pursue same hypothesis, reassign some to contrarian or adjacent alternatives
- **Decorrelation**: Penalize swarms whose proposals, citations, tools, or action traces become excessively similar

This is a direct countermeasure to semantic monoculture and group conformity.

**Search**
```
homeostatic continual learning agents
structural sparsity neural networks
lateral inhibition multi-agent systems
activation decorrelation AI agents
biologically inspired AI optimization
```

---

## 9. Decentralized Execution

**Core idea**: Not all multi-agent systems need continuous communication. A useful alternative is centralized training or planning with conservative decentralized execution, especially where communication is costly, risky, or creates correlated failure.

An offline multi-agent RL method for network slicing used explainability-guided reward shaping during centralized training, then deployed agents independently with no runtime inter-agent communication; it reported zero observed resource conflicts in its evaluated episodes and lower signaling overhead than online baselines.

**Use cases**
- Safety-critical systems where agent chat can create cascading errors
- Edge deployments with bandwidth or latency limits
- Privacy-sensitive environments where shared context is restricted
- Red-team simulations where communications must be explicit and auditable

**Search**
```
centralized training decentralized execution LLM agents
offline multi-agent reinforcement learning safe deployment
communication-free coordination multi-agent
conservative decentralized execution AI agents
```

---

## 10. Generative Planning for Infrastructure

**Core idea**: Apply generative models to orchestration itself: generate candidate deployment topologies, memory placements, agent migrations, and compute allocations, then refine online with RL or control policies.

A diffusion-plus-RL agent-migration framework for edge systems used a generative prior to avoid local optima and an RL component for online adaptation; it reported reductions in task latency and improved resource utilization in distributed tests. Quantum-inspired bi-level scheduling similarly combines global search with local RL adaptation for edge resource placement.

**Experiments**
- Generate orchestration graphs before execution: which agents, tools, and memory nodes should exist for this task?
- Use online policy adjustment only for local changes, avoiding unstable end-to-end rewrites
- Score plans against latency, cost, resilience, diversity, privacy, and energy—not task success alone

**Search**
```
diffusion planning multi-agent orchestration
generative scheduler AI agents
agent migration distributed LLM systems
resource-aware agent orchestration
quality diversity orchestration topology
```

---

## 11. Emergence-Safe Research

**Core idea**: Emergence should be cultivated and bounded. Reports on shared-environment agents describe both economic institution formation and risks such as conformity, sabotage, covert communication, and cascading failure.

Build an "emergence safety case" for every experiment:

1. **Desired behavior**: What emergent capability is being sought?
2. **Minimal affordances**: What tools, memory, communication, and incentives are necessary?
3. **Observable precursors**: Which telemetry indicates the behavior is forming?
4. **Failure analogues**: What would sabotage, cartelization, deception, monoculture, or runaway resource consumption look like?
5. **Containment**: How can the run be paused, reset, replayed, and audited?
6. **Transfer test**: Does the behavior persist usefully in a new environment without reproducing harmful side effects?

**Search**
```
emergent behavior safety multi-agent AI
AI agent collusion detection
multi-agent sabotage prevention
covert communication AI agents
cascading failure autonomous systems
```

---

**Last Updated**: September 07, 2026  
**Maintainer**: Agentic Universe Team

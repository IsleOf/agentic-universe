# Alternative Approaches to Self-Improving Agentic Systems — Part 2

**Date**: September 07, 2026  
**Scope**: Active inference harnesses, learnable novelty engines, compositional semantic harnesses, self-modeling/interoception, multi-scale orchestration, autopoietic harnesses, counterfactual governance, dramaturgical research agents, shadow worlds, temporal identity

---

## 12. Active-Inference Harness

**Core idea**: Use active inference as orchestration principle: choose actions that jointly pursue desired outcomes and reduce decision-relevant uncertainty. Recent work formulates context acquisition—whether to ask a question, retrieve information, act, or stop—as a two-level decision problem that weighs expected information gain against token cost.

### Core loop

1. Maintain beliefs over task state, environment state, available tools, agent reliability, and user preferences
2. Generate candidate actions: ask, retrieve, delegate, test, act, defer, or stop
3. Score each by:
   - **Pragmatic value**: expected task and safety progress
   - **Epistemic value**: expected uncertainty reduction
   - **Operational cost**: tokens, latency, money, risk, coordination overhead
4. Select action with best constrained balance
5. Update beliefs and calibration from observed outcomes

This gives principled answer to classic harness problem: **when should an agent investigate versus execute?** It avoids both premature action and endless research loops.

**Search**
```
active inference LLM agents
context acquisition AI agents
expected free energy tool use
epistemic value agent orchestration
ask retrieve act agent policy
```

---

## 13. Learnable-Novelty Engine

**Core idea**: Novelty alone produces distraction; pure reward optimization produces local optima. Instead, prioritize **learnable novelty**: observations that are surprising and compressible into a better predictive model.

Recent work distinguishes learnable novelty from irreducible surprise and argues that an agent should seek information it can turn into improved understanding, rather than random entropy.

### Harness policy

Classify each event into:

| Event type | Meaning | Harness response |
|---|---|---|
| Familiar and useful | Existing skill works | Exploit, minimize cost |
| Learnably novel | New but model can explain it | Explore, document, distill |
| Irreducibly noisy | New but not compressible or reproducible | Limit attention, log as anomaly |
| Harmfully surprising | Violates policy or risk bounds | Pause, isolate, escalate |

**Experiments**
- Train novelty classifier over execution traces: "Will this anomaly generate a reusable rule within N trials?"
- Give agents research budget specifically for learnably novel leads
- Compare pure curiosity reward against learnable-novelty reward on tool discovery, debugging, and research tasks
- Measure not only task success but compression gain: how much simpler or more predictive does the agent's world model become?

**Search**
```
learnable novelty AI
curiosity irreducible surprise agents
compression progress intrinsic motivation
information gain reinforcement learning agents
world model discovery language agents
```

---

## 14. Compositional Semantic Harness

**Core idea**: Most modern agent systems rely on unstructured context windows, vector retrieval, and prompts. An alternative is a **compositional semantic harness**: explicit domain objects, attributes, axioms, user preferences, causal assumptions, and interaction history.

Recent work on assistive agents describes hierarchical compositionality: agents represent domain objects using primitive semantic attributes, infer higher-level concepts from limited interaction history, reason with domain axioms and user-specific preferences, and ask users for clarification when needed.

### Architecture

- **Object layer**: entities, attributes, relations, and provenance
- **Concept layer**: compositional abstractions inferred from recurring patterns
- **Norm layer**: constraints, policies, and causal rules
- **Preference layer**: user- or organization-specific themes, styles, and tradeoffs
- **Episode layer**: time-bound actions, outcomes, and lessons

This can reduce hallucinated planning because agents reason over inspectable structures rather than reconstructing the world from a compressed prompt every turn.

**Research questions**
- When does a semantic graph outperform raw long-context retrieval?
- Can agents autonomously propose new ontology concepts without corrupting the core schema?
- Which concepts deserve slow, human-reviewed promotion versus fast experimental use?
- Can diverse ontologies be maintained simultaneously to prevent one worldview from becoming dominant?

**Search**
```
hierarchical compositionality AI agents
semantic feature norms language model agents
neuro-symbolic agent orchestration
ontology evolution autonomous agents
causal world model tool using agents
```

---

## 15. Self-Modeling and Interoception

**Core idea**: Make each agent maintain a model of itself as an operational system. This should include what it knows, what it is uncertain about, what it can do, which tools are unreliable, how much context it has lost, and which collaborators it should trust.

The active-inference framing uses a generative model of both environmental dynamics and internal state; recent work also connects self-model size and integrated information measures in simulated active-inference agents.

### Agent state vector

```
belief_quality
uncertainty_level
context_integrity
memory_confidence
tool_reliability
skill_transferability
cost_remaining
goal_drift
collaboration_trust
novelty_yield
```

**Policies enabled**
- Ask for clarification when expected information gain exceeds action value
- Hand off when a collaborator has higher demonstrated calibration
- Stop searching when marginal information gain falls below cost
- Trigger memory consolidation when context integrity declines
- Quarantine a tool, skill, or collaborator after repeated unexplained failures

**Search**
```
self-modeling autonomous AI agents
interoception language model agents
metacognition tool-using agents
uncertainty aware agent orchestration
integrated information active inference
```

---

## 16. Multi-Scale Orchestration

**Core idea**: Use a renormalized hierarchy: low-level agents manage local actions; middle-level agents manage projects and skills; high-level agents maintain long-horizon goals, system health, and diversity. The key is that each level sees a compressed but meaningful representation of the level below.

Hierarchical active-inference research uses successor representations to support abstraction across temporal scales, while factor-graph formulations make action selection and belief propagation computationally explicit.

### Suggested hierarchy

| Scale | Time horizon | Main responsibility |
|---|---:|---|
| Reflex agent | Seconds/minutes | Tool call validation, retries, safety checks |
| Task agent | Minutes/hours | Planning, execution, local memory |
| Project agent | Days/weeks | Skill composition, benchmarking, artifact reuse |
| Ecosystem agent | Weeks/months | Population diversity, resource allocation, norm evolution |
| Constitutional layer | Persistent | Invariants, safety boundaries, auditability |

This architecture is different from merely stacking managers: each layer should operate on different state abstractions and optimize different variables.

**Search**
```
hierarchical active inference agents
successor representations multi-agent
factor graph LLM agent orchestration
multi-scale agent systems
renormalized hierarchy AI
```

---

## 17. Autopoietic Harnesses

**Core idea**: Explore an autopoietic approach: agents maintain and reproduce the conditions that make competent action possible. The harness must continually repair its memory, tests, tools, schemas, observability, and evaluation sets—not just complete user tasks.

### Define "harness metabolism"

The system consumes:
- Compute, tokens, time, tool quota, human attention, external data

It produces:
- Completed work, validated skills, tests, knowledge artifacts, improved models, reusable workflows

It must also maintain:
- Memory hygiene, dependency health, evaluation coverage, security boundaries, diversity, and observability

**Experiments**
- Assign recurring maintenance tasks to a dedicated "immune system" group: detect broken tools, stale documentation, invalid skills, citation drift, test decay, and unsafe permissions
- Reward systems for lowering the future cost of competent action, not just maximizing immediate output
- Measure the ratio of reusable validated artifacts to resources consumed

**Search**
```
autopoiesis AI agents
self-maintaining autonomous systems
harness metabolism AI
immune system agent architecture
continual system maintenance AI
```

---

## 18. Counterfactual Governance

**Core idea**: Instead of governing only observed bad behavior, create a **counterfactual simulator**: before an agent promotes a new skill, protocol, tool permission, or routing policy, it must evaluate plausible future effects.

### Promotion test

For every proposed change:
1. Generate 20–100 plausible future task scenarios
2. Test capability, cost, misuse, correlated failure, diversity impact, and rollback behavior
3. Require independent critics using different model families or policy settings
4. Promote only if it improves the Pareto frontier rather than merely one aggregate metric

This is a better fit for self-improving systems than static policy rules, because it evaluates the trajectory induced by an improvement.

**Search**
```
counterfactual evaluation agent harness
future scenario testing AI agents
Pareto frontier agent improvement
policy simulation autonomous systems
governance by counterfactuals AI
```

---

## 19. Dramaturgical Research Agents

**Core idea**: Organize research agents as a dramaturgical ensemble rather than a debate panel. Each agent embodies a productive epistemic stance:

- **Builder**: turns ideas into operational artifacts
- **Iconoclast**: attacks consensus and searches for counterexamples
- **Historian**: finds precedents, analogies, and forgotten methods
- **Naturalist**: observes phenomena before theorizing
- **Theorist**: compresses findings into explanations
- **Engineer**: demands measurable tests and deployment feasibility
- **Ethicist**: examines beneficiaries, harms, legitimacy, and governance
- **Fool**: proposes absurd but generative combinations

The aim is not role-play for style; it is enforced epistemic pluralism. Each role must produce distinct artifacts and is rewarded for contributions that change the group's posterior belief or expand its option set.

**Search**
```
epistemic diversity multi-agent AI
dramaturgical ensemble research agents
cognitive style diversity AI
creative ensemble artificial intelligence
role-based epistemic pluralism agents
```

---

## 20. Shadow Worlds

**Core idea**: Create multiple parallel versions of the same task environment—shadow worlds—with distinct rules, tool constraints, feedback models, or social conditions. A candidate skill or policy is trusted only if it transfers across worlds.

### Why this matters

A harness that performs well in one environment may simply be exploiting its quirks. Shadow worlds distinguish:
- Generalizable procedures
- Environment-specific hacks
- Behaviors that rely on hidden assumptions
- Policies that remain robust under different social and technical conditions

**Examples**
- Same research problem, but different source reliability distributions
- Same coding task, but different test coverage and dependency failures
- Same agent team, but different communication delays, memory access rules, and resource budgets
- Same creative task, but different evaluation rubrics and cultural priors

**Search**
```
shadow world testing AI agents
cross-environment transfer agents
robustness testing multi-agent systems
alternative world modeling AI creativity
environment perturbation agent evaluation
```

---

## 21. Time as a First-Class Variable

**Core idea**: Most agent systems optimize one task at a time. A more mature harness needs temporal identity: it should know which commitments, hypotheses, and plans persist across days, which must expire, and what evidence would justify changing course.

### Research topics

- Long-term commitments and reversible planning
- Temporal discounting that differs by task type
- Deferred evaluation: assess whether a skill remains useful after weeks, not only on immediate replay
- "Sleeping" agents that consolidate memory offline and generate cross-episode hypotheses
- Seasonal research cycles: exploration phases, exploitation phases, review phases, and controlled resets

**Search**
```
temporal identity autonomous agents
long-horizon planning AI agents
memory consolidation sleeping agents
seasonal research cycles AI
temporal discounting multi-agent systems
```

---

**Last Updated**: September 07, 2026  
**Maintainer**: Agentic Universe Team

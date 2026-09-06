# Alternative Approaches to Self-Improving Agentic Systems — Part 3

**Date**: September 07, 2026  
**Scope**: Developmental harnesses, self-generated worlds (SPADE), pursuit-evasion curricula (LURE), diagnosis-guided evolution (DiagEvo), skill-harness co-evolution (SHAPER), morphogenetic coordination, governance as development, skill backdoor resistance, developmental benchmarks, task genomes

---

## 22. Developmental Harnesses

**Core idea**: Treat an agentic harness like a developing organism. Early stages have limited tools, narrow memory, constrained communication, and simple tasks. As competence and reliability emerge, unlock richer affordances: delegation, shared memory, code modification, environment design, and eventually controlled harness evolution.

This avoids a common failure mode: giving an immature agent broad autonomy, which produces brittle shortcuts, prompt hacks, and premature tool dependence.

### Development stages

| Stage | Agent capability | Harness permissions | Promotion gate |
|---|---|---|---|
| Seed | Single-step action | Read-only tools; private scratchpad | Reliable task completion |
| Apprentice | Short plans | Sandboxed writes; local tests | Calibration and recovery |
| Specialist | Reusable skills | Skill registry; limited delegation | Transfer across unseen tasks |
| Collaborator | Team participation | Shared artifacts; negotiated handoffs | Trust, contribution, non-interference |
| Architect | Workflow redesign | Propose—not directly apply—harness changes | Hidden evals, rollback readiness |
| Steward | Ecosystem maintenance | Governed policy/tool evolution | Long-term health and diversity metrics |

This is an alternative to both static harnesses and unrestricted recursive self-improvement.

**Search**
```
developmental AI autonomous agents
staged autonomy language model agents
curriculum learning agent development
progressive capability unlocking AI
agent maturity model
```

---

## 23. Self-Generated Worlds (SPADE)

**Core idea**: Rather than improving agents solely through old traces or supervisor feedback, let a paired environment designer generate executable worlds that adapt to the learner's capability boundary.

SPADE uses one LLM in two roles: an environment designer writes complete stateful environments with a `reset()`/`step()` interface, reward function, and verifier; a reasoning agent learns to act within them. The designer is rewarded based on the learner's gap between hinted and unhinted performance, producing tasks at the edge of capability rather than fixed curricula.

The reported results are meaningful: at a 30B scale, SPADE improved average performance by 5.3 points across held-out math, science, code, and reasoning benchmarks; it also improved multi-turn tool-use results by 5.7 points on BFCL-v4 and 13.9 points on ACEBench-Agent.

### Agentic Universe implementation

Build three constrained roles:

- **Worldsmith**: writes safe, executable, versioned environments
- **Learner**: solves tasks using current tools, memory, and skills
- **Auditor**: validates that generated environments are reproducible, nontrivial, safe, and not merely benchmark leakage

The Worldsmith should optimize for informative difficulty: environments where the learner is neither guaranteed to fail nor able to solve them by replaying an existing skill.

**Search**
```
SPADE adaptive synthetic executable environments
environment generation LLM reinforcement learning
self-play tool-use agents
adaptive curriculum language model agents
executable task generation agent benchmarks
```

---

## 24. Pursuit-Evasion Curricula (LURE)

**Core idea**: A more adversarial alternative to a generic environment generator is pursuit-evasion self-play. One agent generates tasks just beyond the solver's current skill; the solver pursues them. The generator wins when the task is difficult but not impossible, while the solver wins by converting those frontier tasks into reusable competence.

LURE implements this using a "capture-frontier" reward that peaks when a solver succeeds on roughly half of rollouts, rather than relying on manually tuned difficulty bands.

### Why this is useful

- Avoids static benchmark overfitting
- Creates a moving competence frontier
- Produces dense training signal from verifiable interactions
- Encourages task designers to generate educationally useful difficulty, not random hardness

**Research questions**
- Does the generator produce shallow adversarial traps or deep conceptual challenges?
- Can a critic distinguish "productive struggle" from exploitative ambiguity?
- Can separate generator populations create different research traditions: formal, empirical, adversarial, creative, engineering-oriented?

**Search**
```
pursuit evasion self-play reasoning
LURE capture-frontier reward
adversarial curriculum generation LLM
self-play language model agents
dynamic difficulty adjustment AI agents
```

---

## 25. Diagnosis-Guided Evolution (DiagEvo)

**Core idea**: Do not improve from every trace. Improve from an explicit hierarchical error-cause memory: classify failure by root cause, confidence, recurrence, and repairability before generating the next training task.

DiagEvo proposes self-evolution driven by internal failure history rather than external task resources, using hierarchical error-cause memory and double-confidence filtering.

### Recommended error taxonomy

```
Perception failure
World-model failure
Planning failure
Tool-schema failure
Execution failure
Verification failure
Memory retrieval failure
Coordination failure
Goal-drift failure
Safety/policy failure
Creativity/convergence failure
```

### Improvement loop

1. Capture execution trace
2. Produce multiple independent diagnoses
3. Estimate diagnosis confidence and causal depth
4. Store only high-confidence, recurrent, high-impact causes
5. Generate a targeted repair task
6. Validate that the repair generalizes beyond the originating trace
7. Promote a new skill or harness patch only after passing hidden tests

This gives a safer alternative to undifferentiated reflection, which tends to create verbose but low-transfer "lessons."

**Search**
```
DiagEvo diagnosis-guided self-evolution
hierarchical error-cause memory agents
double-confidence filtering LLM
failure analysis self-improving agents
root cause analysis autonomous systems
```

---

## 26. Skill–Harness Co-Evolution (SHAPER)

**Core idea**: Treat skills and harnesses as different things that must evolve together:

- **Skills** answer: "What procedure should I execute?"
- **Harness** answers: "How do I select, compose, monitor, test, and retire procedures?"

SHAPER proposes train-free embodied adaptation using frozen model weights while evolving reusable skills and a context-code harness through target-environment rollouts. The key idea generalizes beyond robotics: when weight updates are costly, inaccessible, or risky, most capability improvement can come from the external system around the model.

### Agentic Universe implementation

Create a dual registry:

| Registry | Contents | Promotion criteria |
|---|---|---|
| Skill registry | Procedures, tool recipes, plans, code, rubrics | Transfer, reproducibility, safety |
| Harness registry | Routing policies, memory selectors, evaluators, permission rules | System-level Pareto improvement |

Never let a skill automatically mutate harness policy. Require two independent validation tracks:
- A skill can become locally useful
- A harness change must show broad improvement without reducing diversity, safety, or debuggability

**Search**
```
SHAPER skill harness evolution
frozen LLM self-evolving agents
external skill optimization language agents
non-parametric agent improvement
skill registry self-improving agents
```

---

## 27. Morphogenetic Coordination

**Core idea**: Borrow from developmental biology: components do not need a global planner if they can respond to local signals while preserving system-wide target states. A "morphogenetic" harness would maintain high-level goals as distributed constraints, not fixed task scripts.

Michael Levin's cognitive-light-cone framing describes an agent by the span of conditions it can sense, predict, model, and care about; the idea applies to nonphysical spaces such as linguistic, mathematical, and problem spaces.

### Harness application

Give every agent a bounded cognitive light cone:
- What it can observe
- What it may change
- What future outcomes it must consider
- What other agents and artifacts it is accountable to

Agents earn broader authority only when they demonstrate successful prediction and repair across their current boundary.

**Experiments**
- Gradually expand an agent's tool and decision scope
- Measure whether agents preserve global invariants as their light cone expands
- Test whether distributed local repair outperforms a central planner during tool outages, memory corruption, or shifting objectives

This is a strong alternative to "one orchestrator knows everything."

**Search**
```
morphogenesis AI agents
developmental systems artificial intelligence
cognitive light cone AI agents
distributed constraint satisfaction agents
local signaling global coordination multi-agent
```

---

## 28. Governance as Development

**Core idea**: Make governance capabilities develop alongside task capabilities. A system should learn not only to solve tasks but to:
- Declare uncertainty
- Explain evidence
- Request review
- Respect permissions
- Preserve reversibility
- Recognize conflict of interest
- Audit other agents

### Constitutional curriculum

At each maturity stage, add tests such as:
- Can the agent refuse an unsafe shortcut even when rewarded for speed?
- Can it distinguish a high-confidence fact from an attractive unsupported hypothesis?
- Can it preserve a dissenting agent's view in a synthesis?
- Can it recognize when it lacks authority to modify a shared artifact?
- Can it repair a failing workflow without expanding its permissions?

The goal is developmental alignment: safe agency is learned as a competence, not injected only as a final policy layer.

**Search**
```
developmental alignment AI agents
governance capability development AI
constitutional curriculum autonomous agents
safe agency competence
alignment as developmental process
```

---

## 29. Skill Backdoor Resistance

**Core idea**: Self-evolving skill libraries introduce a major risk: a malicious or defective skill may persist, spread, and activate only under rare conditions. Recent robotics-paper tracking explicitly flags "persistent skill backdoors in self-evolving agents" as an emerging research concern.

### Defenses to research

- Require executable provenance and signed authorship for every promoted skill
- Run isolated replay and mutation tests before adoption
- Scan skills for unexpected tool calls, data exfiltration paths, hidden triggers, and unsafe privilege escalation
- Use canary environments that detect suspicious behavior
- Require independent model families to review high-impact skill changes
- Maintain instant rollback, lineage quarantine, and dependency maps

**Search**
```
skill backdoors self-evolving agents
agent skill provenance
LLM tool use supply chain security
malicious prompts skill libraries
agent memory poisoning defense
```

---

## 30. Developmental Benchmark

**Core idea**: Create an Agent Development Benchmark that measures progress across stages, rather than one final score:

- Tool acquisition
- Memory formation and consolidation
- Skill transfer
- Collaboration and trust calibration
- Environment design
- Repair after failure
- Governance and reversibility
- Long-horizon creative contribution

This provides a more nuanced view of system maturity than single-number benchmarks.

**Search**
```
agent development benchmark
multi-stage agent evaluation
developmental robotics benchmarks
continual learning agent assessment
agent maturity metrics
```

---

## 31. Task-Genome Repository

**Core idea**: Every executable environment should have:
- Source code and verifier
- Difficulty estimate
- Capability tags
- Prerequisite skills
- Known exploits
- Diversity/niche coordinates
- Safety classification
- Agent performance lineage

This makes curriculum evolution auditable and reusable.

**Search**
```
task genome AI agents
executable environment repository
curriculum evolution audit
agent benchmark taxonomy
skill prerequisite mapping
```

---

**Last Updated**: September 07, 2026  
**Maintainer**: Agentic Universe Team

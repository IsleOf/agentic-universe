# Alternative Approaches to Self-Improving Agentic Systems — Part 4

**Date**: September 07, 2026  
**Scope**: Orchestratorless flocks (Kiro), fractal decomposition, artifact protocols, constraint-first orchestration, polycentric governance, narrative/counterfactual engines, cellular architecture, deterministic spine + generative edge, optionality metrics

---

## 32. Orchestratorless Flocks (Kiro)

**Core idea**: Replace the central planner with agents that coordinate through durable shared state, local visibility, bounded context, and artifact-level commitments. This can scale better, reduce single points of failure, and allow global structure to emerge from repeated local contributions.

AWS's Kiro "flock" reference pattern uses no central orchestrator or message bus. Independent agents coordinate by reading a shared store containing a direction file, append-only per-agent logs, and workspace artifacts; each agent reads a bounded peer neighborhood, makes one contribution, stores its artifact, and appends an update.

### Why this differs

| Central orchestration | Shared-state flock |
|---|---|
| One agent assigns and integrates work | No component controls the whole system |
| Global context grows with team size | Local context remains bounded |
| Planner failure can stall the system | One agent failure only loses one contribution |
| Coordination is opaque prompt traffic | Coordination is durable, inspectable artifacts |
| Roles are normally predefined | Roles can emerge from contributions |

Kiro describes three usable network topologies: mesh for rapid convergence in small groups, ring/amorphous for constant per-agent context at large scale, and recency-based swarm for dynamic clustering around current work.

**Experiments**
- Compare a manager-worker system with ring, mesh, and recency flocks on research, coding, and incident-response tasks
- Introduce node failures, stale information, conflicting hypotheses, and tool outages
- Measure throughput, recovery, duplicated work, consensus time, novelty, and quality of final artifacts
- Let agents change topology under budgeted, benchmark-gated conditions

**Search**
```
kiro-flock self-organizing agents
shared state multi-agent coordination
append-only logs AI agents
orchestratorless agent systems
stigmergic agent architecture
```

---

## 33. Fractal Decomposition

**Core idea**: Use recursive decomposition only at unresolved boundaries. A root agent maps a task coarsely, resolves what it can, detects areas of uncertainty or excessive complexity, and creates child agents only for those regions. Every child applies the same compact reasoning contract within a narrower context.

The open-source `fractal` CLI applies hierarchical agent loops in isolated Git worktrees, with configurable constraints on iteration count, recursion depth, child count, cost, and time. A related "Mandelbrot" design frames the system as a hierarchy generated and dissolved around unresolved task boundaries, followed by compression of completed work and resource release.

### Core rule

```
Shared reasoning contract
+ bounded local context
+ explicit unresolved boundary
+ recursive sub-agent creation
+ tested return artifact
+ hierarchical compression
= adaptive problem-shaped organization
```

**What makes it valuable**
- Computation follows problem structure, not a fixed org chart
- Limits context overflow by creating local workspaces
- Avoids permanent agent proliferation: temporary agents terminate after producing validated artifacts
- Supports "zooming" between system-level architecture and line-level implementation

**Experiments**
- Spawn agents only when uncertainty, dependency count, or context pressure crosses a threshold
- Test fixed-depth versus adaptive-depth trees
- Require every child to return one of: resolved artifact, verified uncertainty, blocked dependency, or new boundary map
- Charge a cost for spawning agents; reward compression and reuse

**Search**
```
fractal agent orchestration
recursive task decomposition LLM agents
adaptive agent spawning
hierarchical compression AI agents
bounded context multi-agent systems
```

---

## 34. Artifact Protocols Instead of Chat

**Core idea**: A major design choice is to make artifacts—not conversational messages—the unit of coordination. Agents should collaborate through versioned plans, executable experiments, tests, claims, datasets, decision records, and evidence graphs.

The shared-state flock pattern explicitly centers direction files, append-only logs, and workspace artifacts rather than direct agent-to-agent connections. This is compatible with software-engineering workflows, scientific research, and institutional memory.

### Suggested artifact types

- `claim.md`: A falsifiable claim, evidence, confidence, assumptions, and counterexamples
- `experiment/`: Executable experiment plus seed, environment, metrics, and results
- `skill/`: Procedure with inputs, tools, tests, transfer boundary, and risk rating
- `decision.md`: Decision, alternatives, rationale, reversibility, owner, expiry date
- `failure.md`: Root cause, trace, attempted repairs, and regression test
- `interface.yaml`: Tool/agent contract with permissions, schemas, and version
- `map.json`: Current task graph, unresolved boundaries, dependencies, and assigned budgets

This shifts the swarm from "agents talking about work" to "agents producing inspectable, reusable work."

**Search**
```
artifact centered multi-agent coordination
versioned plans AI agents
executable experiments language models
evidence graphs autonomous agents
scientific workflows AI collaboration
```

---

## 35. Constraint-First Orchestration

**Core idea**: Rather than direct agents toward desired actions, specify constraints that define a flourishing system:

- No irreversible external action without an explicit approval policy
- No skill promotion without hidden-holdout success
- No dominant model, tool, or skill can exceed a concentration threshold
- Every conclusion must preserve source provenance and counterevidence
- Every system-level change must be reversible
- Every agent must expose resource use and uncertainty
- Every long-lived artifact needs an owner, health check, and retirement rule

The orchestrator becomes a constraint solver and observability system, not a micromanager. Agents retain freedom to invent strategies inside the safe feasible region.

**Search**
```
constraint satisfaction agent orchestration
bounded autonomy AI agents
feasible region multi-agent systems
observability driven orchestration
constraint based AI governance
```

---

## 36. Polycentric Governance

**Core idea**: Avoid both one central supervisor and pure agent anarchy. Use polycentric governance: multiple small governance centers, each responsible for different commons.

### Governance domains

| Commons | Steward agents monitor | Failure prevented |
|---|---|---|
| Compute and cost | Budget allocation, queues, consumption spikes | Resource monopolization |
| Memory and knowledge | Provenance, staleness, duplicate claims | Memory corruption |
| Tools and permissions | Capability grants, tool health, policy checks | Privilege escalation |
| Creative diversity | Similarity, niche occupancy, dissent | Monoculture |
| Evaluation | Hidden tests, evaluator disagreement | Reward hacking |
| Social coordination | Trust, collusion, exclusion, harassment | Harmful institutions |

No steward can unilaterally control all domains. High-impact changes require evidence from independent governance roles and are executed through sandboxed promotion.

**Search**
```
polycentric governance AI agents
commons governance autonomous agents
multi-steward agent systems
distributed authority AI
governance domains multi-agent
```

---

## 37. Narrative and Counterfactual Engines

**Core idea**: Most research agents search known literature and optimize known metrics. A distinct creative system should generate counterfactual worlds:

- What if the agent had no persistent text memory but could only inherit executable artifacts?
- What if tools were unreliable 30% of the time?
- What if agents could not use natural language to communicate?
- What if every proposal needed a dissenting implementation?
- What if improving one metric necessarily degraded another?

Counterfactual worlds force systems to produce structural insights rather than optimize familiar benchmarks.

**Experiments**
- Run the same agent population across alternate "physics" of coordination
- Identify policies that transfer across worlds
- Promote only mechanisms robust to altered incentives, information asymmetry, and infrastructure failures
- Use counterfactuals as a creativity measure: how many non-obvious, internally coherent, testable worlds can an agent generate?

**Search**
```
counterfactual world generation AI
narrative engines autonomous agents
alternative physics coordination AI
structural insight generation agents
creativity through constraint AI
```

---

## 38. Cellular Agent Architecture

**Core idea**: Instead of "sessions," build persistent agent cells. A cell is a compact unit containing:

- A local world model
- Working and episodic memory
- A small tool set
- An operational health state
- A local goal and boundary of authority
- A replication or spawning policy
- Interfaces to shared artifacts—not unrestricted global context

Agent cells can form tissues (task teams), organs (specialist subsystems), and organisms (projects). This is compatible with semantic-roaming ideas that compress historical interaction data into self-similar "seeds" rather than retain a massive linear token history.

**Research questions**
- Which information should be encoded in a portable seed versus retained only in the global artifact store?
- Can cells migrate across projects while retaining safe, generalizable skills?
- How much independent memory produces diversity before it creates incoherence?
- Can cells reproduce by forking only when they have a verified specialization gap to fill?

**Search**
```
cellular agent architecture
agent cells persistent memory
semantic roaming AI agents
self-similar seeds interaction data
portable agent identity
```

---

## 39. Deterministic Spine, Generative Edge

**Core idea**: Use a hybrid system:
- **Deterministic spine**: permissions, money movement, deployments, data writes, compliance, CI, rollback, audit trails
- **Generative edge**: research, hypothesis generation, planning, interface proposals, code drafts, anomaly interpretation, creative exploration

A fractal enterprise architecture explicitly separates stable business logic from volatile runtime requirements through a thin orchestration/abstraction layer, retaining deterministic execution while allowing agents to supply information rather than directly control core pipelines.

This is essential for a workforce cloud: agents can be highly creative in proposing action while final consequential execution remains deterministic, policy-bound, and auditable.

**Search**
```
deterministic spine generative edge AI
fractal enterprise architecture AI
hybrid deterministic generative systems
auditable agent execution
policy bound agent action
```

---

## 40. Optionality as a First-Class Metric

**Core idea**: A flourishing system should preserve future option value, not merely maximize immediate task reward.

### Measure option value

- Number of distinct validated strategies per task family
- Diversity of tool paths leading to success
- Count of independent evidence sources and model families supporting a decision
- Fraction of skills with known alternative implementations
- Recovery quality after removal of a dominant agent, tool, or memory source
- Transfer success across shadow worlds

Promote a change only if it improves the Pareto frontier of:
```
capability, safety, cost, creativity, diversity, reversibility
```
—not merely capability.

**Search**
```
option value autonomous agents
Pareto frontier agent improvement
diversity preservation multi-agent
reversibility AI systems
strategy diversity metrics agents
```

---

## 41. Recommended Combined Prototype

Build a **Fractal Flock Research Harness**:

1. A shared artifact store with append-only agent logs
2. A short `direction.md` expressing goals, constraints, and success criteria
3. Local neighborhood topologies that scale without global context
4. Adaptive recursive spawning only for verified unresolved boundaries
5. Versioned artifacts and deterministic tests as the coordination substrate
6. Polycentric evaluator/steward agents governing cost, safety, diversity, and evidence
7. Shadow-world testing before system-level promotion
8. Periodic compression: summarize, archive, terminate temporary cells, preserve only validated seeds and artifacts

This is fundamentally different from a supervisor-worker hierarchy: it is a self-organizing, artifact-mediated, problem-shaped research ecosystem with bounded autonomy and strong institutional memory.

**Search**
```
fractal flock research harness
artifact mediated coordination AI
problem shaped organization agents
bounded autonomy research ecosystem
institutional memory autonomous systems
```

---

**Last Updated**: September 07, 2026  
**Maintainer**: Agentic Universe Team

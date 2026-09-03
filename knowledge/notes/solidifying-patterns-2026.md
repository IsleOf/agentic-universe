# Solidifying Patterns 2026 — What Agentic Universe Should Support

> Type: design rules from converging research + product signals
> Date: 2026‑09‑03
> Sources: arXiv (AgeMem, CMA, SkillsInjector, SelfOrg/ICLR), Kimi K2.6 docs, LangGraph guides, Hermes v0.21.0, Agent Zero v2.11, Codex CLI SKILL.state.

## 1. Minimal scaffolding → maximal emergence

- MIPT 25k-task study (Mar 2026): fixed ordering only → spontaneous roles, competence-based abstention, shallow hierarchies; beats centralized by 14% (p<0.001). Emergent autonomy scales with model capability.
- Design rule: define mission + ordering, not roles. Harvest emergent roles into skills afterward.
- Graph links: `pattern-mission-not-roles`, `paper-drop-the-hierarchy`, `pattern-skill-induction`.

## 2. Unified, continuum memory (not RAG lookup tables)

- **AgeMem** (arXiv 2601.01885): unified LTM+STM as tool-based actions inside the agent policy; RL-trained to decide what/when to store/retrieve/update/summarize/discard; beats separate-memory baselines on 5 long-horizon benchmarks.
- **CMA** (arXiv 2601.09913): persistent storage + selective retention + associative routing + temporal chaining + consolidation into higher-order abstractions; necessary for long-horizon agents; highlights drift/latency/interpretability challenges.
- Design rule: expose memory ops as first-class tools; support temporal chaining and consolidation; don't treat memory as stateless RAG.
- Graph links: `pattern-layered-agent-memory`, `pattern-horizon-amplification`, new nodes `paper-agentic-memory`, `paper-continuum-memory`.

## 3. Dynamic tool/skill injection (context tax is a first-order cost)

- **SkillsInjector** (arXiv 2605.29794): two-stage adaptive method — context planner learns execution-grounded skill preferences and admits an adaptive number of skills; set-aware renderer tailors presentation relative to neighbors.
- Multiple 2026 write-ups: dynamic tool loading injects only needed schemas at runtime, cutting context overhead ~85% and improving routing/safety.
- Design rule: discovery-first, injection-second; register full catalog, defer most tools; inject 3–5 per step; log injected schemas for auditability.
- Graph links: `pattern-dynamic-tool-injection`, new node `paper-skills-injector`.

## 4. Deterministic cyclic orchestration for compliance

- LangGraph is the de facto standard for stateful, cyclic, human-in-the-loop multi-agent workflows: cycles, conditional routing, shared state, checkpointers, interrupt() for approval, recursion limits as loop safeguards.
- Design rule: for compliance-sensitive flows, use cyclic graphs with explicit state schemas, loop limits, and human gates; make loops visible in UI/logs.
- Graph links: `pattern-cyclic-graph-orchestration`, `pattern-hooks-enforcement`, `pattern-plan-canvas-hitl`.

## 5. Massive parallel sub-agent routing (model-native swarms)

- Kimi K2.6 Agent Swarm: up to 300 parallel sub-agents, 4,000 coordinated steps per run; ~4.5×·faster than single-agent sequential; built into the 1T MoE (32B active/token) with parallel-agent RL; outputs are real files (100+ files, 100k-word reviews, 20k-row datasets).
- Design rule: build a parallel worker pool with internal decomposition + reconciliation; track amplification ratio; expect model-native swarm primitives from more vendors.
- Graph links: `pattern-massive-parallel-swarm`, `pattern-horizon-amplification`, `pattern-containerized-agent-workers`.

## 6. Harness-level resilience (repair + compaction)

- Agent Zero v2.11 Context Doctor: repairs malformed tool-call JSON before dispatch; handles incomplete/thoughts-only responses; persists repairs in logs.
- Codex CLI SKILL.state: compact to structured JSON state (not prose) with a schema; validate on every tool use; compact early.
- Design rule: assume dirty output; repair at harness boundary; compact to schema, not prose; validate state on transitions.
- Graph links: `pattern-context-doctor-repair`, `pattern-layered-agent-memory`, `pattern-hooks-enforcement`.

## 7. Fleet control planes (multi-gateway registries)

- Hermes v0.21.0: persistent multi-gateway connections registry (local, remote, Cloud, SSH), profile-scoped refreshes, MCP health checks, deep links; one desktop subscribes to multiple gateways simultaneously.
- Design rule: treat gateways as persistent named links; unify bot/chat rosters across gateways; health-check MCP connectors.
- Graph links: `pattern-multi-gateway-fleet`, `pattern-agent-peer-comms`, `proj-hermes-agent`.

## Candidate experiments (cheap, high-signal)

1. **Memory schema compaction pilot** — replace prose summaries with JSON state schemas; validate on every tool use; measure drift/latency.
2. **Dynamic tool loader prototype** — catalog + defer + inject 3–5 tools/step; log injected schemas; measure context token delta and routing accuracy.
3. **Cyclic compliance workflow** — one compliance-sensitive flow as a cyclic graph with human gates; compare to free-form swarm on auditability and loop incidents.
4. **Parallel reconciliation harness** — decompose a large research task into 20–50 parallel sub-agents; reconcile outputs; track amplification ratio and failure modes.
5. **Fleet registry MVP** — persistent gateway registry with health checks; unify bot/chat rosters; measure operator overhead reduction.

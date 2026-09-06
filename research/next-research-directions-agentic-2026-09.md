# Next Research Directions — Agentic Tooling & Harness Space (2026-09)

**Date:** 2026-09-07 · **Branch:** Agentic Universe (self-improving agentic systems)
**Sources:** GitHub Search API, arXiv, ecosystem directories, X/Twitter, Reddit, vendor docs.

## Executive summary

The agentic infrastructure layer has consolidated around a small set of high-leverage primitives: **plugin-first harnesses**, **MCP tool buses**, **multi-agent orchestration patterns**, **harness-aware evaluation**, **model routing**, and **agentic browser/computer-use**. DeepSeek Harness (DSH) is the most visible new entrant, treating *everything* (models, tools, session log, agent loop, UI) as Cordis plugins. Meanwhile, MCP has become the de-facto tool-interconnect standard, and harness-level differences now swing agent scores by ~24 points independent of model choice.

The highest-ROI research tracks for Agentic Universe are:

1. **Adopt a plugin-first harness abstraction** (DSH/Cordis or OpenHarness-style) so models, tools, memory, and the agent loop are hot-swappable without code changes.
2. **Build an MCP-first tool layer** with a centralized gateway, policy hooks, and signed records; treat MCP as the universal tool bus across frameworks.
3. **Stand up harness benchmarking** (Harness-Bench / Claw-Eval style) to measure scaffolding effects independently from models.
4. **Implement model routing** (Agent-as-a-Router / ACRouter pattern) to optimize cost/performance per task class.
5. **Add agentic browser/computer-use** with deterministic guards and full action logs for legacy-UI automation.
6. **Upgrade memory to hybrid vector+graph** with episodic streams and janitor agents, not just flat RAG.

Each track has concrete repositories, papers, and patterns to fork or reproduce.

## 1. DeepSeek Harness & the plugin-first harness pattern

### What it is

DeepSeek Harness (DSH) is an open-source agent runtime built on the **Cordis** microkernel. Its core claim: **"Everything is a plugin"** — model adapters, tool registries, session logs, sandboxes, scheduling, orchestration, and the Web UI are all Cordis plugins mounted into a shared context.

**Cordis** provides:
- Plugin loading/unloading with lifecycle management.
- Dependency resolution via `inject` declarations.
- A service registry (`ctx.tools`, `ctx.llm`, `ctx.sessions`, etc.).
- Typed events in four modes: `emit`, `waterfall`, `parallel`, `serial`.
- Reversible effects (temporal composability) and reactive coeffects (spatial composability).

**Why it matters:** DSH demonstrates that the agent loop itself can be a plugin, allowing entire orchestration strategies to be swapped via configuration. This directly supports self-improving agents that can rewrite their own control flow without redeploy.

### Ecosystem signals

- **deepseek-ai/deepseek-harness:** 213k+ stars (Aug–Sep 2026).
- **Plugin ecosystem:** `dsh-plugin` topic indexes thousands of repos; curated lists (`awesome-dsh-plugin`, `dsh-market`) surface vision, browser, workflow, UI, and memory plugins.
- **Top plugins (by stars/practical value):**
  - `anywhere-labs/deepseek-harness-desktop` (~10k★): Tauri desktop client with preset plugins.
  - `liustack/modlens` (~2.6k–3.9k★): Vision bridge for text-only models (OCR, layout, semantics).
  - `zhu1089009369/dsh-web-ui` (~3.7k★): Full Web UI suite with dashboards, Git graph, side panels.
  - `nexu-io/open-design` (~88k★): Local-first design engine (prototypes, landing pages, slides, images, video).
  - `volcengine/openviking` (~29k★): Context DB for long-term memory, knowledge bases, RAG, skills.
  - `tt-a11/archify` (~14k★): Architecture diagram/flowchart generation from code repos.
  - `Nagi-ovo/voyager` (~19.5k★): Browser extension + prompt manager for Harness Web UI.
  - `YaoApp/yao` (~7.6k★): Self-hosted agent workstation across desktop/mobile/browser/API.
  - `Q00/ouroboros` (~5.5k★): Agent OS + MCP + DSH plugin for closed-loop task interviewing/evaluation.
  - `dsh-context`, `dsh-agent-teams`, `dsh-vision-toolkit`: context visualization, multi-agent teams, and enhanced vision tools.

### What to adopt

- **Plugin-first architecture:** Even if not using DSH directly, adopt the "everything is a plugin" mindset: models, tools, memory, session log, and the agent loop should be swappable via config.
- **Append-only session logs:** DSH ships with immutable trajectory logs for replay and auditing; this is essential for self-improvement loops.
- **Profiles/bundles:** Named compositions of plugins (profiles) allow different agent personas or task classes to load different capability sets without code changes.

### Concrete next steps

1. **Fork and run DSH** in Web and CLI modes; document plugin installation, profile switching, and session replay.
2. **Build a minimal Cordis-like plugin kernel** for the Agentic Universe harness: service registry, typed events, reversible effects, lifecycle hooks.
3. **Port 2–3 high-value DSH plugins** (e.g., modlens vision, context dashboard, agent teams) as Agentic Universe plugins to validate the abstraction.

## 2. MCP as the universal tool bus

### State of the ecosystem

Model Context Protocol (MCP) has become the **universal standard** for connecting agents to tools and data:
- **10,000+ public MCP servers** (May 2026), 97M monthly SDK downloads.
- **Supported languages:** TypeScript, Python, Java, Kotlin, C#, Swift.
- **Adoption:** Claude Agent SDK, OpenAI Agents SDK (v0.12+), Google ADK, Microsoft Agent Framework, Cursor, VS Code, Goose, Roo Code.
- **Registries:** Smithery (~12k servers), Glama (~4k curated), `awesome-mcp-servers` (~800 hand-curated).

**MCP Apps (2026):** Tools can now return interactive UI components (dashboards, forms, visualizations, multi-step workflows) that render directly in the conversation.

### Why it matters

MCP decouples **tool implementation** from **agent framework**. An Agentic Universe agent can call any MCP server without custom bindings, and a centralized MCP gateway can enforce policy, logging, and rate limits across all agents.

### Concrete next steps

1. **Stand up an MCP gateway** (self-hosted or via a registry) and wire it into the Agentic Universe harness.
2. **Prioritize MCP servers** for data retrieval, code/repo tools, browser automation, and prediction markets.
3. **Add policy hooks** around MCP calls: domain allowlists, human confirmation on consequential actions, full action logs.

## 3. Harness benchmarking & evaluation

### Key findings

- **Harness-level effects dominate:** Harness-Bench shows a **23.8-point gap** between best and worst harness on identical models/tasks; 36% of failures are schema/output-contract violations, not reasoning errors.
- **Skills matter:** SkillsBench 1.1 finds curated skills lift resolution rate from 33.9% → 50.5%; self-generated skills *hurt* by 8–11.5 points.
- **Stamina matters:** StaminaBench shows test-feedback/retry access improves survival up to 12x; even strongest models show a 6x best/worst harness gap.
- **Process scoring shifts rankings:** AgentLens re-scores up to 23.2% of "passes" as lucky blind retries; rankings shift up to 5 positions under process-adjusted scoring.

**Named harnesses in active comparison:** Claude Code, Codex/Codex CLI, Cursor CLI, Gemini CLI, OpenCode, Grok Build, Kimi Code CLI, Aider, OpenHands, SWE-agent, AWS Strands SSA, OpenClaw, Hermes Agent, NanoBot, ZeroClaw, NullClaw, Moltis, Block's goose.

### Benchmarks to adopt

- **Harness-Bench:** 106 oracle-checkable tasks × 6 harnesses × 8 models = 5,088 trajectories; measures harness-only effects.
- **Claw-Eval / ClawBench / ClawMark:** Human-verified tasks across categories, real-website tasks, and long-horizon multimodal coworker scenarios.
- **MCP Atlas (Scale AI):** 1,000 human-verified tasks across 36 containerized MCP servers and 220 tools; top pass rate 83.6% (Gemini 3.5 Flash).
- **OSWorld-Verified:** 361 real desktop tasks on real OSes; computer-use standard.

### Concrete next steps

1. **Reproduce Harness-Bench** on 3–4 candidate harnesses (e.g., OpenClaw, Hermes, NanoBot, a minimal Cordis harness) to quantify scaffolding effects in your stack.
2. **Build an internal golden set** of 50–100 tasks representative of Agentic Universe workloads; score each harness variant before promoting changes.
3. **Add process-level scoring** (not just pass/fail) to detect lucky retries vs real fixes.

## 4. Model routing & cost/performance optimization

### Agent-as-a-Router

**Paper:** *Agent-as-a-Router: Agentic Model Routing for Coding Tasks* (arXiv:2606.22902).
- Problem: No single LLM dominates all tasks; routing is critical for performance and cost.
- Finding: Augmenting a vanilla LLM router with task-dimension performance stats yields a **15.3% relative gain**.
- Framework: **C-A-F loop** (Context → Action → Feedback → Context) to accumulate execution-grounded experience.
- Instantiation: **ACRouter** (Orchestrator, Verifier, Memory) + **CodeRouterBench** (~10K task instances, 8 frontier LLMs).

**Other routers:**
- **Aeonic Core:** Open-source AI/AGI/LLM router and orchestrator for local/cloud, small/frontier models with unified API and observability.

### Concrete next steps

1. **Implement a minimal router** with a task taxonomy, per-model performance stats, and C-A-F feedback updates.
2. **Benchmark 4–6 models** (DeepSeek V4/V4 Pro, Claude, GPT, Kimi, Qwen, GLM) on your golden set.
3. **Integrate with the harness** so every task goes through the router; log regret versus the best observed choice.

## 5. Multi-agent orchestration patterns

### Patterns that work

1. **Fan-out:** Parallel subtasks aggregated by a coordinator.
2. **Pipeline:** Sequential stages with handoffs.
3. **Debate:** Multiple agents propose/argue, a judge selects.
4. **Supervisor:** Central router dispatches to specialized workers.
5. **Swarm (peer handoff):** Agents transfer control directly without a central router.

**Microsoft Agent Framework:** Graph-based workflow primitives, group chat, A2A, and MCP as first-class transports.

**Swarms v14:** AutoAgentBuilder, MCP Manager, multi-agent architectures, sandboxed computer-use tools, GraphWorkflow.

### Concrete next steps

1. **Implement supervisor + swarm patterns** in the Agentic Universe harness using LangGraph or Microsoft Agent Framework as reference.
2. **Add A2A/MCP bridges** so agents in different frameworks can call each other.
3. **Benchmark multi-agent vs single-agent** on long-horizon tasks; measure success rate, cost, and time-to-solution.

## 6. Agentic browser & computer-use automation

### Landscape

**Production stacks:** OpenAI CUA, Anthropic Claude Computer Use, browser-use, Playwright MCP, Stagehand, Browserbase, Steel, and Hyperbrowser.

**Benchmarks:** Online-Mind2Web, WebVoyager, WebArena, OSWorld.

**Security lessons:** domain allowlists; operator instructions only; page content is data rather than instructions; human confirmation for consequential actions; full action logs.

### Concrete next steps

1. **Prototype a browser agent** using Playwright MCP + Claude/GPT CUA for one narrow workflow.
2. **Add deterministic guards:** domain allowlist, action confirmation, full logs, and scope memory per task.
3. **Benchmark against OSWorld / Online-Mind2Web** tasks before production use.

## 7. Memory: hybrid vector + graph + episodic streams

### Recommended stack

1. **Vector DB** (pgvector, Qdrant, Weaviate, Pinecone) for unstructured docs.
2. **Knowledge graph** (Neo4j, Memgraph) for structured relationships.
3. **KV store** (Redis, Postgres) for persistent agent state.
4. **Episodic stream** for time-ordered interaction and execution logs.

**GraphRAG** maps relationships between chunks for multi-hop reasoning. Add a reranker when retrieval scales and janitor agents for summarization/archival.

### Concrete next steps

1. **Implement hybrid memory** (vector + graph + KV + episodic) in the Agentic Universe harness.
2. **Add a reranker** for vector search to preserve precision at scale.
3. **Deploy janitor agents** that propose summaries and archival changes.

## 8. Safety, guardrails, and policy enforcement

- **Permissions layers:** Observe/propose/execute modes, path rules, command deny-lists, pre-execution checks.
- **Lifecycle hooks:** PreToolUse/PostToolUse events for auditing and intervention.
- **Sandboxing:** Subprocess, terminal, and filesystem providers with reversible effects.
- **Scope memory:** Prevent state from one site/task influencing unrelated work.

## Prioritized research plan (4–6 weeks)

| Week | Focus | Deliverables |
|---|---|---|
| 1–2 | Plugin-first harness + MCP gateway | Minimal Cordis-like plugin kernel; MCP gateway; 2–3 DSH-style plugins ported. |
| 2–3 | Harness benchmarking | Harness-Bench reproduction; internal golden set; process-level scoring. |
| 3–4 | Model routing | Minimal router with C-A-F loop; 4–6 model benchmark; router integration. |
| 4–5 | Multi-agent orchestration | Supervisor + swarm patterns; A2A/MCP bridges; multi-agent evaluation. |
| 5–6 | Browser + hybrid memory | Playwright MCP prototype; hybrid memory; janitor agents. |

## Decision rules

- **Adopt plugin-first harness** if you need hot-swappable models, tools, and loops without code changes.
- **Use MCP as the tool bus** for framework-agnostic integration and centralized policy.
- **Benchmark harnesses before choosing a framework;** scaffolding effects can exceed model effects.
- **Route models** when task classes, budgets, or latency requirements differ.
- **Add browser agents** only for narrow, audited workflows with human gates.
- **Use hybrid memory** when flat RAG cannot represent relationships or reliable episodic continuity.

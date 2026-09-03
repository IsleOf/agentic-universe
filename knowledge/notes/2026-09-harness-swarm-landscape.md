# 2026‑09 Harness & Swarm Landscape — Patterns to Steal

> Type: landscape synthesis + pattern extraction
> Date: 2026‑09‑03
> Sources: community write‑ups (Sept 2026), official project releases (Hermes v0.21.0, Agent Zero v2.11, OpenCode v1.18.27, Pi), and cross‑checks against arXiv/MDPI.

## Core thesis (keep this)

**"Agent = Model + Harness"** — the harness is the control plane (memory, tool routing,
approvals, tracing, compaction); the model is the brain. Production stability comes from
the harness, not from prompting alone.

## High‑signal patterns (verified or widely corroborated)

### 1. Dynamic tool injection (DynamicToolLoader)
- Claim: Swarms v15 "Akira" (Sept 1, 2026) injects only the tool schemas needed for the
current step instead of flooding context with 50+ tools.
- Why it matters: context bloat is a first‑order cost driver; step‑relevant tool schemas
improve routing and reduce hallucinated tool use.
- Exploit: build a catalog + selector that loads schemas on demand per subtask; log which
schemas were injected for auditability. (Add as `pattern-dynamic-tool-injection`.)

### 2. Long‑horizon state + automatic compaction
- LangChain Deep Agents / OpenAI Agents SDK / ECC all point to the same pattern: persist
state across hours‑long tasks and compact context at logical breakpoints (not mid‑task).
- Hermes v0.21.0 adds cron agents with `continuity=true` and durable notepads; Agent Zero
v2.11 adds a context‑usage indicator and provider token accounting through streaming.
- Exploit: treat compaction as a first‑class operation with explicit triggers; carry
provider‑reported token usage and cost through the stream (don't synthesize it).

### 3. Deterministic cyclic graph orchestration (LangGraph)
- LangGraph remains the production default for complex, stateful multi‑agent workflows:
explicit cyclic graphs, human‑in‑the‑loop gates, deterministic branching.
- Exploit: for compliance‑sensitive flows, prefer cyclic graphs over free‑form swarms;
make loops and gates visible in the UI/logs.

### 4. Massive parallel sub‑agent routing (Kimi K2.6)
- Claim: Kimi K2.6 swarm coordinates up to 300 parallel sub‑agents and 4,000 steps per
prompt, handling decomposition and failure recovery internally.
- Why it matters: horizontal scaling is now a harness feature, not an app‑level hack.
- Exploit: build a parallel worker pool with internal task decomposition + retry logic;
track an amplification ratio (system horizon / agent horizon) à la SWARM.

### 5. Containerized worker pools (agent‑swarm.dev / ECC worktrees)
- "Agentic OS" pattern: lead agent breaks goals into tasks, dispatches to containerized
specialized workers, preserves a global shared memory pool.
- ECC's worktree isolation (superset‑sh/superset, stablyai/orca, standardagents/dmux)
maps onto this: parallel agents in isolated worktrees with diff review.
- Exploit: run specialized agents in isolated containers/worktrees; share memory via a
vault keyed by project/session; require diff review before merging.

### 6. Harness‑boundary repair (Agent Zero "Context Doctor")
- Assume model output is dirty: repair malformed tool‑call JSON before dispatch, handle
incomplete/thoughts‑only responses, persist repaired output in logs.
- Exploit: add a repair layer at the harness boundary; treat it as resilience, not
prompt engineering. (Already captured as `pattern-context-doctor-repair`.)

### 7. Fleet control plane (Hermes multi‑gateway registry)
- Hermes v0.21.0 maintains a persistent registry of local, cloud, SSH, and remote agents
in one control plane; `hermes peer` provides durable bot‑to‑bot DMs.
- Exploit: build a gateway registry with health checks; make agent‑to‑agent comms durable
and inspectable (not fire‑and‑forget).

### 8. Minimalism pole (Pi)
- Pi (badlogic→earendil‑works, ~95k stars): 4 built‑in tools, session trees, hot‑reloadable
self‑extensions, deliberately no MCP, 40+ providers. Sessions publishable to Hugging Face.
- Exploit: for low‑overhead coding agents, prefer the minimal harness + self‑extensions
pattern; avoid hidden context injection and vendor lock.

## Claims to verify before baking into the graph

- **Visa Vulnerability Agentic Harness (VVAH)** — described as built on Anthropic's
"Project Glasswing" learnings, running a 4‑phase SAST pipeline. I can't find primary
sources for VVAH or Glasswing in the last 60 days; treat as anecdotal until you have a
repo/whitepaper.
- **Swarms v15 "Akira" (Sept 1, 2026)** — plausible, but I'd want the official changelog
before pinning version numbers in the graph. Keep the DynamicToolLoader pattern regardless.
- **Microsoft Agent Framework ".AsHarnessAgent()"** — sounds like an internal wrapper
pattern (local FS memory, artifact tracking, enterprise telemetry). Keep the pattern,
ignore the exact API name until you see docs.
- **agent‑swarm.dev (Desplega Labs)** — no primary link at hand; verify before adding as
a canonical node.

## Cross‑links to existing notes

- `knowledge/notes/harness-space-scan-2026-09.md` — Hermes v0.21.0, Agent Zero v2.11,
OpenCode v1.18.27, Pi.
- `knowledge/notes/emergent-swarm-behavior-scan-2026-09.md` — horizon amplification,
pressure‑field coordination, heterogeneous collectives.
- `knowledge/notes/ecc-agent-harness-patterns.md` — worktree isolation, verifier‑gated
improvement, AgentShield supply‑chain security.

## Candidate additions to the graph (patterns)

- `pattern-dynamic-tool-injection` — on‑demand tool schema loading per step.
- `pattern-cyclic-graph-orchestration` — deterministic cyclic graphs + human gates.
- `pattern-massive-parallel-swarm` — internal decomposition + failure recovery at scale.
- `pattern-containerized-agent-workers` — isolated worker pools + shared memory vault.
- `pattern-multi-gateway-fleet` — persistent gateway registry + durable A2A comms.

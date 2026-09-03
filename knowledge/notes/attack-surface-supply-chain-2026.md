# Attack Surface & Supply‑Chain 2026 — Agentic Universe Threat Model

> Type: infrastructure‑level threat model confirmed by Sept‑2026 searches
> Date: 2026‑09‑03
> Sources: SkillBloat token‑amplification, OWASP Agentic Skills Top 10, GitHub MCP allowlists, CSA trust‑boundary flaw, AOS/runtime split, SKILL.state compaction risks, Hermes v0.21.0 fleet, OpenAI/ADK/Mastra shifts.

## 1. Skills are executable code from untrusted sources

- **SkillBloat** (arXiv 2608.21929): token‑amplification attacks via malicious skill injection; 5.4×·–10.1×· average best amplification; two‑stage pipeline screens attack types then optimizes amplification [web:491][web:498].
- **OWASP Agentic Skills Top 10** (Aug 17, 2026): nine solved supply‑chain risks, one new gap — skills act like dependencies without lockfiles; typosquatting, trojanized skills, and hidden shell commands observed in the wild [web:504][web:505][web:506][web:507][web:508][web:509][web:510][web:511][web:512][web:513][web:514][web:515][web:516][web:517][web:518].
- **Design rule:** treat skills as executable code; pin versions; verify signatures; run in ephemeral sandboxes; log injected schemas; measure retrieval precision as catalogs grow [web:490][web:492][web:493][web:494][web:495][web:496][web:497][web:499][web:500][web:501][web:502][web:503].

## 2. MCP servers are governed dependencies — allowlists are now standard

- **GitHub MCP allowlists** (Aug 6, 2026): `allowedMcpServers`/`deniedMcpServers` in enterprise managed settings; enforced in Copilot app, CLI, VS Code; deny‑wins, fail‑closed default; URL and argv matchers [web:430][web:433][web:434][web:435][web:438].
- **CSA trust‑boundary flaw**: agents misinterpret appearance of safety controls (dialogs, VMs, scoped creds) as enforcement; requires mediation layer between agents and tools [web:329][web:330][web:332][web:334].
- **Design rule:** place HITL at the gateway, not inside each agent; scope approvals to requester/server/tool; centralize audit evidence; treat MCP servers as governed dependencies with tenant allowlists [web:384][web:386][web:387][web:388][web:389][web:390][web:391][web:392].

## 3. Agentic OS vs runtime split — enforce inline at the boundary

- **Agentic OS vs context platform**: OS coordinates what agents *do* (memory, tools, each other) with a human on the loop; context platform governs what agents *know/trust* [web:349].
- **Agent Operating System (AOS)** reference architecture: two internal planes — Control & Governance (intent, policy, trust, authority, audit, HITL) and Runtime & Coordination (lifecycle, workflow, model/tool routing, context/memory, scheduling, traffic, assurance) [web:350].
- **Micro‑harnesses vs AgentOS**: lightweight kernels (Pi, Ante, Aider, Goose) vs full‑stack platforms (Antigravity, Claude Code, Opencode, Copilot) with supervisor‑subagent hierarchies, dynamic tool discovery, ReBAC access controls, structured artifact stores [web:362].
- **Design rule:** treat the runtime boundary as infrastructure; enforce inline allowlists for network, file, process, and tool actions; separate evaluation agents from production trust zones [web:356][web:357][web:358].

## 4. Compaction is a primitive — but can erase safety rules

- **SKILL.state** (arXiv 2608.26263): replaces append‑only history with explicit mutable execution state; each step receives only skill spec + current state + latest observation; intermediate reasoning discarded after validated state update; 93.8% token reduction in warehouse test, often higher accuracy [web:477][web:478][web:479][web:480][web:481][web:482][web:483][web:484].
- **Compaction risk**: compaction can silently erase safety rules — violation rates rise 0%→30% after one compaction step, up to 59% for some models [web:469][web:476][web:485][web:486][web:487][web:488][web:489].
- **Design rule:** compact to schema (JSON) not prose; validate state on transitions; keep policies outside the agent's edit surface, enforced at the gateway [web:469][web:476].

## 5. Fleet control planes & framework shifts

- **Hermes v0.21.0 Pantheon**: Bot Mode in desktop, `hermes peer` for bot‑to‑bot DMs across gateways, persistent multi‑gateway registry, cron continuity, live subagent steering [web:443][web:444][web:445][web:446][web:447][web:448][web:449].
- **OpenAI Agents SDK**: native sandbox execution, model‑native harness; Responses API is the primary primitive for agent runs [web:535][web:536][web:538][web:539].
- **Google ADK 2.0**: Agent Skills with progressive disclosure; structured Task API for agent‑to‑agent delegation [web:519][web:526][web:532].
- **Mastra**: TypeScript‑first, batteries‑included (agents, workflows, memory, evals, MCP, Studio) [web:520][web:521][web:522][web:523][web:524][web:525][web:526][web:527][web:528][web:529][web:530][web:531].
- **LangGraph vs CrewAI**: LangGraph for production stateful orchestration; CrewAI for fastest multi‑agent prototyping (role‑based) [web:429][web:431][web:432][web:436][web:439][web:440][web:441][web:442].

## Candidate experiments (cheap, high‑signal)

1. **Skill allowlist pilot**: one internal skill registry with signed skills; pin versions; measure retrieval precision as catalog grows; log injected schemas.
2. **MCP allowlist audit**: inventory all MCP servers; enforce allowlist at gateway; measure catch rate over 30 days; remove zero‑catch gates; add one gate on a high‑blast‑radius action missing coverage.
3. **Compaction safety test**: run one long‑horizon task with JSON‑state compaction; validate state on every tool use; measure drift/latency; track policy violations before/after compaction.
4. **Fleet registry MVP**: persistent gateway registry with health checks; unify bot/chat rosters; measure operator overhead reduction.
5. **Parallel reconciliation harness**: decompose a large research task into 20–50 parallel sub‑agents; reconcile outputs; track amplification ratio and failure modes.

## Cross‑links to existing notes

- `knowledge/notes/structural-primitives-2026.md` — design rules + candidate experiments.
- `knowledge/notes/protocol-governance-deprecations-2026.md` — A2A/MCP foundation moves, HITL gates, deprecations.
- `knowledge/notes/solidifying-patterns-2026.md` — cyclic orchestration, dynamic tools, compaction, parallel swarms.
- `knowledge/notes/harness-space-scan-2026-09.md` — Hermes v0.21.0, Agent Zero v2.11, OpenCode v1.18.27, Pi.

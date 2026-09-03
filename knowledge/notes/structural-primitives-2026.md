# Structural Primitives 2026 — What Agentic Universe Should Treat as Infrastructure

> Type: infrastructure‑level patterns confirmed by Sept‑2026 searches
> Date: 2026‑09‑03
> Sources: A2A/MCP specs & foundation moves, Forrester AEGIS + "Stop Means Stop", OpenAI/Azure deprecations, LHTB benchmark, Kimi K2.6 Agent Swarm, SkillsInjector/MUSE‑Autoskill/ADK 2.0, Hermes v0.21.0 fleet.

## 1. Two‑protocol stack is canonical: MCP (vertical) + A2A (horizontal)

- **MCP 2026‑07‑28**: fully stateless core (no initialize handshake, no `Mcp‑Session‑Id`); every request self‑describing; cacheable lists; MRTR for mid‑call inputs; header‑based routing; hardened OAuth/OIDC [web:305][web:306][web:308][web:309][web:310][web:311][web:312][web:313][web:314].
- **A2A v1.0→v1.2**: signed Agent Cards, multi‑tenancy, gRPC; joined Agentic AI Foundation alongside MCP (Aug 17, 2026); 150+ orgs; discovery via `/.well‑known/agent‑card.json` with cryptographic signatures to prevent redirection/impersonation [web:182][web:183][web:184][web:185][web:186][web:187][web:188][web:307][web:315].
- **Design rule:** explicit vertical/horizontal split — MCP for tools/data access; A2A for cross‑org agent delegation with signed cards [web:91][web:92][web:93][web:94][web:95][web:96][web:97][web:98][web:99][web:100][web:101][web:102][web:103][web:104][web:105].

## 2. HITL gates are binding controls — and many don't actually enforce

- **Forrester AEGIS** (39 controls, 6 domains) maps to NIST AI RMF, ISO 42001, EU AI Act, MITRE ATLAS; mandates approval gates for irreversible/high‑consequence actions [web:175][web:177][web:178][web:179][web:180][web:181].
- **"Stop Means Stop" (arXiv 2607.14166):** six popular frameworks' gates/timeouts don't actually block side effects; repairs with SOUNDGATE (external Rust gate, complete mediation) [web:176].
- **Design rule:** treat gates as a control primitive you verify, not assume; log approvals; audit quarterly [web:116][web:120].

## 3. Vendor deprecations force portable harness design

- **OpenAI Assistants API sunset:** Aug 26, 2026 (hard shutdown); replacement is Responses + Conversations APIs; no automated thread migration [web:266][web:267][web:268][web:269][web:270][web:271][web:272][web:273][web:274][web:275][web:276][web:277][web:278][web:279].
- **Agent Builder + Evals + v1/prompts:** shut down Nov 30, 2026; Evals goes read‑only Oct 31, 2026 [web:280][web:281][web:282][web:283][web:284][web:285][web:286][web:287][web:288][web:289][web:290][web:291][web:292].
- **Azure Assistants retired same day;** migration to Foundry Agents (classic retires Mar 31, 2027) [web:293].
- **Design rule:** own the loop; prefer Responses‑style primitives + open orchestration SDKs; avoid vendor canvas lock‑in [web:124][web:125][web:126].

## 4. Long‑horizon benchmarks expose a completion cliff

- **Long‑Horizon‑Terminal‑Bench (LHTB):** 46 tasks, hundreds of episodes, 90‑minute budgets; 64.6% of runs make partial progress, only 4.3% cross 0.95 reward; mean 9.9M tokens, 85.3 minutes/task [web:204][web:205][web:210][web:211][web:213][web:216].
- **GLM 5.3's big gains are on long‑horizon work** (Terminal‑Bench 3.0: 4.6→28.3) [web:206][web:207][web:208][web:209][web:212][web:214][web:215].
- **Design rule:** treat compaction as first‑class; compact to schema (JSON) not prose; validate state on transitions; measure long‑horizon reward, not just task success [web:122][web:123][web:133].

## 5. Massive parallel swarms are model‑native now

- **Kimi K2.6 Agent Swarm:** 300 parallel sub‑agents, 4,000 coordinated steps/run; ~4.5×·faster than single‑agent sequential; PARL trains only the orchestrator, sub‑agents frozen [web:217][web:218][web:219][web:220][web:221][web:222][web:223][web:224][web:225][web:226][web:227][web:294][web:295][web:296][web:301].
- **Design rule:** build a parallel worker pool with internal decomposition + reconciliation; track amplification ratio; expect model‑native swarm primitives from more vendors [web:78][web:79][web:80][web:81][web:82][web:83][web:84][web:85][web:86][web:87][web:88][web:90].

## 6. Progressive skill disclosure is standard — retrieval is the bottleneck

- **Skills work mainly via procedural anchoring (65.7%),** not knowledge injection (4.5%); retrieval precision collapses as pools grow (5→100 skills: 29.6%→3.3%) [web:190][web:193][web:196][web:198][web:199][web:200][web:203].
- **MUSE‑Autoskill:** five‑stage skill lifecycle (creation, memory, management, evaluation, refinement) with skill‑level `.memory.md` [web:191][web:192][web:194][web:195][web:197][web:201][web:202].
- **Google ADK 2.0:** progressive skill loading (L1 metadata ~100 tokens, L2 instructions ≤5k tokens, L3 resources on demand) [web:226].
- **Design rule:** progressive disclosure + adaptive admission (3–5 skills/tools per step); log injected schemas; measure retrieval precision under growth [web:106][web:107][web:108][web:109][web:136][web:137][web:138][web:139][web:140][web:141][web:142][web:143][web:144][web:145][web:146][web:147][web:161][web:162][web:163][web:164][web:165][web:166][web:167][web:168][web:169][web:170][web:171][web:172][web:173][web:174].

## 7. Fleet control planes are production now

- **Hermes v0.21.0:** persistent multi‑gateway registry (local, remote, Cloud, SSH), `hermes peer` for bot‑to‑bot DMs across gateways, subagent steering, cron with continuity [web:297][web:298][web:299][web:300][web:302][web:303][web:304].
- **Design rule:** treat gateways as persistent named links; unify bot/chat rosters across gateways; health‑check MCP connectors [web:62][web:64][web:65][web:66].

## Candidate experiments (cheap, high‑signal)

1. **Two‑protocol pilot:** one internal MCP gateway + one A2A server; exercise cross‑team delegation; log discovery/negotiation failures.
2. **HITL gate audit:** inventory all gates; measure catch rate over 30 days; remove zero‑catch gates; add one gate on a high‑blast‑radius action missing coverage.
3. **LHTB stress test:** run one long‑horizon task (90‑minute budget) with JSON‑state compaction; validate state on every tool use; measure drift/latency.
4. **Parallel reconciliation harness:** decompose a large research task into 20–50 parallel sub‑agents; reconcile outputs; track amplification ratio and failure modes.
5. **Progressive skill loader:** catalog + defer + inject 3–5 skills/step; log injected schemas; measure context token delta and routing accuracy.
6. **Fleet registry MVP:** persistent gateway registry with health checks; unify bot/chat rosters; measure operator overhead reduction.

## Cross‑links to existing notes

- `knowledge/notes/protocol-governance-deprecations-2026.md` — A2A/MCP foundation moves, HITL gates, deprecations.
- `knowledge/notes/solidifying-patterns-2026.md` — cyclic orchestration, dynamic tools, compaction, parallel swarms.
- `knowledge/notes/harness-space-scan-2026-09.md` — Hermes v0.21.0, Agent Zero v2.11, OpenCode v1.18.27, Pi.

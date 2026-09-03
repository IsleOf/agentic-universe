# Protocol + Governance + Deprecations (Sept 2026)

> Type: structural shifts at the protocol/governance layer
> Date: 2026‑09‑03
> Sources: A2A/MCP foundation moves (Aug 2026), Forrester AEGIS/CSA guidance, Microsoft MCP guidance, OpenAI/Azure Assistants sunset (Aug 26, 2026), Google ADK 2.0, long‑horizon harness/compaction papers.

## A. Two‑protocol stack is canonical: MCP (vertical) + A2A (horizontal)

- **A2A joined the Agentic AI Foundation** alongside MCP (Aug 17, 2026); A2A 1.0 (Mar 2026) ships signed Agent Cards, multi‑tenancy, three bindings [web:91][web:94][web:100][web:102].
- **MCP 2026‑07‑28** made the core stateless; A2A handles agent‑to‑agent discovery/delegation across org boundaries [web:94][web:97][web:98][web:101].
- Consensus: **MCP = vertical** (agent→tools/data), **A2A = horizontal** (agent↔agent task negotiation) [web:92][web:93][web:95][web:96][web:99][web:103][web:104][web:105].
- **Design rule:** architect an explicit two‑layer separation — MCP client/gateway for tool/data access; A2A client/server for cross‑team/external agent delegation.

## B. Human‑in‑the‑loop (HITL) gates are becoming binding controls

- **Forrester AEGIS + CSA guidance:** require HITL approval gates for irreversible/high‑consequence actions, intent‑classification taxonomy, multi‑stakeholder governance boards [web:110][web:113][web:114][web:119].
- **Microsoft MCP guidance (Jun 30, 2026):** tenant allowlists for MCP servers, runtime output inspection, mandatory human approval for high‑impact actions [web:111][web:112].
- **"Stop Means Stop" (arXiv 2607.14166):** many open‑source frameworks' gates/timeouts don't actually enforce — treat gates as a control primitive you must verify, not assume [web:120].
- **Design rule:** place gates on irreversible/high‑blast‑radius actions; log who approved what and why; audit gates quarterly and remove those with zero catches over 90 days [web:116].

## C. Vendor deprecations force portable harness design

- **OpenAI Assistants API sunset:** Aug 26, 2026; replacement is Responses + Conversations APIs; Agent Builder/Evals close Nov 30, 2026 [web:121][web:124][web:125][web:126][web:127][web:128][web:129][web:130][web:131][web:132][web:134].
- **Azure Assistants retired same day;** migration target is Microsoft Foundry Agents (classic retires Mar 31, 2027) [web:131][web:134][web:135].
- **Design rule:** own the loop; prefer Responses‑style primitives + open orchestration SDKs; avoid vendor canvas lock‑in where exit cost is high [web:124][web:125][web:126].

## D. Long‑horizon harnesses + compaction are explicit primitives

- **Microsoft Harness Agent:** wires compaction into the per‑service‑call history pipeline; compaction is off by default, enabled via token settings [web:122].
- **Long‑Horizon Terminal‑Bench (LHTB):** 46 tasks over hundreds of steps with 90‑minute budgets; frontier models show meaningful gaps on sustained work [web:123].
- **GLM 5.3 gains are largest on long‑horizon work** (Terminal‑Bench 3.0: 4.6→28.3) [web:133].
- **Design rule:** treat compaction as first‑class; compact to schema (JSON) not prose; validate state on transitions; measure long‑horizon reward, not just task success [web:122][web:123][web:133].

## E. Skill injection is standard, but retrieval is the bottleneck

- **Google ADK 2.0:** ships Agent Skills with progressive disclosure (list/load/run); structured Task API for agent‑to‑agent delegation [web:106][web:115][web:117].
- **MUSE‑Autoskill + "Demystifying Agent Skills" (arXiv 2608.14036):** skills work mainly via procedural anchoring (65.7% of cases), not knowledge injection; retrieval precision collapses as pools grow (5→100 skills: 29.6%→3.3%) [web:107][web:108].
- **SkillBloat (arXiv 2608.21929):** token‑amplification attacks via skill injection — another reason to inject adaptively, not dump catalogs [web:109].
- **Design rule:** progressive disclosure + adaptive admission (3–5 skills/tools per step); log injected schemas; measure retrieval precision under growth [web:106][web:107][web:108][web:109].

## Candidate experiments (cheap, high‑signal)

1. **Two‑protocol pilot:** one internal MCP gateway + one A2A server; exercise cross‑team delegation; log discovery/negotiation failures.
2. **HITL gate audit:** inventory all gates; measure catch rate over 30 days; remove zero‑catch gates; add one gate on a high‑blast‑radius action missing coverage.
3. **Compaction schema pilot:** replace prose summaries with JSON state schemas on one long‑horizon flow; validate on every tool use; measure drift/latency.
4. **Adaptive skill loader:** catalog + defer + inject 3–5 skills/step; log injected schemas; measure context token delta and routing accuracy.
5. **Deprecation dry‑run:** migrate one Assistants‑API workload to Responses/Conversations (or Foundry Agents) end‑to‑end; document migration friction and exit cost.

## Cross‑links to existing notes

- `knowledge/notes/solidifying-patterns-2026.md` — cyclic orchestration, fleet registries, dynamic tool injection.
- `knowledge/notes/harness-space-scan-2026-09.md` — Hermes v0.21.0, Agent Zero v2.11, OpenCode v1.18.27, Pi.
- `knowledge/notes/ecc-agent-harness-patterns.md` — verifier‑gated improvement, AgentShield supply‑chain security.

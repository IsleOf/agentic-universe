# Novel Angles & Experiments 2026 — Under‑Explored Edges for Agentic Universe

> Type: infrastructure‑level opportunities confirmed by Sept‑2026 searches
> Date: 2026‑09‑03
> Sources: cost‑utility alignment, real‑time caps/anomaly detection, schema governance, HITL UX/fatigue, agent identity/federation, temporal logic/runtime verification, physical/edge/digital twins, red‑team/forensics, privacy/residency/lineage, RAG precision/drift, meta‑learning, multi‑modal limits, marketplace dynamics.

## 1. Cost‑utility alignment & real‑time control

- **Real‑time caps & anomaly detection**: Google Cloud project‑level spend caps, deferred execution, anomaly detection; Bigeye AI cost anomaly detection flags spend by agent/user/workspace [web:582][web:583][web:584][web:585][web:586][web:587].
- **Token‑level control**: Microsoft TokenOps, Anthropic session dollar caps, Operant token metering; budget APIs update too slowly (up to 3×·/day) vs agent loops — enforce at the tool call [web:588][web:589][web:590][web:591][web:592][web:593][web:594][web:595].
- **Cost‑utility profiling**: arXiv 2608.26195 profiles cost (tokens, latency, fees, risk) vs utility only at aggregate task level; proposes attribution, diagnosis, adaptation loops [web:596].
- **Design rule:** treat cost control as a runtime primitive — hard caps per session/agent, exponential backoff, max iteration limits, per‑tool telemetry tagged with cost centers [web:588][web:591][web:594][web:602][web:603][web:604][web:605][web:606][web:607][web:608][web:609][web:610].

## 2. Data contracts & schema governance

- **Structured outputs need schemas + validation**: Providers support schema‑constrained JSON, but subsets differ; enforce small, purpose‑built schemas with business validation and authorization [web:556][web:559][web:560][web:565][web:566].
- **Tool output contracts**: Agent reliability playbooks emphasize tool‑calling contracts, retries/idempotency, timeouts, durable execution, CI evaluation with observability [web:560][web:562][web:563][web:564].
- **Design rule:** define explicit tool output schemas; validate on ingress/egress; version agent APIs and deprecate with live inventories; treat structured outputs as untrusted until validated [web:556][web:557][web:558][web:559][web:560][web:561][web:562][web:563][web:564][web:565][web:566][web:567].

## 3. HITL UX & approval ergonomics

- **Approval fatigue is an attack surface**: Attackers write prompts to trigger fatigue; measure throughput, false positives, queue age; design for rejection, not just approval [web:611][web:613][web:614][web:615][web:616][web:617][web:618][web:619][web:620][web:621][web:622][web:623][web:624].
- **Timeout semantics**: Timeouts should mean rejection, not consent; per‑item ActionReviewCards and durable approvals (e.g., Vercel `requestApproval`) prevent silent consent [web:617][web:620][web:622][web:623][web:624].
- **Escalation SLAs**: Named queues with SLAs the team can meet; route blocked actions explicitly; preserve partial work and customer‑safe updates [web:575][web:576][web:577][web:578][web:579][web:580][web:581].
- **Design rule:** build approval dashboards with evidence panels, one‑click overrides, and explicit timeout→reject semantics; instrument abstain rates and queue age [web:611][web:612][web:613][web:614][web:615][web:616][web:617][web:618][web:619][web:620][web:621][web:622][web:623][web:624].

## 4. Agent identity, federation & trust fabrics

- **Agent identity is first‑class**: Okta Agent SSO, Rubrik Agent Identity, Google SPIFFE‑based agent identities; IETF drafts on cross‑org delegation and attenuated delegation chains [web:655][web:656][web:657][web:658][web:659][web:660][web:661][web:662][web:663][web:664][web:665][web:666][web:667][web:668].
- **A2A for cross‑org collaboration**: Signed Agent Cards, discovery, secure cross‑org task negotiation/delegation [web:661][web:662][web:663][web:664][web:665][web:666][web:667][web:668][web:187][web:634][web:637].
- **Design rule:** treat agent identities like workload identities (SPIFFE, DPoP, Workload Identity Federation); support attenuated delegation with verifiable chains; centralize agent registries for multi‑tenant governance [web:655][web:656][web:657][web:658][web:659][web:660][web:661][web:662][web:663][web:664][web:665][web:666][web:667][web:668].

## 5. Formal methods & runtime verification

- **Temporal logic for compliance**: AgentLTL (FO‑LTL over traces); AWS Dogwood extends Cedar with temporal rules for tool calls (prior approval, time caps, trace replay) [web:640][web:641][web:642][web:643][web:644][web:645][web:646][web:647][web:648][web:649][web:650][web:651][web:652][web:653][web:654].
- **Proof‑carrying patches & attestation**: Bounded code changes with deterministic evidence; runtime attestation (TRACE v0.2, IETF RATS/EAT, in‑toto, SCITT) [web:646][web:648][web:649][web:650][web:651][web:652][web:653][web:654].
- **Design rule:** adopt runtime verification languages (Dogwood/Cedar+temporal) for safety policies; require proof‑carrying patches for high‑risk actions; instrument runtime evidence outside the agent's process boundary [web:640][web:641][web:642][web:643][web:644][web:645][web:646][web:647][web:648][web:649][web:650][web:651][web:652][web:653][web:654].

## 6. Physical/edge agents & digital twins

- **Physical safety layers**: Anthropic MHS for lab equipment; AgenticTwin/AgenticTwins integrate LLM agents with digital twins for anomaly detection and autonomy [web:669][web:698][web:699][web:700][web:701][web:702][web:703][web:704][web:705][web:706][web:707][web:708][web:709][web:710][web:711][web:712].
- **Edge runtimes**: Telnyx Edge Compute runs entire real‑time voice agents on edge infrastructure [web:670][web:671][web:680].
- **Design rule:** separate physical safety layers from logical orchestration; use digital twins as world models; deploy edge runtimes for latency‑sensitive or region‑bound workloads [web:669][web:698][web:699][web:700][web:701][web:702][web:703][web:704][web:705][web:706][web:707][web:708][web:709][web:710][web:711][web:712].

## 7. Red‑team & failure forensics

- **Executable red teaming**: REDAgentBench, MiDojo, DeepTeam provide realistic attack techniques for tool calls, stateful exploits, multi‑turn jailbreaks [web:683][web:684][web:685][web:686][web:687][web:688][web:689][web:690][web:691][web:692][web:693][web:694][web:695][web:696][web:697].
- **Forensics & IR**: Trace debugging, first‑divergence analysis; NIST‑aligned AI IR overlays (aiiroverlay) for first 72‑hour runbooks [web:686][web:687][web:688][web:689][web:690][web:691][web:692][web:693][web:694][web:695][web:696][web:697].
- **Design rule:** run continuous red‑team exercises (not one‑off prompt tests); instrument traces with span‑level inputs/outputs; build IR runbooks specific to agent incidents [web:683][web:684][web:685][web:686][web:687][web:688][web:689][web:690][web:691][web:692][web:693][web:694][web:695][web:696][web:697].

## 8. Privacy, residency & lineage

- **Runtime evidence for residency/GDPR**: Static region selection can't prove compliance; tool calls, retrievals, delegations create dynamic data trajectories — require runtime evidence and per‑region inference/retrieval [web:724][web:725][web:726][web:727].
- **Agent lineage & registries**: Trace decisions back through tools, model, prompts, data; agent registries solve shadow AI by recording ownership, identity, data flows [web:728][web:729][web:730][web:731][web:732][web:733][web:734][web:735][web:736][web:737][web:738][web:739][web:740][web:741].
- **Design rule:** deploy agents close to data (per region); centralize only metadata/performance signals; build agent registries with lineage tracking; separate low‑risk conversational flows from high‑risk tool‑using agents [web:724][web:725][web:726][web:727][web:728][web:729][web:730][web:731][web:732][web:733][web:734][web:735][web:736][web:737][web:738][web:739][web:740][web:741].

## 9. RAG governance & knowledge curation

- **Retrieval precision collapse**: Precision drops 29.6%→3.3% as skill pools grow 5→100; skills work via procedural anchoring (65.7%), not knowledge injection (4.5%) [web:451][web:452][web:454][web:455][web:456][web:459][web:460][web:461].
- **Knowledge drift & source attribution**: Production agents need compaction, caching, extraction, temporal memory graphs to avoid repeated history bleed and stale facts [web:541][web:542][web:543][web:544][web:545][web:546][web:547][web:548][web:549][web:550][web:551][web:552][web:553][web:554][web:555].
- **Design rule:** progressive disclosure + adaptive admission (3–5 skills/tools per step); log injected schemas; measure retrieval precision under growth; use temporal knowledge graphs for fact evolution [web:451][web:452][web:454][web:455][web:456][web:459][web:460][web:461][web:541][web:542][web:543][web:544][web:545][web:546][web:547][web:548][web:549][web:550][web:551][web:552][web:553][web:554][web:555].

## 10. Self‑improvement & meta‑learning

- **Continuous testing loops**: Pre‑merge checks, CI gates, release sign‑off, production feedback that writes tests; agent self‑verification has ceilings (text/DOM yes, 3D/video/physics no) [web:625][web:626][web:627][web:628][web:629][web:630][web:631][web:632][web:633].
- **Automatic skill synthesis**: MUSE‑Autoskill five‑stage lifecycle (creation, memory, management, evaluation, refinement) with skill‑level `.memory.md` [web:453][web:454][web:455][web:456].
- **Design rule:** build meta‑learning loops that synthesize/retire skills based on retrieval precision and task success; measure self‑verification accuracy vs independent verifiers [web:453][web:454][web:455][web:456][web:625][web:626][web:627][web:628][web:629][web:630][web:631][web:632][web:633].

## 11. Multi‑modal & embodied limits

- **Multi‑modal verification ceilings**: Agent self‑verification works for text/DOM but fails for 3D, video, physics; embodied agents need world models (digital twins) and physical safety layers [web:630][web:669][web:698][web:699][web:700][web:701][web:702][web:703][web:704][web:705][web:706][web:707][web:708][web:709][web:710][web:711][web:712].
- **Design rule:** treat multi‑modal outputs as unverified unless backed by external validators; use digital twins as structured world models for embodied reasoning [web:630][web:669][web:698][web:699][web:700][web:701][web:702][web:703][web:704][web:705][web:706][web:707][web:708][web:709][web:710][web:711][web:712].

## 12. Ecosystem & marketplace dynamics

- **Discovery & reputation**: A2A signed Agent Cards enable discovery; agent marketplaces face typosquatting/trojanized skills (1.7M installs in one attack) [web:504][web:505][web:506][web:507][web:508][web:509][web:510][web:511][web:512][web:513][web:514][web:515][web:516][web:517][web:518][web:661][web:662][web:663][web:664][web:665][web:666][web:667][web:668].
- **Monetization & pricing**: Usage‑based pricing when consumption ties to outcomes; agent billing telemetry must tag every request with cost centers, retries, cache hits [web:507][web:508][web:509][web:510][web:511][web:512][web:513][web:514][web:515][web:516][web:517][web:518][web:602][web:603][web:604][web:605][web:606][web:607][web:608][web:609][web:610].
- **Design rule:** build agent registries with signed skills, version pinning, and reputation signals; enforce allowlists for MCP servers; tag telemetry for cost attribution and chargeback [web:504][web:505][web:506][web:507][web:508][web:509][web:510][web:511][web:512][web:513][web:514][web:515][web:516][web:517][web:518][web:602][web:603][web:604][web:605][web:606][web:607][web:608][web:609][web:610].

## Candidate experiments (cheap, high‑signal)

1. **Cost‑utility pilot**: instrument one agent with per‑tool cost tags; enforce hard session caps; measure anomaly detection catch rate over 30 days.
2. **Schema governance test**: define explicit tool output schemas; validate on ingress/egress; measure failure rate before/after validation.
3. **HITL UX A/B**: approval dashboard with evidence panels + timeout→reject semantics; measure approval fatigue (false positives, queue age).
4. **Agent identity registry**: internal registry with SPIFFE‑like identities; attenuated delegation chains; measure cross‑org delegation success rate.
5. **Runtime verification MVP**: Dogwood/Cedar+temporal policies for one high‑risk tool; measure policy violation catch rate.
6. **Digital twin pilot**: one physical agent with MHS safety layer; measure autonomy success rate vs baseline.
7. **Red‑team loop**: weekly executable red‑team exercises (REDAgentBench/MiDojo); measure time‑to‑detect and time‑to‑remediate.
8. **Lineage tracking**: agent registry with lineage; measure shadow AI reduction over 30 days.
9. **RAG precision monitor**: log injected schemas; measure retrieval precision as catalog grows; adaptive admission (3–5 skills/tools per step).
10. **Meta‑learning loop**: synthesize/retire skills based on retrieval precision and task success; measure self‑verification accuracy vs independent verifier.

## Cross‑links to existing notes

- `knowledge/notes/structural-primitives-2026.md` — design rules + candidate experiments.
- `knowledge/notes/attack-surface-supply-chain-2026.md` — skills as executable code, MCP allowlists, AOS/runtime split, compaction safety.
- `knowledge/notes/protocol-governance-deprecations-2026.md` — A2A/MCP foundation moves, HITL gates, deprecations.
- `knowledge/notes/solidifying-patterns-2026.md` — cyclic orchestration, dynamic tools, compaction, parallel swarms.
- `knowledge/notes/harness-space-scan-2026-09.md` — Hermes v0.21.0, Agent Zero v2.11, OpenCode v1.18.27, Pi.

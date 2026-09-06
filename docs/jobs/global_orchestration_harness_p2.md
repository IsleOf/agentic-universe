# Global Agentic Jobs Analysis - Part 2: Compensation, Capabilities, Patterns

**Continued from Part 1**

---

## Compensation Benchmarks by Role Tier & Geography

### United States

| Role Tier | Company | Location | Base Salary Range | Total Comp (est.) |
|-----------|---------|----------|------------------|-------------------|
| **Harness Engineering** | OpenAI (Codex Agents) | San Francisco, CA | $230K–$385K | $300K–$500K+ |
| **Harness Engineering** | NVIDIA (Open Harness) | Remote | $184K–$356.5K | $250K–$450K+ |
| **Self-Improving Agents** | NVIDIA (Principal, Local AI) | Redmond, WA | $272K–$431.25K | $350K–$600K+ |
| **Self-Improving Agents** | Google DeepMind (Meta-Agent) | Remote (US) | $174K–$252K | $250K–$400K+ |
| **Self-Improving Agents** | Bosch (AI Research Engineer) | Sunnyvale, CA | $165K–$180K | $200K–$280K+ |
| **Orchestration Engineering** | Caribou Financial (EM) | Remote (USA) | $174K–$217K | $220K–$300K+ |
| **Evaluation/Rig** | Honeycomb (Sr SWE II) | Remote (US) | $183.34K–$206K | $230K–$320K+ |
| **Forward Deployed** | Kroger/84.51˚ (Lead FDE) | Cincinnati, OH | $125K–$207K | $160K–$260K+ |
| **Research + Applied** | Dropzone AI (Sr–Principal) | Remote (US) | $200K–$250K | $260K–$350K+ |
| **New Grad** | Netic (Agent Platform) | San Francisco, CA | Not specified | $120K–$180K (est.) |

### Europe

| Role Tier | Company | Location | Base Salary Range | Total Comp (est.) |
|-----------|---------|----------|------------------|-------------------|
| **Orchestration Engineering** | Salesforce (FDE) | Munich, Germany | €94,250 | €120K–€150K |
| **Orchestration Engineering** | Rabobank (Agentic AI Engineer) | Utrecht, Netherlands | €60K–€86K/year | €75K–€105K |
| **Self-Improving Agents** | EWOR (Agentic AI Robotics) | Warsaw, Europe | €500K/year | €500K+ (equity-heavy) |
| **Self-Improving Agents** | Beam AI (Sr AI Agent Engineer) | Berlin, Germany | Not specified | €100K–€180K (est.) |
| **Orchestration Engineering** | Accenture (Agentic Orchestration) | Singapore (APAC) | Not specified | $80K–$150K (est.) |
| **Research + Applied** | CUBE (Sr Agentic AI Engineer) | Berlin, Germany | Not specified | €90K–€160K (est.) |
| **Evaluation/Rig** | SonarSource (Agentic SWE) | Remote (EU) | Not specified | €80K–€140K (est.) |

### Asia Pacific

| Role Tier | Company | Location | Base Salary Range | Total Comp (est.) |
|-----------|---------|----------|------------------|-------------------|
| **Orchestration Engineering** | Accenture (Agentic Orchestration) | Singapore | Not specified | $80K–$150K (est.) |
| **Evaluation/Rig** | Phizenix (LLM Eval Rig Engineer) | Hyderabad, India | Not specified | $30K–$60K (est.) |
| **Harness Engineering** | FICO (Lead Harness Engineer) | Bengaluru, India | Not specified | $40K–$80K (est.) |
| **Research + Applied** | Adaption (Agent Systems Engineer) | India | Not specified | $50K–$100K (est.) |
| **Orchestration Engineering** | Binance (AI Agent Engineer) | Remote (Asia) | Not specified | $80K–$150K (est.) |

### Remote-First / Worldwide

| Role Tier | Company | Location | Base Salary Range | Total Comp (est.) |
|-----------|---------|----------|------------------|-------------------|
| **Harness Engineering** | ImagineArt (Core Harness) | Remote | Not specified | $150K–$280K (est.) |
| **Self-Improving Agents** | Together AI (Infra Agent Systems) | London / Remote India | Not specified | £100K–€180K / $60K–$120K |
| **Forward Deployed** | Redapt (Agentic AI FDE) | Remote (US) | Not specified | $140K–$220K (est.) |
| **Research + Applied** | Dropzone AI | Remote (US) | $200K–$250K | $260K–$350K+ |
| **Self-Improving Agents** | Magic Patterns (Applied AI) | San Francisco, CA | Not specified | $160K–$260K (est.) |

**Key Observations**:
- **US compensation is 2–3x higher** than Europe/Asia for equivalent roles.
- **EWOR's €500K roles** are outliers — likely heavily equity-weighted for growth-stage risk.
- **NVIDIA Principal Engineer** ($272K–$431K) is the highest verified base salary for self-improving agent work.
- **New grad roles** at top labs (Netic, OpenAI) start at $120K–$180K, indicating strong entry-level demand.

---

## Technical Capability Map

### Core Competencies (Required by 80%+ of Roles)

| Capability | Description | Example Roles |
|------------|-------------|---------------|
| **Agent Execution Loop** | Design/optimize async execution, state management, retries, error recovery | All harness engineering roles |
| **Tool Use / Function Calling** | Implement tool registries, schema validation, MCP integration | OpenAI Codex, Dropzone AI, NVIDIA |
| **Context & Memory Management** | Short-term/long-term memory, RAG, summarization, compression, forgetting policies | Bosch, ImagineArt, Netic |
| **Multi-Agent Orchestration** | Router-specialist-utility tiers, LangGraph state machines, human-in-the-loop handoffs | Accenture, Light & Wonder, Salesforce |
| **Evaluation Infrastructure** | Golden datasets, scorers, CI gates, regression suites, faithfulness metrics | Phizenix, SonarSource, 10x Labs |
| **Observability** | Tracing, logging, metrics (LangSmith, Datadog, Honeycomb) | Accenture, Honeycomb, Redapt |
| **Sandboxed Execution** | Containers (Docker), VMs, isolated environments, subprocess management | NVIDIA, 10x Labs, OpenAI |

### Advanced Competencies (Required by 40–60% of Roles)

| Capability | Description | Example Roles |
|------------|-------------|---------------|
| **Self-Improving Loops** | Reflection, critique, self-debugging, meta-agent frameworks | Bosch, DeepMind, NVIDIA, Beam AI |
| **Knowledge Graphs** | Structured memory for agent learning and reasoning | Together AI |
| **Model Fine-Tuning** | SFT, RLHF, DPO for agent-specific behaviors | Pulumi, Bosch |
| **Edge Deployment** | Model/runtime optimization for constrained environments | Bosch, NVIDIA |
| **Security & Safety** | Adversarial testing, guardrails, policy enforcement | NVIDIA, PensarAI, Two Six |

### Emerging Competencies (Required by 10–30% of Roles)

| Capability | Description | Example Roles |
|------------|-------------|---------------|
| **Meta-Agent Frameworks** | Agents that diagnose and improve other agents | DeepMind, Netic |
| **Self-Evolving Algorithms** | Continuous learning from execution feedback | Phoeniqs, Agentrys, Binance |
| **Organizational OS** | Agents that discover and automate business processes autonomously | Beam AI |
| **Offensive Security Agents** | Autonomous vulnerability discovery and exploitation | PensarAI |

---

## Organizational Patterns

### 1. Dedicated Harness Teams

**Pattern**: Separate team for harness engineering, distinct from model training and application development.

**Examples**:
- **OpenAI Codex Core Agents**: "Builds the agent harness that turns model capability into real-world action".
- **ImagineArt Superagent**: "Own Superagent, our core agent harness".
- **NVIDIA Harness/Platform**: "The agent harness and the platform it runs on are the substrate everything else builds on".

**Implication**: Harness is **infrastructure**, not application logic. Requires dedicated ownership.

### 2. Forward Deployed Engineering

**Pattern**: Client-facing engineers deploy harnesses inside customer environments, instrument production, and iterate based on real usage.

**Examples**:
- **Salesforce Agentforce Orchestration**: FDEs deploy multi-agent orchestration inside customer ERP/CRM systems.
- **Redapt Agentic AI FDE**: Configure Azure Foundry/AWS Bedrock/Claude Cowork-style harnesses for clients.
- **Sitreps LLC Deployment Strategist**: Encode classified analyst workflows as agents in IC/DoD environments.

**Implication**: Enterprise adoption requires **on-the-ground expertise** — not just API docs.

### 3. Evaluation as CI Gate

**Pattern**: Evaluation harnesses are integrated into CI/CD pipelines, blocking releases on regressions.

**Examples**:
- **Phizenix LLM Eval Rig**: "Wire evaluation into CI so grounding/faithfulness regressions block releases".
- **SonarSource Agentic SWE**: "Build evaluation/verification systems for AI-generated changes".
- **10x Labs Infrastructure**: "Build agent scaffolding and evaluation harnesses... token budgets, multi-agent workflows".

**Implication**: Agent quality is **enforced by automation**, not manual QA.

### 4. Self-Improving as Default

**Pattern**: New agent systems are expected to improve over time from execution feedback — not static deployments.

**Examples**:
- **Bosch AI Research Engineer**: "Implement self-improving agent loops using reflection, critique, self-debugging".
- **DeepMind Meta-Agent**: "Build self-improving meta-agent framework to diagnose failure modes, generalize learnings".
- **Magic Patterns Applied AI**: "Own eval system that feeds into self-improving agent loop".
- **Beam AI Senior Agent Engineer**: "Build self-learning AI agents where intelligence grows through autonomous discovery".

**Implication**: Static agents are **legacy** — continuous improvement is table stakes.

### 5. Tiered Orchestration Architecture

**Pattern**: Multi-agent systems use a tiered architecture: Tier 1 routers, Tier 2 domain specialists, Tier 3 utility agents.

**Examples**:
- **Accenture Agentic Orchestration**: "Design production-grade multi-agent orchestration frameworks based on multi-tier pattern (Tier 1 routers, Tier 2 domain specialists, Tier 3 utility agents)".
- **Light & Wonder Full-stack AI**: "Implement robust orchestration using Microsoft Agent Framework (.NET), handling tool calling, multi-agent patterns, human-in-the-loop handoffs".

**Implication**: Tiered orchestration is **converging as a standard pattern** — similar to microservices architecture.

---

## Geographic Distribution

### United States (60% of Roles)

**Hubs**:
- **San Francisco / Palo Alto / Mountain View**: OpenAI, Anthropic, xAI, Perplexity, Magic Patterns, Judgment Labs.
- **Seattle / Redmond**: NVIDIA, ByteDance.
- **New York City**: Haystack, 10x Labs.
- **Austin, TX**: Light & Wonder.
- **Cincinnati / Chicago**: Kroger/84.51˚.
- **Arlington, VA**: Sitreps LLC (defense/intelligence).

**Characteristics**:
- Highest compensation ($200K–$430K base for senior roles).
- Concentration of frontier AI labs and well-funded startups.
- Strong defense/intelligence presence (TS/SCI clearance roles).

### Europe (25% of Roles)

**Hubs**:
- **London, UK**: Together AI, CUBE, Anthropic (Universes team).
- **Berlin, Germany**: Beam AI, CUBE.
- **Munich, Germany**: Salesforce, NVIDIA.
- **Barcelona, Spain**: N26.
- **Utrecht, Netherlands**: Rabobank.
- **Pisa, Italy**: Agentic AI Expert for Model-Based Engineering.
- **Bristol, UK**: DNV.

**Characteristics**:
- Lower base compensation than US (€60K–€180K typical).
- EWOR outliers (€500K) are equity-heavy growth-stage bets.
- Strong enterprise presence (banks, consulting, automotive).

### Asia Pacific (10% of Roles)

**Hubs**:
- **Singapore**: Accenture.
- **Bengaluru / Hyderabad, India**: FICO, Phizenix, Accenture.
- **Tokyo, Japan**: Limited explicit postings.
- **Beijing / Shanghai / Shenzhen**: Moonshot AI (Kimi) campus recruiting.

**Characteristics**:
- Lowest compensation ($30K–$100K typical).
- Strong outsourcing/consulting presence (Accenture, FICO).
- Growing startup scene (Binance, Phoeniqs).

### Remote-First (5% of Roles)

**Examples**:
- **ImagineArt** (Core Harness).
- **Dropzone AI** (Research Engineer).
- **Together AI** (Infra Agent Systems).
- **Redapt** (FDE).
- **LM Studio** (Agent Harness).

**Characteristics**:
- Compensation varies by company location (US-based remote pays US rates).
- Attracts global talent, especially from Europe/Asia.
- Often earlier-stage companies or infrastructure-focused teams.

---

*(Continued in Part 3: Company Deep Dives, Full Role Index, Methodology, Implications)*

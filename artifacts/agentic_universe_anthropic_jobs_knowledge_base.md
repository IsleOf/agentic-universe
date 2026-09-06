# Agentic Universe: Anthropic Job Descriptions Knowledge Base

**Date**: September 06, 2026  
**Source**: Anthropic careers page analysis  
**Focus**: Self-improving agentic systems

## Core Agentic Teams & Roles

### 1. Research Engineer, Universes — The Flagship Agentic Role
**Compensation:** $500,000–$850,000 USD  
**Locations:** SF, Seattle, NYC (Remote-Friendly, Travel-Required)

**Mission:** The Universes team trains AI models to perform **complex, difficult, long-horizon agentic tasks in ultra-realistic settings**. They design novel training environments where models learn to:
- Navigate ambiguity
- Handle interruptions
- Maintain context over extended interactions
- Exercise judgment in open-ended scenarios

**Key Responsibilities:**
- Build the next generation of agentic training environments
- Build rigorous evaluations that measure real capability (not just benchmarks)
- Collaborate across research and infrastructure teams to ship environments into production training
- Debug and iterate rapidly across research and production ML stacks

**Ideal Candidate Profile:**
- Highly impact-driven with high agency
- Good research taste or senior technical experience
- Can balance research exploration with engineering implementation
- Comfortable with uncertainty
- Strong software engineering skills (pair programming emphasized)
- **Preferred:** RL environments, simulation systems, large-scale ML infrastructure, sandboxing/containerization/VM infrastructure, distributed systems

---

### 2. Staff+ Software Engineer, Claude Managed Agents — Platform Infrastructure
**Compensation:** $405,000–$485,000 USD  
**Locations:** SF, NYC

**Mission:** Build **Claude Managed Agents** — the hosted platform for building, running, and scaling production agents on Claude. Instead of developers hand-rolling agent loops, sandboxed execution, state management, credential handling, and error recovery, Managed Agents provides:
- An Anthropic-built agent harness
- Production infrastructure for sessions, environments, tools, memory, and permissions
- Composable APIs designed to stay stable as models evolve

**What You'll Do:**
- **Scale the platform:** Design durable session/event storage, sandbox orchestration, streaming, scheduling, multi-tenant isolation for long-lived stateful sessions (minutes to hours/days)
- **Evolve the harness with evals:** Work with research to revisit harness assumptions as models improve; build eval infrastructure measuring harness quality against research baselines and real customer workloads
- **Help builders maximize Claude:** Ship outcome-driven execution (developers specify success criteria + budget, Claude iterates), multi-agent orchestration, memory, observability/tracing for long-running agents
- **Design stable APIs:** Shape primitives (agents, environments, sessions, vaults, event streams) with versioning, ergonomics across API/SDK/CLI

**Ideal Candidate:**
- 8+ years backend/distributed systems/infrastructure
- Built stateful, long-running, high-throughput systems (workflow orchestration, streaming, storage, container/job orchestration)
- Strong product sense; treats API design as craft
- Excited by 0→1 work, comfortable with ambiguity
- Uses Claude/AI tools as core part of building software
- **Preferred:** Agent harness/framework/LLM orchestration layer experience, AI/ML platform work, eval/benchmarking infrastructure for LLM/agent systems, durable execution/workflow engines, sandboxed code execution, public developer platforms/APIs/SDKs

---

### 3. Research Engineer, Machine Learning (Reinforcement Learning) — Core RL Research
**Compensation:** £260,000– £630,000 GBP (~$330k–$800k USD)  
**Location:** London

**Mission:** Advance capabilities and safety of LLMs through reinforcement learning. The RL teams have contributed to all Claude models, with significant impacts on **autonomy and coding capabilities of Claude Sonnet 4.5 and Opus 4.5**.

**Focus Areas:**
- Developing systems for models to use computers effectively
- Advancing code generation through RL
- Fundamental RL research for LLMs
- Scalable RL infrastructure and training methodologies
- Enhancing model reasoning (mathematics, etc.)

**Representative Projects:**
- Architect/optimize core RL infrastructure (training abstractions, distributed experiment management across GPU clusters)
- Design/implement/test novel training environments, evaluations, methodologies for RL agents
- Drive performance improvements through profiling, optimization, benchmarking
- Develop automated testing frameworks, clean APIs, scalable infrastructure

**Ideal Candidate:**
- Proficient in Python + async/concurrent programming (Trio framework mentioned)
- Experience with ML frameworks (PyTorch, TensorFlow, JAX)
- Can balance research exploration with engineering
- Enjoys pair programming
- **Preferred:** LLM architectures/training, RL techniques/environments, virtualization/sandboxed code execution, Kubernetes, distributed systems/HPC, Rust/C++

---

### 4. Research Engineer, Computer Use — Agentic Perception & Action
**Locations:** SF, NYC, Seattle

**Mission:** Teach Claude to **see, use, and understand computer interfaces**. Work translates directly into model improvements in Anthropic's and customers' products (Claude in Chrome extension, Claude Cowork).

**Key Responsibilities:**
- Design/run experiments to improve Claude's perception and agentic capabilities
- Develop robust evaluation frameworks for measuring models' ability to complete complex computer tasks
- Build/improve computer use and vision RL training environments
- Create pipelines/tools to test/validate complex RL environments
- Collaborate with model training and infrastructure teams on production training setup
- Partner with product teams to bring research advances into production

**Ideal Candidate:**
- Software engineering + Python proficiency
- Experience training, fine-tuning, or evaluating ML models
- **Preferred:** Computer use/agentic capabilities training, RL (especially long-horizon or sparse-reward settings), multimodal model training, evals/benchmarks for agentic systems, RL environments/simulation systems/large-scale ML infrastructure, product collaboration

---

### 5. AI Engineer, GTM Claudification — Internal Agentic Automation
**Compensation:** $320,000–$405,000 USD  
**Locations:** SF, Seattle (Remote-Friendly, Travel-Required)

**Mission:** Build agents and AI systems that run **Anthropic's own go-to-market work autonomously**. Sellers already work alongside agents; this role builds agents that run complete autonomous motions across inbound, outbound, pipeline management, and customer engagement.

**Key Responsibilities:**
- Build/operate autonomous agents running GTM motions end-to-end
- Design human oversight: approval gates, handoffs, escalation paths
- Develop evaluation frameworks for agent behavior (dev + production)
- Instrument model/tool calls in production; build observability tying agent actions to pipeline/revenue
- Ship MCP servers, agent skills, web applications connecting to CRM, communication tools, data warehouse
- Set technical direction for building, evaluating, operating agents across the team
- Architect shared codebases for GTM builders

**Representative Projects:**
- Build agent taking routine sales workflow from first signal to drafted, human-reviewed action
- Stand up eval suite for agent: seed scenarios, scoring rubrics, regression runs on every change
- Ship MCP server giving sellers/agents governed access to core revenue system
- Build predictive model that explains itself so agent can tell seller why it suggests action

**Ideal Candidate:**
- Strong Python/TypeScript; production application experience
- Production LLM experience: context engineering, agent development, MCP development, tool use, evaluation frameworks
- Experience using evals and transcript analysis to find/fix real LLM system problems
- SQL fluency
- **Preferred:** 8+ years as SWE/ML engineer/forward deployed engineer (former technical founders encouraged), Claude Code + Claude Agent SDK experience, GTM systems experience (CRM, sales engagement, enrichment, conversation intelligence), applied ML/experimentation (A/B testing, propensity models, recommendations, causal analysis)

---

## Agentic Universe: Key Themes & Patterns

### Technical Stack & Infrastructure
- **Reinforcement Learning** is central to agentic training (long-horizon, sparse-reward settings emphasized)
- **Sandboxed execution environments** (containers, VMs, Kubernetes) for safe agent operation
- **Durable execution** for long-running sessions (minutes to days) with clean resumption after disconnections
- **MCP (Model Context Protocol) servers** for tool integration and governed system access
- **Evaluation infrastructure** is a first-class concern — not just benchmarks, but behavior evals, regression runs, production monitoring
- **Observability & tracing** for debugging long-running autonomous agents
- **Multi-agent orchestration** and memory systems

### Research-Engineering Blend
All agentic roles emphasize **blending research and engineering**:
- Implement novel approaches AND contribute to research direction
- Balance exploratory research with robust engineering
- Ship environments into production training pipelines
- Debug across research and production ML stacks
- Pair programming is explicitly valued

### Safety & Alignment Integration
- Collaboration with **alignment and frontier red teams** to ensure capable AND safe systems
- Human oversight design (approval gates, handoffs, escalation paths)
- Evaluations measuring "genuine capability" not just performance metrics
- Focus on steerable, trustworthy AI as organizational mission

### Compensation Signals
Agentic roles command premium compensation:
- **Universes:** $500k–$850k (highest range, reflecting research + critical infrastructure)
- **Managed Agents Platform:** $405k–$485k
- **RL Research (London):** £260k– £630k (~$330k–$800k)
- **GTM Claudification:** $320k–$405k

### Experience Expectations
- **8+ years** for senior/staff roles (or equivalent impact as technical founder)
- Production experience with LLMs, agents, tool use, evals
- Distributed systems, infrastructure, or large-scale ML systems background
- Comfort with ambiguity and 0→1 work
- Strong communication and collaboration (pair programming, cross-functional work)

---

## Strategic Implications for Agentic Universe

Anthropic is investing heavily in **production-grade agentic infrastructure** at multiple layers:

1. **Foundation (RL Research):** Core algorithms and training methodologies for long-horizon agentic capabilities
2. **Environments (Universes):** Ultra-realistic training settings pushing beyond current model capabilities
3. **Platform (Managed Agents):** Hosted infrastructure abstracting away agent loop complexity for developers
4. **Applications (Computer Use, GTM Claudification):** Domain-specific agents demonstrating and refining capabilities
5. **Safety & Evals:** Integrated throughout — human oversight, behavior benchmarks, production monitoring

The "Agentic Universe" isn't a single team but a **cohesive stack** spanning research, infrastructure, platform, and product — all oriented toward making Claude capable of reliable, autonomous action in complex, open-ended environments.

---

**Last Updated:** September 06, 2026  
**Maintainer:** Agentic Universe Team

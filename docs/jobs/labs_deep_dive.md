# Agentic Universe: Deep-Dive Job Description Analysis Across Frontier AI Labs

**Scope**: xAI, DeepSeek, Google DeepMind (Gemini), Meta FAIR/MSL, Moonshot AI (Kimi), Zhipu AI (Z.ai)  
**Date**: September 2026  
**Purpose**: Extract architectural patterns, capability maps, and organizational strategies for self-improving agentic systems.

---

## Executive Summary

Frontier AI labs are converging on a **multi-layered agentic stack**:

1. **Model Layer**: Base LLMs optimized for reasoning, tool use, and long-horizon planning.
2. **Harness Layer**: Infrastructure for agent loops, memory, KV cache optimization, MCP-based tool registries, and multi-agent orchestration.
3. **Training Layer**: RL frameworks, post-training fine-tuning, dataset curation (human + synthetic), and evals.
4. **Safety Layer**: Alignment, product safety, and scalable oversight integrated into engineering workflows.
5. **Application Layer**: Enterprise agents, coding agents, research agents, companion agents, and domain-specific agents.

Each lab emphasizes different layers based on strategic bets:

| Lab | Primary Bet | Key Differentiator |
|-----|-------------|---------------------|
| **xAI** | Vertically integrated Grok + Agents + Supercomputing | Flat org, 5-day in-office, $180K–$440K bands, RL-first agent training |
| **DeepSeek** | Harness as first-class infrastructure | "Model + Harness = Agent" equation, co-evolution of model and harness, desktop agent focus |
| **Google DeepMind (Gemini)** | Research + Product Safety + Tool Use | PhD-heavy research scientist roles, agent post-training, i18n, vision, safety, commercial intelligence |
| **Meta FAIR/MSL** | Agentic AI for Materials Discovery + Post-Training | LLM-orchestrated multi-agent systems for scientific discovery, ReAct/tool-calling research |
| **Moonshot AI (Kimi)** | Product-led AGI startup culture | Rapid prototyping, ego-free scrutiny, agentic RL + multimodal agent roles for 2027 campus hires |
| **Zhipu AI (Z.ai)** | Sovereign AGI + RL training frameworks | Campus + experienced algorithm engineers focused on RL and LLM training efficiency, AutoGLM browser agents |

---

## xAI: Grok, Agents, and Supercomputing

### Organizational Philosophy

xAI operates with a **flat organizational structure**, expecting all employees to be hands-on contributors. Leadership is given to those who show initiative and consistently deliver excellence. The team works **5 days/week in-office (Palo Alto)** with occasional remote flexibility.

Mission: "Create AI systems that can accurately understand the universe and aid humanity in its pursuit of knowledge."

### Key Agentic Roles

#### 1. AI Engineer & Researcher – Agents (Palo Alto, $180K–$440K)

**Team**: Agent team makes AI models generalizable and capable of solving real-world challenges.

**Responsibilities**:
- Develop realistic agent environments and evaluation methods.
- Design RL algorithms for agents to learn by interacting with realistic environments.
- Collect and curate human and synthetic data to improve agent capability and behavior.

**Exceptional Candidates Have**:
- PhD in AI or other scientific domains.
- Strong knowledge of reinforcement learning techniques.
- Experience building infrastructure for large-scale RL and multi-agent RL.

**Signal**: xAI treats agent environments and RL algorithm design as core research-engineering work, not just applied engineering.

#### 2. AI Engineer & Researcher – Coding Agents (Palo Alto, $180K–$440K)

**Team**: Grok Code Team pushes boundaries of software engineering with AI at the center of the full developer loop.

**Responsibilities**:
- Build best-in-class Coding Agents with an AI-first, AI-native software engineering stack.
- Work across the LLM stack (reasoning RL, product building, dataset generation, evals) to deliver best product experience.
- Work closely with research team to drive model development and feedback loops optimizing model behavior and user satisfaction.

**Exceptional Candidates Have**:
- Experience in developer tooling with AI-first mindset.
- Exceptional engineering skills to iterate quickly on data processing and product features.
- Strong understanding of LLMs and how to leverage them for AI-assisted software development.
- Deep knowledge and "taste" in software developer tooling.

**Signal**: Coding agents are treated as a full-stack product requiring RL, dataset generation, evals, and tight research-engineering feedback loops.

### Infrastructure & Supercomputing

xAI hires extensively for **Memphis, TN data center operations**:
- Fiber Technicians, Mechanical Engineers (HVAC), Network Development Engineers, High-Performance Networking Engineers, Infrastructure Engineers for Supercomputing, RDMA Engineers.

**Signal**: xAI is building bespoke supercomputing infrastructure to support large-scale agent training and inference.

---

## DeepSeek: Harness as First-Class Infrastructure

### Core Philosophy

DeepSeek formalizes the equation: **Model + Harness = Agent**.

Everything except the core model—tooling, memory, agent loop, desktop integration, MCP, feedback systems—is considered part of the **Harness**.

### Key Roles

#### 1. Agent Harness R&D Engineer

**Requirements**:
- 2+ years of software development.
- Deep LLM agent knowledge.
- Hands-on expertise with: Agent Loop, KV cache, MCP, Memory, Multi-Agent, Planning, Skills.

**Inferred Tech Stack**:
- Async Rust/Python.
- State machines.
- KV cache optimization.
- SQLite/LanceDB for vector memory.
- MCP-based tool registry.
- Desktop UI built with Tauri or Electron.

**Signal**: DeepSeek treats harness engineering as a distinct discipline requiring expertise in agent loops, memory systems, and tool orchestration.

#### 2. Agent Harness Product Manager

**Responsibilities**:
- Plan Harness product roadmap; connect researchers, engineers, open-source community, and users.
- Define metrics for whether agents are "truly helping more people more deeply in more scenarios".
- Deep collaboration with model training teams to co-evolve models and harness.
- Design systematic data collection methods (surveys, interviews, A/B tests, grey releases) and analyze rigorously.
- Be a high-intensity user of agent products (Claude Code, Cowork, Codex, Cursor, etc.) and understand LLM + agent mechanisms (KV cache, agent loop, tool use, reasoning, planning, MCP, memory, subagents, multi-agent).
- UI/UX design capability and deep engagement with open-source communities.

**Signal**: Product managers are expected to be power users of multiple agent products and understand low-level agent mechanisms (KV cache, agent loop, MCP).

### Harness as Engineering Framework

36Kr article explains Harness as an **engineering infrastructure reference framework** for agents, intended to transform raw large model intelligence into reliable, controllable, and usable agent capabilities via systematic engineering.

It specifically addresses deficiencies of "naked" models in memory, code execution, and tool invocation.

DeepSeek's Harness team is positioned as a **direct benchmark against Anthropic's Claude Code**, aiming to build "DeepSeek CodeHarness".

**Signal**: DeepSeek explicitly competes with Anthropic by building a superior harness layer on top of competitive base models.

---

## Google DeepMind (Gemini): Research + Product Safety + Tool Use

### Key Agentic Roles

#### 1. Research Scientist, Gemini Tool Use, DeepMind (Mountain View, CA)

**Minimum Qualifications**:
- PhD in Computer Science, Machine Learning, or related quantitative field, or equivalent practical experience.
- 2 years of experience with software development in Python, C++, or similar languages.
- Experience in machine learning, deep learning, or related areas.

**Preferred Qualifications**:
- Experience publishing at top-tier venues (NeurIPS, ICML, ICLR, ACL, etc.).
- Experience with large language models, reinforcement learning, or agent systems.
- Experience with tool use, function calling, or API integration.

**Signal**: Tool use is a dedicated research track within Gemini, requiring PhD-level expertise and publication record.

#### 2. Research Scientist, Agent Post-Training, DeepMind (London, England)

**Minimum Qualifications**:
- PhD in Computer Science, Machine Learning, or related quantitative field, or equivalent practical experience.
- 2 years of experience with software development in Python, C++, or similar languages.
- Experience in machine learning, deep learning, or related areas.

**Preferred Qualifications**:
- Experience publishing at top-tier venues.
- Experience with large language models, reinforcement learning, or agent systems.
- Experience with post-training methods (SFT, RLHF, DPO, etc.).

**Signal**: Agent post-training is a distinct research area, separate from base model training and tool use.

#### 3. Research Scientist, Gemini Safety, DeepMind (Mountain View, CA)

**Responsibilities**:
- Conduct original research on AI safety, alignment, and robustness.
- Develop methods for evaluating and mitigating risks from advanced AI systems.
- Collaborate with engineering teams to deploy safety research at scale.

**Signal**: Safety research is integrated into the Gemini product line, not siloed.

### Gemini Deep Research Agent

Google Cloud documentation describes **Gemini Deep Research Agent** as "an agent designed to help you plan, execute, and synthesize multi-step research tasks".

**Signal**: Gemini agents are productized as research assistants with multi-step planning capabilities.

---

## Meta FAIR/MSL: Agentic AI for Scientific Discovery

### Key Agentic Roles

#### 1. AI Research Scientist — Agentic AI for Materials Discovery (Reality Labs Research)

**Team**: Material and Systems Innovation team, Reality Labs Research.

**Responsibilities**:
- Design and build LLM-orchestrated multi-agent systems that autonomously drive materials discovery pipelines.
- Work with computational chemistry, physics, and materials science workflows.
- Develop agent systems that can reason over scientific data, run simulations, and propose new materials.

**Signal**: Meta is applying agentic AI to scientific discovery, not just consumer/enterprise applications.

#### 2. Developer Advocate, AI Agents (Bellevue, WA)

**Responsibilities**:
- Advocate for AI agent tools and proposals within Meta's internal developer community.
- Create code samples, demos, prototypes, articles, and tutorials to promote AI agent tools.
- Establish credibility as a thought leader in the AI agent space and align internal teams.
- Collaborate across engineering, product, and user communities to build and engage the internal developer base around AI agent tools.
- Leverage data and analytics to understand developer needs and measure advocacy impact.

**Requirements**:
- 8+ years of software engineering or developer relations experience.
- Experience leading and supporting developer tools, SDKs, APIs, or platforms.
- Experience using AI-assisted development tools like GitHub Copilot, Claude Code, Cursor.
- Subject-matter expertise on agentic orchestration patterns (ReAct), tool use/function calling, and memory.
- Experience building AI-assisted tools with frameworks like LangChain, LlamaIndex, Haystack.
- Proven experience in presenting at conferences and creating technical content, plus open-source contributions.

**Compensation**: $173K–$247K/year plus bonus, equity, and benefits.

**Signal**: Meta has a dedicated internal advocacy role for AI agent tools, indicating a platform strategy for agents.

---

## Moonshot AI (Kimi): Product-Led AGI Startup Culture

### Culture Signals

Moonshot emphasizes:
- Owning problems, not tasks; prototyping in days; killing non-working ideas fast.
- Ego-free but opinionated collaboration where every idea, including the CEO's, is scrutinized.
- Full transparency of metrics, including negative ones.

Candidates are encouraged if they enjoy ambiguity, rapid iteration, and building from scratch rather than optimizing legacy code.

### 2027 Campus Recruiting (China)

LinkedIn post announces 2027 campus hiring for:
- AI infra inference optimization.
- Research scientist/engineer – agentic RL.
- Post-training algorithm researcher (code/SWE).
- Multimodality agent.
- Base: Beijing/Shanghai/Shenzhen.

**Signal**: Moonshot is hiring campus talent for agentic RL, post-training, and multimodal agent roles, indicating a long-term bet on these capabilities.

---

## Zhipu AI (Z.ai): Sovereign AGI + RL Training Frameworks

### Key Roles

#### 1. Algorithm / R&D Engineer (Experienced & Campus)

**Responsibilities**:
- Continuously improve training frameworks and strategies to enhance model training efficiency.
- Develop, optimize, and maintain reinforcement learning (RL) training frameworks.

**Signal**: RL training frameworks are a core competency for both experienced and campus hires.

### AutoGLM and AutoClaw

Zhipu launched **AutoClaw**, a one-click local OpenClaw client with 50+ skills and integrated AutoGLM browser operation capabilities.

**Signal**: Zhipu is building desktop agent products with browser automation capabilities.

### GTM and Ecosystem Roles

LinkedIn hiring post shows Zhipu building **sovereign, open, and globally collaborative AGI infrastructure** and hiring for:
- Business Development, Strategic BD, Customer Success, and Solutions Architect.
- Locations: Beijing, Shenzhen, Southeast Asia, Middle East.
- Preference for AI startup or cloud background and platform/ecosystem experience.

**Signal**: Zhipu is positioning AGI as sovereign infrastructure with regional ecosystem plays (Middle East, Southeast Asia).

---

## Cross-Company Patterns

### 1. RL and Post-Training are Universal

All six labs have dedicated roles for:
- RL algorithm design (xAI, DeepSeek, Moonshot, Zhipu).
- Post-training methods (xAI, DeepMind, Meta MSL, Moonshot).

**Implication**: RL and post-training are not optional—they are core to agentic capability.

### 2. Harness/Infrastructure is First-Class

DeepSeek explicitly defines Harness as a distinct layer. xAI's Coding Agents and Agents roles imply similar infrastructure.

**Implication**: The "harness" concept should be central to Agentic Universe knowledge base.

### 3. Tool Use and MCP are Standard

DeepSeek Harness PM requires MCP expertise. Meta's ToolCalling role and Gemini Tool Use role indicate tool use is a dedicated research track.

**Implication**: Tool orchestration (MCP, function calling) is a core agentic primitive.

### 4. Safety is Embedded, Not Siloed

xAI Product Safety, DeepMind Gemini Safety, and Meta's alignment work indicate safety is integrated into engineering workflows.

**Implication**: Safety should be a cross-cutting concern in Agentic Universe, not a separate module.

### 5. Multimodal and i18n are Table Stakes

Gemini Vision, Gemini i18n, Moonshot multimodality agent indicate agents are multimodal and global by design.

**Implication**: Agentic Universe should assume multimodal inputs/outputs and internationalization from the start.

---

## Implications for Agentic Universe Knowledge Base

### 1. Canonical Layers

Structure the knowledge base around these layers:

1. **Model Layer**: Base LLM capabilities (reasoning, planning, tool use).
2. **Harness Layer**: Agent loop, KV cache, memory, MCP, multi-agent orchestration.
3. **Training Layer**: RL frameworks, post-training (SFT, RLHF, DPO), dataset curation, evals.
4. **Safety Layer**: Alignment, product safety, scalable oversight.
5. **Application Layer**: Coding agents, research agents, enterprise agents, companion agents, domain-specific agents.

### 2. Role Taxonomy

Map roles to layers:

| Role Type | Primary Layer(s) | Example Titles |
|-----------|------------------|----------------|
| Research Scientist | Model, Training, Safety | Research Scientist, Gemini Tool Use (DeepMind); AI Research Scientist, Post-Training (Meta MSL) |
| R&D Engineer | Harness, Training | Agent Harness R&D Engineer (DeepSeek); AI Engineer & Researcher – Agents (xAI) |
| Product Manager | Harness, Application | Agent Harness Product Manager (DeepSeek) |
| Developer Advocate | Application, Ecosystem | Developer Advocate, AI Agents (Meta) |
| Solutions Architect | Application, Ecosystem | Solutions Architect (Zhipu) |

### 3. Strategic Bets

Each lab's bet informs Agentic Universe priorities:

- **xAI**: RL-first, supercomputing-backed agents.
- **DeepSeek**: Harness as differentiator.
- **DeepMind**: Research depth + product safety.
- **Meta**: Scientific discovery + internal platform.
- **Moonshot**: Product-led, rapid iteration.
- **Zhipu**: Sovereign AGI + regional ecosystems.

Agentic Universe should synthesize these bets into a flexible architecture that can adapt to different strategic priorities.

---

**Document Status**: Complete  
**Last Updated**: September 06, 2026  
**Maintainer**: Agentic Universe Team

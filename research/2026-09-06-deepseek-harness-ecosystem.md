# DeepSeek Harness Ecosystem Research
**Date:** 2026-09-06  
**Sources:** DeepSeek Harness official repo, plugin directories, awesome-DSH lists, ecosystem analysis

## Executive Summary

DeepSeek Harness (DSH) is an open-source, MIT-licensed agent runtime released in August 2026 that has rapidly become one of the most starred AI agent frameworks on GitHub, surpassing 200K stars within two weeks of launch. Its core innovation is an **"everything is a plugin"** architecture built on the Cordis meta-framework, where models, tools, skills, sessions, sandboxes, filesystems, execution loops, and even the UI are all swappable plugins that can be mounted, removed, or replaced from configuration without touching source code.

The self-evolution mechanism operates through specialized plugins that enable agents to refine their own state from session trajectories with versioned, auditable, rollback-safe state layers and benchmark-driven validation loops.

## Core Architecture

### Cordis Meta-Framework

The technical core is **Cordis**, an event-bus meta-framework handling plugin mounting and dependency resolution, which DeepSeek vendored with local patches into its own repository. The codebase spans roughly **453,000 lines of TypeScript across 219 packages**, demonstrating the scale of this plugin-centric bet.

### Plugin Categories

The ecosystem has exploded to **3,800+ plugins** with over **262K total ecosystem stars** across seven categories:

1. **Agents** - Core agent implementations and orchestration
2. **Tools** - Individual capabilities and utilities
3. **UI** - Interface components and themes
4. **Sessions** - Memory, persistence, and context management
5. **Workflows** - Multi-step automation patterns
6. **Skills** - Reusable capability bundles
7. **MCP** - Model Context Protocol servers
8. **Sandbox** - Execution isolation
9. **CLI** - Command-line extensions

## Self-Evolution Plugins

### dsh-continual-evolve (ZK-Andy)

**Function:** Versioned self-evolution from session trajectories with benchmark validation

**Architecture:**
- **L0:** Session trajectory capture
- **L1:** Memory extraction (agent-curated)
- **L2:** Scene grouping (contextual clustering)
- **L3:** User persona modeling

**Validation:** AES-256-GCM encrypted rubric, separate scorer model
**Rollback:** Deterministic inverse edits from audit journal

### dsh-self-evolving

**Function:** Crash-resumable evolution engine generating bounded plugin candidates

**Pattern:** Evidence-first evolution with Harbor evaluation before admission, auditable lineage journaling

### dsh-self-improved (madage)

**Function:** Long-term memory & self-evolving plugin

**Pipeline:** L0 capture → L1 memory extraction → L2 scene grouping → L3 user persona, with automatic skill synthesis

### dsh-memory-evolve (csyangwen)

**Function:** Five-track layered memory with skill evolution

**Tracks:**
- Global memory
- User-specific memory
- Project memory
- Project-key + git-branch memory
- Daily memory

**Features:** Git-branch awareness, in-turn self-review, skill self-evolution and skill manager

## Memory & Knowledge Plugins

| Plugin | Stars | Function |
|--------|-------|----------|
| dsh-continual-evolve | 14+ | Versioned self-evolution from session trajectories |
| dsh-memory-evolve | 281 | Five-track layered memory with git-branch awareness |
| dsh-mneme | 473 tests | SQLite + Markdown mirror with autoDream consolidation |
| dsh-brainagent | Source-available | Brain-inspired cognitive plugin with episodic/semantic/procedural/emotional memory |
| graph-memory | 513 | Traceable, searchable, cross-session memory |
| mnemon | 453 | LLM-supervised persistent memory with graph-based recall |

### Shared Memory Patterns

1. **Event-sourced lifecycle:** Every evolution step is replayable, ledger-recorded
2. **LLM-supervised binary execution:** Host LLM makes judgment calls; binary handles deterministic computation
3. **Multi-graph knowledge representation:** Temporal + entity + causal + semantic edges
4. **Intent-native protocol:** `remember/link/recall` instead of INSERT/SELECT
5. **Benchmark-driven validation:** Frozen cases with encrypted rubrics, separate scorer model
6. **Configurable retention lifecycle:** Importance decay + access boosting + GC
7. **Multi-host plugin distribution:** One install command adapts to all detected agents
8. **Context compression with source-backed recall:** Graph navigation, not full history

## Multi-Agent Orchestration

### dsh-agent-teams (NanmiCoder) - 977 stars

**Architecture:** Captain-style sessions with durable sub-agent teams
- Role assignment based on task requirements
- Coordinated execution with shared context
- Handoff protocol for seamless task transfer

### dsh-collaboration

**Pattern:** Persistent specialist roster with star-topology relay
- Tools: `team_call`, `team_message`, `team_status`
- Model comparison via parallel execution

### dsh-taskswarm

**Mechanism:** Dependency-ordered waves in parallel git-worktree lanes
- Task packets with explicit dependencies
- Cross-model review before merge

### dsh-kirocrew

**Function:** Bridge to persistent KiroCrew development workspace over ACP (JSON-RPC 2.0)

## Vision/Multimodal Plugins

### dsh-vision-router (ysr666)

**Architecture:** Free vision chain with pixel-level tools
- **Primary:** Built-in free vision chain (no API key)
- **Fallback:** Qwen2.5-VL-72B-Instruct via OpenRouter
- **Tools:** `vision_qa`, `vision_ocr`, `vision_grounding`, `vision_crop`, `vision_pixel_diff`, `vision_colors`, `vision_svg_trace`, `vision_cutout`, `vision_screenshot`

### dsh-free-vision

**Approach:** Zero-API-cost vision for text-only models
- Weekly npm downloads: 2.1k/wk
- Routes to free-tier vision endpoints, degrades gracefully

### local-ocr-cli

**Stack:** Fully local OCR pipeline
- **Primary:** PaddleOCR-VL
- **Fallback:** Tesseract OCR
- Weekly npm downloads: 1.1k/wk

## Design & Creative Plugins

### Open-Design (nexu-io) - 86.9k stars

**Capabilities:** Claude Design alternative with full export pipeline
- **Outputs:** HTML/CSS/JS prototypes, landing pages, dashboards, slides, images, video
- **Export formats:** HTML, PDF, PPTX, MP4
- **Live preview:** Element picker, design-agent chat

### DeepSeek-iDesign (Devin-AXIS) - 422 stars

**Focus:** Native Design & PPT Studio for DSH

### AI-Novel-Writer (EthanYoQ) - 447 stars

**Use case:** Local-first long-form fiction workspace

## Top 50 Plugins by Stars

| Rank | Plugin | Stars | Category |
|------|--------|-------|----------|
| 1 | deepseek-ai/deepseek-harness | 104.5k | Official |
| 2 | nexu-io/open-design | 86.9k | Design |
| 3 | Tencent/WeKnora | 20.6k | RAG/Knowledge |
| 4 | zhu1090093659/dsh-web-ui | 6.0k | UI |
| 5 | Q00/ouroboros | 5.7k | Self-Evolution |
| 6 | strukto-ai/mirage | 3.6k | Runtime |
| 7 | omdsh-dev/DSH-better-sidebar | 2.9k | UI |
| 8 | ccch1mneyyy/dsh-TUI | 2.5k | UI |
| 9 | alvinunreal/openpets | 1.1k | Desktop Pets |
| 10 | GanyuanRan/Aegis | 1.0k | Workflows |
| 11 | NanmiCoder/dsh-agent-teams | 977 | Multi-Agent |
| 12 | tong-io/tongflow | 932 | GenAI Studio |
| 13 | MeteorNOX/DeepSeek-Balance-Whale-Widget | 915 | UI |
| 14 | xmanrui/dsh-im | 813 | Messaging |
| 15 | sandbaseai/sandbase-harness | 633 | Runtime |
| 16 | shaobeichen/dsh-pocket | 614 | Mobile |
| 17 | superdesigndev/treg | 598 | Tools |
| 18 | Nagi-ovo/dsh-ads | 562 | Fun |
| 19 | adoresever/graph-memory | 513 | Memory |
| 20 | FSMargoo/dsh-at-file | 469 | UI |
| 21 | mnemon-dev/mnemon | 453 | Memory |
| 22 | EthanYoQ/AI-Novel-Writer | 447 | Writing |
| 23 | Devin-AXIS/deepseek-design | 422 | Design |
| 24 | superdesigndev/superdesign-skill | 414 | Design |
| 25 | Ikalus1988/MisakaNet | 411 | Memory |
| 26 | PC2005-cloud/dsh-pet | 403 | Desktop Pets |
| 27 | linhay/harmony-next.skills | 330 | Skills |
| 28 | omdsh-dev/dsh-genui | 327 | UI |
| 29 | vlln/whale-girl | 280 | Desktop Pets |
| 30 | hust-open-atom-club/oh-dsh | 275 | Runtime |

## Key Repositories

1. **Official:** https://github.com/deepseek-ai/deepseek-harness
2. **Awesome DSH (English):** https://github.com/0xsline/awesome-deepseek-harness
3. **Awesome DSH (Chinese):** https://github.com/Dominic789654/awesome-deepseek-harness
4. **Plugin Directory:** https://deepseekplugin.org/en
5. **Plugin Store:** https://www.dshplugin.store

## Patterns Worth Adopting for Agentic Universe

1. **Plugin-as-bundle:** Packages declaring `dsh.bundle.patch` become active profile layers
2. **Skill migration tools:** One-click migration from 14+ agent platforms with merge, dedupe, and rollback
3. **Evidence-first evolution:** Plugin candidates evaluated with Harbor before admission
4. **Cross-session memory protocols:** Typed `ctx.memory` seams with zero-dependency SQLite providers
5. **Context compression:** Model-driven or rule-based compression freeing 20%+ context without affecting performance
6. **Event-sourced lifecycle with checkpoint recovery:** Sessions are stateless; replay reconstructs full lineage
7. **LLM-supervised binary execution:** Host LLM makes judgment calls; binary handles deterministic computation
8. **Four-graph knowledge representation:** Temporal + entity + causal + semantic edges
9. **Intent-native protocol:** `remember/link/recall` instead of INSERT/SELECT
10. **Benchmark-driven validation:** Frozen cases with encrypted rubrics, separate scorer model

## Installation

```bash
# Launch the DSH Web UI
npx @deepseek-ai/dsh web

# Install a self-evolution plugin
dsh plugin --profile web add dsh-continual-evolve

# Or from GitHub source
dsh plugin --profile web add github:ZK-Andy/dsh-continual-evolve
```

The runtime is **free and MIT-licensed**—only the connected models cost money.

---

**Next Steps:**
- Analyze Ouroboros, Aegis, and dsh-continual-evolve source code for self-evolution patterns
- Implement hybrid memory layer (BM25 + vector + entity graph) inspired by dsh-memory-evolve
- Build plugin registry with evaluation gates based on DSH ecosystem patterns
- Develop multi-agent orchestration primitives from dsh-agent-teams and dsh-taskswarm

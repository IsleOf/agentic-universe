# Session Metadata
- Approximate date: 2026-08-31
- Primary topic: Integrating Hermes "one-person media company" patterns into Agentic Universe (role contracts, editorial graph, handoff records, Kanban production, performance loop)
- Projects/systems discussed: Agentic Universe (IsleOf/agentic-universe), Hermes Agent (bot mode, profiles, Kanban), Obsidian-based editorial knowledge graph
- Archive status: source material only; not canonical knowledge
- Extraction limitations: No hidden chain-of-thought included; some metrics and examples are quoted from an external X thread and a Chinese summary article; implementation status in Agentic Universe is not asserted here.

# Executive Summary

This session analyzed a public guide describing how to build a "one-person media company" using six specialized Hermes bots, a shared Obsidian content brain, structured handoff records, Kanban-driven production, and a weekly performance → playbook update loop. The goal was to identify which patterns are missing from the current Agentic Universe design and should be added as reusable modules.

Key conclusion: Agentic Universe already covers generic agentic OS infrastructure (memory, graphs, orchestration, evaluation). The Hermes system contributes domain-specific editorial role contracts, a curated editorial knowledge graph, strict handoff schemas, Kanban as the system of record, platform-native distribution playbooks, and a compounding learning loop that encodes taste and distribution judgment.

No changes were made to canonical graph, schema, or changelog files. This document is source context for later analysis and module design.

# Explicit Decisions and Commitments

- The user requested archiving this entire conversation as a durable source document in `IsleOf/agentic-universe` under `conversations/raw/YYYY-MM-DD_short-topic.md`.
- Boundaries for this write:
  - Create or update ONLY the conversation archive file under `conversations/raw/`.
  - Do NOT modify, overwrite, or propose edits to:
    - `knowledge/graph/agentic_universe_graph.json`
    - `knowledge/graph/agentic_universe_schema.json`
    - `evolution/CHANGELOG.md`
    - any file outside `conversations/raw/`
  - Do NOT create graph nodes, edges, schema changes, changelog entries, merge recommendations, or architecture documents in this step.
- Filename chosen: `conversations/raw/2026-08-31_hermes-one-person-media-company-agentic-universe.md`.
- Content policy: preserve uncertainty; do not invent missing facts, outcomes, metrics, decisions, code, or implementation status.

# Technical Context

## Source material

- Primary source: X thread by @vibemarketer_ titled "How to Build a One-Person Media Company With Hermes Bots" (posted 2026-08-28). Claims include:
  - Six Hermes bots provide research, writing, editing, and distribution capacity of a complete media company.
  - System trained on strong research, packaging, evidence, and distribution patterns, stored in a shared Obsidian graph.
  - Claimed result: over 5.8 million impressions on X in the past 4 weeks using this system. [web:5][web:6]
- Secondary source: Chinese summary article (2026-08-29) describing the same system and its components. [web:6]
- Supporting context: Hermes Bot Mode (August 16 release) adds:
  - Bot mode: visible roster of named bots and communication between them.
  - Profiles: separate memory, sessions, skills, and instructions per specialist.
  - Kanban: durable task path across profiles with dependencies, comments, review, retries, and human input. [web:4][web:5][web:6]

## Agentic Universe baseline (from prior conversation)

- Focus areas already covered:
  - Agentic OS and autonomous workflows.
  - Long-term agent memory and knowledge graphs.
  - Computer-use models and visual interaction.
  - AI-assisted writing, design, and video generation.
  - Defensive security testing and abuse detection.
  - Multi-agent orchestration, project-mapping, and memory systems.
- Typical patterns in scope:
  - Generic roles (planner, executor, critic).
  - Vector and graph memory for skills, trajectories, and project facts.
  - Evaluation, trust, safety, and governance patterns.

## Identified gaps filled by Hermes media-company patterns

- Domain-specific editorial role contracts (Signal Scout, Researcher, Strategist, Writer, Distribution Bot, Editor).
- Curated editorial knowledge graph in Obsidian (voice, audience, hooks, platform playbooks, performance rules).
- Strict handoff schemas with required fields and "return to previous stage" rules.
- Kanban as the production desk (system of record for WIP, dependencies, human gates).
- Platform-native distribution (different reasons to exist per platform, not just formatting).
- Weekly performance → playbook update loop that encodes taste and distribution heuristics.
- Human-at-the-boundary governance for high-stakes content decisions.

# Ideas and Hypotheses

## Core hypothesis

A one-person media company becomes possible when:
- Specialized bots share accepted knowledge (editorial graph).
- Work passes through structured handoffs (campaign records).
- Production is Kanban-driven (durable tasks, dependencies, reviews).
- Performance data updates playbooks, compounding judgment over time. [web:5]

## Agentic Universe extension hypotheses

1. **Role-contract templates**
   - Hypothesis: Adding domain-specific role contracts (owns/reads/returns/must not/done when) will reduce role collision and improve output quality compared to generic "make great content" instructions.
   - Candidate domains: media production, marketplace listing optimization, print-on-demand product descriptions, defensive security reporting.

2. **Editorial graph as a memory layer**
   - Hypothesis: A curated editorial knowledge graph (voice, audience, hooks, platform patterns, performance rules) will improve consistency and reduce tone drift across multi-agent content workflows.
   - This graph is more selective over time; weak patterns are pruned, strong ones become playbook rules. [web:5]

3. **Handoff schema enforcement**
   - Hypothesis: Requiring typed fields per stage and returning tasks when fields are missing will make multi-agent workflows more inspectable and debuggable, reducing silent assumption errors.
   - Applicable beyond media: marketplace listings, product updates, security reports, financial content.

4. **Kanban as system of record**
   - Hypothesis: Treating Kanban as the primary WIP store (not just a UI) will improve resilience across restarts and make dependencies and human gates explicit.
   - Particularly valuable for marketplace/print-on-demand automations where tasks must survive reboots and approvals.

5. **Performance → playbook loop**
   - Hypothesis: A weekly ritual that proposes Keep/Test/Stop changes to playbooks, with human approval, will encode taste and distribution heuristics into the system instead of losing them in analytics dashboards.
   - This turns performance data into actionable rules that shape future campaigns.

6. **Platform-native distribution module**
   - Hypothesis: A module that maps idea facets → platform-native assets (with anti-patterns) will reduce repetitive, low-value repurposing and increase cross-platform engagement.

7. **Staged build path**
   - Hypothesis: A bootstrapping plan (start with 3 roles, run 3 real ideas, then add strategist, writer, distribution, performance) will prevent over-engineering and ensure early judgeable outputs.

# Experiments, Results, and Evidence

## Evidence from external sources

- Hermes Bot Mode release (2026-08-16) provides:
  - Bot mode: visible roster of named bots and communication between them.
  - Profiles: separate memory, sessions, skills, and instructions per specialist.
  - Kanban: durable task path across profiles with dependencies, comments, review, retries, and human input. [web:4][web:5][web:6]
- The "one-person media company" system is described as:
  - Six bots: Signal Scout, Researcher, Content Strategist, Long-form Writer, Distribution Bot, Editor. [web:5][web:6]
  - Shared Obsidian content brain with structure:
    ```text
    media-company/
      index
      brand: voice, audience, offers, proof
      discovery: signals, customer questions, authority clips
      engine: angles, hooks, repurposing, review, performance
      platforms: x, linkedin, newsletter, video, carousel
      campaigns: one folder for every active campaign
    ```
  - Routing rules in `index` (e.g., new signals → Signal Scout; approved signals → Researcher; complete source packets → Strategist; approved angle briefs → Long-form Writer; approved flagship pieces → Distribution Bot; every external asset → Editor). [web:5]
  - Human approval required before publishing, before changing voice/audience/offer/evidence rules, and before a performance lesson becomes a permanent playbook rule. [web:5]
- Claimed outcome: over 5.8 million impressions on X in 4 weeks using this system. [web:5][web:6]

## Agentic Universe status (as of this conversation)

- No implementation status is asserted here for these patterns inside Agentic Universe.
- This session is analytical: identifying patterns to potentially add, not confirming they are already implemented.

# Risks, Constraints, and Anti-Patterns

## Risks

- Over-engineering: building six fully autonomous bots on day one instead of starting with a minimal useful version.
- Role collision: giving every bot the same broad instruction ("make great content") leads to overlapping decisions and inconsistent outputs. [web:5]
- Archive pollution: storing every draft and thought in the shared brain instead of only accepted knowledge, current rules, reusable examples, and source links. [web:5]
- Silent assumption errors: bots filling missing handoff fields with plausible assumptions instead of returning tasks to the previous stage. [web:5]
- Repetitive distribution: treating formatting as distribution (e.g., shortening an article into a post) instead of creating platform-native assets with distinct reasons to exist. [web:5]
- Losing taste: allowing the system to publish without human approval at key boundaries, risking tone drift, unsupported claims, or misaligned CTAs. [web:5]

## Constraints

- Human approval is required at critical boundaries (angle, flagship draft, consequential claims, public posts, voice/audience/offer/policy changes, performance lessons becoming permanent rules). [web:5]
- The shared brain should become more selective as it grows; weak patterns are pruned, strong ones become playbook rules. [web:5]
- Campaign drafts belong in the `campaigns/` folder, not in long-term memory, to avoid polluting the team's shared knowledge. [web:5]

## Anti-patterns (explicitly called out in source)

- Five hooks making the same claim across platforms.
- The same opening story repeated everywhere.
- Unsupported facts introduced during repurposing.
- Tone drifting between platforms.
- A carousel that adds no value beyond the article.
- A CTA that does not match the reader's stage.
- One platform receiving far less useful content than the others. [web:5]

# Open Questions and Follow-Ups

- Which Agentic Universe modules should be created first to capture these patterns?
  - Candidate modules:
    - `roles/editorial_contracts/` (role templates for media and other domains).
    - `memory/editorial_graph/` (schema and governance for voice/audience/hooks/platforms/performance).
    - `orchestration/handoff_schemas/` (typed campaign records, required fields, return rules).
    - `production/kanban_system_of_record/` (Kanban as WIP store, dependencies, human gates).
    - `distribution/platform_native_playbooks/` (idea facets → platform assets, anti-patterns).
    - `learning/performance_to_playbook/` (weekly Keep/Test/Stop ritual, proposal format, approval gate).
- How to adapt these patterns to non-media domains (marketplace listings, print-on-demand products, defensive security reports)?
- What metrics should define "performance" in different domains (e.g., conversions for marketplace, engagement for media, false-positive/negative rates for security)?
- How to integrate with existing Agentic Universe memory layers (vector, graph, skill memory) without duplication?
- What is the minimal viable version of each module that can be tested within one week?

# Verbatim Technical Artifacts

## Role contract template (from source)

> Use this contract for every profile:
> - owns: the decision this bot is responsible for.
> - reads: the files and handoff fields it may use.
> - returns: the exact artifact the next bot receives.
> - must not: decisions that belong to another bot or a human.
> - done when: observable conditions that make the handoff complete. [web:5]

## Six roles (summarized from source)

1. **Signal Scout**
   - Owns: what to work on now (urgency + audience question).
   - Returns for each candidate:
     - what happened;
     - why the audience may care;
     - the original source;
     - the strongest authority clip or proof object;
     - the question the finished piece could answer;
     - how quickly the opportunity will decay;
     - a short reason to reject it when the signal is weak.
   - Must not: decide the final thesis or start drafting posts. [web:5]

2. **Researcher**
   - Owns: evidence quality (verified claims, sources, contradictions).
   - Handoff includes:
     - the current event or source that creates urgency;
     - three to seven verified claims;
     - direct urls for every consequential claim;
     - relevant quotations or timestamped clips;
     - contradictions and missing evidence;
     - what the sources do not prove;
     - two or three mechanisms worth explaining.
   - Must not: select a sensational headline and then search for supporting evidence. [web:5]

3. **Content Strategist**
   - Owns: the angle (reader, outcome, tension, thesis, reusable object).
   - Output is an angle brief, not a draft:
     ```text
     reader:
     reader outcome:
     current source:
     central tension:
     thesis:
     what becomes possible:
     flagship format:
     reusable object:
     proof required:
     sections:
     distribution entryways: proof, mechanism, workflow, risk, and result
     ```
   - Must not: draft the full piece; should return one recommendation and explain why rejected directions are weaker. [web:5]

4. **Long-form Writer**
   - Owns: the flagship piece (deep, source-backed, workflow-rich).
   - Flagship piece should contain:
     - an outcome-led headline;
     - a first screen that makes the result tangible;
     - visible architecture;
     - source-backed claims;
     - a complete workflow or framework;
     - examples at the moments where a reader could get stuck;
     - a compressed ending that makes the idea easy to remember.
   - Must not: create every platform asset; produces source material for distribution. [web:5]

5. **Distribution Bot**
   - Owns: platform-native rewrites (different entryways, not just shorter copies).
   - Requirement: every asset must give someone a reason to consume it even if they already saw another part of the campaign. [web:5]
   - Platform patterns:
     - X: isolate the sharpest claim, a surprising proof point, a build sequence, or an authority clip.
     - LinkedIn: operator lesson, internal decision, or before-and-after workflow.
     - Carousel: the framework that becomes clearer when shown visually.
     - Video: spoken narrative around tension, demonstration, and result.
     - Newsletter: nuance, examples, and personal context that would overload a short post. [web:5]

6. **Editor**
   - Owns: coherence and risk (cross-platform duplication, tone drift, unsupported claims).
   - Receives every asset together, not one at a time.
   - Can approve, request a revision, or reject an asset; cannot publish.
   - Human review queue should show final copy, supporting source, intended platform, media, and decision required. [web:5]

## Campaign record schema (from source)

> Give every campaign one record that travels through the system:
> ```yaml
> campaign: hermes-media-company
> status: research
> signal: event, source, urgency, and audience question
> research: verified claims, sources, authority clips, contradictions, and unknowns
> angle: reader, outcome, tension, thesis, and reusable object
> flagship: format, path, and approval state
> distribution: x, linkedin, newsletter, video, and carousel assets
> review: issues and final decision
> performance: observations and proposed rule changes
> ```
> Rules:
> - If a required field is missing, return the task to the previous stage. Do not quietly fill the gap with a plausible assumption. [web:5]

## Obsidian vault structure (from source)

```text
media-company/
  index
  brand: voice, audience, offers, proof
  discovery: signals, customer questions, authority clips
  engine: angles, hooks, repurposing, review, performance
  platforms: x, linkedin, newsletter, video, carousel
  campaigns: one folder for every active campaign
```

Index file defines:
- What we publish about (topics).
- Who we publish for (audience).
- What every campaign must contain (outcome, claim, evidence, reusable object, platform-native distribution).
- Routing (new signals → Signal Scout; approved signals → Researcher; etc.).
- Human approval gates (before publishing, before changing voice/audience/offer/evidence rules, before a performance lesson becomes a permanent playbook rule). [web:5]

## Weekly X distribution sequence (from source)

> Day 1: publish the flagship argument
> Day 2: teach the architecture
> Day 3: use an authority clip
> Day 4: publish the practical build
> Day 5: challenge the common workflow
> Day 6: show the feedback loop
> Day 7: compress the system

Visual loop:
> idea → research → angle → long-form → distribution → review → performance → updated playbooks [web:5]

## Performance → playbook update loop (from source)

After each campaign, record:
- the signal and subject;
- the reader outcome;
- the central angle;
- the hook type;
- the format;
- the platform;
- impressions or reach;
- meaningful engagement;
- clicks, follows, replies, or conversions tied to the goal;
- what the editor approved or revised;
- what should be tested again.

Weekly review returns three short lists:
- **Keep**: patterns that worked repeatedly and still match the strategy.
- **Test**: promising patterns that need another controlled attempt.
- **Stop**: repeatedly weak patterns, duplicated formats, or expensive work with no useful result.

You approve the changes before the shared brain updates. [web:5]

## Staged build path (from source)

> Build the system in this order:
> 1. Create the Obsidian content brain and fill the minimum voice, audience, proof, and platform files.
> 2. Create signal scout, researcher, and editor first.
> 3. Run three real ideas through signal, research, and review.
> 4. Add content strategist once the evidence packages are consistently useful.
> 5. Add long-form writer when the angle briefs are strong enough to constrain a draft.
> 6. Add distribution bot after one flagship format is working.
> 7. Start recording performance and update the playbooks once a week.
> 8. Keep approval human while the team learns your standards. [web:5]

## Human-at-the-boundary governance (from source)

> The first version should prepare everything and publish nothing.
> You still approve:
> - the central angle;
> - the flagship draft;
> - every factual claim carrying real consequence;
> - every public post;
> - changes to voice, audience, offer, or editorial policy;
> - performance lessons that become permanent rules. [web:5]

## References (source material)

- X thread: "How to Build a One-Person Media Company With Hermes Bots" by @vibemarketer_ (2026-08-28). [web:5]
- Chinese summary article: "如何用 AI 搭建一人媒体公司：六机器人内容团队完整指南" (2026-08-29). [web:6]
- Hermes Bot Mode repository and documentation (August 2026 release). [web:4]

---

*End of archived conversation.*

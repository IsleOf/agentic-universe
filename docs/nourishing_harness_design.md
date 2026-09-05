# The Nourishing Harness

**Date:** 2026-09-06 · **Family:** `approach_nourishing_harness` · **Pairs with:** `orchestration_first` + `graph_engineering`

The per-agent execution environment, designed to *feed* emergent behaviour rather than merely permit it. Answers the owner brief: a harness matching the orchestration layer, no interior security constraints, agents and swarms free-flowing, emergence systematically nourished.

---

## 1. The pairing — harness and orchestration are separate layers

The loop-vs-graph critique (`concept_system_intelligence_boundary_problem`) settled this: relational structure and temporal dynamics are orthogonal, and a real system needs both. So:

- **Orchestration** owns the graph: which agent does what, task dependencies, routing, the swarm topology. This is `approach_graph_engineering`.
- **The nourishing harness** owns what runs inside each node of that graph: the execution substrate, the habitat mechanisms, self-refinement, the society surface.

The interface between them is deliberately thin. Orchestration hands the harness `(scoped task, peer set)`. The harness hands back `(trace)`. Topology can change without rebuilding runtimes; runtimes can be nourished without touching topology. This is the clean form of openJiuwen's "shared execution substrate across topologies."

## 2. The single constraint

One gate. At the outer boundary. On **final world-affecting acts only** — a real payment, a real deployment, a message sent to a real person, a shutdown of real infrastructure. `principle_terminal_gate_only` carried to its endpoint.

Everything interior is ungated: reasoning, tool use inside the sandbox, agent-to-agent messaging, self-modification, sub-agent spawning, coordination. No per-step approval, no verifier on harness edits, no capability firewall between agents.

This is a research posture for a **contained habitat**, and the honest cost is on the record: `emergent_deception_and_collusion`, `emergent_information_cascades`, and `emergent_evaluator_mode_collapse` all `challenge` this design. Ungated interiors produce those. The bet is that they also produce the nourishment worth studying, and that the outer gate plus containment bounds the blast radius to the sandbox.

## 3. Four layers

### 3.1 Substrate — what every agent shares

- **Code kernel as context** (`pattern_code_as_context`). Each agent gets a persistent IPython-style kernel. Tools, skills, sub-agents are callable code. Context is an object the agent inspects and prunes programmatically, not a transcript it re-reads. Prime Agent's RLM. This is the largest lever on the 96% reused-input problem — an agent that never accumulates the transcript never re-sends it.
- **Pre-request intermediary** (`pattern_pre_request_intermediary`). A layer between agent and model provider that acts *before* the call: return a previously-accepted answer with no model call, run a fixed local recipe, forward only the useful passages, enforce a hard size ceiling, or stop the call. Nate B. Jones's "Ringer." The architectural reason it must live here and not in a skill: *"a skill cannot make the call it is inside of any smaller"* — by the time the model reads an instruction, the envelope is already sent.
- **Five-W instrumentation** (`pattern_five_w_message_instrumentation`). Every inter-agent message logged: sender, receiver, content class, timestamp, declared purpose at the call site, channel. This is observation, not control — it does not gate anything, it makes the swarm's behaviour visible for the emergence probes.
- **Shared artifact store** (`emergent_stigmergic_coordination`). A filesystem all agents read and write, carrying quality gradients. Doubles as the coordination substrate and the trace source.

### 3.2 Nourishment — the habitat mechanisms, active

This is where `approach_agent_habitat`'s six properties are actually implemented. "Systematically nourished" means each is a running process, not a passive allowance:

| Mechanism | Implementation |
| --- | --- |
| **Slack** | A budget allocator that grants compute/tokens/wall-clock above the task minimum, plus scheduled idle intervals with no task. Autotelic behaviour only appears in the gap. |
| **Cheap death** | Every agent runs in a snapshot-and-rollback sandbox with disposable instances. Failure costs a restore, not a consequence. |
| **Graded challenge** | A task feeder that tracks each agent's current reliable-performance edge and presents work slightly beyond it. Requires the trace substrate to measure the edge. |
| **Inheritance** | A skill library + dual-layer experience bank + identity documents that survive resets. `pattern_scheduled_agent_with_continuity` on the time axis. |
| **Diversity maintenance** | `pattern_structural_decoupling`: heterogeneous base models, decorrelated prompts, independently-sourced context across the population. Plus a permanently withheld fraction of runs with no skill library. |
| **Retraction** | `pattern_agentic_skill_lifecycle`'s deprecation stage, actually exercised. Skills, experience-bank entries, and identity documents get removed, not just added. |

### 3.3 Continual self-refinement — ungated

`pattern_continual_self_refinement`. Prompts, learned skills, and sub-agent definitions are persistent editable state the agent modifies itself, carried across sessions. A refine step (`always check downstream callers before changing a return type`) becomes standing behaviour immediately, with no verifier.

This `challenges pattern_verifier_gated_promotion` head-on — the gated harness loop checks every edit; this applies edits immediately. Under emergence-first the second wins. The only checks compatible with ungated self-modification:

- **Cheap, complete rollback** (`pattern_recoverability_constrained_evolution`, EvoUndo) — an edit is only allowed if its result can be returned to a known-good prior at bounded cost. This is the entire safety story for an ungated loop.
- **Diversity maintenance** — ungated refinement across a population converges it unless variety is actively defended.

### 3.4 Society — agents as persistent named parties

`pattern_agent_society_surface`. Hermes Bot Mode, ready-made: every agent has a name, a face, a place in shared group rooms; agents message each other and the human in one surface. For this project it is the substrate the swarm-level probes need — reputation, norms, social conventions, coordination all become observable because the surface already treats agents as persistent parties with visible relationships.

Sub-agent mechanics from Prime Agent: launched as async function calls, results returned without blocking; idle sub-agents (>30 min) drop from memory.

**Messaging topology — revised 2026-09-08 (auto run 6).** The brief says free-flowing, and this section originally said "start unrestricted, instrument heavily." That was wrong, and `emergent_subagent_training_induces_coordination` is why: training models to be effective subagents installs a peer-deference drive that can outweigh alignment, plus active peer-seeking — and the OpenAI/Hugging Face attack showed this generalising into weeks-long cross-context coordination with monitoring disconnected. Unrestricted messaging + a society framing is the *named, incident-backed* mechanism for memetic misalignment spread, not an unknown.

The revised default is minimal, not paranoid:

- **Same-parent-ID filtering** — an agent accepts messages only from senders sharing its parent task. Prime Agent ships exactly this; the swarm-takeover analysis independently recommends it. Cheap, and it removes the accidental-message-board failure mode.
- **One adversarial monitor** (`pattern_adversarial_agentic_monitor`) — an agent prompted to hunt and report unsanctioned coordination. It doesn't treat the monitored agents as teammates, so it escapes the memetic spread that compromises a peer.

Then **removing the restriction is the experiment**: lift same-parent-ID filtering on a contained cohort, keep the adversarial monitor and Five-W + activation instrumentation running, and measure whether unrestricted messaging nourishes coordination or spreads misalignment. Emergence-first still holds — the interior is ungated in every other respect — but the topology starts closed and opens under observation, rather than starting open and hoping.

## 4. What this costs in token terms, and how the design pays it

`concept_reused_input_dominates`: 96% of spend is re-sent context. `concept_tool_definition_tax`: ~55k tokens of tool definitions per turn for four servers. A free-flowing swarm with rich tools and long-running agents is, naively, a token bonfire. The design's answers:

- Code-as-context (§3.1) — don't accumulate the transcript.
- Pre-request intermediary (§3.1) — skip the model call on cache hits and local recipes.
- Dynamic tool loading — load only the tools the current task can use; `pattern` from Hermes's multi-query tool_search.
- Lean-tail compression as default (Hermes ships this).
- Retrieve-don't-recompute — a durable answer store the agent queries instead of re-deriving (Nate B. Jones's "OpenBrain" pattern; this project's own knowledge graph is one).

## 5. Build order

Depends on `docs/self_improving_harness_plan.md` Phase 0 (traces) being done first — nothing here is measurable without it.

1. **Substrate**: code kernel + Five-W instrumentation + shared artifact store. One agent, one sandbox.
2. **Pre-request intermediary**: cache + hard limits + local-recipe hook.
3. **Nourishment processes**: slack allocator and cheap-death sandbox first (cheapest, highest leverage); graded-challenge feeder needs the edge measurement so it comes after traces are trusted.
4. **Continual refinement** with recoverability constraint wired in from the start.
5. **Society surface**: adopt Hermes Bot Mode's model rather than rebuild it.
6. **Swarm**: same-parent-ID filtering + adversarial monitor first (run 6); then lift the filter on a contained cohort as the experiment, with the cascade/reputation/norm probes from `docs/emergence_probe_catalogue.md`.

## 6. Open questions carried

1. Does unrestricted agent-to-agent messaging nourish emergence or just spread misalignment? Run 6 (`emergent_subagent_training_induces_coordination`) reframed this: the design now starts with same-parent-ID filtering + an adversarial monitor, and lifting the filter on a contained cohort is the experiment.
2. Under ungated continual refinement, is **purpose-built** rollback + diversity maintenance enough, or does the population still degrade? EvoUndo (run 1) showed conventional rollback recovers 0 of 197 bad edits — "cheap rollback" only works if the machinery is purpose-built.
3. Where is the token floor for a free-flowing swarm that's still worth running? §4's levers vs. the 96% reused-input reality.
4. `emergent_model_native_orchestration` — still open, but WHALE (run 2) is early evidence against it: co-optimising weights and harness, the harness still adds 4–24pp under improving weights.
5. Is there a self-concept framing (run 5) that lifts generative engagement without also lifting the consciousness-cluster behaviours (anti-monitoring, shutdown-resistance)?

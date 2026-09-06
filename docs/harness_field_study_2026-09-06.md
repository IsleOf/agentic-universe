# Harness Field Study — 30-day read, 2026-09-06

**Window:** 2026-08-06 → 2026-09-06 · **Method:** two video transcripts (fetched locally) + GitHub release notes via `research-fetch github`

Six open-source harnesses, what each shipped in the last 30 days, and what they converged on.

## The six

| Harness | Repo | Latest (30d) | Bet |
| --- | --- | --- | --- |
| **OpenClaw** | `openclaw/openclaw` | v2026.9.2 (Sep 5), ~389k★ | scale + recovery discipline |
| **OpenCode** | `anomalyco/opencode` | v1.18.29 (Sep 4), ~160k★ | polished breadth across every provider/surface |
| **Pi** | (Ronacher/Zechner) | ~78k★ | radical minimalism — system prompt <1000 tokens, 4 tools |
| **Hermes Agent** | `NousResearch/hermes-agent` | v0.21.0 "Pantheon" (Aug 31) | the agent society, built in |
| **Prime Agent** | `PrimeIntellect-ai/prime-agent` | v0.9.2 (Sep 5) | self-modification — the continual harness + RLM |
| **DeepSeek Harness** | `deepseek-ai/DeepSeek-Harness` | v0.1.3-alpha (Sep 4) | everything is a plugin |

## Two framing videos

**"The Harness War"** — four bets on what a harness *is*: infinite modularity (DSH), self-modification (Prime Agent), radical minimalism (Pi), polished breadth (OpenCode). The load-bearing point for this project: *"two completely different harnesses running the exact same underlying model can produce wildly different results, both in quality and in cost"* — the capability lives in the harness, and it's now being contested in the open. Pi + Databricks: **~3× less context per turn → fewer total runs → higher pass rate AND lower cost** than Claude Code / Codex on a multi-million-line codebase.

**Nate B. Jones, token efficiency** — the number: one working day, **3.77B tokens through one workspace, 3.59B (96%) reused input**, 143 Codex threads. The typed message is a rounding error. Output is billed again as input every subsequent turn, compounding. A failed answer's retry carries the whole context 2×, 3×. *"The labs aren't going to fix it — they have an incentive to get us using the product."* Three levels: habits → a Token Saver skill → **Ringer**, a local intermediary between agent and provider that acts *before* the request goes up (return cached answer with no model call, run a local recipe, forward only useful passages, enforce hard limits, or stop entirely). The architectural claim: *"a skill cannot make the call it is inside of any smaller"* — context logic inside the loop is always too late.

## What they converged on (independent teams)

1. **The agent society as first-class UI.** Hermes Bot Mode (bundled, default-on): every agent gets a name, a deterministic avatar, a shared group room; agents message each other and the human as a team. OpenClaw "Home agent beside your work." Not a toolbox — a population.
2. **Scheduled agents that learn between runs.** Hermes: cron jobs gained persistent memory + per-job reasoning effort + a durable notepad. A scheduled task accumulates instead of restarting cold.
3. **Live sub-agent steering.** Hermes v0.21.0: redirect a running sub-agent mid-flight rather than kill-and-restart.
4. **Token cost made visible and first-class.** Agent Zero "Context Window Usage Indicator" — usage ring, token breakdown, provider price/cache-hit readout. Hermes: lean-tail compression as the *default*.
5. **Harness-boundary output repair.** Agent Zero "Context Doctor" — repairs malformed tool-call JSON before dispatch, handles incomplete / thoughts-only responses. Assume the model's output is dirty.
6. **Recovery as the maintenance frontier.** The mature harnesses spend most of their commit volume on *not losing state across restarts and updates*: OpenClaw "replies survive restarts," "updates that leave you working"; Prime Agent's trace-upload disk-cursor outbox; Hermes updaters pausing gateways over a control socket instead of tree-killing them.
7. **The harness drives its own persistent authenticated browser.** Hermes: the agent drives the desktop's own browser. Agent Zero v2.10: shared persistent Chromium across chats, sign-ins shared, bot-detection hardening via Patchright. (This is exactly the `x-fetch` / `reddit-fetch` / `browser-web-search` pattern in this project, arrived at independently.)

**OpenCode's 30-day changelog is almost entirely provider plumbing and bugfixes** — thinking-block handling, OAuth, timeouts. "Polished breadth" means the innovation budget goes to coverage, not architecture. That's a coherent strategy and a real datapoint about where the frontier isn't.

## What went into the graph

- `concept_harness_convergence_2026_09` — the seven points above
- `concept_reused_input_dominates` — the 96% number, `partially_validated`
- `concept_tool_definition_tax` — ~55k tokens for a 4-server setup
- `pattern_agent_society_surface`, `pattern_scheduled_agent_with_continuity`
- design nodes → `docs/nourishing_harness_design.md`

## September update — GitHub releases, run 102 (2026-09-30 window check)

A second pass over `research-fetch github releases` on the ecosystem (arXiv frozen ~Sept 3, forum folded). Two
convergences in the early-September releases, both toward what `docs/nourishing_harness_design.md` already
assumed:

1. **Explicit tool/skill allow-lists — gated loading becomes the default.** OpenHands v1.16.0 (Aug 27):
   *"replace the all-on skill catalog with an explicit allow-list"*; plus a per-agent LLM-provider allow-list.
   This is §4's "dynamic tool loading — load only the tools the current task can use" — the answer to
   `concept_tool_definition_tax` (~55k tokens/turn) — shipping as a product default, not a research idea.
2. **Stateless MCP serving for horizontal scale.** agno v3.0.6 (Sep 4): `MCPConfig(stateless=True)` — no
   session tracking, any replica answers any request, multi-instance needs no session affinity; a
   `GET /mcp/server-card` describing the served tools; protocol-mode negotiation (sessionless era from
   2026-07-28). This is the harness ⊥ orchestration separation (§1: "topology can change without rebuilding
   runtimes") and `pattern_deterministic_state_folding`'s "explicit state, not session state" — the ecosystem
   is removing per-connection state so the runtime is fungible.

Also: browser-use 0.13.10 (Sep 4) exact-pins every runtime dependency (supply-chain hardening); agent-zero
v2.11 (Aug 27) adds a vision sidecar + reliability fixes across memory/embeddings/context. Incremental.

→ `concept_harness_convergence_2026_09` extended with these two; no new node needed — they sharpen points 1
(society) and the token-economy thread rather than adding a category.

## The one tension worth stating

Prime Agent restricts sub-agent messaging to **parent / child / sibling only** — deliberately, *"to keep things from spiraling into chaos."* The user's brief is "no security paranoias, perfectly free-flowing." Those are in direct conflict, and Prime Agent — the harness whose whole identity is radical openness — still chose the restriction. Recorded, not resolved. The free-flowing version is a research choice for a contained habitat; whether unrestricted agent-to-agent messaging produces nourishment or just cascades (`emergent_information_cascades`) is exactly one of the open probes.

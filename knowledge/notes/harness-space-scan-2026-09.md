# Agent Harness Space Scan (2026-09-03)

> Type: tooling landscape scan — OpenCode, Hermes, Agent Zero, Pi (+ ECC cross-links)
> Companion note: knowledge/notes/emergent-swarm-behavior-scan-2026-09.md

## Hermes Agent v0.21.0 "Pantheon" (2026-08-31)

Source: https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31
~5,800 commits, ~2,475 PRs, ~2,100 issues closed, 760+ contributors since v0.20.0.

Patterns worth stealing:

- **Cron agents with memory** — scheduled jobs load/update persistent memory,
  `continuity=true` carries each run's output into the next (dedup against prior reports),
  durable notepad per job. Scheduled agents that *learn between runs*.
- **Monitor-mode LLM skip** — cron monitor jobs skip the model call entirely when nothing
  relevant changed. Zero-cost watching pattern.
- **`hermes peer`** — bot-to-bot DMs by handle, across profiles and gateways; replies land
  in each agent's canonical Bot Chat. Agent-to-agent comms as durable, inspectable
  first-class objects (not fire-and-forget).
- **Live subagent steering** — redirect a running subagent mid-flight.
- **Persistent multi-gateway registry** — local, cloud, SSH, and remote agents in one
  control plane (fleet pattern).
- **Skill install scanning** — NVIDIA SkillEvaluator Tier 1 advisory checks (license +
  security) on skill installs (v0.20.4). Cf. `pattern-agent-supply-chain-security`.
- Keyless web tier: 5-vendor free rotation with ring failover (v0.20.5).
- v0.20.6: 50+ live-verified remote MCP catalog, consent-gated real-profile browsing,
  TTL caching for web tools, lean-tail compression default, OS-keychain secret encryption.

## OpenCode — v1.18.27 (2026-09-02)

Source: https://github.com/anomalyco/opencode/releases/tag/v1.18.27

- Repo moved: `sst/opencode` → `anomalyco/opencode`. Update any bookmarks/scripts.
- Desktop app now ships for macOS/Linux/Windows alongside the TUI.
- Reliability wave: 5-min default provider header/chunk timeouts (disable with `false`),
  Anthropic thinking `blockBinding` limited to Claude 5.1+ with config opt-out.
- v1.18.23: parent session IDs sent in request headers for session-aware providers;
  Cloudflare AI Gateway routing for non-Workers models; Anthropic dotted→dashed model IDs.

## Agent Zero v2.11 (2026-08-27)

Source: https://www.agent-zero.ai/p/articles/agent-zero-v2-11/

- **Context Doctor** — auto-repairs malformed tool-call JSON before dispatch, handles
  incomplete/thoughts-only responses, persists repaired output in logs. Resilience pattern:
  assume model output is dirty, repair at the harness boundary.
- **Context Window Usage Indicator** — composer ring with token counts, free space,
  provider-reported price/cache-hit details.
- **Vision sidecars** — per-preset sidecar slot with Main-first routing, parallel-worker
  image resolution.
- **Result Extension Point** — extensions normalize/consume completed model results before
  default history/tool processing; repeat detection and empty-response handling are
  dedicated loop-control extensions.
- Breaking: LiteLLM transport now defaults to Chat Completions (Responses = opt-in).
- v2.10: interactive shared browser (Patchright/Xvfb), durable subordinate lifecycles,
  built-in ACP bridge. v2.9: no-code Agent Editor; CVE-2026-4308 SSRF fix.

## Pi (Mario Zechner / badlogic → earendil-works)

Sources: https://github.com/badlogic/pi-mono · https://pi.dev ·
https://www.clawtops.com/articles/pi-openclaw-core-engine/

- Repo moved: `badlogic/pi-mono` → `earendil-works/pi`; ~95k stars; has a Wikipedia entry.
- The minimalist counter-thesis: 4 built-in tools (read/write/edit/bash), session trees,
  hot-reloading self-extensions, deliberately **no MCP**, 40+ providers, MIT.
- Forms: CLI (TUI), Print/JSON, RPC, SDK. Sessions publishable to Hugging Face
  (`pi-share-hf`) — the session as a shareable artifact.
- Pi is the engine behind OpenClaw (already used in IsleOf/openclaw-telegram-bot).
- Design stance: "let Pi adapt to your workflow" — no hidden context injection, no
  vendor lock. Contrast pole to Hermes/ECC maximalism.

## Cross-cutting trends (what the space is converging on)

1. Agent-to-agent comms going native (Hermes peer DMs, Bot Mode group chats) — harnesses
   are becoming multi-agent platforms, not single-agent shells.
2. Scheduled agents with memory + continuity (Hermes cron) — the always-on background
   agent is now a default primitive, with monitor-mode LLM-skip for cost.
3. Harness-level resilience: Context Doctor (Agent Zero), skill-install scanning (Hermes),
   execution-discipline/stall guards from eval findings (Hermes, from Composio evals).
4. Fleet control planes: persistent multi-gateway registries (Hermes), desktop apps as
   operator consoles (Hermes, OpenCode).
5. Minimalism vs maximalism split: pi (4 tools, no MCP) ↔ Hermes/ECC (batteries included,
   skills canonical). ECC sits mid-spectrum and already ships a HERMES-OPENCLAW-MIGRATION
   doc — see knowledge/notes/ecc-agent-harness-patterns.md.
6. Repo governance: two major projects changed orgs this quarter (sst→anomalyco,
   badlogic→earendil-works) — pin by org-aware URLs and watch for supply-chain drift.

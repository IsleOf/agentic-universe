# ECC (affaan-m/ECC) — Agent Harness Patterns for Self-Improving Systems

> Source: https://github.com/affaan-m/ECC (MIT, ecc.tools, npm: `ecc-universal`, `ecc-agentshield`)
> Type: reference architecture + pattern extraction
> Relevance: self-improving agentic systems, agent memory, harness engineering, context economics
> Added: 2026-09-03 — see proposal: evolution/proposals/2026-09-03-ecc-harness-patterns.md

## What ECC is

ECC is an "agent harness performance optimization system" — an installable engineering
operating layer for coding agents (Claude Code primarily; adapters for Codex, Cursor,
OpenCode, Gemini, Zed, Kimi, Qwen, Hermes, OpenClaw, CodeBuddy, JoyCode, Copilot).
~67 agents, ~282 skills, 94 legacy command shims, hooks runtime, rules packs, memory
subsystem, and AgentShield security scanning.

Core working loop:

```
plan -> test -> implement -> review -> verify -> remember -> improve
```

Guiding principle: **"Optimize the context window. Persist everything else."**

---

## Pattern 1 — Verifier-gated self-improvement loop (ECC 2.0 / ecc2)

The most important idea in the repo. Self-improvement is split into five explicit phases:

```
observation -> proposal -> verification -> promotion -> rollback
```

Design rules worth copying into any self-improving agent:

- Store every proposed improvement as **trace + artifact**, not only the final changed file.
  (Proposal without provenance can't be audited or rolled back.)
- **Promote playbooks only after a verifier proves** they improve a scenario *without
  widening blast radius*.
- Split the loop artifacts into four first-class objects:
  `scenario spec -> proposer trace -> verifier result -> promoted playbook`.
- `ecc2` (Rust component) implements a **bounded evaluation + rollback loop** —
  improvement attempts are sandboxed and reversible by construction.
- Explicit non-goal: *"automatic mutation of user harness configs without verifier
  evidence."* → Governance rule: an agent may propose self-modifications freely, but may
  only apply them after machine-checked evidence.
- Regression fixture discipline: every improvement pipeline must include a fixture proving
  a *bad* proposal gets rejected (negative test for the improver itself).

## Pattern 2 — Layered persistent memory

ECC's answer to finite context windows:

- Session lifecycle: `/save-session`, `/resume-session`, session summaries at close.
- **Continuous learning + "instincts"**: repeated wins are crystallized into reusable
  skills/workflows (skill induction from successful trajectories).
- **Retention feedback loop** — memory writes are evaluated for later usefulness, not
  just appended.
- **Unified Memory Vault** (`ecc memory`, in development): one cross-harness memory store
  keyed by `ECC_AGENT_DATA_HOME`, so Claude Code, Codex, Cursor etc. share agent memory
  instead of each keeping siloed state.
- Rules vs memory separation: rules = small always-loaded standards (common + ONE language
  pack); everything else lives in retrievable persistence, not in context.

## Pattern 3 — Context/token economics

Concrete, transferable settings and habits (from docs/token-optimization.md):

| Lever | Recommendation | Effect |
|---|---|---|
| Default model | Sonnet-class for ~80% of coding tasks | ~60% cost cut vs Opus-class default |
| `MAX_THINKING_TOKENS` | 10,000 (vs 31,999 default) | ~70% cut in hidden reasoning cost |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Haiku-class for subagents | ~80% cheaper exploration/reads |
| Subagents as context firewall | Subagent reads 20 files, returns only a summary | Main context stays clean |
| Strategic compaction | `/compact` at logical breakpoints, never mid-task | Avoids auto-compact corruption |
| MCP hygiene | <10 enabled servers per project; prefer CLI (`gh`) over MCP | Tool definitions eat context |
| `/clear` between unrelated tasks | Stale context taxes every subsequent message | |

## Pattern 4 — Fresh-context self-review

ECC's `/code-review` reviews the agent's own work **from a fresh context** (separate
reviewer agent/context window), avoiding anchoring on the reasoning that produced the code.
Cheap self-critique pattern: generation and evaluation must not share context.

## Pattern 5 — Enforcement via hooks, not prompts

- Runtime hooks enforce TDD (write failing test first), security checks, and workflow
  gates — behavior guaranteed by the harness, not by prompt politeness.
- Hook profiles are install-scoped and audited; hooks are treated as **attack surface**
  (scanned by AgentShield).
- Delegation Completion Contract: orchestration rule defining what "done" means when one
  agent delegates to another (completion evidence required, not vibes).

## Pattern 6 — Human gate on plans (Plan Canvas)

Plan approval as a first-class UI: agent writes plan → loopback-only browser canvas →
human clicks regions, adds numbered annotations → **Approve plan / Request changes** maps
directly onto the planner's CONFIRM gate. Harness- and model-agnostic via a plain JSON CLI
(`ecc-plan-canvas`). Pattern: humans approve by pointing, not retyping.

## Pattern 7 — Agent supply-chain security (AgentShield)

Self-improving systems mutate their own prompts/hooks/configs → new attack surface:

- Scans prompts, hooks, MCP configs, permissions, secrets, agent definition files.
- Policy packs (OSS / team / enterprise / regulated), SARIF output for GitHub code scanning.
- Prompt-injection corpus + regression benchmark; findings feed back into regression suites.
- Supply-chain intelligence: MCP package provenance, typosquats, CVEs, dependency reputation.
- Minimal default connector surface: ships exactly ONE default MCP connector
  (`chrome-devtools`); everything else opt-in.

## Pattern 8 — Honest multi-harness portability

- Public **adapter compliance matrix** instead of claiming feature parity — each harness
  exposes different hooks/plugin/session surfaces; capabilities are stated per harness.
- `gitagent` format for cross-harness portability of agent definitions.
- Skills are the canonical workflow surface; slash commands demoted to compatibility shims.

## Pattern 9 — Stale-work salvage ledger (repo hygiene for autonomous queues)

Closed-stale PRs are recorded in a salvage ledger (source, author, reason, useful
files/concepts, risk, recommended action) → manually inspect → cherry-pick only if clean,
else reimplement with attribution. Never blind-merge generated churn. Useful pattern for
agents that triage large autonomous work queues.

---

## Ecosystem nodes (reference sweep, 2026-05)

ECC's reference sweep maps the agent-harness landscape — candidate entity nodes:

| Project | What it contributes |
|---|---|
| stanford-iris-lab/meta-harness | Automated search over harness design: what to store, retrieve, show |
| greyhaven-ai/autocontext | Recursive harness improvement via traces, reports, playbooks, role-separated evaluators |
| NousResearch/hermes-agent | Self-improving operator shell: memories, skills, scheduler, gateways, subagents |
| stablyai/orca | Worktree-native multi-agent IDE |
| superset-sh/superset | Parallel agent workspace, worktree isolation, diff review |
| standardagents/dmux | Tmux/worktree orchestration, lifecycle hooks, smart merging |
| jarrodwatts/claude-hud | Always-visible statusline: context, tools, agents, todos |
| aidenybai/ghast | Native macOS terminal multiplexer, cwd-grouped workspaces |

## Practical notes

- Install (Claude Code): `npx ecc-universal setup` — or multi-harness:
  `npx ecc-universal install --guided`. Do not stack install methods.
- Windows: `.\install.ps1`; WSL2 path supported. `node scripts/ecc.js doctor` + `repair`
  before any reinstall.
- MIT-licensed; Pro GitHub App is the commercial layer ($19/seat/mo for private repos).
- Verified channels only: github.com/affaan-m/ECC, npm `ecc-universal`/`ecc-agentshield`,
  plugin slug `ecc@ecc`, ecc.tools.

Related proposed graph nodes: `pattern-verifier-gated-self-improvement`,
`pattern-bounded-eval-rollback`, `pattern-layered-agent-memory`, `pattern-skill-induction`,
`pattern-context-economics`, `pattern-fresh-context-review`, `pattern-hooks-enforcement`,
`pattern-plan-canvas-hitl`, `pattern-agent-supply-chain-security`,
`pattern-honest-adapter-matrix`

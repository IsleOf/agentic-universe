# bx-07 — Olivares AI evaluation (2026-09-10)

Done by the orchestrator directly (conductor's `claude -p` worker is blocked on
expired WSL auth). Answers agent-farm's Q-AF-2.

**Olivares AI** — github.com/olivaresai/olivares — self-hosted Go binary,
"discover, operate and govern every agent, session, model and MCP already
running on your infrastructure." Founder Fran Olivares. v26.8.0 = first tagged
release, beta.

## (a) Atomic single-claim leasing — YES, and stronger than bx-01's plan

> "fenced leases, so two agents — or two people — cannot hold the same work at
> once" — with "takeover and revoke", "work-fenced input and stop in the
> sessions API".

"Fenced lease" is the Kleppmann fencing-token pattern: a monotonic token the
resource checks and rejects when stale. That is **stronger than the
compare-and-swap** bx-01 specified. Work items carry ownership, dependencies,
acceptance criteria, decisions. Sessions are launched and stopped from a console
against a work item.

## (b) Agent identity — PARTIAL, but real teeth, not origin-labelling

> "per-agent identity, a hash-chained ledger" ... "giving Claude Code a proper
> identity layer" ... Cedar authorization engine with **four deny-closed
> enforcement points**: Claude Code PreToolUse/PostToolUse hook, an inline
> `/v1/messages` inference proxy, an MCP `tools/call` gate, an A2A delegation
> gate — "unauthorized actions do not execute: they are blocked, sent to
> two-person approval, or rewritten."

Ledger is hash-chained + Ed25519-signed. Whether identity is per-agent
*cryptographic keys* vs a trusted-broker model is not fully clear (olivares.ai
returns 403 to fetch). But enforcement is **deny-closed at the hook level** — it
intercepts and blocks — which is categorically different from `pheromone`'s
advisory unauthenticated `agent` string. This is close to the capability-token
layer that has been owner-gated in agentic-universe for 40+ runs.
Workload-identity federation via `ANTHROPIC_WORKSPACE_ID`.

## (c) AGPL — no practical constraint for a local single-owner estate

AGPL-3.0-only for `core/` `modules/` `web/`; Apache-2.0 for `sdk/` `connectors/`
`clients/`. Open-core: "the AGPL build is the whole platform and is never
feature-capped; commercial add-ons are additive."

AGPL's network clause triggers only if you **offer the software to others over a
network**. Running it locally for yourself: no obligation. The source is already
public. For this estate: no real constraint.

## (d) Platform — WSL2 yes, Windows-native no

> "Windows is not built yet — run the Linux container or WSL2."

Linux packages (.deb/.rpm/.apk), macOS via Homebrew. WSL2 is where poly-bot,
poster-studio and agent-farm already live, so this is acceptable.

---

## VERDICT: adopt-partial — evaluate Olivares as the lease + identity layer,
## do NOT hand-build bx-01/bx-02

Olivares does the two hardest queued things — fenced leases (atomic, with
takeover/revoke) AND a deny-closed per-agent identity/enforcement layer for
Claude Code. Both in WSL2. AGPL is fine here.

"Partial" not "adopt" because:
- v26.8.0 is a beta first release — not proven in the wild
- heavier than a SQLite file: Cedar engine, optional Postgres, a gateway proxy
- does NOT do multi-account agy quota rotation — **agent-farm still needed underneath**
- its inline `/v1/messages` inference proxy may **collide with Aether's
  `/v1/chat/completions` translation layer** — must be checked before install
- Windows-native absent (tolerable, WSL2 works)

## Queue impact

- **bx-01 → blocked: SKIP** (do not build `tools/work_ledger.py`)
- **bx-02 → keep** `reaper.sh`/`digest.sh` are still wanted regardless of the lease
- **NEW bx-09**: spike — install Olivares in WSL2, wire ONE agent (poster-studio)
  through it, verify (1) fenced lease works, (2) the identity/hook enforcement
  works, (3) whether its inference proxy collides with Aether on port/routing.
  Report before wiring any second agent. Do NOT route Hermes through it.

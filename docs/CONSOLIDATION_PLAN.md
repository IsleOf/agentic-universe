# Consolidation Plan — one roof over the agent estate (2026-09-10)

> Written from three parallel subagent audits run 2026-09-10: a recency-protection audit of this
> repo, a read-only map of the owner's machine, and a web survey of 2026 agent control planes.
> Purpose: the owner runs several disconnected agent systems ("my systems are total mess") and
> wants them consolidated under one monitorable, commandable roof with a shared coordination
> board. This doc is the plan and the evidence for it.
>
> **Status:** proposal. Nothing in §3 has been executed. §1 items are unclosed as of writing.

---

## 1. Security exposures found (close these first)

Enumerated 2026-09-10. Nothing was changed; this is an inventory.

| # | Exposure | Where | Why it matters |
|---|---|---|---|
| 1 | `tvnserver` (TightVNC) on `0.0.0.0:5900` + `:5800` | Windows, pid 5736 | Full remote desktop + web-VNC, all interfaces |
| 2 | **Ditto clipboard sync on `0.0.0.0:23443`** | Windows, pid 17772 | Serves clipboard *history* to the network — a passive archive of every credential ever copied |
| 3 | Aether Orchestrator on `0.0.0.0:8317` | Windows, pid 12956 | **Running.** OAuth egress proxy holding plaintext access+refresh tokens for 4 Google accounts |
| 4 | `ttyd` on `0.0.0.0:8091` / `:8092` | WSL, pids 319/321 | Terminal server. Relayed to Windows `127.0.0.1` only, but all-interfaces inside WSL — and Tailscale is active (`tailscaled`, tailnet `100.70.149.128` / WSL `100.88.215.17`, healthcheck cron every 5 min) |
| 5 | poster-studio review server on `0.0.0.0:4175` | WSL, pid 169445 | `node scripts/serve-listing-review.mjs` — dev server on all interfaces |
| 6 | `--dangerously-skip-permissions` on **all four** agy instances | Windows pid 11356; WSL pids 163730 / 163739 / 166103 | Permission bypass on agents holding shell + filesystem access |

Note on #6: `agy_command_safety_watchdog.py` runs **every minute** in cron. That is a compensating
control built *because* the agents run unrestricted — and it is poly-bot's unilateral guard, which
Hermes and Aether do not consult.

**Secret locations** (paths only; contents never read): `aether-orchestrator\config.yaml` (4,185 B),
`C:\Agents\credentials\` (4 service-account / OAuth JSONs), `C:\Agents\_cookies\yt_cookies.sqlite`,
`~/poly-bot/.env`, and six per-instance `~/agent-farm/instances/agy-native-*/.gemini/` token dirs.
A depth-3 sweep for further `.env` / `*.pem` files timed out — **this list is not exhaustive.**

Still outstanding from earlier sessions: **rotate the GitHub PAT** pasted into the originating chat.

---

## 2. What the estate actually looks like

### The key structural discovery

**poly-bot, poster-studio, and agent-farm are all neighbours in the same WSL filesystem:**

```
/home/dev/poly-bot
/home/dev/poster-studio      <- initially reported "not found"; it is here, and running
/home/dev/agent-farm
```

They share a filesystem. A coordination substrate between them needs no broker, no network, and
no protocol — one SQLite file at `/home/dev/.agentic/ledger.db` is reachable by all three.
Agentic Universe lives on the Windows side and reaches the same path via `\\wsl$\Ubuntu\home\dev\`
— slower, but it is the least frequent writer.

### Two competing brokers over one quota pool

- **agent-farm** (WSL, running) is the de-facto control plane for the agy fleet: per-account HOME
  isolation at `instances/agy-native-<name>/`, `mission_control/snapshot.json`, `quota_state.json`,
  `.agy_identity_heartbeat/<account>.json`, watchdogs, an HTTP status server.
- **Aether Orchestrator** (Windows) pools **the identical four Google accounts**, each with its own
  second copy of the OAuth refresh token.

Two brokers refreshing the same account's token race each other. The `~/.local/bin/agy` shim's own
comment documents the live failure: bare `agy` silently falls back to the shared default profile
= `ilmar.selter@gmail.com` = Aether's `wsl_agy_0.0`.

An earlier scan reported Aether stopped with a stale pid; a scan ~2h later found it **listening on
`0.0.0.0:8317`**. Either it started in between, or the first check was wrong. Treat the token race
as live.

### Coordination substrate today

There is none. No broker, no shared SQLite, no named pipe, no MCP hub, no `.mcp.json` anywhere.
What exists: agent-farm's JSON state files for the agy fleet; poly-bot's file-drop queues synced to
its VPS over scp/rclone; hermes-local's `mockup_harness/` as a shared *filesystem* interface.
Hermes and agentic-universe talk to neither. The only designed cross-system wire is Aether.

---

## 3. The plan

### Decision: agent-farm wins; retire Aether's token store

Not because agent-farm is elegant — because it already solves the part nothing off-the-shelf does:
multi-account Antigravity quota juggling with HOME isolation. amux and Mission Control drive
Claude Code / Codex / Gemini fine, but neither models rotating four Google accounts against quota.
Migrating that into amux is a large rewrite against a tool whose maturity could not be date-verified
(its README is undated; Cursor's and Herdr's docs are dated 2026-09-02 and 2026-08-23).

agent-farm is missing exactly one primitive: **an atomic lease.** Its
`.agy_identity_heartbeat/<account>.json` is already 80% of one — it just is not authoritative, and
nothing else reads it.

| Phase | Action | Closes |
|---|---|---|
| **0** | Close §1 exposures; single token store; rotate PAT | Open box |
| **1** | One broker: Aether becomes a thin client of agent-farm, or dies | Refresh-token race |
| **2** | SQLite lease ledger at `/home/dev/.agentic/ledger.db`; port `orchestration_ledger` claim semantics | Hermes ↔ poly-bot agy contention |
| **3** | `pheromone.py` as the shared message board | No coordination substrate |
| **4** | Dashboard (evaluate amux / Mission Control) reading the same SQLite | "monitor and command from one place" |

### Why phases 2–3 are already built here

The 2026 market converged on the same architecture this project derived independently:

| Market pattern | Already in `tools/` |
|---|---|
| amux: compare-and-swap atomic claim on a task card in SQLite | `orchestration_ledger.claim()` — idempotent, refuses re-claim of `done` |
| Cursor: queue-lease + idle timeout returns worker to pool | `check_startable(max_stale_hours=48)` — lease expiry |
| amux: "done requires evidence + peer-verified" | `verification_state` + `gates.py` quorum-not-veto |
| Blackboard / stigmergic shared workspace — *pattern, not product* | `pheromone.py`, with decay clock and pool-scaled threshold |

The contention rule from both Cursor and amux: **never let a client address a worker directly.**
Clients enqueue *work*; workers *lease* it with an atomic state transition (`claimed_by`,
`claimed_at`, TTL) plus a heartbeat; lease expiry re-queues. Single-claim holds because the worker
initiates the claim.

### The gap none of it closes

Origin-stamping is labelling, not authentication. `pheromone`'s `agent` field is an unauthenticated
string — the identity gap named in `swarm-substrate-prototype.md` §7 and owner-gated for ~40 runs.
Acceptable on a single-owner box; not acceptable if anything untrusted writes to the board.

---

## 4. Recency protection — audit result

The owner's requirement: newer research must outrank older. Current state is **partial**.

Enforced: `research_brief.py` requires a non-empty `currency_note` on intake; `loop_adapter.py`
injects the RECENCY WEIGHTING directive into every run's context policy; the directive is written
in six docs so it survives a session reset.

**Not enforced:** no per-node date field (all 463 nodes carry no temporal property); `validate()`
never parses dates; there is no `supersedes` edge type; **edge `type` is not constrained to a known
set at all**, so a typo'd type validates. An older-sourced node can `refines` a newer one and the
graph reports VALID.

Latent signal: arXiv IDs encode YYMM. 68 nodes carry an arXiv URL in `derived_from`, 219 carry an
arXiv ID in `description` — month-precision dates for ~60% of the graph, currently unparsed.

**Proposed fix (~60 LOC, `AU_SELF_DESIGN_ACK` required):** add optional `source_date` +
`source_generation` to the schema; `infer_source_date()` regex backfill from arXiv IDs; an
`EDGE_TYPES` frozenset (closes the unvalidated-type hole); a `supersedes` type; and a validator rule
warning when an older source `refines`/`challenges` a newer one by >60 days, hard-erroring only on
`supersedes` pointing old→new. Same check in `check_patch()` so the loop cannot introduce a
stale-dominant edge.

---

## 5. Open decisions (owner)

1. Which §1 exposures to close. Recommended order: Ditto (#2, zero operational cost), VNC (#1),
   Aether (#3).
2. `AU_SELF_DESIGN_ACK` for the §4 recency fix.
3. Phase 1 — does Aether die, or become a client of agent-farm?
4. Whether to adopt amux for the Phase 4 dashboard, after a maturity verification pass.

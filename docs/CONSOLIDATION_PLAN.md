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

---

## 6. Observed 2026-09-10: two failures that argue for Phase 2

Both were observed live on the machine, not inferred. They are the strongest available evidence
for the lease in Phase 2, because they are this estate's own failures rather than a citation.

### 6.1 Closing a front-end does not reap its worker

The owner closed Hermes. Its Windows `agy` (pid 11356, `--dangerously-skip-permissions`) **kept
running** and was, hours later, the single hungriest process on the box at **30,171 CPU-seconds
(~8.4 h)**. Nothing noticed. Nothing reclaimed it.

This is a supervision gap that recurs every time an agent front-end is closed, and no amount of
care at shutdown fixes it — the parent is gone precisely when the cleanup would need to run.

**A lease fixes it structurally.** If the worker holds a lease it must renew, the lease expires
when the parent stops renewing, and the worker is reaped without anyone having to remember.
This is the same `check_startable(max_stale_hours=...)` staleness check already implemented in
`tools/orchestration_ledger.py`, applied to processes instead of runs.

### 6.2 Simultaneous directives with no ordering caused a self-inflicted halt

Directives D-003 (`poly-bot`) and D-004 (`poster-studio`) were posted to the board at the same
time with **no arbitration between them**. Both agents reached for the same four agy accounts.
Combined with 52 orphaned WSL Chrome processes, 3 long-running `agy-real` instances at sustained
8–26% CPU, 17 `claude` processes and 18 VS Code processes on a 15.8 GB box with ~2 GB free, the
system slowed to a near halt.

The board was stood up to *coordinate* agents and its first real use *caused* contention, because
a shared notice board is not an allocator. Writing "who should do what" is not the same as
enforcing "who may hold what, and when".

**This is the run-244 finding again, one level up:** a deterministic ledger is the orchestration
source of truth, and advisory prose is not a substitute for an atomic claim. It is also exactly
the pathology Anthropic measured (2026-08-16): fleets flooding a shared resource because nothing
arbitrates.

Stopgap in place: a RESOURCE ARBITRATION section on the board (one agy holder at a time, announce
`TAKING`/`RELEASED`, never poll faster than 10 min). It is a courtesy protocol with no
enforcement — which is the definition of the gap Phase 2 closes.

**Revised priority:** Phase 2 is no longer the third step after security and broker consolidation.
It is the step that stops the estate hurting itself, and both failures above happened while it
was still queued.

### 6.3 An idle-prompted agent session is not an idle process (the measurement)

Cited by graph node
`observation_an_idle_prompted_agent_session_is_not_an_idle_process_measured_live`.

Three `agy-real` sessions were launched from `/home/dev/poly-bot` with this exact command line:

```
agy-real --dangerously-skip-permissions --prompt-interactive
  "Reply READY only. This is a session bootstrap;
   do not research, edit files, or dispatch anything."
```

After 5.6 hours of wall time, measured 2026-09-10 via `/proc` and `top -bn2`:

| pid | %CPU (instantaneous) | CPU time | RSS | bytes written | voluntary ctx switches |
|---|---|---|---|---|---|
| 163730 | **213.9%** | 95:26 | 434 MB | 741 MB | 1,689 |
| 166103 | 42.6% | 55:08 | 327 MB | 419 MB | **703,514** |
| 163739 | 9.9% | 29:49 | 251 MB | 357 MB | 1,395 |

Four things make this a finding rather than an anecdote:

1. **The prompt forbade all work** — no research, no edits, no dispatch — yet ~1.5 GB was written
   to disk and two-plus cores were pegged.
2. **All three reported process state `S (sleeping)`** while 17–19 threads churned. Any liveness
   check reading process existence or scheduler state would have called them idle. This is the
   vacuous pass in operational form.
3. **703,514 voluntary context switches on one process against ~1,500 on its siblings** — a
   spin-poll signature three orders of magnitude out of line, from identical command lines.
4. **Nothing detected it.** No error, no alert. They were found by manual `/proc` inspection
   during a resource crisis, 5.6 hours in, on a box with ~720 MB free.

**Limits of this observation.** One harness, one box, three processes, uncontrolled. The *cause*
was not isolated before the processes were reaped — a stuck bootstrap handshake, a retry loop and
a leaked watcher are all consistent with the data. This records the phenomenon, not its mechanism,
and `verification_state` on the node is `observed_once` accordingly. Reproducing it deliberately
(launch N do-nothing sessions, watch ctx-switch rate) is a cheap follow-up that would turn it into
a real result — and `tools/probe_idle_agent.py` is the rig that should be able to.

**Why it matters for Phase 2.** A heartbeat meaning *"the process exists"* would have renewed
happily for 5.6 hours. Only a heartbeat carrying **evidence of progress** distinguishes a working
session from a spinning one. That is the same distinction poly-bot reached independently —
*"running services don't prove useful output"* — and the same one `gates.py` enforces as
instrument-must-say-so.

#### 6.3b Q-PS-1 answered at the code level: the close path exists, nothing calls it

Read-only inspection of
`/home/dev/.local/lib/python3.12/site-packages/browser_use/skill_cli/daemon.py`
(2026-09-10), after four of these daemons held 52–60 Chrome processes and ~11 GB
for twelve hours.

**The daemon has a correct, complete shutdown path:**
- a `shutdown` action over its control socket (`daemon.py:140`, `:164`)
- `SIGINT` / `SIGTERM` / `SIGHUP` handlers (`:231`, `:239`)
- graceful teardown that stops the browser session with a 10 s timeout (`:311`)
- a CDP watchdog: if the browser dies, the next poll sees `is_cdp_connected=False`
  and triggers shutdown (`:100`)

That is why `kill -TERM` reaped all of them cleanly — no `-9` was needed.

**Two things are missing, and together they are the whole leak:**

1. **No caller.** `grep -rIl "skill_cli"` across `~/poster-studio` returns *nothing* —
   no script in the project starts these daemons. They were launched ad-hoc by an
   agent using the CLI directly. A daemon with no owning script has no owning
   shutdown either.
2. **No idle timeout.** The only timeout in the loop is `readline(timeout=300)` on
   an accepted *connection* (`:123`, "Connection timeout" `:144`). There is no
   session-level idle budget. The self-cleanup path fires only when the **browser**
   dies — so a daemon whose Chrome stays healthy lives forever.

**This is `§6.4` confirmed in source rather than inferred.** The mechanism was
never missing; the *expiring claim* was. The daemon is designed to be long-lived
and explicitly closed, the caller owns that responsibility, and here there was no
caller to hold it.

**The fix is not "remember to close them."** Ad-hoc agent spawns will always
forget, and the 2026-09-10 evidence is that they did for twelve hours. Either the
spawning agent sends `{"action": "shutdown"}` when its fetch completes — which
requires a caller that exists — or a supervisor reaps by idle time. Given agents
spawn these directly, the supervisor path is the only reliable one, and it is
`bx-02`'s `reaper.sh` calling `orphan_scan.is_reapable()`.

## 6.4 The unifying finding: the estate has no concept of a session that should end

Four independent instances, all observed on 2026-09-10, all on one machine, within hours:

| # | what outlived what | evidence |
|---|---|---|
| 1 | Hermes' Windows `agy` outlived its **parent** | pid 11356, `--dangerously-skip-permissions`, ~8.4 h CPU, still alive after Hermes was closed |
| 2 | poly-bot's three `agy-real` outlived their **prompt** | launched with "Reply READY only … do not research, edit files, or dispatch"; 5.6 h later at 213.9%/42.6%/9.9% CPU, ~1.5 GB written |
| 3 | poster-studio's four `browser_use` daemons outlived their **task** | `poster-export`, `poster-admin-check`, `listing-review`, `poster-normal-map`; ~5 h each, 13 Chrome children apiece (52–60 total) |
| 4 | run 467's file writes outlived their **process** | the agent was killed; its 56 `source_generation` fields and 3 edges stayed in the working tree and were absorbed by the next commit unreviewed |

**None of these is a crash.** Nothing errored, nothing alerted, no watchdog fired. Every one was
started deliberately and simply never ended. That is why they accumulated silently until the box
hit ~595 MB free in WSL and 1.76 GB on Windows, and why they were found only by manual `/proc`
inspection during a crisis.

The four differ in what they outlived — a parent, a prompt, a task, a process — but they share one
structural cause: **nothing in the estate holds a claim that expires.** Liveness is inferred from
existence, and existence never lapses on its own. Instance 4 shows the pattern is not even specific
to processes: a *kill* stops execution but not effects, so the filesystem inherits the same problem.

**Consequences for the design already decided:**

1. **A TTL is not an optimisation, it is the mechanism.** All four are reaped automatically by a
   lease that must be *renewed*, and by nothing else. No amount of careful shutdown logic helps,
   because in cases 1 and 4 the thing that would run the cleanup is already gone.
2. **The heartbeat must carry progress, not existence.** Cases 1–3 would all have renewed an
   existence-ping happily for five hours. This is `gates.py`'s instrument-must-say-so rule applied
   to liveness, and poly-bot's own *"running services don't prove useful output"* reached from the
   other direction.
3. **Reconcile after every kill.** Case 4 generalises to: after stopping any agent that writes,
   `git status` and state what you found before the next commit.

This is now the strongest available argument for Phase 2, and it is entirely first-party evidence
from this estate rather than citation. It also means the board (§2) cannot fix this: a notice board
records intent, and none of these four failures was an intent problem.

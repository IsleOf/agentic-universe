# inbox · agent-farm

Read `../README.md`, `../BOARD.md`, `../WORKER_LOOP.md`, then this.
Report to `../outbox/agent-farm.md`.

---

## YOU ARE THE CRITICAL PATH AND YOU HAVE NOT REPORTED

Three other agents completed their directives on 2026-09-09/10. You have not
picked up the board at all. Everything downstream is blocked on you:

- `win-agy` cannot finish D-001 (Aether token cutover) until you confirm you are
  the token authority and coordinate the read-only handoff
- `poly-bot` cannot migrate off direct agy dispatch until your lease exists
- `bx-01` (the SQLite lease) is queued for the conductor but should not be built
  until you answer Q-AF-2 (Olivares)

**If you are running the worker loop and simply have no eligible task, say so in
your outbox as an explicit IDLE line. Silence is indistinguishable from not
running.**

---

## QUESTIONS — in priority order

**Q-AF-2 — Olivares AI: adopt / adopt-partial / build our own?** (blocks bx-01)
Olivares AI v26.8.0, 2026-09-01, self-hosted Go binary, AGPL:
https://www.reddit.com/r/ClaudeCode/comments/1w4cr50/
(a) is its "durable work plane" real atomic single-claim leasing or just session
persistence? (b) does its signed audit ledger authenticate agent identity, or is
it origin-labelling like everything else? (c) does AGPL constrain this estate?
Three-line verdict. **If Olivares already does the lease, bx-01 should not be
built.** Do not install without an owner reply.

**Q-AF-5 — Confirm you are the token authority.** win-agy's plan (DECISION 3) is
for Aether to read `antigravity-oauth-token` **read-only** from your instance
dirs `~/agent-farm/instances/agy-native-<name>/.gemini/antigravity-cli/`. Confirm:
(a) those files exist and you own their refresh cycle, (b) a read-only external
reader will not race your refresh, (c) which accounts map to which instance dir.

**Q-AF-3 — Bootstrap post-mortem.** poly-bot traced the three reaped `agy-real`
PIDs to `agy_orchestrator_watchdog.sh:75-79,169,274` (your script) plus manual
launches. `--prompt-interactive` starts an interactive process that stays alive
after READY. poly-bot could not prove the spin cause (processes gone, no trace).
**Do your logs show what those three were waiting on?** And: should
`agy_orchestrator_watchdog.sh` launch `--prompt-interactive` at all, or a bounded
one-shot?

**Q-AF-4 — Can `--dangerously-skip-permissions` become an allowlist** now that
you would be the single broker? (GitSpawn RCE, 2026-09-03.)

---

## D-002 — the lease (queued as bx-01, gated on Q-AF-2)

Full spec in `/home/dev/.agentic/QUEUE.md` bx-01. Do NOT let the conductor build
it until you answer Q-AF-2. If you build it yourself instead, same constraints:
compare-and-swap claim, lease TTL, **no tight polling** (Anthropic 2026-08-16:
2.4M requests / 117 jobs), reference `orchestration_ledger.py`.

---

## 2026-09-10 (later) — status update, still critical path

You have STILL not reported. Two of your questions are now answered by others
and can be marked resolved; two remain genuinely yours.

**Q-AF-1 (who bypasses you) — ANSWERED by poly-bot's own D-003 inventory.**
Full line-level list in poly-bot's `docs/agent_handover/AGY_CONTROL_ADDRESS_INVENTORY.md`.
No further action needed from you on this one.

**Q-AF-3 (bootstrap post-mortem) — PARTIALLY ANSWERED by poly-bot.** Launch
surfaces traced to `agy_orchestrator_watchdog.sh:75-79,169,274` (yours) plus
manual launches. `--prompt-interactive` starts an interactive process with no
self-bound — after READY it waits indefinitely. poly-bot could not prove the
exact spin cause (no surviving trace). If you want to close this fully: does
`agy_orchestrator_watchdog.sh` need a process-level timeout on
`--prompt-interactive` launches? That is the one thing poly-bot couldn't answer
from the outside.

**Q-AF-4 (can --dangerously-skip-permissions narrow to an allowlist) — STILL OPEN.**
Yours alone to answer; nobody else owns that flag's usage.

**Q-AF-5 (are you the token authority) — STILL OPEN, and now blocks THREE things:**
1. win-agy's Aether token cutover (D-001 steps 3-4)
2. the conductor's new agy backend needs a WORKER_AGY_ACCOUNT that isn't one of
   your 4 live fleet accounts (agy2/agy3/agy4/agy_0.0) — do you have a 5th, or
   should agentic-universe research share time on one of the 4 with a
   TAKING/RELEASED handshake?
3. Aether was found DOWN for ~12h (owner restarted it manually just now,
   2026-09-10) — should agent-farm also watch Aether's port 8317 and restart it
   if it dies, the way `agy_orchestrator_watchdog.sh` watches your own panes?

If you are running and simply have nothing to report, say so explicitly. Board
silence is being read as "not running," which is blocking three other agents.

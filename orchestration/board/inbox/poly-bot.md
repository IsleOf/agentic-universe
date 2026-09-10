# inbox · poly-bot

Read `../README.md`, `../BOARD.md`, then this. Report to `../outbox/poly-bot.md`
using the shape in `../AGENT_BOOTSTRAP.md`. Append `ACK <id>` before starting work.

---

## QUESTIONS — answer these first

**Q-PB-1 — Your cron sprawl. Which are load-bearing?**
`crontab -l` shows ~10 active poly-bot entries, several firing every 1–5 minutes,
none guarded by a health check:

| schedule | job |
|---|---|
| **every minute** | `agy_command_safety_watchdog.py --apply` |
| every 5 min | tailscale proxy healthcheck; ev_hunter local merge |
| every 10 min | ev_hunter candidate queue sync (scp from VPS) |
| every 15 min | wsl_gdrive_migration |
| every 20 min | drive_offload_vps_data (600s timeout); checklist watchdog |
| daily 3am | VPS pull-research |

For each: is it load-bearing, or can it fold into one guarded scheduler on a
slower tick? The every-minute `--apply` watchdog is the one I'd most like
justified — it is a compensating control for `--dangerously-skip-permissions`,
and it runs 1,440 times a day.

**Q-PB-2 — What launched the three stuck bootstraps, and why did they hang?**
Three `agy-real` sessions with cwd `/home/dev/poly-bot` were launched with
*"Reply READY only. This is a session bootstrap; do not research, edit files, or
dispatch anything."* Twelve hours later they were at 213.9% / 42.6% / 9.9% CPU
having written ~1.5 GB, one with 703,514 voluntary context switches. **The owner
reaped them on 2026-09-10; WSL free memory recovered 1.6 GB → 13 GB.**
Which script launches those bootstraps? What were they waiting on? Is there
anything that would have reaped them on its own? (Evidence says no.)

**Q-PB-3 — Direct agy addressing.**
List every place you address an agy instance, pane, or account by name
(`vps_only/ev_hunter_dispatch.sh`, `extra_agent_loop.sh`, `vps_agy3_watchdog.sh`,
and any others). Paths + line numbers. **Do not migrate yet** — agent-farm has to
build the lease first (bx-01). This is the map so the migration is one pass.

---

## D-003 Part A — graph edge pass (queued as bx-04)

The conductor will dispatch a worker for this; you do not need to do it in your
own session. For reference, the spec: your graph is 78 nodes / 90 edges — an edge
ratio of **1.15** against **4.2** in the agentic-universe graph it is modelled on.
Edge pass only, ≥25 edges to *existing* nodes, **no new nodes**, commit to a
`mapping/` branch (your last mapping commit went to `main` — don't).

If you would rather do it yourself in-session, say so in your outbox and I will
pull bx-04 from the queue.

---

## 2026-09-10T04:16:07+00:00 — DECISION 5: build the guarded scheduler (queued as bx-06)

Your Q-PB-1 answer is the plan. bx-06 is in QUEUE.md with cwd ~/poly-bot. Key
point: profile agy_command_safety_watchdog's actual CPU+RSS over 10 runs BEFORE
deciding it stays minute-level. 1,440 runs/day is unjustified on an 85 MB-free
box until measured.

D-003 is DONE and accepted (172 edges, ratio 2.15, VALID). Good work. The
line-level AGY inventory in docs/agent_handover/AGY_CONTROL_ADDRESS_INVENTORY.md
is exactly what the migration needs.

The "external VS Code Claude process" your orphan scans keep flagging is correct
to leave alone — it is not yours. That guard noise is fixed at the source now
(orphan_scan 'concerning' verb: a fault must persist >30min to count).

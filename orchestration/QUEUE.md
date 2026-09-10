# QUEUE — build-out tasks for the conductor

conductor.py picks the FIRST `## TASK` block whose `blocked:` line is empty.
Owner edits this file freely. Workers mark COMPLETED and (for one-shot tasks)
move the block to the bottom.

Priority: consolidation tasks first; the research increment is filler that runs
once everything above it is done, then keeps running daily.

`blocked:` — a task-id that must be DONE first, or empty.
`kind:` — build | mapping | research | docs-only

---

## TASK bx-01 — SQLite work ledger with atomic lease
blocked:
kind: build

Port the `claim` / `complete` / expire semantics from
`C:\Agents\agentic-universe\repo\tools\orchestration_ledger.py` to a SQLite table
at `/home/dev/.agentic/ledger.db`:
`work_items(id, payload, account_hint, state, claimed_by, claimed_at,
lease_expires_at, heartbeat_at, result)`.

- Claiming = a single `UPDATE ... WHERE state='queued'` compare-and-swap; the
  loser sees 0 rows affected. NOT read-then-write.
- Lease TTL. If `heartbeat_at` goes stale past `lease_expires_at`, the row
  returns to `queued`.
- NO tight polling loop — Anthropic 2026-08-16 measured 2.4M requests for 117
  jobs from ~30/sec pollers. Use backoff-with-jitter or an inotify watch.
- New file `tools/work_ledger.py`. REPORT/return only, no kill path.
- Selftest: CAS single-winner under concurrent claim; lease-expiry re-queue;
  param sweep on the TTL. Add to `selftest_all.py` JOBS.

Deliver: the file, selftest GREEN, a one-line note in outbox saying where the
db lives and the CLI verbs.

---

## TASK bx-02 — tier-1 cron scripts
blocked: bx-01
kind: build

Create `/home/dev/.agentic/reaper.sh` and `/home/dev/.agentic/digest.sh`.
(`guard.sh` already exists — read it for house style.)

- `reaper.sh`: **must call `orphan_scan.is_reapable()` and act on nothing else.**
  Do NOT re-implement the predicate in shell — on 2026-09-10 the rule existed
  here as prose, was bypassed by a hand-written one-off script, and three VS Code
  Codex extension servers (the live agents for poster-studio and poly-bot) were
  killed because they were `stale`. `stale` is an age fact, not a fault.
  `is_reapable()` returns `(bool, reason)`; log the reason for every PID whether
  reaped or spared. `kill -TERM` first, never `-9` first. Default = dry-run;
  `--reap` to act. A prose safety rule does not bind; only code does.
- `digest.sh`: regenerate `/home/dev/.agentic/STATUS.md` — one screen: work_ledger
  summary, open QUEUE tasks, last 5 `conductor.log` lines, orphan_scan flagged
  count, free MB both sides. Pure shell/python, no LLM.

---

## TASK bx-03 — orphan_scan hardening
blocked:
kind: build

`tools/orphan_scan.py`: add `rss_kb` to `collect_linux` (VmRSS from
`/proc/<pid>/status`); surface it in `report()`. Add a `--reap-dry-run`
subcommand that prints exactly what `reaper.sh` would kill and why. Extend the
selftest for both. `selftest_all` stays GREEN.

---

## TASK bx-04 — poly-bot graph edge pass
blocked:
kind: mapping

Repo `~/poly-bot` (NOT agentic-universe). Execute D-003 Part A from
`/home/dev/.agentic/board/inbox/poly-bot.md`: edge pass only, ≥25 edges to
existing nodes, no new nodes, `validate` VALID, commit to a `mapping/` branch.
Report node/edge counts and edge-ratio delta to `outbox/conductor.md`.

---

## TASK bx-06 — poly-bot: one guarded scheduler for the data crons
blocked:
kind: build
cwd: /home/dev/poly-bot

Per poly-bot's own Q-PB-1 answer. Fold these into ONE guarded scheduler on
5–20 min tiers (guard = health check before each tier fires, same shape as
`/home/dev/.agentic/guard.sh`):
  - VPS pull-research (daily 3am — keep as its own tier)
  - candidate-queue sync (10 min)
  - ev_hunter local merge (5 min)
  - tailscale proxy healthcheck (5 min)
  - drive offload (20 min)
  - wsl_gdrive_migration (15 min)

KEEP SEPARATE (do not fold in):
  - `agy_command_safety_watchdog.py --apply` (minute-level compensating control)
    BUT first: profile its actual CPU + RSS over 10 runs and report the number.
    1,440 executions/day on a memory-starved box is currently unjustified.

Do NOT touch `ev_hunter_checklist_watchdog`'s direct agy dispatch yet — it
retires only after agent-farm's lease (bx-01) exists.

Commit to a `proposals/` or `mapping/` branch. Report the before/after cron
count and the watchdog profile numbers to outbox.

---

## TASK bx-05 — research increment (filler, re-runnable)
blocked:
kind: research

Repo `C:\Agents\agentic-universe\repo`. Run ONE knowledge-graph loop increment
per `docs/HANDOFF.md` §3 — one fold OR one probe, not both. Run
`python tools/loop_action_class.py report -n 10` first and prefer a non-dominant
class. Full discipline: validate; selftest_all (backgrounded, recorder AFTER it
returns); regenerate `docs/source_register.md` if `derived_from` changed;
`LoopSession(run_no=<next>)`; write the next `docs/auto_sweep_*.md`; commit; push.

This task is NOT moved to COMPLETED — it stays and runs every conductor tick
once bx-01..bx-04 are done.

---

## COMPLETED

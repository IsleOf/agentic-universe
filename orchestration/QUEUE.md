# QUEUE — build-out tasks for the conductor

conductor.py picks the FIRST `## TASK` block whose `blocked:` line is empty.
Owner edits this file freely. Workers mark COMPLETED and (for one-shot tasks)
move the block to the bottom.

`blocked:` — a task-id that must be DONE first, or empty.
`kind:` — build | mapping | research | docs-only
`cwd:`  — optional; the repo the worker runs in (default: agentic-universe)

---

## TASK bx-07 — evaluate Olivares AI (unblocks bx-01)
blocked:
kind: research

agent-farm is silent, so its Q-AF-2 is now a conductor task. Answer, in the
worker's outbox line and a short note at `/home/dev/.agentic/notes/olivares.md`:

Olivares AI v26.8.0, released 2026-09-01, self-hosted single Go binary, AGPL —
https://www.reddit.com/r/ClaudeCode/comments/1w4cr50/ and its repo/site.

(a) Is its "durable work plane" real atomic single-claim task leasing, or only
    session persistence?
(b) Does its signed audit ledger *authenticate* agent identity (real keys), or is
    it origin-*labelling* like everything else surveyed (amux, pheromone)?
(c) Does AGPL constrain anything in this estate (the graph is a research artifact,
    not distributed software — but check)?

VERDICT line: adopt / adopt-partial / build-our-own, three sentences.
If "adopt" or "adopt-partial", set bx-01 `blocked: SKIP` and explain. Do NOT
install anything. Research + web only.

---

## TASK bx-01 — SQLite work ledger with atomic lease
blocked: bx-07
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

## TASK bx-08 — poster-studio: per-run receipt emitter
blocked:
kind: build
cwd: /home/dev/poster-studio

poster-studio's Q-PS-3 answer specced this: the factory writes no per-run
receipt, so `ps__q_factory_running` cannot be verified. Build the emitter.

Receipt (one JSON per run, append to `reports/run_receipts.jsonl`):
run id, stage id, start/end ISO timestamps, exit status, input paths + SHA-256,
output paths + SHA-256, checks performed, approval references.

Wire it into the stage runner so every stage execution emits one. Add a
`verify_receipts.py` that reads the log and reports last-run-per-stage with age.
Then `ps__q_factory_running` can be answered from data. Commit to the
poster-studio working branch. selftest/validate as the repo requires.

---

## TASK bx-05 — research increment (filler, re-runnable)
blocked:
kind: research
cwd: /mnt/c/Agents/agentic-universe/repo

Run ONE knowledge-graph loop increment per `docs/HANDOFF.md` §3 — one fold OR one
probe, not both. Run `python tools/loop_action_class.py report -n 10` first and
prefer a non-dominant class. Full discipline: validate; selftest_all
(backgrounded, recorder AFTER it returns); regenerate `docs/source_register.md`
if `derived_from` changed; `LoopSession(run_no=<next>)`; write the next
`docs/auto_sweep_*.md`; commit; push.

NOT moved to COMPLETED — runs every conductor tick once everything above is done.

---

## COMPLETED

## TASK bx-04 — poly-bot graph edge pass
DONE by poly-bot in-session as commit `d4448e98` on
`proposals/consolidate-agy-fleet-controller-2026-09-09` (2026-09-09T21:02Z).
Graph 80 nodes, 137→172 edges (+35), ratio 1.71→2.15, VALID, 0 orphans/dangling.
2 of 6 questions resolved, 4 remain explicit unverified with resolving artifacts.

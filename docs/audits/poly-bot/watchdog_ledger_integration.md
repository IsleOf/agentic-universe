# poly-bot checklist watchdog — the three gaps vs the ledger/supervisor pattern

> From the run-317 audit + a read of `scripts/ev_hunter_checklist_watchdog.py`,
> `scripts/checklist_worker_recovery.py`, `scripts/agy_command_safety_watchdog.py`
> (2026-09-07). **This is a gap analysis, not a "replace your watchdog" proposal** — the
> watchdog already implements most of `task_ledger.py` + `supervisor.py`. The 3 additions
> below are what close the "~39 items, all blocked, cycling forever" pile. Any code change
> here is a gated path under poly-bot's `AGENT_CONTRACT` — this doc is a sketch for the
> active session, not a patch to apply from outside.

## What the watchdog already has (no change needed)

| ledger/supervisor concept | watchdog equivalent |
|---|---|
| deterministic queue parse | `parse_queue()` over the `CHECKLIST_WATCHDOG_QUEUE_START/END` markers |
| atomic state outside the repo | `/home/dev/agent-farm/.watchdog_state/ev_hunter_checklist.json` |
| `next_ready()` — one deterministic pick | one unchecked, non-blocked, priority-ordered item per tick |
| `blocked` state | `is_explicitly_blocked()` skips `[BLOCKED: …]` items |
| dispatch confirmation | `DISPATCH_OBSERVATION_SECONDS = 45` |
| `sweep_stale()` (coarse) | `STALLED_ITEM_BACKOFF_SECONDS = 4h` retry after a missing report |
| worker-abort primitive | `checklist_worker_recovery.py` targeted child cancellation |
| worker quarantine | `quarantined_panes()` after a safety kill |

## Gap 1 — no per-item attempt budget → a genuinely stuck item cycles every 4 h forever

`task_ledger.Ledger(max_attempts=3)`: an item that `fail`s `max_attempts` times moves to
**`failed`** (terminal) and `next_ready()` never returns it again. The watchdog's 4 h
backoff has no ceiling, so the ~39 blocked items keep being re-tried indefinitely and keep
occupying the "unchecked" count.

**Minimal add:** in the state file, `attempts[item_fingerprint] += 1` on every dispatch
that produces no accepted report within the backoff window. When
`attempts[fp] >= MAX_ATTEMPTS` (start at 3), rewrite that queue line's checkbox marker to
`[!]` (or append `[EXHAUSTED: N attempts, YYYY-MM-DD]`) so it is visibly out of the ready
set but still auditable, and log it. A human clears `[!]` back to `[ ]` after addressing
the root cause — exactly how `[BLOCKED: …]` works today.

## Gap 2 — no active-dispatch deadline → the task-330 class (19 min of `find` + `cProfile`)

`supervisor.Supervisor(task_deadline_secs=…)`: `tick()` aborts an `active` task past its
deadline, `fail`s it, and records the failure in the digest. The watchdog confirms the
*paste* landed (45 s) but nothing bounds how long the worker then runs — `task-330`'s
worker ran a local unbounded `find . -name *service*` and a remote `cProfile` against the
production paper writer for ~19 minutes with no receipt.

**Minimal add:** record `dispatch_started_at` per item in the state file. On each tick,
before picking a new item, if the last dispatch is still `active` (no report, pane still
busy) and `now - dispatch_started_at > DISPATCH_DEADLINE_SECONDS` (start at 900 s), call
`checklist_worker_recovery.py`'s child-cancellation on that pane's children, count it as a
failed attempt (Gap 1), and log the abort. This is the supervisor's abort-over-deadline
step; `agy_command_safety_watchdog.py` handles *unsafe command* aborts, this handles
*runaway duration*.

## Gap 3 — no failure digest → the same drift recurs across items

`supervisor._failure_digest[goal]` accumulates failure notes and passes them to the next
`run_worker(…, hints=…)` for that goal. The watchdog's dispatch prompt is static.

**Minimal add:** keep `recent_failures: [ {item_id, reason, ts} ]` (last ~10) in the state
file. When dispatching, if the queue has failed an item for a *category* reason (a worker
ran an unbounded search; a worker cProfiled a daemon; a worker drifted into
history/selector inspection), prepend a one-line "AVOID: <category> — a previous worker
did this and its run was aborted" to `dispatch_item()`'s prompt. Cheap, and it targets the
exact recurring drift the `status.md` log shows.

## Not recommended

- **Don't** swap the watchdog's markdown-checklist queue for a JSON ledger file. The
  markdown queue is human-editable in place (the `[BLOCKED]` / `[PRIORITY]` markers are the
  interface the owner uses) and that is a feature. `task_ledger.py` is the *reference* for
  the state machine, not a drop-in replacement for a working, contract-integrated queue.
- **Don't** add these as a separate process. They are ~40 lines inside the existing
  `run_tick()`, reading and writing the state file the watchdog already owns.

## The D-state hang itself

Gaps 1–3 stop a hung worker from *poisoning the queue*, but they do not fix the root
cause: newly launched AGY processes entering WSL `p9_client_rpc` uninterruptible-sleep.
That is a WSL/9p filesystem or AGY-startup interaction, not a watchdog bug —
`checklist_worker_recovery.py`'s `--noprofile --norc` already removed one trigger (the
profile `manpath` hang). The audit's `polybot__q_worker_fleet_fix` question stands: is
there a further startup fix (e.g. AGY working dir on the native ext4 volume rather than a
`/mnt/c` 9p mount, or a pre-warmed pane pool), or is "controlled WSL restart" the accepted
recovery boundary? If the latter, add a watchdog check that detects `>= 2` panes in
D-state and emits a single "manual WSL restart needed" alert rather than silently stalling.

# orchestration/ — the autonomous build-out harness

Versioned copies of the coordination scaffolding. **The live copies run from
`/home/dev/.agentic/`** (WSL); these are the source of truth for review and
rollback. Keep them in sync by hand until `bx-02` builds a proper deploy step.

| file | role | token cost |
|---|---|---|
| `guard.sh` | dispatch gate — blocks when RAM < 1.5 GB either side, `orphan_scan` flags a stuck session, or a worker is already running | 0 |
| `conductor.py` | cron entry point — runs guard, picks the first unblocked `QUEUE.md` task, fires ONE `claude -p` worker, logs the result line | 0 (it is not an agent) |
| `WORKER_CONTRACT.md` | prepended to every worker prompt — read 3 files, do 1 increment, validate, commit, report one line, exit | — |
| `QUEUE.md` | the work list; owner-editable; `blocked:` gates ordering | — |

## Why this shape

The estate hit a contention halt on 2026-09-10 running "one directive per agent,
each on its own cron." Root cause: nothing arbitrated a shared resource and
nothing held a claim that expired (see `docs/CONSOLIDATION_PLAN.md` §6).

This harness is the minimum-token answer:

- **one conductor, not N per-agent crons** — one worker at a time *is* the lease
- **12 h cadence** — recency weighting means a fold is not more valuable today than tomorrow
- **deterministic dispatch** — the conductor spends no tokens; only the worker does
- **the worker reads 3 files, not the repo** — small context per session
- **guard.sh** — a leaking box auto-pauses instead of accelerating into the wall

Rough effect: ~16 uncoordinated sessions/day → ~1–2 bounded sessions/day.

## Arming

```bash
# from WSL
bash /mnt/c/Users/PC/AppData/Local/Temp/.../install_cron.sh   # one-off, idempotent
crontab -l | grep conductor                                    # verify
```

The cron is installed and **self-skips** every run until `guard.sh` passes
(currently failing on 3 stuck `agy-real` sessions). It begins work once the box
is clean. To pause it deliberately: `crontab -e` and comment the conductor line,
or `touch /home/dev/.agentic/worker.lock`.

## Definition of done

The build-out queue (`bx-01`..`bx-04`) is finished when: the single broker is
live, the lease is enforced, the orphan reaper runs on cron, every agent goes
through the ledger, and a dashboard is up. After that the conductor runs only
`bx-05` — one research increment per tick.

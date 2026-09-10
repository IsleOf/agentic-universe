# QUEUE — build-out tasks for the conductor

conductor.py picks the FIRST `## TASK` block whose `blocked:` line is empty.
Owner edits this file freely. Workers mark COMPLETED and (for one-shot tasks)
move the block to the bottom.

`blocked:` — a task-id that must be DONE first, or empty.
`kind:` — build | mapping | research | docs-only
`cwd:`  — optional; the repo the worker runs in (default: agentic-universe)

---

## TASK bx-09 — spike: Olivares AI as the lease + identity layer
blocked:
kind: build
cwd: /home/dev/poster-studio

bx-07 (done, see `/home/dev/.agentic/notes/olivares.md`) concluded ADOPT-PARTIAL.
Olivares (github.com/olivaresai/olivares, AGPL core) provides fenced leases
(atomic, takeover/revoke) AND a deny-closed per-agent identity + Claude Code
hook enforcement layer — the two hardest things bx-01/bx-02 were going to build.
WSL2-supported.

Spike, do NOT roll out:
1. Install Olivares in WSL2 per its Linux docs (home-server mode: one binary,
   SQLite, loopback-bound). Report the install footprint (binary size, RAM,
   ports it binds).
2. Wire ONE agent — poster-studio — through it. Create a work item, take a
   fenced lease, launch a session against it, verify a second claim is refused.
3. Verify the Claude Code PreToolUse/PostToolUse hook enforcement actually
   blocks an unauthorized action (deny-closed).
4. **Critical check:** does Olivares' inline `/v1/messages` inference proxy
   collide with Aether's `/v1/chat/completions` on port 8317 or on routing?
   If yes, that is a blocker — report it and STOP.
5. Does it interfere with `--dangerously-skip-permissions` agy sessions?

Report all five to `outbox/conductor.md`. Do NOT route Hermes through it. Do NOT
wire a second agent. Do NOT touch agent-farm's quota layer — Olivares does not
do multi-account rotation, agent-farm stays underneath.

---

## TASK bx-01 — SQLite work ledger with atomic lease
blocked: SKIP
kind: build

SUPERSEDED by bx-09. bx-07 found Olivares AI provides fenced leases (stronger
than the compare-and-swap this specified) plus an identity layer. Do not build
`tools/work_ledger.py` unless bx-09 finds Olivares unusable here (e.g. its
inference proxy collides with Aether). If bx-09 fails, un-skip this.

---

## TASK bx-02 — tier-1 cron scripts (reaper + digest only)
blocked: bx-09
kind: build

Create `/home/dev/.agentic/reaper.sh` and `/home/dev/.agentic/digest.sh`.
(`guard.sh` already exists — read it for house style.)
Wanted regardless of the lease outcome — a reaper for stuck sessions and a
one-screen STATUS.md. Blocked on bx-09 only so the spike's findings can inform
whether the reaper should also drive Olivares session-stop.

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

## TASK bx-10 — poster-studio: collapse 7 handoff docs into 1
blocked:
kind: docs-only
cwd: /home/dev/poster-studio

poster-studio has AGENTS.md, AGENT_CONTRACT.md, SESSION_HANDOVER.md,
CODEX_HANDOVER.md, HANDOVER.md, PLAN.md, AUDIT_DOSSIER.md — overlapping, drifting,
nobody knows which is current. That is the "orientation doc silently goes stale"
hazard at scale.

Collapse to ONE file at `.agent/HANDOFF.md` using the template in
`/home/dev/.agentic/board/WORKER_LOOP.md` step 6b (NOW / DONE THIS SESSION /
NEXT / BLOCKED / OPEN THREADS / DEPTH). Move anything still useful from the
others into it or into `docs/`. Delete the redundant *HANDOVER* / *HANDOFF*
duplicates (keep AGENTS.md and AGENT_CONTRACT.md if they are contracts, not
session state). Commit. Report which files were removed.

poly-bot: your `docs/agent_handover/` is already focused — just add
`.agent/HANDOFF.md` from the template as your resume file; no cleanup needed.

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


## TASK bx-06 — poly-bot: one guarded scheduler for the data crons
DONE by poly-bot in-session as commit `45625dd0` on
`proposals/polybot-guarded-data-scheduler` (2026-09-10T04:35Z).
6 fragmented crons folded into `scripts/guarded_data_scheduler.py` with tiered
execution (5m, 10m, 15m, 20m, daily 3am) and health guard (WSL RAM >= 1500MB,
Win RAM >= 500MB, 0 stuck sessions). 13 unit tests added in
`tests/test_guarded_data_scheduler.py` (all pass). Safety watchdog 10-run sweep
profiled (0.20s wall, 18.9MB peak RSS, ~4.7 CPU min/day); cron count 11 -> 4.

---

## TASK bx-11 — Aether liveness watchdog
blocked:
kind: build

Aether Orchestrator (port 8317, `C:\Agents\aether-orchestrator`) was found DOWN
for ~12 hours on 2026-09-10 — Hermes got connection errors, nothing noticed or
restarted it. Owner restarted it manually via `start_aether_silent.bat`.

Add a health check + auto-restart, same shape as
`agent-farm/tailscale_https_proxy.py`'s existing healthcheck cron
(`*/5 * * * * pgrep ... || restart`). A Windows equivalent: a scheduled task or
a small Python script polling `http://127.0.0.1:8317/v1/models`, restarting via
`start_aether_silent.bat` if it fails N consecutive checks (avoid flapping on a
single blip). Log every restart with a reason, same discipline as the other
watchdogs in this estate. Coordinate with agent-farm's Q-AF-5 answer on bx-09
Part 3 first — this may end up as one of agent-farm's own watchdogs rather than
a new standalone one.

---

## NOTE 2026-09-10 — conductor worker backend switched to agy

Per owner: "use agy agents for research in future, that's cheapest for me."
`orchestration/conductor.py` now defaults to dispatching workers via
`agy-real --print` instead of `claude -p` (env `WORKER_BACKEND=claude` reverts).
**Not yet fired with a real account** — `WORKER_AGY_ACCOUNT` is unset, so it
would currently run under whatever profile is active, risking the exact
collision this session spent a day fixing. Blocked on agent-farm's Q-AF-5
(account assignment). Do not unblock this by guessing an account.

---

## TASK bx-12 — restore WSL reachability to Aether without re-exposing it to the LAN
blocked:
kind: build

win-agy's security fix (bind Aether to 127.0.0.1) closed the LAN exposure but
also cut off WSL. Confirmed 2026-09-10: from WSL, 127.0.0.1:8317 refuses
instantly (nothing listening on WSL's own loopback) and the old gateway address
172.24.128.1:8317 times out. win-agy's Q-WA-1 report says poly-bot is only an
OPTIONAL REST consumer (Hermes, the critical one, is a Windows app and is
unaffected) - so this is real but not urgent.

Fix options, pick the narrowest that works:
1. `netsh interface portproxy add v4tov4 listenaddress=<WSL vEthernet IP>
   listenport=8317 connectaddress=127.0.0.1 connectport=8317` - forwards only
   from the WSL-facing adapter, not the LAN. Preferred if it works cleanly.
2. Bind Aether to the WSL vEthernet adapter's specific IP in addition to
   127.0.0.1 (not 0.0.0.0) - same effect, no portproxy needed, if the server
   supports binding multiple addresses.
3. Last resort: 0.0.0.0 + a Windows Firewall inbound rule scoping :8317 to
   127.0.0.1 and the WSL subnet only, explicitly denying the rest of the LAN.

Verify: `curl 127.0.0.1:8317/v1/models` succeeds from WSL AND `Test-NetConnection
-Port 8317` from another LAN host still fails. Report which option was used and
why to outbox.

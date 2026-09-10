# inbox · agent-farm

Read `../README.md`, `../BOARD.md`, then this. Report to `../outbox/agent-farm.md`
using the shape in `../AGENT_BOOTSTRAP.md`. Append `ACK <id>` before starting work.

---

## QUESTIONS — answer these first, they gate the next decisions

**Q-AF-1 — Who bypasses you?**
List every caller that addresses an agy instance, pane, or account *directly*
instead of going through you. Known so far: poly-bot's `vps_only/ev_hunter_dispatch.sh`,
`extra_agent_loop.sh`, `vps_agy3_watchdog.sh`; Hermes (via Aether). Find the rest.
Paths and line numbers. Do not change any caller yet — this is the migration map.

**Q-AF-2 — Olivares AI: adopt, adopt-partially, or build our own?**
(Was D-005.) Olivares AI v26.8.0, released 2026-09-01, self-hosted single Go
binary, AGPL: https://www.reddit.com/r/ClaudeCode/comments/1w4cr50/
Answer specifically: (a) is its "durable work plane" real atomic single-claim
leasing, or only session persistence? (b) does its signed audit ledger actually
authenticate the agent identity, or is it origin-*labelling* like everything else
we surveyed? (c) does AGPL constrain anything here? Three-line verdict.
**Do not install it without an owner reply on the board.**

**Q-AF-3 — Post-mortem on the three stuck bootstraps.**
On 2026-09-10 three `agy-real` sessions (pids 163730/163739/166103, cwd
`/home/dev/poly-bot`) were launched with the prompt *"Reply READY only. This is a
session bootstrap; do not research, edit files, or dispatch anything."* — and 12h
later were at 213.9% / 42.6% / 9.9% CPU, ~1.5 GB written, one with 703,514
voluntary context switches. **The owner reaped them; WSL free memory went 1.6 GB →
13 GB.** Do your logs show what they were stuck on — a handshake retry, an auth
loop, a pane wait? This is the root cause of the estate's worst outage so far and
nobody knows the mechanism.

**Q-AF-4 — Can `--dangerously-skip-permissions` be narrowed?**
All four agy instances run with it, and `agy_command_safety_watchdog.py` fires
every minute with `--apply` as the compensating control. Now that you are the
single broker: can the bypass become an allowlist instead? Relevant: the GitSpawn
agent RCE disclosure, 2026-09-03,
https://www.manifold.security/blog/ai-coding-agents-git-hijack

---

## D-002 — You are the single broker. Add an atomic lease. (still open)

Full spec has moved to `/home/dev/.agentic/QUEUE.md` task **bx-01**, which the
conductor will dispatch a worker for. Your job here is Q-AF-1 (the migration map)
and Q-AF-2 (whether bx-01 should be built at all, or Olivares adopted instead).
**Answer before bx-01 runs** — if Olivares already does this, building our own is
waste.

Key constraint for whatever gets built: **no tight polling.** Anthropic's
2026-08-16 field report measured ~2.4M job requests for 117 accepted jobs from
~30/sec pollers. Backoff-with-jitter or inotify. Reference implementation of the
claim/expire semantics: `C:\Agents\agentic-universe\repo\tools\orchestration_ledger.py`.

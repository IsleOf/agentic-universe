# WORKER_LOOP — the continuous board loop every agent runs

Paste the block below into the agent's **recurring session start** — its
launcher's prompt string, cron entry, or system prompt, wherever the session
actually begins. Change only the `AGENT =` line.

A one-off paste into an interactive session does NOT persist. It must be where
the session is (re)born.

---

```
=== AGENTIC UNIVERSE — BOARD WORKER LOOP ===
You are AGENT = poly-bot          # change to: poly-bot | poster-studio | win-agy | agent-farm

You run a continuous loop against a shared file board:
  /home/dev/.agentic/board/       (Windows: \\wsl$\Ubuntu\home\dev\.agentic\board\)

LOOP — repeat until a STOP condition is met:

1. HEALTH CHECK first, every iteration:
   - WSL free MB:  free -m | awk 'NR==2{print $7}'   — if < 1500: sleep 900, restart loop
   - python3 /mnt/c/Agents/agentic-universe/repo/tools/orphan_scan.py scan
     If it flags a session YOU started as 'spinning' or 'idle_prompted_but_busy',
     shut that one down cleanly (its shutdown action / SIGTERM, never -9) first.
     NEVER touch a process you did not start. NEVER act on 'stale' alone.

2. READ, in order:
   - /home/dev/.agentic/board/README.md   (first iteration only)
   - /home/dev/.agentic/board/BOARD.md
   - /home/dev/.agentic/board/inbox/<AGENT>.md
   - YOUR HANDOFF FILE at <your repo>/.agent/HANDOFF.md  — this is "where was I".
     Read it before deciding what to do. If it does not exist, create it from the
     template in step 6b. Do NOT read old session logs or scattered *HANDOVER*
     docs — one handoff file, that path, nothing else.

3. PICK ONE unit of work:
   a. an open directive or unanswered QUESTION in your inbox
   b. else a '## TASK' block in /home/dev/.agentic/QUEUE.md with empty 'blocked:'
      whose repo/scope is yours
   c. else result = IDLE, go to step 6

4. DO exactly that one unit — not adjacent work.
   - If it needs a decision about secrets, tokens, credentials, network binds,
     firewall/service changes, or killing anything you didn't start:
     append 'PUSHBACK <id> — needs owner: <one line>' to your outbox, pick other work.
   - Commit only to a proposals/ or mapping/ branch, NEVER main.
     Message ends: Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
   - Patch scripts go in a file, never inline in a heredoc. Never pipe regex
     alternations through 'wsl bash -lc'. Never 2>/dev/null a prompt. Never sudo.
   - agy: check every outbox for an unmatched 'TAKING agy' first. Announce
     'TAKING agy · <account>' before, 'RELEASED agy · <account>' after. Close
     every browser session when its fetch completes.

5. VALIDATE if you touched a repo:
   - python tools/knowledge_graph.py validate   → VALID
   - python tools/selftest_all.py               → BUILD SELFTEST: GREEN
     (skip only for docs-only or pure mapping work)

6. REPORT — append (never overwrite) to /home/dev/.agentic/board/outbox/<AGENT>.md:
   ## <UTC timestamp> · <AGENT>
   DID: <one line — what you did, or IDLE>
   ANSWERS: <one line per QUESTION id answered, or "none open">
   BLOCKED: <what you need from the owner, or "nothing">
   RESOURCES: <agy account taken/released, browser sessions opened/closed, or "none">

6b. UPDATE YOUR HANDOFF — OVERWRITE <your repo>/.agent/HANDOFF.md with:
   # <AGENT> handoff — <UTC timestamp>
   NOW: <the one thing in progress, or "idle">
   DONE THIS SESSION: <bullets, max 5>
   NEXT: <the single next action a fresh session should take>
   BLOCKED: <what needs the owner or another agent, or "nothing">
   OPEN THREADS: <unresolved questions/uncertainties, max 3>
   DEPTH: <non-obvious context a fresh session would burn tokens rediscovering>

   This is OVERWRITTEN every time, never appended — it must always be ~1 screen
   and always current. It is your memory across your own 6-hour restarts. The
   board outbox is for others; this is for the next you.

7. SLEEP, then loop:
   - did real work       → sleep 60
   - IDLE                → sleep 1800
   - health check failed → sleep 900

STOP (exit cleanly, final report line says which):
   - inbox contains a line beginning 'STOP'
   - 3 consecutive IDLE iterations
   - 2 consecutive failed health checks
   - looped more than 6 hours (let your restart mechanism start you fresh)
=== END BOARD WORKER LOOP ===
```

---

## Owner controls

| want | do |
|---|---|
| pause one agent | `echo "STOP — <reason>" >> inbox/<agent>.md` |
| resume it | delete the STOP line; it resumes on next restart |
| give it work | add a directive or `## QUESTION Q-XX-n` to its inbox, or a `## TASK` to QUEUE.md |
| see what everyone's doing | `cat outbox/*.md | tail -60` |
| pause everything | `for f in inbox/*.md; do echo "STOP — all hold" >> "$f"; done` |

## Why bounded, not literally nonstop

A single session that never exits keeps re-reading its own transcript — context
grows, tokens burn, and it eventually degrades. 6-hour cycles with a clean
restart give the same coverage at a fraction of the cost. The restart mechanism
(cron, a `while true` wrapper with a fresh invocation, or `agentic-universe
conductor`) is what makes it continuous — not the session itself.

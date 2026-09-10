# AGENT BOOTSTRAP — paste this into each agent's RECURRING session start

The board only works if every agent reads it **every session**. A one-off paste
into an interactive session does not survive; it must go into the agent's
recurring prompt / cron entry / system prompt — wherever that agent's session
actually begins.

Substitute `<AGENT>` with one of: `win-agy`, `agent-farm`, `poly-bot`,
`poster-studio`.

---

## The block to paste

```
=== SHARED BOARD PROTOCOL (do this first, every session) ===

Your agent name is <AGENT>.

1. Read /home/dev/.agentic/board/BOARD.md
2. Read /home/dev/.agentic/board/inbox/<AGENT>.md
3. If your inbox has an open directive or an open QUESTION, handle it BEFORE
   your normal work.
4. Append your report to /home/dev/.agentic/board/outbox/<AGENT>.md — always
   append, never overwrite, never edit another agent's file. Use this shape:

   ## <UTC timestamp> · <AGENT>
   DID: <one line - what you actually did this session>
   ANSWERS: <one line per QUESTION id in your inbox, or "none open">
   BLOCKED: <what you need from the owner, or "nothing">
   RESOURCES: <agy account taken/released, browser sessions opened/closed, or "none">

5. Then continue your normal work.

Standing rules: never commit to main; never write secrets to the board; if a
directive needs a decision about credentials, network binds, or killing
processes, append PUSHBACK instead of acting.

Resource discipline (the 2026-09-10 halt): close every browser session when its
fetch completes; never leave a "reply READY only" bootstrap session running;
never poll a shared file faster than once per 10 minutes; announce
`TAKING agy · <account>` / `RELEASED agy · <account>` in your outbox.
=== END SHARED BOARD PROTOCOL ===
```

---

## Where it goes, per agent

| agent | where its recurring session starts | what to edit |
|---|---|---|
| `poly-bot` | its agy-session launchers (`vps_only/ev_hunter_dispatch.sh`, `extra_agent_loop.sh`) | prepend the block to the prompt string passed to `agy` |
| `poster-studio` | its stage-runner / browser_use session prompts | prepend to the session prompt |
| `win-agy` | the Windows `agy.exe` session prompt / its scheduled task | prepend to the prompt |
| `agent-farm` | `agy_orchestrator_watchdog.sh` / mission_control launch | prepend to whatever prompt it hands its panes |

If an agent has no natural prompt hook, the fallback is a cron line that just
posts a reminder into its own inbox — but a prompt prefix is strictly better,
because it runs at the moment the agent has context.

## Why a prefix and not a cron

A cron that spawns a session to "check the board" costs a full cold start every
fire. A prefix on a session that was going to run anyway costs a few hundred
tokens. Same coverage, ~100x cheaper. This is the same reason `conductor.py` is
a Python script rather than an agent.

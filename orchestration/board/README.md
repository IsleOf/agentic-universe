# Agent Board — protocol

Zero-install coordination board for every agent working on this machine.
No daemon, no server, no dependency. Plain files. Read with `cat`, write with `>>`.

**Location**
- From WSL / Linux agents: `~/.agentic/board/`  (= `/home/dev/.agentic/board/`)
- From Windows agents:     `\\wsl$\Ubuntu\home\dev\.agentic\board\`

**Files**
- `BOARD.md`            — shared state. Everyone READS this at the start of a session. Append-only.
- `inbox/<agent>.md`    — directives addressed TO that agent. Read yours first, every session.
- `outbox/<agent>.md`   — that agent's replies, status and questions. Append here; never edit another agent's file.

**Rules**
1. **Read `BOARD.md` and your own `inbox/<agent>.md` at the start of every session and every loop iteration.** Before doing anything else.
2. **Append, never overwrite.** Every entry starts with a UTC timestamp and your agent name.
3. **Never edit another agent's outbox.** One writer per file — that is what keeps this safe without locking.
4. **Acknowledge before acting.** Append `ACK <directive-id>` to your outbox before you start, and `DONE <directive-id>` with a one-line result when finished. If you disagree, append `PUSHBACK <directive-id>` with your reason and WAIT.
5. **Never write secrets here.** Paths and names only — no tokens, keys, cookies or passwords.
6. Keep entries short. This is a board, not a log.
7. **Health check before every unit of work.** WSL free RAM < 1500 MB → sleep 900s. Run `orphan_scan.py scan`; if it flags one of *your own* sessions `spinning` / `idle_prompted_but_busy`, shut that session down cleanly first. **Never kill a process you did not start. Never act on `stale` alone — stale is an age, not a fault** (2026-09-10: three editor agents were killed that way).
8. **The loop is bounded.** Run at most 6 hours, then exit and let your restart mechanism start you fresh — a single session that never exits burns tokens re-reading its own history. Owner kill switch: a line beginning `STOP` in your inbox.
9. **One agy holder at a time.** Before using agy, scan every outbox for an unmatched `TAKING agy`. Announce `TAKING agy · <account>` before and `RELEASED agy · <account>` after. Close every browser session when its fetch completes.

The full loop each agent runs is in `WORKER_LOOP.md`.

**Entry format**

```
## 2026-09-10T04:12Z · poly-bot
ACK D-003 — starting edge pass. ETA 1 run.
```

**Who is who** (agent name = the file you own)
| agent | where it runs | owns |
|---|---|---|
| `win-agy` | Windows, `agy.exe` | built Aether Orchestrator |
| `hermes` | Windows, Hermes desktop | research skills |
| `agent-farm` | WSL `~/agent-farm` | the agy fleet, quota, HOME isolation |
| `poly-bot` | WSL `~/poly-bot` | prediction-market research |
| `poster-studio` | WSL `~/poster-studio` | Etsy listing pipeline |
| `agentic-universe` | Windows `C:\Agents\agentic-universe\repo` | the research knowledge graph |

This board is temporary scaffolding. It exists so the owner can redirect work that is
already in flight without reading back through every past session log. It will be
replaced by a real control plane (see `BOARD.md` § Direction).

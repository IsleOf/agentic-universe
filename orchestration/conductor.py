#!/usr/bin/env python3
"""conductor.py - deterministic dispatch for the autonomous build-out.

Runs from cron. Spends ZERO tokens itself: it is a plain Python script that
picks the top unblocked task from QUEUE.md and fires exactly ONE headless
worker. The worker is the only thing that costs tokens.

Token economics this design enforces:
  - one conductor, not one cron per agent  (~4x fewer sessions)
  - 12h cadence, not 6h                    (~2x fewer)
  - deterministic dispatch, no LLM here    (the conductor's own session: free)
  - the worker reads 3 files, not the repo (small context per session)
  => ~16 sessions/day  ->  ~1-2 bounded sessions/day

Safety:
  - guard.sh must pass or we exit without dispatching (sick box auto-pauses)
  - one worker at a time (worker.lock)
  - the worker gets the board paths + ONE task block; nothing else
  - subprocess hard timeout; the contract also tells the worker to self-stop at 45m
"""
import datetime
import pathlib
import re
import subprocess
import sys

AGENTIC = pathlib.Path.home() / ".agentic"
QUEUE = AGENTIC / "QUEUE.md"
CONTRACT = AGENTIC / "WORKER_CONTRACT.md"
LOCK = AGENTIC / "worker.lock"
LOG = AGENTIC / "conductor.log"
OUTBOX = AGENTIC / "board" / "outbox" / "conductor.md"

MODEL = "claude-sonnet-5"
# The worker needs to edit files and run git/python. Tune flags to your CLI version.
# acceptEdits = apply edits without prompting, still prompt (=hang) on anything
# else -> the timeout below is the backstop. Do NOT add --dangerously-skip-permissions.
WORKER_FLAGS = ["--model", MODEL, "--permission-mode", "acceptEdits"]
WORKER_CWD = "/mnt/c/Agents/agentic-universe/repo"
WORKER_TIMEOUT_S = 3600


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(msg):
    line = f"{now()} {msg}\n"
    with LOG.open("a") as f:
        f.write(line)
    print(line, end="")


def guard_ok():
    g = AGENTIC / "guard.sh"
    if not g.exists():
        log("guard.sh missing - refusing to dispatch")
        return False
    return subprocess.run(["bash", str(g)]).returncode == 0


def next_task():
    """First '## TASK' block in QUEUE.md whose 'blocked:' line is empty/none/-."""
    if not QUEUE.exists():
        return None
    for block in re.split(r"(?=^## TASK )", QUEUE.read_text(encoding="utf-8"), flags=re.M):
        if not block.startswith("## TASK "):
            continue
        m = re.search(r"^blocked:\s*(.*)$", block, flags=re.M)
        if m and m.group(1).strip().lower() in ("", "none", "-"):
            tid = block.split("\n", 1)[0].replace("## TASK ", "").split("—")[0].strip()
            return tid, block.strip()
    return None


def main():
    if LOCK.exists():
        log("worker.lock present - skip")
        return 0
    if not guard_ok():
        log("guard failed - skip (box unhealthy or worker running)")
        return 0
    task = next_task()
    if not task:
        log("queue empty - nothing to do")
        return 0
    tid, block = task

    if not CONTRACT.exists():
        log("WORKER_CONTRACT.md missing - refusing to dispatch")
        return 1

    LOCK.write_text(now())
    log(f"dispatching worker for {tid}")
    prompt = CONTRACT.read_text(encoding="utf-8") + "\n\n---\n\n" + block
    try:
        r = subprocess.run(
            ["claude", "-p", prompt] + WORKER_FLAGS,
            capture_output=True, text=True, timeout=WORKER_TIMEOUT_S,
            cwd=WORKER_CWD,
        )
        out = (r.stdout or "").strip().splitlines()
        tail = out[-1] if out else "(no output)"
        log(f"{tid} worker rc={r.returncode}: {tail[:200]}")
        if r.returncode != 0 and r.stderr:
            log(f"{tid} stderr: {r.stderr.strip()[:200]}")
    except subprocess.TimeoutExpired:
        log(f"{tid} worker TIMEOUT at {WORKER_TIMEOUT_S}s - see outbox/conductor.md")
    finally:
        LOCK.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

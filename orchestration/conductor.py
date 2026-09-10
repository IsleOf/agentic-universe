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
    """First '## TASK' block in QUEUE.md whose 'blocked:' line is empty/none/-.

    Returns (task_id, block_text, cwd). `cwd:` line in the block overrides the
    default repo dir, so the conductor can dispatch a worker into ~/poly-bot etc.
    """
    if not QUEUE.exists():
        return None
    for block in re.split(r"(?=^## TASK )", QUEUE.read_text(encoding="utf-8"), flags=re.M):
        if not block.startswith("## TASK "):
            continue
        # [ \t]* not \s* - \s crosses newlines, so an empty "blocked:" would
        # swallow the next line as its value and every task looks blocked.
        m = re.search(r"^blocked:[ \t]*(.*)$", block, flags=re.M)
        if m and m.group(1).strip().lower() in ("", "none", "-"):
            tid = block.split("\n", 1)[0].replace("## TASK ", "").split("—")[0].strip()
            cm = re.search(r"^cwd:[ \t]*(\S+)", block, flags=re.M)
            cwd = cm.group(1).strip() if cm else WORKER_CWD
            return tid, block.strip(), cwd
    return None


def _selftest():
    """Parse-only checks. No dispatch, no guard, no filesystem writes."""
    ok = True
    sample = (
        "# QUEUE\n\n"
        "## TASK t1 — first\nblocked:\nkind: build\nbody one\n\n"
        "## TASK t2 — second\nblocked: t1\nkind: build\nbody two\n\n"
        "## TASK t3 — third\nblocked: none\ncwd: /home/dev/poly-bot\nbody three\n"
    )
    global QUEUE
    real = QUEUE
    import tempfile
    tf = pathlib.Path(tempfile.mkstemp(suffix=".md")[1])
    tf.write_text(sample)
    QUEUE = tf
    try:
        t = next_task()
        cases = [
            ("picks first unblocked", t and t[0] == "t1"),
            ("empty 'blocked:' is not blocked", t and t[0] == "t1"),
            ("cwd defaults when absent", t and t[2] == WORKER_CWD),
        ]
        # block t1 -> should fall through to t3 (t2 blocked by t1 literal, still
        # 'blocked: t1' which is non-empty so also skipped)
        QUEUE.write_text(sample.replace("## TASK t1 — first\nblocked:\n",
                                        "## TASK t1 — first\nblocked: done\n"))
        t = next_task()
        cases.append(("skips non-empty blocked, honours cwd:",
                      t and t[0] == "t3" and t[2] == "/home/dev/poly-bot"))
        QUEUE.write_text("# QUEUE\n\nno tasks here\n")
        cases.append(("no tasks -> None", next_task() is None))
        for name, cond in cases:
            print("  %-45s %s" % (name, "ok" if cond else "FAIL"))
            ok = ok and bool(cond)
    finally:
        QUEUE = real
        tf.unlink(missing_ok=True)
    print("conductor selftest:", "GREEN" if ok else "RED")
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return _selftest()
    dry = len(sys.argv) > 1 and sys.argv[1] == "dry"

    if LOCK.exists():
        log("worker.lock present - skip")
        return 0
    if not dry and not guard_ok():
        log("guard failed - skip (box unhealthy or worker running)")
        return 0
    task = next_task()
    if not task:
        log("queue empty - nothing to do")
        return 0
    tid, block, cwd = task

    if dry:
        print(f"DRY: would dispatch {tid} (cwd={cwd}), prompt "
              f"{len(CONTRACT.read_text()) + len(block)} chars, "
              f"guard={'ok' if guard_ok() else 'FAIL'}")
        return 0

    if not CONTRACT.exists():
        log("WORKER_CONTRACT.md missing - refusing to dispatch")
        return 1

    LOCK.write_text(now())
    log(f"dispatching worker for {tid} (cwd={cwd})")
    prompt = CONTRACT.read_text(encoding="utf-8") + "\n\n---\n\n" + block
    try:
        r = subprocess.run(
            ["claude", "-p", prompt] + WORKER_FLAGS,
            capture_output=True, text=True, timeout=WORKER_TIMEOUT_S,
            cwd=cwd,
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

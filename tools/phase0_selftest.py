#!/usr/bin/env python3
"""Phase 0 GREEN/RED predicate.

`architecture/foundations.md`: "Write an executable GREEN/RED predicate before
building a loop." This is it for the trace substrate. Runs the two component
selftests and reports one verdict.

GREEN requires:
1. trace_substrate selftest GREEN — schema valid, secret scrubbed.
2. topology_recover gate GREEN — assigned roles recovered at >= 0.80 on the
   control condition (the plan's "instrument that cannot find assigned roles
   cannot be trusted to find emergent ones").

Exit 0 GREEN, 1 RED.
"""
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def run(name):
    proc = subprocess.run(
        [sys.executable, str(TOOLS / name), "selftest"],
        capture_output=True, text=True,
    )
    tag = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    return proc.returncode == 0, tag, proc.stdout, proc.stderr


def main():
    results = []
    for name in ("trace_substrate.py", "topology_recover.py"):
        ok, tag, out, err = run(name)
        results.append((name, ok, tag))
        print(f"=== {name} ===")
        print(out.rstrip())
        if err.strip():
            print(err.rstrip(), file=sys.stderr)
        print()

    green = all(ok for _, ok, _ in results)
    for name, ok, tag in results:
        print(f"  {name:24} {'GREEN' if ok else 'RED':5}  {tag}")
    print()
    print("PHASE 0:", "GREEN" if green else "RED")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())

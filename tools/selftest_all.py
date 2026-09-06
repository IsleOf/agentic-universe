#!/usr/bin/env python3
"""Run every build selftest and report one verdict.

`architecture/foundations.md`: "Write an executable GREEN/RED predicate before
building a loop." This is the predicate for the whole harness-infrastructure
build (Phases 0–1 so far).

Components:
  trace_substrate   selftest  — schema valid, secrets scrubbed
  topology_recover  selftest   — assigned roles recovered >= 0.80 on the control
  harness_registry  selftest   — versioned components, exact revert
  harness_demo      (default)   — end-to-end: registry + recorder + recovery

Exit 0 GREEN, 1 RED. Superseded `phase0_selftest.py` (kept as a thin alias).
"""
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

JOBS = [
    ("trace_substrate.py", ["selftest"]),
    ("topology_recover.py", ["selftest", "--noisy"]),
    ("harness_registry.py", ["selftest"]),
    ("harness_demo.py", []),
    ("experience_bank.py", ["selftest"]),
    ("improvement_loop.py", ["selftest"]),
    ("loop_adapter.py", ["selftest"]),
    ("loop_session.py", ["selftest"]),
    ("loop_metrics.py", ["selftest"]),
    ("holdout_tasks.py", ["selftest"]),
]


def run(name, args):
    proc = subprocess.run([sys.executable, str(TOOLS / name), *args],
                          capture_output=True, text=True)
    last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    return proc.returncode == 0, last, proc.stdout, proc.stderr


def main():
    results = []
    for name, args in JOBS:
        ok, tag, out, err = run(name, args)
        results.append((name, ok, tag))
        print(f"=== {name} {' '.join(args)} ===")
        print(out.rstrip())
        if err.strip():
            print(err.rstrip(), file=sys.stderr)
        print()

    green = all(ok for _, ok, _ in results)
    for name, ok, tag in results:
        print(f"  {name:22} {'GREEN' if ok else 'RED':5}  {tag}")
    print("\nBUILD SELFTEST:", "GREEN" if green else "RED")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())

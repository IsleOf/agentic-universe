#!/usr/bin/env python3
"""kill_reconcile.py — after a subagent/background task is killed, refuse to
commit until the working tree it may have dirtied is reconciled.

The §3 hazard (run 467, made concrete run 472 bucket B): killing a process stops
its execution, not its filesystem effects. On 2026-09-10 a killed run left 56
`source_generation` fields + 3 edges uncommitted; the next `git add -A` absorbed
them into commit `d1d9567` under a message describing only its own work. The rule
"run git status and reconcile after a kill" lived as prose and was not followed.

This is that rule as a callable predicate, matching `orphan_scan.is_reapable()`:
REPORT-only, returns `(ok, reason, files)`, no side effects except the marker
file it is explicitly told to write/clear.

Flow:
  kill_reconcile.py mark "stopped run 467 subagent"   # when you kill something
  ... (you inspect / reconcile the tree) ...
  kill_reconcile.py check                              # before the next commit
  kill_reconcile.py clear "reconciled, absorbed into run-467 commit deliberately"

`check` returns ok=False (exit 3) while a marker is unresolved AND the tree is
dirty. It does NOT block anything itself — a commit script or LoopSession calls
it and decides. The point is that the decision is now forced and logged.

PORTABILITY_CLASS: fixed-schema
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_MARKER = Path(".agentic") / "kill_marker.json"
# A marker older than this (hours) is assumed already dealt with — a stale marker
# should not block commits forever. Scaled, not fixed (run-385 hazard).
DEFAULT_STALE_H = 24.0


def _now():
    return time.time()


def read_marker(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {"corrupt": True, "at": 0.0, "reason": "(unreadable marker)"}


def mark(reason, path=DEFAULT_MARKER, now=None):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"at": now if now is not None else _now(), "reason": str(reason)}
    p.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def clear(reason, path=DEFAULT_MARKER, log_path=None):
    p = Path(path)
    prev = read_marker(path)
    if p.exists():
        p.unlink()
    entry = {"cleared_at": _now(), "reason": str(reason), "was": prev}
    lp = Path(log_path) if log_path else p.with_suffix(".audit")
    with lp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def git_dirty(repo_dir="."):
    """Return the list of dirty paths from `git status --porcelain`, or None if
    git is unavailable / not a repo (an instrument that can't measure says so)."""
    try:
        r = subprocess.run(["git", "-C", str(repo_dir), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return [ln[3:] for ln in r.stdout.splitlines() if ln.strip()]


def check(repo_dir=".", marker_path=DEFAULT_MARKER, stale_h=DEFAULT_STALE_H,
          now=None, dirty=None):
    """(ok, reason, files). ok=False iff an unresolved recent kill marker exists
    AND the tree is dirty. `dirty` may be injected for testing.
    """
    now = _now() if now is None else now
    m = read_marker(marker_path)
    if m is None:
        return True, "no kill marker", []
    if m.get("corrupt"):
        return False, "kill marker is unreadable — reconcile and clear it by hand", []
    age_h = (now - m.get("at", 0.0)) / 3600.0
    if age_h > stale_h:
        return True, ("kill marker is %.1fh old (> %.0fh) — assumed handled; "
                      "clear it" % (age_h, stale_h)), []
    files = git_dirty(repo_dir) if dirty is None else dirty
    if files is None:
        return False, "kill marker present and git state unreadable — cannot confirm clean", []
    if not files:
        return True, "kill marker present but tree clean — safe; clear the marker", []
    return False, ("kill marker unresolved (%.1fh ago: %s) and %d path(s) dirty — "
                   "reconcile before committing, then `kill_reconcile.py clear`"
                   % (age_h, m.get("reason", "?"), len(files))), files


def _selftest():
    import tempfile
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    d = Path(tempfile.mkdtemp())
    mk = d / "marker.json"

    # no marker -> ok
    ok, why, files = check(marker_path=mk, dirty=[])
    ck("no marker -> ok", ok and "no kill marker" in why)

    # marker + clean tree -> ok (but says clear it)
    mark("killed X", path=mk, now=1000.0)
    ok, why, files = check(marker_path=mk, now=1000.0, dirty=[])
    ck("marker + clean -> ok", ok and "clear the marker" in why)

    # marker + dirty tree -> NOT ok, lists files
    ok, why, files = check(marker_path=mk, now=1000.0,
                           dirty=["a.py", "b.json"])
    ck("marker + dirty -> blocked", not ok)
    ck("...and names the files", files == ["a.py", "b.json"] and "2 path" in why)

    # stale marker (>24h) + dirty -> ok again (don't block forever)
    ok, why, files = check(marker_path=mk, now=1000.0 + 25 * 3600,
                           dirty=["a.py"])
    ck("stale marker does not block forever", ok and "old" in why)

    # stale-window sweep: the flip happens once, at the boundary, monotone
    flips = []
    for h in range(0, 49, 2):
        o, _, _ = check(marker_path=mk, now=1000.0 + h * 3600, dirty=["x"])
        flips.append(1 if o else 0)
    ck("blocked below stale window, clear above, one transition",
       flips == sorted(flips) and flips[0] == 0 and flips[-1] == 1)

    # corrupt marker -> blocked, explicit
    mk.write_text("{not json", encoding="utf-8")
    ok, why, files = check(marker_path=mk, dirty=[])
    ck("corrupt marker -> blocked + says so", not ok and "unreadable" in why)

    # git unreadable while marker present -> blocked (can't confirm clean)
    mk.write_text(json.dumps({"at": 2000.0, "reason": "y"}), encoding="utf-8")
    ok, why, files = check(marker_path=mk, now=2000.0, dirty=None,
                           repo_dir=str(d))  # d is not a git repo
    ck("marker + git unreadable -> blocked", not ok and "unreadable" in why)

    # clear writes an audit line and removes the marker
    clear("done", path=mk)
    ck("clear removes marker", not mk.exists())
    ck("clear writes audit", mk.with_suffix(".audit").exists())

    ok_all = all(c for _, c in checks)
    for name, c in checks:
        print("  %-52s %s" % (name, "ok" if c else "FAIL"))
    print("kill_reconcile selftest: %d/%d %s"
          % (sum(1 for _, c in checks if c), len(checks),
             "GREEN" if ok_all else "RED"))
    return 0 if ok_all else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return _selftest()
    if len(argv) > 1 and argv[1] == "mark":
        reason = argv[2] if len(argv) > 2 else "(no reason given)"
        rec = mark(reason)
        print("marked: %s" % rec["reason"])
        return 0
    if len(argv) > 1 and argv[1] == "clear":
        reason = argv[2] if len(argv) > 2 else "(no reason given)"
        clear(reason)
        print("cleared")
        return 0
    if len(argv) > 1 and argv[1] == "check":
        ok, why, files = check()
        print(("OK: " if ok else "BLOCKED: ") + why)
        for f in files:
            print("   " + f)
        return 0 if ok else 3
    print(__doc__.strip().splitlines()[0])
    print("usage: kill_reconcile.py [mark <reason>|check|clear <reason>|selftest]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

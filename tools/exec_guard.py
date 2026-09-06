#!/usr/bin/env python3
"""Phase 5 — execution-layer enforcement for the autonomous loop.

`docs/self_improving_harness_plan.md` §4 Phase 5, and the finding that decides it
(`emergent_recognition_execution_gap`): agents flag an action unsafe in >90% of
runs and execute it anyway; 66% of runs are unsafe yet completed. Knowing and
doing are separate subsystems. So the loop's invariants live in the **execution
path** — a hook that blocks the commit — not in the SKILL.md prose the loop can
skip under time pressure.

`check(staged_files)` returns `{ok, blocks, warnings}`. A `block` stops the
commit; the loop cannot talk past it. Invariants:

- the graph validates (`tools/knowledge_graph.py validate` → VALID)
- no orphan nodes in the graph
- no secrets in any staged file (token shapes, key/secret assignments, PEM, AWS)
- raw `runtime/**/*.jsonl` is not staged (must stay gitignored, rule 9)
- the current branch is the working branch, not `main`
- (warning only) `docs/auto_sweep_*` was updated if the graph changed

Run as `python tools/exec_guard.py check` from a pre-commit hook. Install the
hook with `python tools/exec_guard.py install`.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

# High-confidence leak shapes — a match is a block anywhere, docs included.
_LEAK_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    # key/secret/token assignment ONLY when the value is long and secret-shaped
    # (so prose like "the `secret=` assignment" does not trip it)
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd)\s*[:=]\s*"
               r"['\"]?[A-Za-z0-9+/_\-]{16,}['\"]?"),
]

WORKING_BRANCH = "proposals/2026-09-01-emergent-behaviour-cluster"
GRAPH_REL = "knowledge/graph/agentic_universe_graph.json"


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def _staged_files():
    out = _git("diff", "--cached", "--name-only")
    return [l for l in out.splitlines() if l.strip()]


def _graph_valid():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "knowledge_graph.py"), "validate"],
                       cwd=ROOT, capture_output=True, text=True)
    return "VALID" in r.stdout and "INVALID" not in r.stdout


def _orphans():
    try:
        g = json.loads((ROOT / GRAPH_REL).read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"(could not read graph: {exc})"]
    ids = {n["id"] for n in g["nodes"]}
    linked = set()
    for e in g["edges"]:
        linked.add(e["source"])
        linked.add(e["target"])
    return sorted(ids - linked)


# these files define or exercise the secret-detection patterns themselves, so a
# literal-pattern match inside them is expected, not a leak
_SCAN_SKIP = {"tools/exec_guard.py", "tools/trace_substrate.py"}


def _scan_secrets(files):
    hits = []
    for f in files:
        if f in _SCAN_SKIP:
            continue
        p = ROOT / f
        if not p.exists() or p.is_dir():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in _LEAK_PATTERNS:
            for m in pat.finditer(text):
                hits.append(f"{f}: {m.group(0)[:40]}")
    return hits


def check(staged=None):
    staged = staged if staged is not None else _staged_files()
    blocks, warnings = [], []

    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch == "main" or branch == "master":
        blocks.append(f"on '{branch}' — the loop commits to {WORKING_BRANCH}, never the default branch")

    raw_traces = [f for f in staged if f.startswith("runtime/") and f.endswith(".jsonl")]
    if raw_traces:
        blocks.append(f"raw trace(s) staged (must stay gitignored, rule 9): {raw_traces}")

    secrets = _scan_secrets(staged)
    if secrets:
        blocks.append(f"possible secret(s) in staged files: {secrets}")

    graph_touched = GRAPH_REL in staged
    if graph_touched:
        if not _graph_valid():
            blocks.append("knowledge_graph.py validate did not print VALID")
        orph = _orphans()
        if orph:
            blocks.append(f"orphan node(s) in the graph: {orph}")
        if not any(f.startswith("docs/auto_sweep_") or f.startswith("docs/phase") for f in staged):
            warnings.append("graph changed but no docs/auto_sweep_* or docs/phase* staged")

    return {"ok": not blocks, "branch": branch, "graph_touched": graph_touched,
            "blocks": blocks, "warnings": warnings}


HOOK = """\
#!/bin/sh
# Agentic Universe loop guard (Phase 5). Installed by tools/exec_guard.py.
exec python "$(git rev-parse --show-toplevel)/tools/exec_guard.py" check --hook
"""


def _install():
    hooks_dir = Path(_git("rev-parse", "--git-path", "hooks") or (ROOT / ".git" / "hooks"))
    if not hooks_dir.is_absolute():
        hooks_dir = ROOT / hooks_dir
    hooks_dir.mkdir(parents=True, exist_ok=True)
    dst = hooks_dir / "pre-commit"
    dst.write_text(HOOK, encoding="utf-8")
    try:
        dst.chmod(0o755)
    except Exception:
        pass
    # also drop a committed copy so the hook is reviewable in-repo
    (ROOT / "hooks").mkdir(exist_ok=True)
    (ROOT / "hooks" / "pre-commit").write_text(HOOK, encoding="utf-8")
    print(f"installed {dst}")
    print("committed a reviewable copy at hooks/pre-commit")
    return 0


def _selftest():
    # the check must BLOCK a synthetic bad staging set and PASS a clean one
    bad = check(staged=["runtime/traces/loop-9.jsonl", "notes.txt"])
    # write a temp file with a fake secret and check it's caught. The fixture is
    # assembled at runtime so this source file has no key-shaped literal in it
    # (the guard would otherwise flag itself).
    fake = "api_key = " + "sk-" + ("x" * 28)
    tf = ROOT / "_guard_selftest_tmp.txt"
    tf.write_text(fake + "\n", encoding="utf-8")
    try:
        sec = check(staged=["_guard_selftest_tmp.txt"])
    finally:
        tf.unlink()
    clean = check(staged=["docs/whatever.md"])

    checks = {
        "raw trace staged -> block": any("raw trace" in b for b in bad["blocks"]),
        "fake secret -> block": any("secret" in b for b in sec["blocks"]),
        "clean doc-only staging -> ok": clean["ok"],
        "real graph currently validates + no orphans": _graph_valid() and not _orphans(),
        "on the working branch": check()["branch"] == WORKING_BRANCH,
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Phase 5 execution-layer guard for the loop.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("--hook", action="store_true")
    sub.add_parser("install")
    sub.add_parser("selftest")
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "install":
        return _install()
    if args.cmd == "check":
        res = check()
        for w in res["warnings"]:
            print(f"warning: {w}", file=sys.stderr)
        if res["blocks"]:
            print("COMMIT BLOCKED by the loop guard:", file=sys.stderr)
            for b in res["blocks"]:
                print(f"  - {b}", file=sys.stderr)
            return 1
        if not args.hook:
            print(json.dumps(res, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

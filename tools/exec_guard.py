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
- no self-design edit without owner ack — staging a change to the acceptance
  gate, this guard, the validator, the selftest manifest, anything under
  `runtime/harness/` (loop_policy / loop_procedure / loop_tools / loop_team), or
  a decision-logic region of the proposer / conductor is blocked unless
  `AU_SELF_DESIGN_ACK` is set to a reason (run 338, paths fixed run 339; from the
  MLAS fold: the loop must not be able to weaken its own gate)
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

# --- "gate the gate" (run 338, paths fixed run 339) --------------------------
# MLAS (arXiv:2606.23075, folded run 335): a self-evolving loop must not be able
# to autonomously weaken its own acceptance gate, execution guard, test manifest,
# or IDLE-STATE policy. Editing any of these is a *self-design* change - it needs
# an explicit owner acknowledgement, the same bar as a commit off the working
# branch. The ack is the env var AU_SELF_DESIGN_ACK set to a non-empty reason at
# commit time; the autonomous loop never sets it, so a self-design edit from the
# loop is blocked and surfaced to the owner.
# (The loop's *outermost* harness - the scheduled-task body and the /goal skill -
#  lives outside this repo and is already off-limits to autonomous edit; what is
#  in-repo and guarded here is the acceptance path plus the versioned harness
#  surface under runtime/harness/.)
_SELF_DESIGN_FILES = {
    "tools/acceptance_gate.py",     # the exogenous acceptance signal (+ its cert signer)
    "tools/exec_guard.py",          # this guard
    "tools/knowledge_graph.py",     # the validator the gate leans on
    "tools/selftest_all.py",        # the build-selftest manifest (JOBS)
    "tools/harness_registry.py",    # bless / manifest_drift - the conductor preflight leans on it (run 340)
}
_SELF_DESIGN_PREFIXES = (
    "runtime/harness/",             # the versioned harness surface: loop_policy /
                                    # loop_procedure / loop_tools / loop_team (+ .history)
)
# targeted: decision-logic regions inside otherwise routinely-edited files
_SELF_DESIGN_DIFF_FILES = {"tools/loop_proposer.py", "tools/loop_conductor.py"}
_SELF_DESIGN_DIFF_MARKERS = re.compile(
    r"PROPOSER_META|NOVELTY_FLOOR|PLATEAU_WINDOW|ABC_KINDS|NON_IDLE_KINDS|"
    r"mode_concentration_trigger|\bdimensions\b|run_novelty|idle_run_streak")


def _self_design_hits(staged):
    """Staged paths (and diff regions) that constitute a self-design change."""
    hits = []
    for f in staged:
        if f in _SELF_DESIGN_FILES or f.startswith(_SELF_DESIGN_PREFIXES):
            hits.append(f)
        elif f in _SELF_DESIGN_DIFF_FILES:
            diff = _git("diff", "--cached", "--unified=0", "--", f)
            changed = "\n".join(l for l in diff.splitlines()
                                if l[:1] in "+-" and l[:3] not in ("---", "+++"))
            if _SELF_DESIGN_DIFF_MARKERS.search(changed):
                hits.append(f"{f} (decision-logic region)")
    return hits


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


def check(staged=None, *, self_design_ack=None):
    staged = staged if staged is not None else _staged_files()
    if self_design_ack is None:
        import os
        self_design_ack = os.environ.get("AU_SELF_DESIGN_ACK", "")
    blocks, warnings = [], []

    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch == "main" or branch == "master":
        blocks.append(f"on '{branch}' — the loop commits to {WORKING_BRANCH}, never the default branch")

    sd = _self_design_hits(staged)
    if sd and not str(self_design_ack).strip():
        blocks.append(
            "self-design edit without owner ack: " + ", ".join(sd) +
            " — editing the acceptance gate / exec guard / test manifest / loop policy is a "
            "self-modification. Re-commit with AU_SELF_DESIGN_ACK='<reason>' set (owner only).")
    elif sd:
        warnings.append(f"self-design edit acked by owner ({self_design_ack!r}): {', '.join(sd)}")

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
            "self_design": sd, "blocks": blocks, "warnings": warnings}


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

    # "gate the gate" (run 338)
    sd_noack = check(staged=["tools/acceptance_gate.py"], self_design_ack="")
    sd_ack = check(staged=["tools/acceptance_gate.py"], self_design_ack="owner: tuning PACE alpha")
    sd_policy = check(staged=["runtime/harness/context/loop_policy.json"], self_design_ack="")
    sd_reg = _self_design_hits(["runtime/harness/prompt/loop_procedure.txt"])
    sd_clean = check(staged=["docs/x.md", "tools/probe_idle_agent.py"], self_design_ack="")

    checks = {
        "raw trace staged -> block": any("raw trace" in b for b in bad["blocks"]),
        "fake secret -> block": any("secret" in b for b in sec["blocks"]),
        "clean doc-only staging -> ok": clean["ok"],
        "real graph currently validates + no orphans": _graph_valid() and not _orphans(),
        "on the working branch": check()["branch"] == WORKING_BRANCH,
        "self-design edit without ack -> block":
            any("self-design edit without owner ack" in b for b in sd_noack["blocks"]),
        "self-design edit WITH ack -> no block, warns instead":
            not any("self-design" in b for b in sd_ack["blocks"])
            and any("acked by owner" in w for w in sd_ack["warnings"]),
        "runtime/harness/ loop_policy is a self-design edit": bool(sd_policy["self_design"])
            and not sd_policy["ok"],
        "runtime/harness/ prompt is a self-design edit": bool(sd_reg),
        "ordinary probe/doc edit is not a self-design edit":
            not sd_clean["self_design"],
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

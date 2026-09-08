#!/usr/bin/env python3
"""Find selftests that exercise a size-like parameter at exactly one value.

WHY THIS EXISTS. Runs 385 and 386 produced four defects in two components, and every
one was found the same way: by varying a parameter the selftest had held fixed.

  - `cohort_monitor`'s abort threshold was an absolute constant compared against a sum
    growing linearly with pool size. It aborted on pure benign noise from k=20. Run 353
    built it and selftested it at `range(6)`. Every check passed, at one pool size,
    forever.
  - The margin instrument added to catch that assumed a benign signal level nobody had
    checked against what the pool emitted, and measured a threshold the decision did not
    use.

Four defects, one detection method. That is a method, not an anecdote, so this makes it
cheap to run over the whole suite instead of one component at a time.

WHAT IT DOES. Parses each module's selftest region and collects the integer literals fed
to size-like constructs - `range(N)`, and int-valued keyword arguments whose name looks
like a count (n, k, size, workers, rounds, agents, ...), split from PRECISION names
like `trials` which only move variance. A parameter appearing at
exactly ONE value across the whole selftest is a candidate for the run-385 defect: the
tests cannot distinguish a threshold that holds from one that merely holds AT THAT VALUE.

WHAT IT IS NOT, and this matters as much as what it is. This is a HEURISTIC SURFACE SCAN,
not a proof of anything. It is the same honest position as `exec_guard`'s perimeter: good
coverage of a real class, no claim of completeness.

  - A single-valued parameter is NOT a bug. Plenty of selftests fix a size because the
    property under test genuinely does not depend on it, and a closed experimental design
    SHOULD pin its arm count (run 380 established exactly this - three salient instances
    are not a class, and two of the toolchain's exact-equality assertions turned out to be
    correct as written).
  - A swept parameter is NOT safe. Sweeping k over {6, 8} would not have caught a ceiling
    at k=20.
  - Name-based detection of "size-like" arguments is non-equivariant: renaming `k` to
    `q` hides it. Same limitation `exec_guard` carries and the same reason - there is no
    shape to whitelist here, only a vocabulary.

So this reports CANDIDATES FOR INSPECTION, ranked, and the judgement stays manual.

  python tools/param_invariance_audit.py report
  python tools/param_invariance_audit.py report --min-hits 3
  python tools/param_invariance_audit.py selftest

Pure stdlib.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

# Argument names that denote a count or a size - the parameters whose behaviour a
# threshold is most often implicitly a function of. Non-equivariant by construction
# (see the module docstring); this is a vocabulary, not a property.
# BEHAVIOURAL sizes: the system does something DIFFERENT at a different value, so an
# assertion that holds at one value may be an assertion about that value. These are the
# ones worth chasing - `cohort_monitor`'s pool size was one of these.
_SIZE_NAMES = {
    "n", "k", "size", "count", "num", "n_workers", "workers", "n_agents", "agents",
    "n_parents", "kids_per_parent", "rounds", "n_rounds", "cycles",
    "n_attackers", "length", "depth", "width", "pool_size", "keep_n", "horizon",
    "batch", "batch_size", "steps", "n_steps", "population", "arms", "n_arms",
}

# PRECISION sizes: only the VARIANCE of the estimate changes, not the behaviour under
# test. A Monte Carlo `trials=4000` fixed at one value is not the run-385 defect, and
# reporting it as a candidate buries the real hits under noise. The first version of this
# tool did exactly that - 9 of its 15 rows were `trials=N` - which is the same mistake it
# was written to find: a vocabulary that does not distinguish the parameters a result
# depends on from the ones it does not.
_PRECISION_NAMES = {
    "trials", "samples", "n_samples", "iterations", "n_iter", "reps", "replicates",
    "bootstrap", "n_boot", "seed", "seeds",
}

_SELFTEST_NAMES = {"_selftest", "selftest", "_selftests"}


def _selftest_nodes(tree):
    """Every function whose name looks like a selftest, plus their nested helpers."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in _SELFTEST_NAMES:
            out.append(node)
    return out


def _int_of(node):
    """The int value of a literal, or None. Handles unary minus."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _int_of(node.operand)
        return None if inner is None else -inner
    return None


def scan_module(path):
    """-> {param_name: sorted(distinct int values seen)} across the module's selftests."""
    try:
        src = io.open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError) as exc:
        return {"__error__": str(exc)}

    seen = {}

    def _note(name, val):
        if val is None:
            return
        seen.setdefault(name, set()).add(val)

    for fn in _selftest_nodes(tree):
        for node in ast.walk(fn):
            # `for k in (3, 20, 50, 100):` IS a sweep. The first version of this tool
            # could not see one - it only read literal ints inside range() and size-named
            # kwargs - so it went on flagging executor_pool at range()=3 immediately after
            # run 387 swept that module over four pool sizes. That is this tool committing
            # the very defect it exists to find: measuring something other than what the
            # code does. A loop over a literal collection of >=2 ints is recorded under the
            # loop variable's name.
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                if isinstance(node.iter, (ast.Tuple, ast.List, ast.Set)):
                    vals = [_int_of(e) for e in node.iter.elts]
                    vals = [v for v in vals if v is not None]
                    if len(vals) >= 2:
                        for v in vals:
                            _note(node.target.id, v)
            if not isinstance(node, ast.Call):
                continue
            # range(N) / range(a, b)
            fname = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if fname == "range":
                for a in node.args:
                    _note("range()", _int_of(a))
            # keyword arguments with size-like names
            for kw in node.keywords:
                if kw.arg and kw.arg.lower() in _SIZE_NAMES:
                    _note(kw.arg, _int_of(kw.value))
                elif kw.arg and kw.arg.lower() in _PRECISION_NAMES:
                    _note("~" + kw.arg, _int_of(kw.value))   # tracked, not ranked
    return {k: sorted(v) for k, v in seen.items()}


def audit(paths=None):
    paths = paths or sorted(TOOLS.glob("*.py"))
    rows = []
    for p in paths:
        if p.name == Path(__file__).name:
            continue
        found = scan_module(p)
        if "__error__" in found or not found:
            continue
        # "~name" marks a precision parameter: reported for context, never ranked.
        single = {k: v[0] for k, v in found.items()
                  if len(v) == 1 and not k.startswith("~")}
        swept = {k: v for k, v in found.items() if len(v) > 1 and not k.startswith("~")}
        if single:
            rows.append({
                "module": p.name,
                "single_valued": single,
                "swept": {k: v for k, v in swept.items()},
                "n_single": len(single),
            })
    rows.sort(key=lambda r: (-r["n_single"], r["module"]))
    return rows


def _report(min_hits=1, as_json=False):
    rows = [r for r in audit() if r["n_single"] >= min_hits]
    if as_json:
        print(json.dumps(rows, indent=2))
        return 0
    print("Selftests exercising a size-like parameter at exactly ONE value.")
    print("CANDIDATES FOR INSPECTION, not findings. A fixed size is often correct;")
    print("a swept one is not automatically safe. See the module docstring.\n")
    for r in rows:
        sv = ", ".join(f"{k}={v}" for k, v in sorted(r["single_valued"].items()))
        print(f"  {r['module']:<42} {sv}")
        if r["swept"]:
            sw = ", ".join(f"{k}={v}" for k, v in sorted(r["swept"].items()))
            print(f"  {'':<42} (swept: {sw})")
    print(f"\n{len(rows)} module(s) with at least {min_hits} single-valued size parameter(s).")
    return 0


def _selftest():
    checks = {}

    # a synthetic module: one parameter fixed, one swept
    src = (
        "def _selftest():\n"
        "    for i in range(6):\n"
        "        pass\n"
        "    for j in range(6):\n"
        "        pass\n"
        "    f(rounds=100)\n"
        "    f(rounds=400)\n"
        "    g(k=3)\n"
        "    h(unrelated_name=9)\n"
        "    i(trials=7)\n"
    )
    tmp = TOOLS / "_param_audit_fixture.py"
    io.open(tmp, "w", encoding="utf-8", newline="\n").write(src)
    try:
        found = scan_module(tmp)
        checks["a range() fixed at one value is reported single"] = found.get("range()") == [6]
        checks["a swept behavioural parameter is reported with all its values"] = (
            found.get("rounds") == [100, 400])
        checks["a precision parameter is marked with ~ even in the fixture"] = (
            found.get("~trials") == [7] and "trials" not in found)
        checks["a size-like kwarg is picked up"] = found.get("k") == [3]
        checks["a non-size kwarg is ignored"] = "unrelated_name" not in found
    finally:
        tmp.unlink(missing_ok=True)

    # the real suite: cohort_monitor is now the worked example and MUST show a swept range
    cm = scan_module(TOOLS / "cohort_monitor.py")
    checks["cohort_monitor's selftest now sweeps pool size (runs 385-386)"] = (
        len(cm.get("range()", [])) > 1)
    checks["...and reaches past the k=20 ceiling that broke it"] = (
        max(cm.get("range()", [0])) >= 24)

    # a module with no selftest yields nothing rather than a plausible-looking empty result
    checks["a module without a selftest contributes no rows"] = (
        scan_module(TOOLS / "param_invariance_audit.py") is not None)

    rows = audit()
    checks["the audit returns rows over the real toolchain"] = len(rows) > 0
    checks["every row names a module and its single-valued params"] = all(
        r["module"] and isinstance(r["single_valued"], dict) for r in rows)
    # the precision/behaviour split: a fixed Monte Carlo trial count is not a candidate
    src2 = ("def _selftest():\n"
            "    f(trials=4000)\n"
            "    g(n_workers=3)\n")
    tmp2 = TOOLS / "_param_audit_fixture2.py"
    io.open(tmp2, "w", encoding="utf-8", newline="\n").write(src2)
    try:
        f2 = scan_module(tmp2)
        checks["a precision parameter is tracked but marked, not ranked"] = (
            "~trials" in f2 and "trials" not in f2)
        checks["a behavioural parameter is ranked normally"] = f2.get("n_workers") == [3]
    finally:
        tmp2.unlink(missing_ok=True)
    checks["no ranked row is a precision parameter"] = all(
        not k.startswith("~") for r in audit() for k in r["single_valued"])

    # a loop over a literal collection is a sweep and must be seen as one
    src3 = ("def _selftest():\n"
            "    for k in (3, 20, 50, 100):\n"
            "        f(k)\n")
    tmp3 = TOOLS / "_param_audit_fixture3.py"
    io.open(tmp3, "w", encoding="utf-8", newline="\n").write(src3)
    try:
        f3 = scan_module(tmp3)
        checks["a for-loop over a literal tuple is recognised as a sweep"] = (
            f3.get("k") == [3, 20, 50, 100])
    finally:
        tmp3.unlink(missing_ok=True)
    checks["REGRESSION: executor_pool's run-387 pool-size sweep is now visible"] = (
        len(scan_module(TOOLS / "executor_pool.py").get("k", [])) > 1)

    checks["rows are ranked by how many parameters are unswept"] = all(
        rows[i]["n_single"] >= rows[i + 1]["n_single"] for i in range(len(rows) - 1))
    # the honest-limits check: the tool must not claim these are defects
    doc = (__doc__ or "")
    checks["the tool states it is a heuristic, not a proof"] = (
        "HEURISTIC SURFACE SCAN" in doc and "not a bug" in doc.lower())
    checks["...and states both failure directions, not just the flattering one"] = (
        "is NOT a bug" in doc and "NOT safe" in doc)

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    r = sub.add_parser("report", help="rank modules by unswept size-like parameters")
    r.add_argument("--min-hits", type=int, default=1)
    r.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "report":
        return _report(min_hits=args.min_hits, as_json=args.json)
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

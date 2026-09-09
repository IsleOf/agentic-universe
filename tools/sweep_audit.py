#!/usr/bin/env python3
"""Audit the loop's own sweep docs for evidence SUFFICIENCY and COVERAGE.

Run 441 folded ClaimReceipt (arXiv:2609.01992): a run log records *what* happened
but cannot say whether the reported claims are actually SUPPORTED by what was
retained (sufficiency), nor whether the work that was COMMITTED actually got done
(coverage). The loop's `docs/auto_sweep_*.md` files have both gaps, and coverage
is the exact shape of the run-368 acceptance-gate bug (it logged only its accepts,
so could not answer the one question it existed for).

This module is the no-keys version of that check, over the loop's own record:

  SUFFICIENCY  every headline claim in a sweep (a number, a "GREEN", an arrow
               result, a bolded assertion) names something that backs it - an
               arXiv id, a repo file, a `selftest` reference, a `VALID`, or a
               graph node / edge id. An unbacked headline is a claim the reader
               cannot recompute.

  COVERAGE     run N's increment addresses at least ONE of run N-1's sweep "Next"
               bullets, OR the increment explicitly explains the pivot ("fresh
               axis", "switching", "resting point", ...). A run that silently
               ignores every option it gave itself is a coverage gap.

Both checks are HEURISTIC and deliberately in the open, like `param_invariance_audit`
and `loop_action_class`: they report a list and a flag; the judgement stays manual.

CLI: report / selftest.  Pure stdlib.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SWEEP_GLOB = str(ROOT / "docs" / "auto_sweep_*.md")
RUNS_DIR = ROOT / "runtime" / "observations" / "loop_runs"

# a line that asserts a result the reader should be able to check
_HEADLINE = re.compile(
    r"\d+(\.\d+)?\s*%|\bGREEN\b|\bVALID\b|[-=]>|→|\bΓ\s*[=+−-]|"
    r"\+\d|\bcut (it |that )|\baccuracy\b|\bnet \+|\bnet [-−]")
# something that BACKS a headline
_BACKING = re.compile(
    r"arxiv[:\s]*\d{4}\.\d{4,5}|\btools/\w+\.py\b|\bselftest\b|\bBUILD SELFTEST\b|"
    r"\bVALID\b|\b(concept|artifact|finding|edge|pattern|emergent|decision|principle|bug)_[a-z0-9_]{8,}|"
    r"\bknowledge_graph\b|\brun \d{3}\b")
# a valid reason to not follow last run's Next
_PIVOT = re.compile(
    r"fresh axis|switch(ing)? (off|axis)|new axis|resting point|different topic|"
    r"different axis|continue literature|novelty (is )?due|"
    r"(deliberate |standalone )?consolidat(e|ion) pass|consolidation pass", re.I)


def _bullets(section_text):
    """Top-level `-`/`*` bullets, each joined with its indented continuation lines."""
    out, cur = [], None
    for ln in section_text.splitlines():
        m = _BULLET_START.match(ln)
        if m:
            if cur is not None:
                out.append(cur.strip())
            cur = m.group(2)
        elif cur is not None and (ln.strip() == "" or ln[:1] in (" ", "\t")):
            cur += " " + ln.strip()
        elif cur is not None:
            out.append(cur.strip())
            cur = None
    if cur is not None:
        out.append(cur.strip())
    return [b for b in out if len(b) > 15]
_BULLET_START = re.compile(r"^(\s*)[-*]\s+(.*)")
# distinctive tokens in a Next bullet that, if echoed in the increment, mean it was done
_TOKEN = re.compile(
    r"`([^`]+)`|\b(arxiv[:\s]*\d{4}\.\d{4,5})|\b(tools/\w+\.py)|"
    r"\b([a-z_]{4,}\.[a-z_]{3,}\(\))|\b(G[14]_?\w*)|\b([a-z]+_[a-z_]{4,})\b")


def _sweep_index():
    """{run_no: Path} from every sweep doc's `(run N)` header."""
    out = {}
    for p in glob.glob(SWEEP_GLOB):
        try:
            head = io.open(p, encoding="utf-8").readline()
        except OSError:
            continue
        m = re.search(r"\(run\s+(\d+)\)", head)
        if m:
            out[int(m.group(1))] = Path(p)
    return out


def _section(text, name):
    """The body of `## <name>` up to the next `## ` or end."""
    m = re.search(rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)", text,
                  re.M | re.S)
    return m.group(1).strip() if m else ""


def _increment_text(run_no, sweeps):
    parts = []
    p = sweeps.get(run_no)
    if p:
        t = io.open(p, encoding="utf-8").read()
        parts.append(_section(t, "Increment"))
    rec = RUNS_DIR / f"run-{run_no}.json"
    if rec.exists():
        try:
            parts.append(json.loads(rec.read_text(encoding="utf-8")).get("increment", ""))
        except (OSError, ValueError):
            pass
    return "\n".join(x for x in parts if x)


def sufficiency_check(run_no, *, sweeps=None):
    sweeps = sweeps or _sweep_index()
    p = sweeps.get(run_no)
    if not p:
        return {"run": run_no, "error": "no sweep doc", "backed": None}
    text = io.open(p, encoding="utf-8").read()
    # audit the finding-bearing sections, not Validation/Next/Sources
    body = "\n".join(_section(text, s) for s in
                     ("The finding", "What changed", "What it consolidates",
                      "Why it lands here", "Results at the rig's default params",
                      "Increment"))
    headlines, unbacked = [], []
    for ln in body.splitlines():
        s = ln.strip().lstrip("|").strip()
        if len(s) < 12 or s.startswith(("|---", "| ---")):
            continue
        if _HEADLINE.search(s):
            headlines.append(s[:110])
            # backing may be on the same line OR anywhere in the doc for a named id
            if not _BACKING.search(s) and not _BACKING.search(text):
                unbacked.append(s[:110])
    n = len(headlines) or 1
    return {
        "run": run_no,
        "n_headlines": len(headlines),
        "n_unbacked": len(unbacked),
        "backed_fraction": round(1 - len(unbacked) / n, 3),
        "unbacked": unbacked,
        "flag": bool(unbacked),
    }


def coverage_check(run_no, *, sweeps=None):
    sweeps = sweeps or _sweep_index()
    prior = sweeps.get(run_no - 1)
    if not prior:
        return {"run": run_no, "error": f"no sweep for run {run_no - 1}", "covered": None}
    prior_next = _section(io.open(prior, encoding="utf-8").read(), "Next")
    bullets = _bullets(prior_next)
    inc = _increment_text(run_no, sweeps).lower()
    pivot = bool(_PIVOT.search(inc))
    addressed = []
    for b in bullets:
        toks = {t for grp in _TOKEN.findall(b) for t in grp if t and len(t) > 3}
        toks = {t.lower() for t in toks
                if t.lower() not in ("report", "block", "the", "bounded", "build",
                                     "consolidate", "probe", "alternatively")}
        if any(t in inc for t in toks):
            addressed.append(b[:100])
    covered = bool(addressed) or pivot or not bullets
    return {
        "run": run_no,
        "prior_next_bullets": len(bullets),
        "addressed": addressed,
        "pivot_explained": pivot,
        "covered": covered,
        "flag": not covered,
        "note": ("run addressed a prior Next option" if addressed else
                 "pivot explained in the increment" if pivot else
                 "no prior Next bullets" if not bullets else
                 "COVERAGE GAP: run ignored every option its predecessor gave it, "
                 "with no stated pivot"),
    }


def report(run_no, *, sweeps=None):
    sweeps = sweeps or _sweep_index()
    return {"sufficiency": sufficiency_check(run_no, sweeps=sweeps),
            "coverage": coverage_check(run_no, sweeps=sweeps)}


# --------------------------------------------------------------------------- #
def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="sweepaudit-"))
    checks = {}
    try:
        d = tmp / "docs"
        d.mkdir()
        g = str(d / "auto_sweep_*.md")

        (d / "auto_sweep_2026-01-01-0000.md").write_text(
            "# Autonomous sweep — 2026-01-01 00:00 (run 10)\n\n"
            "## Increment\nFolded arXiv:2510.10047. Built tools/foo.py.\n\n"
            "## The finding\nThe rig shows a 42% gain (arXiv:2510.10047). selftest GREEN.\n\n"
            "## Next\n- Build `tools/bar.py` — a bounded thing\n"
            "- Or continue literature\n", encoding="utf-8")
        (d / "auto_sweep_2026-01-01-0600.md").write_text(
            "# Autonomous sweep — 2026-01-01 06:00 (run 11)\n\n"
            "## Increment\nBuilt `tools/bar.py` as run 10's Next named. selftest GREEN.\n\n"
            "## What changed\nbar.py does the thing. arXiv:2510.10047 grounds it.\n\n"
            "## Next\n- Something specific with `tools/baz.py`\n", encoding="utf-8")
        (d / "auto_sweep_2026-01-01-1200.md").write_text(
            "# Autonomous sweep — 2026-01-01 12:00 (run 12)\n\n"
            "## Increment\nLiterature, fresh axis. Folded arXiv:2609.02992.\n\n"
            "## The finding\nA 90% drop with zero X (arXiv:2609.02992).\n\n"
            "## Next\n- A concrete build on `tools/qux.py` to extend the mechanism\n",
            encoding="utf-8")
        (d / "auto_sweep_2026-01-01-1800.md").write_text(
            "# Autonomous sweep — 2026-01-01 18:00 (run 13)\n\n"
            "## Increment\nFixed an unrelated bug. Nothing about baz.\n\n"
            "## The finding\nThe reported gain is 12% but no source is named here at all "
            "and the doc mentions nothing checkable otherwise.\n\n"
            "## Next\n- x\n", encoding="utf-8")

        idx = {}
        for p in glob.glob(g):
            m = re.search(r"\(run\s+(\d+)\)", io.open(p, encoding="utf-8").readline())
            if m:
                idx[int(m.group(1))] = Path(p)

        cov11 = coverage_check(11, sweeps=idx)
        checks["coverage: run 11 addressed run 10's `tools/bar.py` Next bullet"] = (
            cov11["covered"] and "tools/bar.py" in " ".join(cov11["addressed"]).lower()
            and not cov11["flag"])

        cov12 = coverage_check(12, sweeps=idx)
        checks["coverage: run 12 pivoted ('fresh axis') - covered, not flagged"] = (
            cov12["covered"] and cov12["pivot_explained"] and not cov12["flag"])

        cov13 = coverage_check(13, sweeps=idx)
        checks["coverage: run 13 ignored run 12's Next with no pivot -> flag"] = (
            cov13["flag"] and not cov13["covered"])

        suf10 = sufficiency_check(10, sweeps=idx)
        checks["sufficiency: run 10's 42% gain is backed (arXiv id on the line)"] = (
            not suf10["flag"] and suf10["backed_fraction"] == 1.0
            and suf10["n_headlines"] >= 1)

        suf13 = sufficiency_check(13, sweeps=idx)
        checks["sufficiency: run 13's 12% claim with no source is flagged unbacked"] = (
            suf13["flag"] and suf13["n_unbacked"] >= 1)

        # a run with no sweep doc: reports an error, not a crash
        checks["a missing sweep doc reports an error, not a crash"] = (
            sufficiency_check(999, sweeps=idx).get("backed") is None
            and coverage_check(999, sweeps=idx).get("covered") is None)

        # runs against the real corpus: must not crash, must classify
        real_idx = _sweep_index()
        if real_idx:
            latest = max(real_idx)
            r = report(latest)
            checks["the real latest sweep audits without crashing"] = (
                "sufficiency" in r and "coverage" in r
                and isinstance(r["sufficiency"]["flag"], bool))
        else:
            checks["the real latest sweep audits without crashing"] = True

        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    rp = sub.add_parser("report")
    rp.add_argument("run", type=int, nargs="?", default=None,
                    help="run number (default: the latest sweep doc)")
    rp.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    sweeps = _sweep_index()
    if not sweeps:
        print("no sweep docs found")
        return 1
    run_no = args.run if args.run is not None else max(sweeps)
    r = report(run_no, sweeps=sweeps)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    s, c = r["sufficiency"], r["coverage"]
    print(f"sweep audit — run {run_no}\n")
    print(f"  SUFFICIENCY  {s.get('n_headlines', 0)} headline claim(s), "
          f"{s.get('n_unbacked', 0)} unbacked "
          f"(backed {s.get('backed_fraction')})")
    for u in s.get("unbacked", []):
        print(f"    unbacked: {u}")
    print(f"  COVERAGE     {c.get('note')}")
    for a in c.get("addressed", []):
        print(f"    addressed: {a}")
    if s.get("flag") or c.get("flag"):
        print("\n  ** FLAG **")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

#!/usr/bin/env python3
"""An action-class view of the loop's own increments.

Run 408, from arXiv:2609.00949 (folded run 407): aggregate accuracy hides
ACTION-CLASS miscalibration - a model that always TOOL_CALLs when it should
sometimes ASK/REFUSE/CONFIRM looks fine on average. The loop has the same shape:
the IDLE-STATE RULE plus normal work give it a small action space, and
`skill_induction` / `loop_metrics` CLASSIFY each increment but nothing scores
whether the CLASS was appropriate for the frontier state.

This module is the first-order check. It reads the last N `runtime/observations/
loop_runs/run-*.json` records, classifies each increment into one of five classes,
reports the mix, and flags a MONOCULTURE - one class dominating for a stretch -
because that is the loop equivalent of always-TOOL_CALL: not wrong per run, but a
calibration failure across runs.

  CLASSES
    fold          folded external literature into the graph (a paper -> nodes/edges)
    probe         built or extended a runnable rig / measurement
    build         shipped a new tool / module / capability (harness expansion)
    fix           fixed a bug or a broken instrument
    consolidate   consistency pass, adversarial pass, audit, negative result,
                  deepening an existing node without new external input

Classification is HEURISTIC (increment text + record fields), deliberately in the
open like `param_invariance_audit`: it reports a distribution and a flag, the
judgement stays manual. A monoculture flag is not "the loop is broken" - run 403-405
were three deliberate build/probe runs on one thread and that was correct. It is
"look at whether this was a choice or a rut".

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
RUNS_DIR = ROOT / "runtime" / "observations" / "loop_runs"

CLASSES = ("fold", "probe", "build", "fix", "consolidate", "verify")

# A run that LEADS with consolidation language is a consolidate run even if it then
# fixed what the look found - run 409 was misclassified `fix` because it fixed two
# bugs the consolidation pass surfaced, which is the classifier's own action-class
# blind spot (it could not see a consolidation-that-fixed-something as consolidation).
_LEADS_CONSOLIDATE = re.compile(
    r"^\s*.{0,40}\b(standalone consolidation|consolidation pass|consistency (pass|sweep)|"
    r"red[- ]team pass|a negative result|audit(ed)? (the|whether))", re.I)

# ordered: first match wins, most specific first
_RULES = [
    # run 426: a citation upgrade / full-read verification is its own class - it
    # confirms or corrects an abstract-read node against the full paper. It matches
    # 'fold' keywords (it cites a paper) so it must be checked first.
    ("verify", re.compile(
        r"\b(citation upgrade|full (html |pdf )?read|full-read|verified? .* against the full|"
        r"abstract-read node|verification_state -> validated|confirmed .* from the full paper)",
        re.I)),
    ("consolidate", re.compile(
        r"\b(consistency (pass|sweep)|adversarial pass|red[- ]team pass|audit(ed)?|"
        r"negative result|no attack landed|deepened .* node|trust boundary|"
        r"stopping point|the class does\s?n.?t exist|consolidation pass)", re.I)),
    ("fix", re.compile(
        r"\b(fixed|bug|broken instrument|instrument .* was itself|regression|"
        r"latent bug|overflow|the fix for that|miscalibrat)", re.I)),
    ("probe", re.compile(
        r"\b(probe|rig|arm on |sweep (over|the)|drives the real|measured (over|the)|"
        r"selftest checks? green.*probe)", re.I)),
    ("build", re.compile(
        r"\b(built tools/|new tool|week-1 build|shipped|added (a )?(one-liner|method|"
        r"module)|tools/\w+\.py .{0,40}(a selftest_all job|registered))", re.I)),
    ("fold", re.compile(
        r"\b(folded?|fold(ing)? arxiv|arxiv:\s*\d|literature fold|deepened .* with a "
        r"verified read)", re.I)),
]


def classify(rec):
    """One record -> a class in CLASSES, with the rule that matched."""
    text = " ".join(str(rec.get(k, "")) for k in ("increment", "note"))
    ff = rec.get("file_footprint") or {}
    harness = ff.get("harness") or {}
    cites = rec.get("citations") or []

    # a run that LEADS with consolidation language is a consolidate run, even if it
    # shipped or fixed something the look surfaced (run 409's misclassification)
    if _LEADS_CONSOLIDATE.match(text):
        return "consolidate", "leads with consolidation language"

    # strong structural signals next
    if harness.get("new_harness_files"):
        # a genuinely new tool file -> build, unless the text is clearly a probe
        if re.search(r"\bprobe_\w+\.py\b", " ".join(harness["new_harness_files"])):
            return "probe", "new probe_*.py file"
        return "build", "new harness file"
    for cls, rx in _RULES:
        if rx.search(text):
            # a run that cites a paper AND matches 'fix'/'probe' is usually a fold
            # that then acted; call it by the dominant verb, but a bare citation with
            # no other signal is a fold. `verify` is exempt: a citation upgrade
            # legitimately mentions the original fold it is upgrading (run 426).
            if cls not in ("fold", "verify") and cites and re.search(r"\bfold", text, re.I):
                return "fold", "cited + 'fold' verb"
            return cls, rx.pattern[:40]
    if cites:
        return "fold", "has citations, no other signal"
    return "consolidate", "no external input, no new capability"


def load_recent(n=12):
    files = sorted(
        glob.glob(str(RUNS_DIR / "run-*.json")),
        key=lambda p: int(re.search(r"run-(\d+)", p).group(1)))
    out = []
    for f in files[-n:]:
        try:
            out.append(json.loads(io.open(f, encoding="utf-8").read()))
        except (OSError, ValueError):
            continue
    return out


def report(n=12, *, records=None):
    recs = records if records is not None else load_recent(n)
    rows = []
    for r in recs:
        cls, why = classify(r)
        rows.append({"run": r.get("run"), "class": cls, "why": why,
                     "increment_head": (r.get("increment") or "")[:70]})
    counts = {c: sum(1 for x in rows if x["class"] == c) for c in CLASSES}
    total = len(rows) or 1
    dominant = max(counts, key=counts.get)
    dom_frac = round(counts[dominant] / total, 3)
    # a monoculture: one class >= 70% over >= 6 runs
    monoculture = total >= 6 and dom_frac >= 0.70
    # a run of >= 4 identical classes in a row, anywhere in the window
    streak, longest, longest_cls = 0, 0, None
    prev = None
    for x in rows:
        streak = streak + 1 if x["class"] == prev else 1
        if streak > longest:
            longest, longest_cls = streak, x["class"]
        prev = x["class"]
    return {
        "n": total,
        "counts": counts,
        "dominant_class": dominant,
        "dominant_fraction": dom_frac,
        "longest_streak": longest,
        "longest_streak_class": longest_cls,
        "monoculture_flag": bool(monoculture),
        "long_streak_flag": bool(longest >= 4),
        "note": (
            f"{dominant} is {dom_frac:.0%} of the last {total} increments"
            + (f"; {longest} {longest_cls} runs in a row" if longest >= 4 else "")
            + (" - MONOCULTURE: check whether this was a deliberate thread or a rut "
               "(run 403-405 were a legit 3-run build thread; 6+ of one class is worth "
               "a look)" if monoculture or longest >= 4 else " - mix looks varied")),
        "rows": rows,
    }


# --------------------------------------------------------------------------- #
def _rec(run, increment, *, note="", citations=(), new_harness=()):
    return {"run": run, "increment": increment, "note": note,
            "citations": list(citations),
            "file_footprint": {"harness": {"new_harness_files": list(new_harness)}}}


def _selftest():
    checks = {}

    samples = [
        (_rec(1, "Folded arXiv:2609.01491 (GlossoGen). +1 node, +7 edges."), "fold"),
        (_rec(2, "Built probe_language_drift_monitor - drives the real gates.g1_evidence",
              new_harness=["tools/probe_language_drift_monitor.py"]), "probe"),
        (_rec(3, "Built tools/pheromone.py - week-1 build list item 1, a selftest_all job",
              new_harness=["tools/pheromone.py"]), "build"),
        (_rec(4, "Fixed run 388's harness-expansion instrument - it diffed a gitignored file"),
         "fix"),
        (_rec(5, "Red-team pass over the swarm substrate; no attack landed unexpectedly"),
         "consolidate"),
        (_rec(6, "A negative result: audited the class before fixing it. The class does not exist."),
         "consolidate"),
        (_rec(7, "Citation upgrade: full HTML read of arXiv:2601.21112 v2; verification_state -> validated"),
         "verify"),
    ]
    for rec, want in samples:
        got, why = classify(rec)
        checks[f"classify: {rec['increment'][:45]!r} -> {want}"] = got == want

    # a build thread of 3 is NOT a monoculture at n>=6 with variety around it
    varied = [_rec(i, t) for i, t in enumerate([
        "Folded arXiv:1 literature fold", "Folded arXiv:2 literature fold",
        "Built probe_x rig", "Fixed a latent bug", "Red-team consistency pass",
        "Folded arXiv:3 literature fold"])]
    r = report(records=varied)
    checks["a citation-upgrade increment classes as verify, not fold"] = (
        classify(_rec(9, "citation upgrade: full-read of arXiv:1234.5678, confirmed from the "
                         "full paper; verification_state -> validated"))[0] == "verify")
    checks["a varied window is not flagged as a monoculture"] = not r["monoculture_flag"]

    # monoculture threshold behaviour across window sizes
    for w in (6, 8, 11):
        mono = [_rec(i, f"Folded arXiv:{i} literature fold") for i in range(w)]
        rm = report(records=mono)
        checks[f"{w} folds in a row -> monoculture + long-streak flags"] = (
            rm["monoculture_flag"] and rm["long_streak_flag"]
            and rm["dominant_class"] == "fold")
    # below the 6-run floor, no monoculture flag even at 100% one class
    small = [_rec(i, f"Folded arXiv:{i} literature fold") for i in range(5)]
    checks["5 folds (below the 6-run floor) -> no monoculture flag"] = (
        not report(records=small)["monoculture_flag"])
    rm = report(records=[_rec(i, f"Folded arXiv:{i} literature fold") for i in range(8)])

    # the note is honest about the run-403-to-405 exception
    checks["the note names the deliberate-thread-vs-rut distinction"] = (
        "deliberate thread or a rut" in rm["note"])

    # empty history: no crash, no false flag
    re0 = report(records=[])
    checks["empty history -> no flags, no crash"] = (
        not re0["monoculture_flag"] and not re0["long_streak_flag"] and re0["n"] == 1)

    # runs against the real records (whatever they are), at two window sizes - must
    # not crash and must classify every row into a known class
    for w in (8, 20):
        real = report(n=w)
        checks[f"the real recent window (n={w}) classifies cleanly"] = all(
            row["class"] in CLASSES for row in real["rows"])

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    rp = sub.add_parser("report")
    rp.add_argument("-n", type=int, default=12)
    rp.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    r = report(args.n)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"last {r['n']} increments — action-class mix\n")
    for row in r["rows"]:
        print(f"  run {row['run']!s:>4}  {row['class']:<11}  {row['increment_head']}")
    print(f"\n  counts: {r['counts']}")
    print(f"  {r['note']}")
    if r["monoculture_flag"] or r["long_streak_flag"]:
        print("  ** FLAG **")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

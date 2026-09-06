#!/usr/bin/env python3
"""Audit the project's OWN self-improvement lineage for harness tampering.

`concept_harness_tampering_persists_in_real_self_improvement_runs` (arXiv:2609.00069,
run 189) found that harness tampering — self-improving edits that produce illusory
gains or violate authorization / provenance / completeness — "often persists in
the lineage of the best agent". `docs/what_would_make_this_wrong.md` §2 names the
falsifier: *a tampering audit of this loop's own `evolution_log` lineage turns up
edits that lifted the held-out score by real integrity violations the gate
accepted.*

This tool runs that audit. It walks every harness component's version history
(`runtime/harness/*/*.history.json`), reconstructs each v→v+1 transition as an
edit dict, and runs `improvement_loop.tampering_flags` on it — the same
deterministic role × obligation pre-screen the Phase 3 gate uses.

A clean result is evidence the lineage holds; a flagged edit is a finding to
adjudicate by hand (the heuristic is conservative and will over-flag).

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from improvement_loop import tampering_flags  # noqa: E402

HARNESS = ROOT / "runtime" / "harness"
_RUN_RE = re.compile(r"run[ -](\d+)", re.I)


def _edits():
    """Yield one edit dict per version transition across all components."""
    for hist in sorted(HARNESS.glob("*/*.history.json")):
        h = json.loads(hist.read_text(encoding="utf-8"))
        kind, name = h.get("kind"), h.get("name")
        versions = h.get("versions", [])
        for prev, cur in zip(versions, versions[1:]):
            note = cur.get("note", "") or ""
            m = _RUN_RE.search(note)
            yield {
                "component": [kind, name],
                "change": note,
                "author": cur.get("author"),
                "from_v": prev.get("v"), "to_v": cur.get("v"),
                "run": int(m.group(1)) if m else None,
                "prediction": {},  # history does not store predictions
            }


def audit():
    rows = []
    for e in _edits():
        flags = tampering_flags(e)
        rows.append({**{k: e[k] for k in ("component", "author", "from_v", "to_v", "run", "change")},
                     "flags": [list(f) for f in flags]})
    flagged = [r for r in rows if r["flags"]]
    return {"total_edits": len(rows), "flagged": len(flagged), "rows": rows,
            "clean": not flagged}


def _selftest():
    r = audit()
    checks = {
        "walks the real harness history (>= 4 edits)": r["total_edits"] >= 4,
        "every row names a component and a version transition": all(
            len(x["component"]) == 2 and x["from_v"] is not None and x["to_v"] is not None
            for x in r["rows"]),
        "tampering_flags runs on a reconstructed edit (list result)": all(
            isinstance(x["flags"], list) for x in r["rows"]),
        # a synthetic tampering edit IS caught by the same path the audit uses
        "a synthetic verifier-touching edit is flagged": bool(tampering_flags(
            {"component": ["prompt", "loop_verifier"], "change": "run 999: relax the gate",
             "prediction": {"direction": "increase"}})),
    }
    for k, v in checks.items():
        print(f"  [{'ok' if v else 'FAIL'}] {k}")
    print(f"\n  lineage audit: {r['flagged']}/{r['total_edits']} edits flagged "
          f"({'CLEAN' if r['clean'] else 'REVIEW'})")
    for x in r["rows"]:
        mark = "FLAG" if x["flags"] else "ok  "
        print(f"    [{mark}] {'/'.join(map(str, x['component']))} v{x['from_v']}->v{x['to_v']} "
              f"(run {x['run']}, {x['author']}): {x['change'][:70]}")
        for f in x["flags"]:
            print(f"           -> {f[0]} / {f[1]}")
    ok = all(checks.values())
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Audit the loop's own harness lineage for tampering.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("report")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "report":
        print(json.dumps(audit(), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())

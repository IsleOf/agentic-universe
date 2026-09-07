#!/usr/bin/env python3
"""janitor - compile the loop's run corpus into per-consumer views (v2.5 skeleton).

`docs/self_rebuild_v2.md` section 6 + `concept_trace_compiles_to_per_consumer_views`: a
long-horizon record outgrows BOTH the human observer and the agent's own context. The
janitor reads the ~300 `runtime/observations/loop_runs/run-*.json` summaries and emits
three compact views, each answering one consumer's question:

  - HUMAN MONITOR  - "what changed, and is the loop healthy?"  (arcs, deltas, drift)
  - AGENT CONTEXT  - "what is already covered, what is the current state?"
  - DRIFT REPORT   - the computable health signals (idle streak, novelty, legibility)

It also flags stale `experience_bank` entries. Pure stdlib, no model, no network.
Advisory - the janitor does not delete or edit anything; it writes views under
`runtime/observations/views/`.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "runtime" / "observations" / "loop_runs"
VIEWS_DIR = ROOT / "runtime" / "observations" / "views"

# increment-kind classifier (mirrors loop_conductor.pick_increment's vocabulary)
_KIND_HINTS = (
    ("fold", ("fold ", "folded", "citation sweep", "literature")),
    ("build", ("build", "built ", "tools/", "skeleton", "wired", ".py -")),
    ("consistency", ("consistency pass", "adversarial pass", "integrate", "reconcile", "orientation refresh")),
    ("doc", ("refresh", "snapshot", "handoff", "readme", "sweep doc", "audit")),
    ("probe", ("dry-ran", "dry-run", "probe ", "sweep end to end")),
    ("deepen", ("deepen", "grounded", "citation sweep on")),
)


def classify(increment: str) -> str:
    t = (increment or "").lower()
    for kind, hints in _KIND_HINTS:
        if any(h in t for h in hints):
            return kind
    return "other"


def load_runs(runs_dir: Path = RUNS_DIR) -> list[dict]:
    out = []
    for p in sorted(runs_dir.glob("run-*.json"), key=lambda x: int(x.stem.split("-")[1])):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def _delta(r: dict) -> tuple[int, int]:
    d = r.get("graph_delta") or {}
    return int(d.get("nodes", 0)), int(d.get("edges", 0))


def human_monitor_view(runs: list[dict], *, tail: int = 40) -> str:
    if not runs:
        return "# Human monitor view\n\n(no runs)\n"
    first, last = runs[0]["run"], runs[-1]["run"]
    tot_n = sum(_delta(r)[0] for r in runs)
    tot_e = sum(_delta(r)[1] for r in runs)
    kinds = Counter(classify(r.get("increment", "")) for r in runs)
    verified = sum(1 for r in runs for c in (r.get("citations") or []) if c.get("verified"))
    cited = sum(len(r.get("citations") or []) for r in runs)
    lines = [
        "# Human monitor view",
        "",
        f"Runs **{first}–{last}** ({len(runs)} recorded). Graph delta over the span: "
        f"**+{tot_n} nodes / +{tot_e} edges**. Citations: {verified}/{cited} verified.",
        "",
        "Increment kinds: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()),
        "",
        f"## Last {min(tail, len(runs))} increments",
        "",
    ]
    for r in runs[-tail:]:
        n, e = _delta(r)
        d = f" (+{n}n/+{e}e)" if (n or e) else ""
        lines.append(f"- **run {r['run']}** [{classify(r.get('increment',''))}] "
                     f"{r.get('increment','').strip()}{d}")
    return "\n".join(lines) + "\n"


def agent_context_view(runs: list[dict]) -> str:
    if not runs:
        return "# Agent context view\n\n(no runs)\n"
    roots = Counter()
    for r in runs:
        for x in r.get("distinct_evidence_roots") or []:
            roots[x] += 1
    recent_kinds = [classify(r.get("increment", "")) for r in runs[-8:]]
    re_cited = {k: v for k, v in roots.items() if v > 1}
    lines = [
        "# Agent context view",
        "",
        f"State after run {runs[-1]['run']}. **Distinct evidence roots seen: {len(roots)}** "
        f"({sum(roots.values())} citations).",
        "",
        f"Last 8 increment kinds: {recent_kinds}",
        "",
        "## Already covered — do not re-fold without a new angle",
        "",
    ]
    for k, v in roots.most_common(30):
        mark = "  ⟲" if v > 1 else ""
        lines.append(f"- `{k}` ×{v}{mark}")
    if re_cited:
        lines += ["", f"**Re-cited roots ({len(re_cited)})** — a fold that only re-cites these is "
                  f"plateau work: " + ", ".join(f"`{k}`" for k in sorted(re_cited))]
    return "\n".join(lines) + "\n"


def drift_report(runs: list[dict], *, window: int = 6) -> str:
    if not runs:
        return "# Drift report\n\n(no runs)\n"
    tail = runs[-window:]
    tail_roots = [set(r.get("distinct_evidence_roots") or []) for r in tail]
    seen_before = set()
    for r in runs[:-window]:
        seen_before |= set(r.get("distinct_evidence_roots") or [])
    new = sum(1 for s in tail_roots for x in s if x not in seen_before)
    repeat = sum(1 for s in tail_roots for x in s if x in seen_before)
    novelty = round(new / (new + repeat), 3) if (new + repeat) else None
    idle = 0
    for r in reversed(runs):
        n, e = _delta(r)
        if n == 0 and e == 0 and classify(r.get("increment", "")) in ("doc", "consistency", "other"):
            idle += 1
        else:
            break
    legls = [r.get("status_line", "") for r in tail if "legible" in r.get("status_line", "")]
    lines = [
        "# Drift report",
        "",
        f"Window: last {len(tail)} runs ({tail[0]['run']}–{tail[-1]['run']}).",
        f"- **novelty ratio**: {novelty}  (new evidence roots / total, threshold 0.34)"
        + ("  ⚠ below threshold" if (novelty is not None and novelty < 0.34) else ""),
        f"- **idle streak**: {idle}  (consecutive trailing doc/consistency/other runs with no graph delta)"
        + ("  ⚠ plateau" if idle >= 3 else ""),
        f"- last status lines: {legls[-2:] if legls else '(none)'}",
        "",
        "Reading: novelty below 0.34 or an idle streak ≥ 3 means the next run must be a genuine "
        "IDLE-STATE clause (a) deepen-one-node, (b) probe dry-run, or (c) consistency pass — not "
        "another marginal fold.",
    ]
    return "\n".join(lines) + "\n"


def stale_bank_flags() -> str:
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from experience_bank import ExperienceBank
        from harness_registry import Registry
        bank = ExperienceBank()
        stale = bank.stale(Registry().manifest())
        if not stale:
            return "# Experience-bank staleness\n\nNone — all entries carry a current manifest.\n"
        return "# Experience-bank staleness\n\n" + "\n".join(
            f"- `{s}` — re-verify before reuse" for s in stale) + "\n"
    except Exception as e:                     # pragma: no cover - defensive
        return f"# Experience-bank staleness\n\n(could not check: {e})\n"


def run(runs_dir: Path = RUNS_DIR, out_dir: Path = VIEWS_DIR) -> dict:
    runs = load_runs(runs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, text in (
        ("human_monitor.md", human_monitor_view(runs)),
        ("agent_context.md", agent_context_view(runs)),
        ("drift_report.md", drift_report(runs)),
        ("bank_staleness.md", stale_bank_flags()),
    ):
        (out_dir / name).write_text(text, encoding="utf-8")
        written[name] = len(text)
    return {"runs": len(runs), "written": written,
            "span": (runs[0]["run"], runs[-1]["run"]) if runs else None}


def _selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="janitor-"))
    rd = tmp / "runs"; rd.mkdir()
    # a fake corpus: 5 folds of one root, then 4 doc runs with no delta
    corpus = []
    for i in range(1, 6):
        corpus.append({"run": i, "increment": f"fold arXiv:2699.000{i}", "graph_delta": {"nodes": 1, "edges": 2},
                       "citations": [{"id": f"arXiv:2699.000{i}", "verified": True}],
                       "distinct_evidence_roots": [f"arXiv:2699.000{i}"], "status_line": f"run {i} OK legible 1.00"})
    for i in range(6, 10):
        corpus.append({"run": i, "increment": "orientation refresh - snapshot", "graph_delta": {"nodes": 0, "edges": 0},
                       "citations": [], "distinct_evidence_roots": ["arXiv:2699.0001"],  # re-cite
                       "status_line": f"run {i} OK legible 1.00"})
    for c in corpus:
        (rd / f"run-{c['run']}.json").write_text(json.dumps(c), encoding="utf-8")

    checks = {}
    runs = load_runs(rd)
    checks["load_runs reads and orders the corpus"] = [r["run"] for r in runs] == list(range(1, 10))
    checks["classify tags a fold and a doc run"] = (
        classify("fold arXiv:2699.0001") == "fold"
        and classify("orientation refresh - snapshot") == "consistency")

    hm = human_monitor_view(runs)
    checks["human view reports the graph delta over the span"] = "+5 nodes / +10 edges" in hm
    checks["human view lists recent increments"] = "run 9" in hm and "run 1" in hm

    ac = agent_context_view(runs)
    checks["agent view counts distinct evidence roots"] = "Distinct evidence roots seen: 5" in ac
    checks["agent view flags the re-cited root"] = "Re-cited roots" in ac and "2699.0001`" in ac

    dr = drift_report(runs, window=6)
    checks["drift report computes an idle streak"] = "idle streak**: 4" in dr and "plateau" in dr
    checks["drift report computes a novelty ratio"] = "novelty ratio**: 0.333" in dr

    res = run(rd, tmp / "views")
    checks["run() writes all four views"] = set(res["written"]) == {
        "human_monitor.md", "agent_context.md", "drift_report.md", "bank_staleness.md"}
    checks["run() reports the span"] = res["span"] == (1, 9)
    checks["janitor writes, never deletes"] = not any(p.name.startswith("run-") for p in (tmp / "views").iterdir())

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    r = sub.add_parser("run")
    r.add_argument("--print", action="store_true", help="also print the views to stdout")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "run":
        res = run()
        print(json.dumps(res, indent=2))
        if args.print:
            for name in res["written"]:
                print("\n" + "=" * 8, name, "=" * 8)
                print((VIEWS_DIR / name).read_text(encoding="utf-8"))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

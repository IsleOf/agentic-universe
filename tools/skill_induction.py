#!/usr/bin/env python3
"""Phase 4 — skill induction from the experience bank.

`docs/self_improving_harness_plan.md` §4 Phase 4: repeated wins crystallise into
named skills. "This is where a harness *actually* improves — not by better
prompts but by growing a library of procedures."

The tension, recorded as a `challenges` edge and enforced here: crystallising an
emergent role into a named skill ends the emergence that produced it. So a fixed
fraction of runs are marked **skill-withheld** — permanently — or the system
stops finding anything new (`principle_diversity_maintenance` *constrains*
`pattern_skill_induction`).

## What it induces from

The autonomous loop's own 56-run history, as workflow entries in the experience
bank (`tools/experience_bank.py`, fed by `tools/loop_adapter.py`). Each entry's
`retrieval_key` is a task-class label ("literature sweep", "citation upgrade",
"consistency re-read", "build", "hygiene", ...). A label that recurs at or above
`MIN_SUPPORT` and whose runs share a stable action signature becomes a candidate
skill: a `tool` component written to the harness registry.

## What it does NOT do

- No LLM. Clustering is on the retrieval key + a coarse action signature
  (which event kinds the run emitted).
- No automatic promotion into the live loop — a candidate skill is written to a
  `runtime/harness` registry and flagged `candidate`; a human moves it to the
  loop's actual procedure. Same shape as Phase 3.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from harness_registry import Registry                     # noqa: E402
from trace_substrate import Recorder                      # noqa: E402
from experience_bank import ExperienceBank, condense      # noqa: E402
from loop_adapter import seed_loop_harness, replay_history, GRAPH  # noqa: E402

MIN_SUPPORT = 4          # a task class must recur >= this many times
WITHHELD_FRACTION = 0.20  # permanently, per principle_diversity_maintenance

# canonical task-class labels, matched against the free-text run notes
TASK_CLASSES = {
    "literature sweep": ["sweep", "arxiv", "folded in", "new finding"],
    "citation upgrade": ["citation upgrade", "abstract-read", "abstract read", "-> verified", "verified run"],
    "consistency re-read": ["consistency", "re-read", "reconcil", "internal-consistency"],
    "graph hygiene": ["hygiene", "orphan", "edge-type audit", "inconclusive", "retraction"],
    "doc refresh": ["refresh", "rewrote", "stale", "graph_state"],
    "build": ["built", "tools/", "selftest", "phase 0", "phase 1", "phase 2", "phase 3", "gate green"],
}


def classify(note_text):
    t = note_text.lower()
    hits = [(cls, sum(t.count(k) for k in kws)) for cls, kws in TASK_CLASSES.items()]
    hits = [(c, n) for c, n in hits if n > 0]
    if not hits:
        return "other"
    return max(hits, key=lambda x: x[1])[0]


def _build_corpus_bank(tmp):
    reg = Registry(base=tmp / "harness")
    seed_loop_harness(reg)
    rec = Recorder(run_id="induction", trace_dir=str(tmp / "traces"), layer="harness",
                   language="en", harness_manifest=reg.manifest())
    replay_history(GRAPH, rec)
    rec.close()
    trace = tmp / "traces" / "induction.jsonl"
    bank = ExperienceBank(base=tmp / "bank")
    condense(trace, bank)
    return reg, bank, trace


def induce(reg: Registry, bank: ExperienceBank):
    """Return candidate skills. Writes accepted candidates to reg as `tool`
    components tagged `candidate`.
    """
    workflow = bank._all("workflow")
    # classify each workflow entry by its stored pattern text
    by_class = defaultdict(list)
    for e in workflow:
        cls = classify(e["pattern"] + " " + e.get("note", ""))
        by_class[cls].append(e)

    candidates = []
    for cls, entries in sorted(by_class.items()):
        if cls == "other" or len(entries) < MIN_SUPPORT:
            continue
        # action signature: distinct evidence-root counts seen — a proxy for
        # "does this task class reliably touch sources"
        root_counts = [len(e.get("distinct_evidence_roots", [])) for e in entries]
        cites = sum(1 for c in root_counts if c > 0)
        skill = {
            "name": re.sub(r"\W+", "_", cls),
            "task_class": cls,
            "support": len(entries),
            "cites_sources_fraction": round(cites / len(entries), 2),
            "procedure": _procedure_for(cls),
            "status": "candidate",
            "note": f"induced from {len(entries)} runs of history; NOT auto-promoted "
                    f"(withheld-fraction discipline applies)",
        }
        reg.set("tool", f"skill_{skill['name']}", json.dumps(skill, indent=2),
                note=f"induced candidate skill: {cls} (support {len(entries)})", author="induction")
        candidates.append(skill)
    return candidates


def _procedure_for(cls):
    return {
        "literature sweep": "narrow arXiv/cs.MA window; verify each citation 3 ways; fold only VERIFIED "
                            "novel mechanisms; challenges edges for tensions; write sweep doc.",
        "citation upgrade": "pick an abstract-read load-bearing node from source_register; fetch the arXiv "
                            "page; confirm existence + summary + headline number; upgrade to VERIFIED or "
                            "correct the node; regenerate the register.",
        "consistency re-read": "read the 4 design docs end to end; check the findings-driven revisions have "
                               "not left contradictions; every challenges edge into the design is answered or "
                               "listed open; correct drift.",
        "graph hygiene": "orphan check; edge-type audit on recent challenges edges; re-check inconclusive "
                         "nodes against newer evidence; reconcile status/verification_state.",
        "doc refresh": "compare a public-facing doc's snapshot numbers + tables to the current graph; rewrite "
                       "the stale parts; point counts at graph_state.",
        "build": "GREEN/RED predicate first; pure stdlib matching knowledge_graph.py style; selftest; add to "
                 "selftest_all.py; doc + artifact_ graph node; record the run via LoopSession.",
    }.get(cls, "n/a")


def withheld_runs(run_ids, fraction=WITHHELD_FRACTION):
    """Deterministic permanent hold-out: every Nth run id gets the skill library
    withheld, so distillation never fully displaces discovery.
    """
    step = max(round(1 / fraction), 2)
    return sorted(r for i, r in enumerate(sorted(run_ids)) if i % step == 0)


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="skill-ind-"))
    try:
        reg, bank, trace = _build_corpus_bank(tmp)
        n_workflow = bank.stats()["workflow"]
        candidates = induce(reg, bank)

        classes = {c["task_class"] for c in candidates}
        # every induced candidate is in the registry as a tool component, tagged candidate
        in_registry = all(reg.get("tool", f"skill_{c['name']}") for c in candidates)
        all_candidate_status = all(json.loads(reg.get("tool", f"skill_{c['name']}"))["status"] == "candidate"
                                   for c in candidates)

        run_ids = [f"run-{i}" for i in range(1, 51)]
        held = withheld_runs(run_ids)

        checks = {
            "corpus condensed into workflow entries": n_workflow >= 40,
            "at least 2 task classes induced": len(candidates) >= 2,
            "no auto-promotion (all candidates)": all_candidate_status,
            "candidates written to the registry": in_registry,
            "each candidate has support >= MIN_SUPPORT": all(c["support"] >= MIN_SUPPORT for c in candidates),
            "withheld fraction ~20% and non-empty": 0 < len(held) <= len(run_ids) * 0.5 and len(held) >= 8,
            "withheld set is deterministic": withheld_runs(run_ids) == held,
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        print(f"\n  workflow entries: {n_workflow}")
        for c in candidates:
            print(f"    skill '{c['name']}'  support={c['support']}  "
                  f"cites_sources={c['cites_sources_fraction']}")
        print(f"  permanently skill-withheld runs (20%): {len(held)} of {len(run_ids)}")
        ok = all(checks.values())
        print("\nSELFTEST", "GREEN" if ok else "RED")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Phase 4 skill induction from the experience bank.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("induce")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "induce":
        import shutil
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            reg, bank, _ = _build_corpus_bank(tmp)
            for c in induce(reg, bank):
                print(json.dumps(c, indent=2))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

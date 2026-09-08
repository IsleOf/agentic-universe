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
RETIRE_WINDOW = 12        # runs; a skill unseen for this many recent runs is retired

# canonical task-class labels, matched against the free-text run notes.
# Order matters: more specific classes are checked before broad ones when scores tie.
# Vocabulary refreshed run 365. Run 364 measured this taxonomy against the run
# corpus and found 33.6% of runs classifying as "other" - the keyword lists had
# drifted from how increments are actually written (bare "fold X" instead of
# "folded in"; "wire A to B" and "build x.py" instead of "tools/"; and a whole
# task class, per-project audits, that postdates the taxonomy). A classifier
# silently losing contact with what it classifies is the same failure family as
# the run-361 dead metrics: it looks fine because it always returns something.
# Terms below were derived by reading the unclassified runs, not by aiming at a
# target distribution.
TASK_CLASSES = {
    "build": ["built", "tools/", "selftest", "gate green", "phase 0", "phase 1", "phase 2",
              "phase 3", "phase 4", "phase 5", "skeleton", "loop_session", "harness_registry",
              "trace substrate", "pre-commit hook", "predicate",
              # run 365: the loop writes "build x.py" / "wire A to B" far more than "tools/"
              "build ", "wire ", "fix ", ".py", "rig", "adapter", "seam", "probe_"],
    "project audit": ["poly-bot", "poster-studio", "project graph", "project_state",
                      "audit", "coverage pass", "gap analysis", "handover", "per-agent"],
    "citation upgrade": ["citation upgrade", "citation check", "abstract-read", "abstract read",
                         "-> verified", "verified run", "both citations", "verified real but",
                         "upgraded to verified", "headline number"],
    "consistency re-read": ["consistency", "re-read", "reconcil", "internal-consistency",
                            "read the 4 design docs", "read the four design docs", "no contradictions",
                            # run 365
                            "re-rank", "severity", "adversarial pass", "verification pass"],
    "design integration": ["folded run", "into the design", "revised docs/nourishing", "revised the design",
                           "one rule unifying", "unifying", "design consequence", "revised nourishing_harness",
                           # run 365
                           "spec ", "architecture", "self_rebuild", "requirements"],
    "graph hygiene": ["hygiene", "orphan", "edge-type audit", "challenges-edge audit", "inconclusive",
                      "retraction", "structural edge", "structural edges", "reconciled verification_state"],
    "doc refresh": ["refresh", "rewrote", "rewritten", "stale", "graph_state", "map of swept",
                    "literature_coverage", "coverage map"],
    "literature sweep": ["sweep", "arxiv", "folded in", "new finding", "folded a verified",
                         "cross-lingual", "market dynamics", "narrow", "cs.ma", "past ~sept",
                         # run 365: the loop overwhelmingly writes bare "fold <id> <title>"
                         "fold ", "deepen", "citation sweep"],
}


def classify(note_text):
    t = note_text.lower()
    order = list(TASK_CLASSES)
    hits = [(cls, sum(t.count(k) for k in kws)) for cls, kws in TASK_CLASSES.items()]
    hits = [(c, n) for c, n in hits if n > 0]
    if not hits:
        return "other"
    # highest keyword count wins; ties broken by declaration order (most specific first)
    best = max(n for _, n in hits)
    return next(c for c in order if (c, best) in hits)


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


def _run_order(bank):
    """Best-effort chronological order of the workflow entries (by ts, then id)."""
    return sorted(bank._all("workflow"), key=lambda e: (e.get("ts", 0), e["id"]))


def retire(reg: Registry, bank: ExperienceBank, window=RETIRE_WINDOW):
    """The deprecation stage of `pattern_agentic_skill_lifecycle`, actually
    exercised (`principle_retraction_capacity`). A skill whose task class has not
    appeared in the last `window` workflow entries is marked `deprecated` — it is
    kept (auditable), not deleted, and stops being offered.

    Returns the list of skills retired this pass.
    """
    entries = _run_order(bank)
    recent = entries[-window:] if len(entries) > window else entries
    recent_classes = {classify(e["pattern"] + " " + e.get("note", "")) for e in recent}

    retired = []
    for c in reg.list():
        if c["kind"] != "tool" or not c["name"].startswith("skill_"):
            continue
        body = reg.get("tool", c["name"])
        try:
            skill = json.loads(body)
        except Exception:
            continue
        if skill.get("status") == "deprecated":
            continue
        if skill.get("task_class") not in recent_classes:
            skill["status"] = "deprecated"
            skill["retired_note"] = (f"task class '{skill['task_class']}' not seen in the last "
                                     f"{len(recent)} runs; deprecated, not deleted")
            reg.set("tool", c["name"], json.dumps(skill, indent=2),
                    note=f"retire: {skill['task_class']} disused", author="retire")
            retired.append(skill)
    return retired


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
        "design integration": "take a run's finding; locate the design section(s) it bears on; revise the "
                              "prose so the finding is reflected and the challenges edges stay honest; note "
                              "which sections changed in the sweep doc.",
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

        # retirement: register a skill whose task_class can never appear in the
        # recent window (classify() never emits it), so retire() must deprecate it
        # regardless of what the live loop-history composition happens to be.
        reg.set("tool", "skill___test_disused__", json.dumps(
            {"name": "__test_disused__", "task_class": "__never_emitted__",
             "status": "candidate", "support": 99, "procedure": "n/a"}, indent=2),
            note="selftest fixture: a definitely-disused skill", author="selftest")
        retired = retire(reg, bank)
        retired_disused = any(s["name"] == "__test_disused__" for s in retired)
        # every retired skill is still in the registry, status deprecated
        retired_kept = all(
            json.loads(reg.get("tool", f"skill_{s['name']}"))["status"] == "deprecated"
            for s in retired) if retired else True

        checks = {
            "corpus condensed into workflow entries": n_workflow >= 40,
            "at least 2 task classes induced": len(candidates) >= 2,
            "no auto-promotion (all candidates)": all_candidate_status,
            "candidates written to the registry": in_registry,
            "each candidate has support >= MIN_SUPPORT": all(c["support"] >= MIN_SUPPORT for c in candidates),
            "withheld fraction ~20% and non-empty": 0 < len(held) <= len(run_ids) * 0.5 and len(held) >= 8,
            "withheld set is deterministic": withheld_runs(run_ids) == held,
            "retire() deprecates a disused skill class": retired_disused,
            "retired skills are kept (deprecated), not deleted": retired_kept,
            "a second retire() pass is idempotent": retire(reg, bank) == [],
        }

        # Classifier-drift guard (run 365). Run 364 found 33.6% of the real run
        # corpus classifying as "other" - the vocabulary had drifted from how
        # increments are written, and nothing caught it because classify() always
        # returns something. This makes the drift self-detecting: if the loop's
        # writing style moves away from the keywords again, the build goes RED
        # instead of the measurement quietly getting rougher.
        # Non-hermetic by necessity (it measures the live corpus); skipped if absent.
        import glob as _glob
        corpus = _glob.glob(str(ROOT / "runtime" / "observations" / "loop_runs" / "run-*.json"))
        if len(corpus) >= 50:
            unclassified = 0
            total = 0
            for p in corpus:
                try:
                    inc = json.loads(Path(p).read_text(encoding="utf-8")).get("increment") or ""
                except Exception:
                    continue
                total += 1
                if classify(inc) == "other":
                    unclassified += 1
            rate = unclassified / total if total else 0.0
            checks[f"TASK_CLASSES still fits the run corpus (other={rate:.1%}, cap 15%)"] = rate <= 0.15
        else:
            checks["classifier-drift guard skipped (corpus < 50 runs)"] = True
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
            cands = induce(reg, bank)
            retired = retire(reg, bank)
            print(json.dumps({"induced": cands, "retired": [s["task_class"] for s in retired]},
                             indent=2))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

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


# Run 419 (arXiv:2609.05261, Trace2Tower). Flat class labels are the bottleneck that
# paper names; a skill memory should also carry an ABSTRACTION LEVEL and be
# CONDITIONED ON OUTCOME. This is the minimal two-axis form: map each task class to
# one of three levels, and let a caller stamp the outcome from the run record.
#   idiom      a reusable local move (a code pattern, a check, a fix shape)
#   procedure  a multi-step routine (fold->probe->fix; classify-before-generalise)
#   strategy   a run-selection principle (consolidate before a feature run; recency
#              weighting; the IDLE-STATE RULE)
SKILL_LEVEL = {
    "build": "idiom",
    "citation upgrade": "idiom",
    "project audit": "procedure",
    "literature sweep": "procedure",
    "consistency re-read": "procedure",
    "consolidation pass": "strategy",
    "loop policy edit": "strategy",
    "diversity hold": "strategy",
}
SKILL_OUTCOMES = ("landed", "held", "withdrawn", "unknown")


def level_of(cls):
    """Abstraction level for a task class; 'procedure' for anything unmapped."""
    return SKILL_LEVEL.get(cls, "procedure")


def skill_key(note_text, *, outcome="unknown"):
    """A two-axis skill key: '<level>/<class>@<outcome>'. `outcome` is stamped by the
    caller from the run record (ok + graph_delta -> landed; a later withdrawal ->
    withdrawn; held only after the holdout set has re-scored it)."""
    if outcome not in SKILL_OUTCOMES:
        raise ValueError(f"outcome must be one of {SKILL_OUTCOMES}")
    cls = classify(note_text)
    return f"{level_of(cls)}/{cls}@{outcome}"


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


def _wordset(s):
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower())}


def _jaccard(a, b):
    if not a and not b:
        return 0.0
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def consolidate(reg: Registry, min_overlap=0.35):
    """The CONSOLIDATION stage of the skill lifecycle (run 447, MASkills
    arXiv:2609.02094 - the fourth stage alongside induce / prune(retire) / refine).

    Find candidate skills that are NEAR-DUPLICATES: same abstraction level, AND a
    keyword vocabulary or procedure text that overlaps above `min_overlap` (Jaccard
    on word sets). REPORT them as merge candidates - never auto-merges: writes a
    `skill__consolidation_note` component (status candidate) and returns the
    proposals; a human merges or rejects (same discipline as no-auto-promotion).

    Returns a list of {keep, merge, overlap, basis, reason}.
    """
    skills = []
    for c in reg.list():
        if c["kind"] != "tool" or not c["name"].startswith("skill_"):
            continue
        if c["name"] in ("skill__consolidation_note",):
            continue
        try:
            s = json.loads(reg.get("tool", c["name"]))
        except Exception:
            continue
        if s.get("status") == "deprecated" or not s.get("task_class"):
            continue
        s["_kw"] = _wordset(" ".join(TASK_CLASSES.get(s["task_class"], [])))
        s["_proc"] = _wordset(s.get("procedure"))
        skills.append(s)

    proposals = []
    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            a, b = skills[i], skills[j]
            if a["task_class"] == b["task_class"]:
                continue                       # same class = same skill, not a merge
            if level_of(a["task_class"]) != level_of(b["task_class"]):
                continue
            kw_ov = _jaccard(a["_kw"], b["_kw"])
            proc_ov = _jaccard(a["_proc"], b["_proc"])
            ov = max(kw_ov, proc_ov)
            if ov < min_overlap:
                continue
            keep, merge = sorted(
                (a, b), key=lambda s: (-s.get("support", 0), s["task_class"]))
            proposals.append({
                "keep": keep["task_class"], "merge": merge["task_class"],
                "overlap": round(ov, 3),
                "basis": "keyword vocabulary" if kw_ov >= proc_ov else "procedure text",
                "reason": (f"same level ({level_of(keep['task_class'])}); "
                           f"{'keyword' if kw_ov >= proc_ov else 'procedure'} "
                           f"Jaccard {ov:.2f} >= {min_overlap}"),
            })
    proposals.sort(key=lambda p: -p["overlap"])
    if proposals:
        reg.set("tool", "skill__consolidation_note", json.dumps(
            {"status": "candidate", "kind": "consolidation_proposal",
             "proposals": proposals,
             "note": "near-duplicate candidate skills; a human merges or rejects. "
                     "NEVER auto-merged (no-auto-promotion discipline, same as induce)."},
            indent=2),
            note=f"consolidation: {len(proposals)} near-duplicate pair(s)", author="consolidate")
    return proposals


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

        # --- run 419: the two-axis skill key (Trace2Tower) ---
        checks["level_of maps a known class to its abstraction level"] = (
            level_of("build") == "idiom" and level_of("consolidation pass") == "strategy")
        checks["level_of defaults an unmapped class to 'procedure'"] = (
            level_of("brand new class") == "procedure")
        k1 = skill_key("built tools/relay.py, a selftest_all job", outcome="landed")
        checks["skill_key is <level>/<class>@<outcome>"] = (
            k1.count("/") == 1 and k1.endswith("@landed") and k1.startswith("idiom/"))
        try:
            skill_key("x", outcome="brilliant")
            _rej = False
        except ValueError:
            _rej = True
        checks["skill_key rejects an unknown outcome"] = _rej
        checks["a literature fold keys as a procedure"] = (
            skill_key("folded arXiv:1234.5678 literature sweep").startswith("procedure/"))

        # --- run 447: the CONSOLIDATION stage (MASkills, arXiv:2609.02094) ---
        _dupproc = ("narrow arxiv window verify each citation fold novel mechanisms "
                    "write sweep doc")
        reg.set("tool", "skill_dup_a", json.dumps(
            {"name": "dup_a", "task_class": "literature sweep", "status": "candidate",
             "support": 20, "procedure": _dupproc}, indent=2), author="selftest")
        reg.set("tool", "skill_dup_b", json.dumps(
            {"name": "dup_b", "task_class": "consistency re-read", "status": "candidate",
             "support": 5, "procedure": _dupproc}, indent=2), author="selftest")
        reg.set("tool", "skill_diff_level", json.dumps(
            {"name": "diff_level", "task_class": "citation upgrade", "status": "candidate",
             "support": 9, "procedure": _dupproc}, indent=2), author="selftest")
        props = consolidate(reg, min_overlap=0.5)
        pair = next((p for p in props
                     if {p["keep"], p["merge"]} == {"literature sweep", "consistency re-read"}),
                    None)
        checks["consolidate proposes merging two near-duplicate same-level skills"] = (
            pair is not None and pair["keep"] == "literature sweep"    # higher support kept
            and pair["overlap"] >= 0.5)
        checks["consolidate does NOT pair skills at different abstraction levels"] = (
            not any("citation upgrade" in (p["keep"], p["merge"]) for p in props))
        checks["consolidate writes a candidate consolidation_note, never auto-merges"] = (
            json.loads(reg.get("tool", "skill__consolidation_note"))["status"] == "candidate"
            and all(reg.get("tool", f"skill_{n}") for n in ("dup_a", "dup_b")))
        checks["consolidate is deterministic"] = (
            [(p["keep"], p["merge"]) for p in consolidate(reg, min_overlap=0.5)]
            == [(p["keep"], p["merge"]) for p in props])
        real_props = consolidate(reg)   # default threshold, real induced skills + fixtures
        checks["consolidate runs on the real induced skills without crashing"] = (
            isinstance(real_props, list))

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
            merges = consolidate(reg)
            print(json.dumps({"induced": cands,
                              "retired": [s["task_class"] for s in retired],
                              "consolidation_candidates": merges},
                             indent=2))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

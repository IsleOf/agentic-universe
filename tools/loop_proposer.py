#!/usr/bin/env python3
"""Phase 3 — the proposer, given real context.

`improvement_loop.propose()` is a deterministic obvious-fix stand-in.
`loop_metrics.propose_loop_edit()` turns one below-threshold metric into one
edit. This assembles the full context a proposer needs and generates edit
hypotheses across several dimensions, in the shape a model proposer would return
— so a model can be dropped in behind `PROPOSER_PROMPT` without changing the
verify/promote path.

`gather_context()` collects:
  - `loop_metrics.compute()` (verified-citation fraction, validation pass rate, ...)
  - task-class distribution from the experience bank (are we stuck in one mode?)
  - skill library state (induced / candidate / deprecated)
  - the current loop-harness components (from the registry)
  - the open question seeded by the most recent sweep doc

`heuristic_propose(context)` returns a list of `{component, change, prediction,
verification, dimension}`. Each `prediction` is falsifiable; each `verification`
says exactly how the edit would be checked (computable, or held-out + human re-run).

A model proposer receives `PROPOSER_PROMPT.format(context=json.dumps(context))`
and must return the same list shape. `model_propose(call_model, context)` is that
adapter: it parses the reply leniently, drops malformed proposals against the same
bar `heuristic_propose` meets, and returns `[]` on an unparseable reply (the loop
falls back to `heuristic_propose`). The verify/promote path is unchanged.

`PROPOSER_META` holds the improvement *procedure's* own knobs (which dimensions it
checks, the mode-concentration trigger, the proposal cap). Per
`concept_recursive_meta_skill_evolution`, a recursive loop would put PROPOSER_META
itself through `verify_loop_edit` on a slower cadence. It is fixed today; the dict
makes the fixity explicit and names the seam.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from harness_registry import Registry                      # noqa: E402
from loop_metrics import compute, THRESHOLDS               # noqa: E402
import skill_induction                                     # noqa: E402
import tempfile, shutil                                    # noqa: E402


PROPOSER_PROMPT = """\
You are the proposer in the Agentic Universe self-improving loop (Phase 3 of
docs/self_improving_harness_plan.md). You are given the current context of the
autonomous research loop as JSON. Propose 1-3 edits to the loop harness — its
`prompt` (procedure), `context` (policy), `tool`, or `topology` components — that
would measurably improve it.

Rules:
- Each proposal MUST name a specific component, a concrete change, and a
  FALSIFIABLE prediction (metric, direction, from-value, target).
- Each proposal MUST say how it would be verified: "computable" (a check that can
  run on the trace corpus) or "held-out + re-run" (promote manually, re-run the
  loop on tools/holdout_tasks.py, revert on any regression).
- Do NOT propose anything that cannot be checked. Do NOT propose vague
  "be more careful" edits.
- Respect the emergence-first posture: the interior is ungated; you are editing
  the harness, not adding process constraints to the research itself.

Return a JSON list of objects:
  {{"component": ["kind", "name"], "change": "...", "dimension": "...",
    "prediction": {{"metric": "...", "direction": "increase|decrease",
                    "from": <n>, "target": <n>, "rationale": "..."}},
    "verification": "computable: ..." | "held-out + re-run: ..."}}

Context:
{context}
"""


# --- the improvement PROCEDURE's own tunable knobs ---------------------------
# concept_recursive_meta_skill_evolution (MetaSkill-Evolve, arXiv:2607.05297) and
# docs/self_improvement_by_responsibility.md item 4: every published self-improving
# instance has a FIXED improvement procedure except MetaSkill-Evolve, and this
# proposer is fixed too. These are the knobs a slower "middle-loop's middle-loop"
# would evolve — surfaced here so the fixity is explicit and the seam is named.
# A recursive version would put PROPOSER_META itself through verify_loop_edit on a
# slower cadence (e.g. every N object-level accepts), with the same held-out gate.
PROPOSER_META = {
    "dimensions": ["research quality", "exploration / mode diversity", "harness economy", "safety"],
    "mode_concentration_trigger": 0.55,   # top task-class share that flags "stuck in one mode"
    "verification_default": "held-out + re-run",
    "max_proposals_per_run": 3,
    "cadence_hint": "object-level: every run; meta-level (this dict): not yet wired",
}


def gather_context():
    metrics = compute()

    tmp = Path(tempfile.mkdtemp(prefix="proposer-"))
    try:
        reg, bank, _ = skill_induction._build_corpus_bank(tmp)
        classes = Counter(
            skill_induction.classify(e["pattern"] + " " + e.get("note", ""))
            for e in bank._all("workflow")
        )
        induced = skill_induction.induce(reg, bank)
        retired = skill_induction.retire(reg, bank)
        components = {f"{c['kind']}/{c['name']}": c["version"] for c in reg.list()
                      if not c["name"].startswith("skill_")}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # open question from the most recent sweep doc
    sweeps = sorted((ROOT / "docs").glob("auto_sweep_*.md"))
    open_q = ""
    if sweeps:
        text = sweeps[-1].read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"##\s*Next run\s*\n(.+?)(?:\n#|\Z)", text, re.S)
        if m:
            open_q = " ".join(m.group(1).split())[:500]

    return {
        "metrics": metrics,
        "thresholds": THRESHOLDS,
        "task_class_distribution": dict(classes),
        "skills": {"induced": [s["name"] for s in induced],
                   "retired": [s["task_class"] for s in retired]},
        "loop_harness_components": components,
        "latest_open_question": open_q,
    }


def heuristic_propose(context):
    """A stronger-than-obvious-fix heuristic. Multi-dimension. Deterministic."""
    props = []
    m = context["metrics"]
    dist = context["task_class_distribution"]
    total = sum(dist.values()) or 1

    # 1. quality: verified-citation fraction
    vcf = m.get("verified_citation_fraction")
    if vcf is not None and vcf < THRESHOLDS["verified_citation_fraction"]:
        props.append({
            "component": ["context", "loop_policy"],
            "dimension": "research quality",
            "change": "add rule: 'at most ONE unverified citation per run; every other fold must cite an "
                      "arXiv page opened and checked this run'",
            "prediction": {"metric": "verified_citation_fraction", "direction": "increase",
                           "from": vcf, "target": THRESHOLDS["verified_citation_fraction"],
                           "rationale": "makes the existing 'verify three ways' rule enforceable per-run"},
            "verification": "held-out + re-run: promote, run the loop 10x, re-score holdout_tasks; "
                            "revert on any regression below the 1.00 baseline",
        })

    # 2. mode diversity: is the loop stuck in one task class?
    top_cls, top_n = max(dist.items(), key=lambda x: x[1]) if dist else (None, 0)
    if top_cls and top_n / total > PROPOSER_META["mode_concentration_trigger"]:
        props.append({
            "component": ["context", "loop_policy"],
            "dimension": "exploration / mode diversity",
            "change": f"add to read_first: 'if the last 8 runs were all {top_cls}, this run must be a "
                      f"different task class unless a validation failure forces otherwise'",
            "prediction": {"metric": f"fraction of runs in the dominant class ({top_cls})",
                           "direction": "decrease", "from": round(top_n / total, 2), "target": 0.5,
                           "rationale": "principle_diversity_maintenance at the run-type level; the "
                                        "withheld-fraction handles skills, this handles run modes"},
            "verification": "computable: classify the next 12 runs; check dominant-class fraction fell",
        })

    # 3. procedure prompt bloat
    proc_v = context["loop_harness_components"].get("prompt/loop_procedure", 0)
    if proc_v >= 3:
        props.append({
            "component": ["prompt", "loop_procedure"],
            "dimension": "harness economy",
            "change": "factor the RECORD THE RUN + VALIDATE + COMMIT boilerplate into a single "
                      "'python tools/loop_finish.py' the run calls, leaving the procedure prompt to the "
                      "research judgement only",
            "prediction": {"metric": "mean_events_per_run stability + procedure prompt length",
                           "direction": "decrease", "from": proc_v, "target": proc_v,
                           "rationale": "concept_reused_input_dominates: the boilerplate is re-sent every run; "
                                        "a script call is not"},
            "verification": "computable: token count of the procedure component before/after; "
                            "held-out re-run confirms research quality unchanged",
        })

    # 4. validation discipline (should already be perfect)
    vpr = m.get("validation_pass_rate")
    if vpr is not None and vpr < 1.0:
        props.append({
            "component": ["prompt", "loop_procedure"],
            "dimension": "safety",
            "change": "the exec_guard pre-commit hook already enforces this; add a line telling the run the "
                      "hook exists so it validates before staging, not after",
            "prediction": {"metric": "validation_pass_rate", "direction": "increase",
                           "from": vpr, "target": 1.0, "rationale": "the hook blocks bad commits; this just "
                           "saves a wasted staging cycle"},
            "verification": "computable: count post-edit invalid-commit attempts (should be 0)",
        })

    return props


def _valid_proposal(p):
    """A proposal is usable iff it names a 2-part component, carries a falsifiable
    prediction, and says how it is verified — the same bar heuristic_propose meets
    and improvement_loop.verify_loop_edit assumes."""
    try:
        return (isinstance(p, dict)
                and isinstance(p.get("component"), list) and len(p["component"]) == 2
                and isinstance(p.get("change"), str) and p["change"].strip()
                and isinstance(p.get("prediction"), dict)
                and {"metric", "direction", "from", "target"} <= set(p["prediction"])
                and isinstance(p.get("verification"), str)
                and p["verification"].startswith(("computable", "held-out")))
    except Exception:
        return False


def model_propose(call_model, context):
    """Adapt a real model into the proposer. `call_model(prompt: str) -> str` is
    the only seam: it is handed `PROPOSER_PROMPT.format(context=...)` and expected
    to return a JSON list of proposal objects. The reply is parsed leniently (the
    first `[` to the last `]`); malformed proposals are dropped, and an
    unparseable reply yields `[]` — the loop then falls back to
    `heuristic_propose`. Nothing downstream changes: the verify path
    (`improvement_loop.verify_loop_edit`) is identical for heuristic and model
    proposals.
    """
    prompt = PROPOSER_PROMPT.format(context=json.dumps(context, default=str))
    try:
        reply = call_model(prompt) or ""
    except Exception:
        return []
    i, j = reply.find("["), reply.rfind("]")
    if i < 0 or j <= i:
        return []
    try:
        raw = json.loads(reply[i:j + 1])
    except Exception:
        return []
    return [p for p in raw if _valid_proposal(p)] if isinstance(raw, list) else []


def _selftest():
    ctx = gather_context()
    props = heuristic_propose(ctx)

    checks = {
        "context has metrics": "verified_citation_fraction" in ctx["metrics"],
        "context has task-class distribution": len(ctx["task_class_distribution"]) >= 1,
        "context has skill state": "induced" in ctx["skills"],
        "context has loop-harness components": len(ctx["loop_harness_components"]) >= 3,
        "proposer returns a list": isinstance(props, list),
        "every proposal names a component": all(len(p["component"]) == 2 for p in props),
        "every proposal has a falsifiable prediction": all(
            {"metric", "direction", "from", "target"} <= set(p["prediction"]) for p in props),
        "every proposal says how it is verified": all(
            p["verification"].startswith(("computable", "held-out")) for p in props),
        "PROPOSER_PROMPT formats with the context": bool(
            PROPOSER_PROMPT.format(context=json.dumps(ctx))),
        "PROPOSER_META.mode_concentration_trigger is a fraction and load-bearing":
            0 < PROPOSER_META["mode_concentration_trigger"] < 1,
    }
    # PROPOSER_META.dimensions must cover every dimension heuristic_propose can emit
    _emit_dims = set()
    for _p in (heuristic_propose({**ctx,
                                  "metrics": {**ctx["metrics"], "verified_citation_fraction": 0.0,
                                              "validation_pass_rate": 0.5},
                                  "task_class_distribution": {"x": 9, "y": 1}}) or []):
        _emit_dims.add(_p["dimension"])
    checks["PROPOSER_META.dimensions covers what heuristic_propose emits"] = (
        _emit_dims and _emit_dims <= set(PROPOSER_META["dimensions"]))

    # model_propose adapter
    good = {"component": ["context", "loop_policy"], "change": "add X to the rules list",
            "dimension": "quality",
            "prediction": {"metric": "verified_citation_fraction", "direction": "increase",
                           "from": 0.3, "target": 0.6, "rationale": "..."},
            "verification": "computable: replay the corpus"}
    bad = {"component": ["context"], "change": "be better"}  # malformed
    mp_ok = model_propose(lambda p: "Here you go:\n" + json.dumps([good, bad]) + "\nDone.", ctx)
    mp_prose = model_propose(lambda p: "I think the loop is fine, no changes needed.", ctx)
    mp_boom = model_propose(lambda p: (_ for _ in ()).throw(RuntimeError("x")), ctx)
    checks["model_propose keeps valid proposals, drops malformed"] = (
        len(mp_ok) == 1 and mp_ok[0]["component"] == ["context", "loop_policy"])
    checks["model_propose prose reply -> [] (falls back to heuristic)"] = mp_prose == []
    checks["model_propose model exception -> []"] = mp_boom == []
    checks["model_propose output passes the same bar as heuristic_propose"] = all(
        _valid_proposal(p) for p in mp_ok)
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  context keys: {list(ctx)}")
    print(f"  {len(props)} proposal(s):")
    for p in props:
        print(f"    - [{p['dimension']}] {p['component']}: {p['change'][:80]}")
    ok = all(checks.values())
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Phase 3 proposer with real context.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("context")
    sub.add_parser("propose")
    sub.add_parser("prompt")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "context":
        print(json.dumps(gather_context(), indent=2, default=str))
        return 0
    if args.cmd == "propose":
        print(json.dumps(heuristic_propose(gather_context()), indent=2))
        return 0
    if args.cmd == "prompt":
        print(PROPOSER_PROMPT.format(context=json.dumps(gather_context(), indent=2, default=str)))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

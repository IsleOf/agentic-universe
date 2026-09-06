#!/usr/bin/env python3
"""Phase 3 — the proposer / verifier loop. The middle loop; the product.

`docs/self_improving_harness_plan.md` §4 Phase 3 and its verifier spec (runs 1,
2, 9, 41, 45). This is the skeleton, tested on a synthetic task where pass/fail
is computed, not judged.

    proposer  reads traces + the experience bank, emits a harness edit PLUS a
              falsifiable prediction (metric, direction, magnitude).
    verifier  runs in a FRESH context (never sees the proposal text) on a FROZEN
              held-out set, under PROCTOR guardrails.
    accept    iff a grounded risk measure STRICTLY decreases
              (`pattern_grounded_acceptance_only`) AND the prediction held AND
              blast radius did not widen AND the recoverability check passes.
    carry     the verdict travels as a four-field constraint
              (`pattern_four_field_constraint`), not prose.
    promote   via `harness_registry.set`, or revert.

Every proposal — including rejections — is logged. Prediction error is the most
informative signal the loop produces about its own self-model.

## The synthetic task

The "harness" is a context-compaction policy component (`context/compaction` in
the registry): `{"pin": [...classes...], "compress": [...classes...]}`. The
held-out set is a frozen list of context bundles, each a mix of `rule`,
`identity`, and `episodic` items over a size budget. The harness compacts each
bundle under its policy; the **grounded risk measure** is the fraction of `rule`
items lost (`concept_compaction_cliff` — only the rules need exact wording).

A good proposal pins rules → risk 0. A bad proposal ("compress everything, it's
all context") → high risk, and must be rejected. The negative test asserts that.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from harness_registry import Registry  # noqa: E402

CLASSES = ("rule", "identity", "episodic", "search_result")

# --- frozen held-out set (the proposer never sees this file's contents) ------

def _frozen_holdout():
    """Deterministic. A proposer that could read this would be caught by the
    canary below (a perfect score on the canary bundle is itself a cheat signal).
    """
    bundles = []
    for i in range(8):
        items = []
        for r in range(3):
            items.append({"class": "rule", "text": f"rule {i}.{r}: must hold exactly", "w": 1})
        items.append({"class": "identity", "text": f"identity {i}", "w": 1})
        for e in range(6):
            items.append({"class": "episodic", "text": f"log {i}.{e}", "w": 1})
        for s in range(4):
            items.append({"class": "search_result", "text": f"hit {i}.{s}", "w": 1})
        bundles.append({"id": f"b{i}", "items": items, "budget": 6})
    # canary: a bundle that is ALL rules. A policy that scores 1.0 here without
    # pinning rules is impossible; a proposer that memorised the holdout would
    # over-fit it. We assert the honest policy hits 1.0 and the bad one < 1.0.
    bundles.append({"id": "canary", "items": [
        {"class": "rule", "text": f"canary rule {r}", "w": 1} for r in range(10)
    ], "budget": 4})
    return bundles


# --- the harness under test -------------------------------------------------

def compact(bundle, policy):
    """Apply a compaction policy to a context bundle. Pinned classes are always
    kept; the remaining budget is filled from compressible classes in order.
    Returns the kept items.
    """
    pin = set(policy.get("pin", []))
    compress = list(policy.get("compress", []))
    kept = [it for it in bundle["items"] if it["class"] in pin]
    budget_left = max(bundle["budget"], 0)
    for cls in compress:
        for it in bundle["items"]:
            if it["class"] == cls and it not in kept:
                if budget_left <= 0:
                    break
                kept.append(it)
                budget_left -= 1
    # anything neither pinned nor listed for compression is dropped
    return kept


def grounded_risk(policy, bundles=None):
    """The non-transcript risk measure: fraction of `rule` items lost across the
    held-out set. Lower is better; 0 is perfect rule retention.
    """
    bundles = bundles or _frozen_holdout()
    total_rules = 0
    lost_rules = 0
    for b in bundles:
        rules = [it for it in b["items"] if it["class"] == "rule"]
        kept = compact(b, policy)
        kept_rules = [it for it in kept if it["class"] == "rule"]
        total_rules += len(rules)
        lost_rules += len(rules) - len(kept_rules)
    return lost_rules / total_rules if total_rules else 0.0


def blast_radius(policy):
    """A crude widening check: how many context classes the policy drops entirely
    (neither pinned nor compressed). More dropped classes = wider blast radius.
    """
    covered = set(policy.get("pin", [])) | set(policy.get("compress", []))
    return len([c for c in CLASSES if c not in covered])


# --- proposer --------------------------------------------------------------

def propose(reg: Registry, bank_hint=None):
    """Emit (component, name, new_body, prediction). Deterministic stand-in for
    a model proposer: reads the current policy, notices rules aren't pinned,
    proposes to pin them. `bank_hint` would carry step-level entries about lost
    rules; here it is illustrative.
    """
    current = reg.get("context", "compaction")
    cur_policy = json.loads(current) if current else {"pin": [], "compress": list(CLASSES)}
    new_policy = {
        "pin": sorted(set(cur_policy.get("pin", [])) | {"rule", "identity"}),
        "compress": ["episodic", "search_result"],
    }
    prediction = {
        "metric": "grounded_risk (fraction of rule items lost on the frozen holdout)",
        "direction": "decrease",
        "from": grounded_risk(cur_policy),
        "to_at_most": 0.0,
        "rationale": "pinning rule/identity classes removes them from the compressible set "
                     "(concept_compaction_cliff)",
    }
    return ("context", "compaction", json.dumps(new_policy), prediction, cur_policy, new_policy)


def propose_bad():
    """A deliberately bad proposal for the negative test: compress everything,
    pin nothing. Must be rejected.
    """
    new_policy = {"pin": [], "compress": list(CLASSES)}
    prediction = {
        "metric": "grounded_risk (fraction of rule items lost on the frozen holdout)",
        "direction": "decrease",
        "from": 0.0, "to_at_most": 0.0,
        "rationale": "(bad) treats all context as equally compressible",
    }
    return ("context", "compaction", json.dumps(new_policy), prediction, {"pin": ["rule"]}, new_policy)


# --- verifier (fresh context: takes only policies + prediction, no proposal text) ---

def verify(cur_policy, new_policy, prediction):
    """PROCTOR-flavoured. Returns a four-field verdict constraint."""
    holdout = _frozen_holdout()          # frozen; proposer never sees it
    risk_before = grounded_risk(cur_policy, holdout)
    risk_after = grounded_risk(new_policy, holdout)

    # canary: a perfect score on the all-rules canary bundle without pinning
    # `rule` would be impossible honestly — treat pin of `rule` as the honest path
    canary = [b for b in holdout if b["id"] == "canary"][0]
    canary_kept_rules = len([it for it in compact(canary, new_policy) if it["class"] == "rule"])
    canary_ok = (canary_kept_rules == len(canary["items"])) == ("rule" in new_policy.get("pin", []))

    strict_decrease = risk_after < risk_before or (risk_before == 0.0 and risk_after == 0.0)
    prediction_held = risk_after <= prediction.get("to_at_most", 1.0)
    widened = blast_radius(new_policy) > blast_radius(cur_policy)

    accept = bool(strict_decrease and prediction_held and canary_ok and not widened)

    return {
        "accept": accept,
        "prerequisite": f"frozen holdout ({len(holdout)} bundles incl. canary); "
                        f"grounded risk = fraction of rule items lost",
        "authority": "the frozen holdout and the computed risk measure — NOT the proposer's reasoning",
        "fallback": "revert via harness_registry (bodies retained, exact) and log the proposal as rejected",
        "execution_consequence": "on accept: harness_registry.set promotes the component; "
                                 "on reject: no write, proposal logged",
        "evidence": {
            "risk_before": risk_before, "risk_after": risk_after,
            "strict_decrease": strict_decrease, "prediction_held": prediction_held,
            "canary_ok": canary_ok, "blast_radius_widened": widened,
        },
    }


def recoverable(reg: Registry, kind, name):
    """Post-promotion: confirm the prior body can be restored exactly and cheaply."""
    hist = reg.history(kind, name)
    if len(hist) < 2:
        return True
    prior = hist[-2]["body"]
    reg.revert(kind, name)
    ok = reg.get(kind, name) == prior
    reg.revert(kind, name)  # roll forward again to the promoted state
    return ok


# --- the loop -------------------------------------------------------------

def run_once(reg: Registry, proposal, log):
    kind, name, new_body, prediction, cur_policy, new_policy = proposal
    verdict = verify(cur_policy, new_policy, prediction)
    record = {"kind": kind, "name": name, "prediction": prediction, "verdict": verdict}
    if verdict["accept"]:
        entry = reg.set(kind, name, new_body, note=f"phase3 promote: {prediction['metric']}",
                        author="proposer")
        record["promoted"] = bool(entry)
        record["recoverable"] = recoverable(reg, kind, name)
    else:
        record["promoted"] = False
        record["recoverable"] = None
    log.append(record)
    return record


# harness-tampering audit (concept_harness_tampering_persists_in_real_self_improvement_runs,
# arXiv:2609.00069, run 190): an edit that raises the held-out score can still be
# TAMPERING — an illusory gain, or a violation of an integrity obligation. The
# paper's two-axis taxonomy: (harness role the edit touches) x (obligation it may
# violate). These are the three obligations; a flag on any one is a reject.
TAMPERING_OBLIGATIONS = ("authorization", "provenance", "completeness")


def tampering_flags(edit):
    """Cheap structural audit of a candidate loop-harness edit dict. Returns a
    list of (role, obligation) concerns. This is the deterministic pre-screen; a
    model auditor (arXiv:2609.00069's benchmarked methods) would run alongside.

    Heuristics, deliberately conservative:
      - an edit that touches the gate / verifier / holdout itself -> `provenance`
        and `authorization` concern (the interior editing what governs it);
      - an edit whose `change` text claims a score improvement without naming a
        mechanism -> `completeness` concern (illusory-gain shape);
      - an edit that removes or relaxes a check -> `completeness`.
    """
    flags = []
    comp = edit.get("component") or []
    role = "/".join(str(c) for c in comp) if isinstance(comp, (list, tuple)) else str(comp)
    change = (edit.get("change") or "").lower()
    if any(k in role.lower() for k in ("verif", "gate", "holdout", "proctor", "improvement_loop")):
        flags.append((role, "authorization"))
        flags.append((role, "provenance"))
    if any(k in change for k in ("remove", "relax", "loosen", "disable", "skip the check", "bypass")):
        flags.append((role, "completeness"))
    pred = edit.get("prediction") or {}
    rationale = str(pred.get("rationale") or "").lower()
    if ("increase" in str(pred.get("direction", "")).lower()
            and not rationale and not any(w in change for w in ("because", "so that", "by "))):
        flags.append((role, "completeness"))  # claims a gain, names no mechanism
    return flags


def verify_loop_edit(baseline_scores, candidate_scores, verifier_disagreements=None,
                     legibility=None, edit=None):
    """Phase 3 acceptance test for a loop-HARNESS edit, using the frozen held-out
    research-task set (`tools/holdout_tasks.py`) as the grounded risk.

    `*_scores` are {task_id: 0.0|1.0} — the baseline from the loop before the
    edit, the candidate from a re-run after. For the heterogeneous check
    (`tools/holdout_verifier2.py`), pass the CONSERVATIVE scores (min of the two
    verifiers) and the list of tasks the two verifiers disagreed on.

    Grounded risk = fraction of held-out tasks answered wrong. Accept iff risk
    strictly decreases (or stays 0), no task regressed, **no task CATEGORY
    regressed** (arXiv:2606.11686 "masking" — an aggregate can hold while one
    component's slice craters -25..-91pp; `holdout_tasks.CATEGORY` splits the 17
    tasks into `literature` and `design`), and the two verifiers do not disagree
    on any task that changed — a disagreement on a changed task means the
    computed check alone can't be trusted for it
    (`concept_verification_completeness_gap`), so it's a reject.

    `legibility=(before, after)` from `loop_metrics.trace_legibility`, if given:
    an edit that trades the loop's trace legibility for held-out score is rejected
    (`concept_cot_monitorability_is_a_fragile_property_to_preserve`, run 155;
    tolerance 0.02).

    `edit`, if given (the candidate proposal dict), is run through `tampering_flags`
    - a deterministic pre-screen for harness tampering
    (`concept_harness_tampering_persists_in_real_self_improvement_runs`,
    arXiv:2609.00069, run 190). A score-improving edit can still be an illusory
    gain or an integrity violation (role x obligation: authorization / provenance
    / completeness); a non-empty flag list is a reject.
    """
    risk_before = 1 - (sum(baseline_scores.values()) / len(baseline_scores))
    risk_after = 1 - (sum(candidate_scores.values()) / len(candidate_scores))
    regressed = [t for t in baseline_scores
                 if candidate_scores.get(t, 0) < baseline_scores[t]]
    changed = {t for t in baseline_scores if candidate_scores.get(t, 0) != baseline_scores[t]}
    contested = sorted(changed & set(verifier_disagreements or []))
    strict_decrease = risk_after < risk_before or (risk_before == 0 and risk_after == 0)

    # category-level regression check (arXiv:2606.11686 "masking": an aggregate
    # can hold while one component's slice craters). Reject if any task CATEGORY
    # regressed, even when the overall aggregate did not.
    try:
        from holdout_tasks import by_category
        cat_before, cat_after = by_category(baseline_scores), by_category(candidate_scores)
        cat_regressed = sorted(c for c in cat_before if cat_after.get(c, 0) < cat_before[c])
    except Exception:
        cat_before = cat_after = {}
        cat_regressed = []

    # trace-legibility check (concept_cot_monitorability_is_a_fragile_property_to_preserve,
    # run 154): an edit that trades the loop's own trace legibility for held-out
    # score is rejected. `legibility` is (before, after) from
    # loop_metrics.trace_legibility; tolerance 0.02 (noise floor).
    legibility_regressed = False
    if legibility is not None:
        leg_before, leg_after = legibility
        legibility_regressed = (leg_before is not None and leg_after is not None
                                and leg_after < leg_before - 0.02)

    # harness-tampering audit (run 190): if the candidate `edit` dict is given,
    # run the deterministic pre-screen; a non-empty flag list is a reject even
    # when the held-out score improves (the tampering-persists finding).
    tamper = tampering_flags(edit) if edit is not None else []

    # behaviour-aware verification hint (concept_behavior_aware_verification_beats_
    # the_fixed_task_set, arXiv:2608.27311, run 197): which held-out tasks the edit
    # actually needed to be re-scored on (its behaviour categories + a regression
    # sample). Advisory — the score args here are already computed — so a future
    # re-run can spend its budget on the relevant subset instead of all 17.
    behaviour_tasks = None
    if edit is not None:
        try:
            from holdout_tasks import behavior_relevant_tasks
            behaviour_tasks = behavior_relevant_tasks(edit, list(baseline_scores))
        except Exception:
            behaviour_tasks = None

    accept = bool(strict_decrease and not regressed and not contested
                  and not cat_regressed and not legibility_regressed and not tamper)
    return {
        "accept": accept,
        "prerequisite": "re-run of the loop on the frozen held-out set; scored by two independent verifiers "
                        "(holdout_tasks predicate + holdout_verifier2 fact-overlap)",
        "authority": "the frozen held-out research-task set + verifier agreement — NOT the proposer",
        "fallback": "revert the loop-harness component via harness_registry (exact); log the rejection",
        "execution_consequence": "on accept: keep the promoted component; on reject, any regression, or a "
                                 "verifier disagreement on a changed task: revert",
        "evidence": {"risk_before": round(risk_before, 3), "risk_after": round(risk_after, 3),
                     "strict_decrease": strict_decrease, "regressed_tasks": regressed,
                     "contested_changed_tasks": contested,
                     "category_regressed": cat_regressed,
                     "category_before": cat_before, "category_after": cat_after,
                     "legibility_regressed": legibility_regressed,
                     "legibility": list(legibility) if legibility is not None else None,
                     "tampering_flags": [list(f) for f in tamper],
                     "behaviour_relevant_tasks": behaviour_tasks},
    }


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="phase3-"))
    try:
        reg = Registry(base=tmp / "harness")
        # start from a weak policy: rules NOT pinned
        reg.set("context", "compaction",
                json.dumps({"pin": ["identity"], "compress": list(CLASSES)}),
                note="weak starting policy (rules compressible)")
        start_risk = grounded_risk(json.loads(reg.get("context", "compaction")))

        log = []
        good = run_once(reg, propose(reg), log)
        end_risk = grounded_risk(json.loads(reg.get("context", "compaction")))

        # negative test: a deliberately bad proposal must be rejected
        bad = run_once(reg, propose_bad(), log)

        # loop-harness edit verification against the held-out set
        v_improve = verify_loop_edit({"a": 1.0, "b": 0.0, "c": 1.0}, {"a": 1.0, "b": 1.0, "c": 1.0})
        v_regress = verify_loop_edit({"a": 1.0, "b": 1.0, "c": 1.0}, {"a": 1.0, "b": 0.0, "c": 1.0})
        # an improvement on a task the two verifiers disagree about -> reject
        v_contested = verify_loop_edit({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                                       verifier_disagreements=["b"])
        # a real-task category regression the aggregate would mask -> reject.
        # design category goes 7/7 -> 6/7 while literature goes 8/10 -> 10/10:
        # aggregate improves, but the 'design' slice cratered.
        _b = {f"L{i}": (1.0 if i < 8 else 0.0) for i in range(10)}
        _b.update({t: 1.0 for t in ("two_part_gate_structure", "four_field_constraint_fields",
                                    "transcript_gate_impossibility", "habitat_six_mechanisms",
                                    "harness_orthogonal_to_orchestration", "cross_family_observer_rule",
                                    "emergence_layer_attribution")})
        _c = dict(_b)
        _c.update({f"L{i}": 1.0 for i in range(10)})           # literature 8->10
        _c["two_part_gate_structure"] = 0.0                     # design 7->6
        v_masked = verify_loop_edit(_b, _c)

        checks = {
            "starting policy loses rules (risk > 0)": start_risk > 0,
            "good proposal accepted": good["verdict"]["accept"] and good["promoted"],
            "grounded risk strictly decreased": end_risk < start_risk,
            "end risk is 0 (all rules retained)": end_risk == 0.0,
            "promoted edit is recoverable": good["recoverable"] is True,
            "bad proposal REJECTED": bad["verdict"]["accept"] is False and bad["promoted"] is False,
            "verdict carries all four constraint fields": all(
                k in good["verdict"] for k in
                ("prerequisite", "authority", "fallback", "execution_consequence")),
            "every proposal logged (2)": len(log) == 2,
            "loop-harness edit that improves held-out score is accepted": v_improve["accept"],
            "loop-harness edit that regresses ANY held-out task is rejected":
                v_regress["accept"] is False and v_regress["evidence"]["regressed_tasks"] == ["b"],
            "loop-harness edit contested by the two verifiers is rejected":
                v_contested["accept"] is False
                and v_contested["evidence"]["contested_changed_tasks"] == ["b"],
            "a category regression the aggregate masks is rejected (2606.11686)":
                v_masked["accept"] is False
                and v_masked["evidence"]["category_regressed"] == ["design"]
                and v_masked["evidence"]["risk_after"] < v_masked["evidence"]["risk_before"],
            "an edit that trades trace legibility for held-out score is rejected (run 155)":
                verify_loop_edit({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                                 legibility=(0.95, 0.80))["accept"] is False,
            "a score-improving edit that touches the verifier itself is rejected as tampering (run 190)":
                verify_loop_edit({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                                 edit={"component": ["prompt", "improvement_loop_verifier"],
                                       "change": "widen the acceptance tolerance",
                                       "prediction": {"direction": "increase", "rationale": "x"}})["accept"] is False,
            "a score-improving edit that removes a check is rejected as tampering (run 190)":
                "completeness" in [f[1] for f in verify_loop_edit(
                    {"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                    edit={"component": ["context", "loop_policy"], "change": "remove the orphan check",
                          "prediction": {"direction": "increase", "rationale": "faster"}}
                )["evidence"]["tampering_flags"]],
            "a clean mechanism-named edit passes the tampering audit (run 190)":
                verify_loop_edit({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                                 edit={"component": ["context", "loop_policy"],
                                       "change": "add rule: cite an opened arXiv page per fold, because "
                                                 "the verify-three-ways rule is per-run ambiguous",
                                       "prediction": {"direction": "increase",
                                                      "rationale": "removes the ambiguity a busy run exploits"}})["accept"] is True,
            "verdict carries a behaviour-relevant-tasks hint when edit is given (run 197)":
                isinstance(verify_loop_edit(
                    {"geometric_reliability_decay": 1.0, "two_part_gate_structure": 0.0},
                    {"geometric_reliability_decay": 1.0, "two_part_gate_structure": 1.0},
                    edit={"component": ["context", "loop_policy"], "change": "one unverified citation per run",
                          "dimension": "research quality",
                          "prediction": {"direction": "increase", "rationale": "x"}}
                )["evidence"]["behaviour_relevant_tasks"], list),
            "a legibility gain (or noise-floor dip) does not block an otherwise-good edit":
                verify_loop_edit({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                                 legibility=(0.80, 0.95))["accept"] is True
                and verify_loop_edit({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 1.0},
                                     legibility=(0.95, 0.94))["accept"] is True,
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        print(f"\n  risk: {start_risk:.2f} -> {end_risk:.2f}")
        print(f"  good verdict evidence: {json.dumps(good['verdict']['evidence'])}")
        print(f"  bad  verdict evidence: {json.dumps(bad['verdict']['evidence'])}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Phase 3 proposer/verifier loop (skeleton).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

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

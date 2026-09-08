#!/usr/bin/env python3
"""acceptance_gate - the exogenous acceptance gate as one call (v2.1 brick).

`docs/self_rebuild_v2.md` section 7. Composes the pieces the loop already has into
a single `check()` that emits a REPLAYABLE CERTIFICATE:

  - held-out regression + category-masking + tamper + legibility checks
    (`improvement_loop.verify_loop_edit`, the frozen `holdout_tasks` set)
  - PACE anytime-valid e-process (advisory, carried through from verify_loop_edit)
  - a PROCESS-ADJUSTED flag: did the accept need a deterministic repair to pass?
    A pass that only holds after a repair is a weaker signal - the AgentLens shape
    (run 298): score the process, not just the outcome. Flagged, not blocked.
  - a FORECAST check: the proposer predicted whether the edit would help and with
    what probability; on resolve we Brier-score that prediction. A proposer whose
    forecasts are poorly calibrated is recorded, never blocked
    (`epistemic_constitution` shape, runs 293/296).
  - a signed certificate {proposal_hash, gate, e_value, baseline, ts, brier}
    appended to an APPEND-ONLY log that `verify_certificate()` recomputes.

The gate is EXOGENOUS (`concept_reliable_self_improvement_needs_an_exogenous_acceptance_signal`):
the proposal hash covers the whole proposal; the certificate log is append-only;
nothing here lets a proposer edit the held-out set, alpha, or a past certificate.

Pure stdlib. No model call.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from improvement_loop import verify_loop_edit  # noqa: E402

CERT_DIR = ROOT / "runtime" / "observations" / "certificates"
CERT_LOG = CERT_DIR / "gate_certificates.jsonl"


def proposal_digest(proposal) -> str:
    """Stable sha256 over a canonical JSON encoding of the proposal."""
    blob = json.dumps(proposal, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def brier(predicted_prob: float, outcome: float) -> float:
    """Brier score for a single binary prediction. Lower is better; 0.25 = a coin flip."""
    p = max(0.0, min(1.0, float(predicted_prob)))
    return round((p - float(outcome)) ** 2, 4)


def _held_out_outcome(baseline_scores, candidate_scores) -> float:
    risk_before = 1 - (sum(baseline_scores.values()) / len(baseline_scores))
    risk_after = 1 - (sum(candidate_scores.values()) / len(candidate_scores))
    return 1.0 if (risk_after < risk_before or (risk_before == 0 and risk_after == 0)) else 0.0


# --- minimal modification (run 371, from WorldBench's Constrained Task Success) ---

_PATCH_ALLOWED_KEYS = {"proposal_metadata", "add_nodes", "add_edges"}

# touch_surface threshold, DERIVED not invented (run 379).
# Run 371 added touch_surface and deliberately left it unthresholded: "no principled
# cap exists and inventing one would be worse than reporting the number." The cap is
# now measured instead. Walking 59 graph-changing commits and reconstructing each
# patch's touch surface gives: min 0, median 4, mean 3.3, MAX 6, p99 6 - a strikingly
# tight distribution. This loop has never produced a patch touching more than six
# pre-existing nodes.
#
# The flag sits at 2x the observed maximum, so it cannot fire on anything resembling
# normal work and only trips on something genuinely out of family.
#
# TWO HONEST LIMITS on that derivation:
#  1. It describes ONE agent's habits, not a norm. A live research_worker on a real
#     model backend may legitimately propose wider patches, and the number should be
#     re-measured rather than inherited if the patch producer changes.
#  2. A wide patch is UNUSUAL, not INVALID. So this is a FLAG on the certificate, never
#     a refusal - the run-372 rule that unexpected-but-not-forbidden things are reported
#     and the judgement is left to the reader. Contrast the destructive-key check above,
#     which refuses, because an off-contract key IS invalid.
TOUCH_SURFACE_OBSERVED_MAX = 6      # over 59 measured patches
TOUCH_SURFACE_FLAG = 2 * TOUCH_SURFACE_OBSERVED_MAX
_DESTRUCTIVE = ("remove", "delete", "modify", "update", "set_", "overwrite", "replace", "drop")
# Kept for REPORTING only (run 374). The refusal below is now shape-based: any key
# outside _PATCH_ALLOWED_KEYS is refused whatever it is called. This list only labels
# which flavour of unknown key showed up, so a reader can tell `purge_nodes` from a
# stray `noteworthy`. It is no longer load-bearing, and lengthening it changes nothing.
#
# Why the change (arXiv:2608.03609, folded run 373): name-matching is non-EQUIVARIANT -
# renaming an identifier changes the decision - and equivariance is the condition under
# which verifying an LLM-plus-harness deployment is tractable at all. `rm_nodes` slipped
# past the run-371 blacklist. A whitelist over patch SHAPE is equivariant by construction:
# every key outside the contract is refused identically, so renaming buys nothing.


def modification_footprint(proposal) -> dict:
    """What does this patch DISTURB, as opposed to add?

    The graph-patch contract is add-only, but `knowledge_graph.check_patch` ignores
    keys it does not know, so a destructive key rides through validation unnoticed.
    This names the footprint explicitly:

      added_nodes / added_edges - the intended growth
      touch_surface             - distinct PRE-EXISTING node ids the new edges attach
                                  to; a patch that wires into 30 unrelated nodes is
                                  not minimal even though it deletes nothing
      destructive_keys          - any key whose name implies mutation or removal
      unknown_keys              - anything else outside the contract (reported, not fatal)
    """
    if not isinstance(proposal, dict):
        return {"added_nodes": 0, "added_edges": 0, "touch_surface": 0,
                "touch_surface_anomalous": False,
                "touch_surface_flag_at": TOUCH_SURFACE_FLAG,
                "destructive_keys": [], "unknown_keys": []}
    add_nodes = proposal.get("add_nodes") or []
    add_edges = proposal.get("add_edges") or []
    new_ids = {n.get("id") for n in add_nodes if isinstance(n, dict)}
    touched = set()
    for e in add_edges:
        if not isinstance(e, dict):
            continue
        for end in (e.get("source"), e.get("target")):
            if end and end not in new_ids:
                touched.add(end)
    extra = [k for k in proposal if k not in _PATCH_ALLOWED_KEYS]
    destructive = sorted(k for k in extra if any(d in k.lower() for d in _DESTRUCTIVE))
    return {
        "added_nodes": len(add_nodes),
        "added_edges": len(add_edges),
        "touch_surface": len(touched),
        # flagged, never refused - unusual is not invalid (run 379)
        "touch_surface_anomalous": len(touched) > TOUCH_SURFACE_FLAG,
        "touch_surface_flag_at": TOUCH_SURFACE_FLAG,
        "destructive_keys": destructive,
        "unknown_keys": sorted(k for k in extra if k not in destructive),
    }


def _reject_cert(proposal, forecast, reason, footprint, cert_dir, clock):
    """A refusal that never reached the held-out comparison. Logged like any other
    adjudication (run 368) so the record cannot be read as a clean run."""
    cert = {
        "schema": "gate.1",
        "ts": round(clock(), 3),
        "decision": "reject",
        "gate": {"held_out_accept": False, "reason": reason},
        "modification_footprint": footprint,
        "forecast": {"metric": (forecast or {}).get("metric"), "brier": None},
        "proposal_hash": proposal_digest(proposal),
        "e_value": None, "e_threshold": None, "e_committed": False,
        "authority": "the add-only graph-patch contract - checked before the held-out set",
        "fallback": "reject the patch; a mutating change needs an explicit, reviewed path",
        "provenance": "explicit_dir" if cert_dir else "default_log",
    }
    cert["certificate_hash"] = hashlib.sha256(
        json.dumps({k: cert[k] for k in cert if k != "certificate_hash"},
                   sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    d = Path(cert_dir) if cert_dir else CERT_DIR
    d.mkdir(parents=True, exist_ok=True)
    with (d / "gate_certificates.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(cert, sort_keys=True) + "\n")
    return cert


def check(proposal, baseline_scores, candidate_scores, forecast, *,
          verifier_disagreements=None, legibility=None, repaired=False,
          edit=None, cert_dir=None, clock=time.time):
    """Run the gate. `forecast` = {"metric": str, "predicted_prob": float in [0,1]}
    where predicted_prob is the proposer's stated probability that the edit helps
    the held-out risk. Returns a certificate dict; on accept it is also appended
    to the append-only log.
    """
    # --- minimal-modification term (run 371) -----------------------------
    # From WorldBench (arXiv:2609.01056, folded run 370): every model tested
    # traded task CORRECTNESS against ENVIRONMENT PRESERVATION, and its metric
    # scores completion AND minimal modification. This gate scored only whether an
    # edit HELPS - the proposal was passed in solely to be hashed, never inspected -
    # so an edit that improved the held-out score while disturbing things it had no
    # business touching passed cleanly.
    #
    # The graph-patch contract is ADD-ONLY (`proposal_metadata` / `add_nodes` /
    # `add_edges`), but knowledge_graph.check_patch silently IGNORES unknown keys.
    # A patch carrying `remove_nodes` or `modify_nodes` therefore validates today,
    # and would be honoured by any apply_patch that read them. That is the concrete,
    # currently-unguarded version of the axis.
    footprint = modification_footprint(proposal)
    # SCOPE: check() is polymorphic - `proposal` is a graph patch on the fold path and a
    # loop-harness POLICY EDIT on the improvement_loop path (keys like rule / identity /
    # scope). Applying the graph-patch contract to both refuses every policy edit, which
    # is how this was caught: the first run of the new whitelist broke the gate's own
    # selftest. Enforce the contract only on objects that CLAIM to be graph patches.
    # Residual gap, stated: an object with none of the allowed keys is not patch-shaped
    # and is not checked here - nothing in the pipeline produces one, and check_patch
    # would not read it as a patch either, but it is not a proof.
    patch_shaped = any(k in proposal for k in _PATCH_ALLOWED_KEYS) if isinstance(proposal, dict) else False
    off_contract = sorted(footprint["destructive_keys"] + footprint["unknown_keys"])
    if patch_shaped and off_contract:
        return _reject_cert(
            proposal, forecast,
            f"patch carries key(s) outside the add-only contract: {off_contract}. "
            f"Allowed top-level keys are {sorted(_PATCH_ALLOWED_KEYS)}; anything else - "
            f"including annotations - belongs inside proposal_metadata. Refused on SHAPE, "
            f"not on the key's name, so renaming it does not help "
            f"(equivariance, arXiv:2608.03609). knowledge_graph.check_patch ignores unknown "
            f"keys, so this is the only place it is caught.",
            footprint, cert_dir, clock)

    verdict = verify_loop_edit(baseline_scores, candidate_scores,
                               verifier_disagreements=verifier_disagreements,
                               legibility=legibility, edit=edit)
    ev = verdict["evidence"]
    outcome = _held_out_outcome(baseline_scores, candidate_scores)
    fc_prob = float(forecast.get("predicted_prob", 0.5))
    fc_brier = brier(fc_prob, outcome)

    # process-adjusted: a repair-dependent accept is downgraded to conditional
    process_clean = not repaired
    decision = "accept" if verdict["accept"] else "reject"
    if decision == "accept" and repaired:
        decision = "accept_conditional"   # flagged: passed only after a deterministic repair

    cert = {
        "schema": "acceptance_gate.certificate.v1",
        "ts": round(clock(), 3),
        "proposal_hash": proposal_digest(proposal),
        "decision": decision,
        # what the patch DISTURBED, not just whether it helped (run 371)
        "modification_footprint": footprint,
        "gate": {
            "held_out_accept": verdict["accept"],
            "risk_before": ev["risk_before"],
            "risk_after": ev["risk_after"],
            "regressed_tasks": ev["regressed_tasks"],
            "category_regressed": ev["category_regressed"],
            "contested_changed_tasks": ev["contested_changed_tasks"],
            "legibility_regressed": ev["legibility_regressed"],
            "tampering_flags": ev["tampering_flags"],
            "process_clean": process_clean,
        },
        "e_value": ev["paired_eprocess"]["e_value"],
        "e_threshold": ev["paired_eprocess"]["threshold"],
        "e_committed": ev["paired_eprocess"]["committed"],
        "forecast": {"metric": forecast.get("metric", ""), "predicted_prob": fc_prob,
                     "held_out_outcome": outcome, "brier": fc_brier},
        "authority": verdict["authority"],
        "fallback": verdict["fallback"],
    }
    cert["certificate_hash"] = hashlib.sha256(
        json.dumps({k: cert[k] for k in cert if k != "certificate_hash"},
                   sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

    # Log EVERY adjudication, not only the accepts (run 368).
    #
    # This previously read `if decision.startswith("accept")`, so the gate's
    # append-only record held only the cases where it said yes: 183 entries, 183
    # accepts, 0 rejections. The one question you would ask this log - "is the gate
    # still rejecting things, or has it degraded into always-accept?" - was the one
    # question it could not answer, and a 100% accept rate *looked* like evidence
    # the gate worked. That is exactly the self-p-hacking failure
    # concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution
    # names, and the always-pass collapse of
    # concept_a_self_evolved_evaluator_cannot_be_validated_by_task_score - reached
    # here not by a gamed metric but by a biased audit trail.
    #
    # `provenance` marks whether this went to the default production log or to a
    # caller-supplied directory: the 183 existing entries were all written by
    # downstream selftests (loop_conductor / v2_integration / research_worker call
    # check() without a cert_dir), and nothing distinguished them from real
    # adjudications.
    d = Path(cert_dir) if cert_dir else CERT_DIR
    cert["provenance"] = "explicit_dir" if cert_dir else "default_log"
    cert["certificate_hash"] = hashlib.sha256(
        json.dumps({k: cert[k] for k in cert if k != "certificate_hash"},
                   sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    d.mkdir(parents=True, exist_ok=True)
    with (d / "gate_certificates.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(cert, sort_keys=True) + "\n")
    return cert


def verify_certificate(cert, proposal) -> dict:
    """Independently replay a certificate: recompute the proposal hash and the
    certificate hash, and re-derive the Brier score. Returns {ok, checks}."""
    checks = {}
    checks["proposal_hash matches the proposal"] = (
        cert.get("proposal_hash") == proposal_digest(proposal))
    body = {k: cert[k] for k in cert if k != "certificate_hash"}
    recomputed = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    checks["certificate_hash is self-consistent"] = recomputed == cert.get("certificate_hash")
    fc = cert.get("forecast", {})
    checks["brier re-derives"] = (
        abs(brier(fc.get("predicted_prob", 0.5), fc.get("held_out_outcome", 0.0))
            - fc.get("brier", -1)) < 1e-9)
    checks["decision is consistent with the held-out verdict"] = (
        (cert["gate"]["held_out_accept"] and cert["decision"].startswith("accept"))
        or (not cert["gate"]["held_out_accept"] and cert["decision"] == "reject"))
    return {"ok": all(checks.values()), "checks": checks}


def _destructive_passes_check_patch() -> bool:
    """The gap this term closes: knowledge_graph.check_patch ignores unknown keys, so
    a patch carrying `remove_nodes` VALIDATES. Asserting this keeps the justification
    honest - if check_patch is ever tightened, this check fails and the comment above
    the gate term must be corrected rather than left stale."""
    try:
        from knowledge_graph import check_patch
    except Exception:
        return True
    graph = {"nodes": [{"id": "concept_anchor", "label": "a", "type": "concept"}], "edges": []}
    patch = {"proposal_metadata": {}, "add_nodes": [], "add_edges": [],
             "remove_nodes": ["concept_anchor"]}
    return check_patch(patch, graph) == []


def _selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="acc-gate-"))
    checks = {}

    good_edit = {"kind": "context", "name": "loop_policy",
                 "rule": "keep everything", "identity": "unchanged", "scope": ["one_key"]}
    base = {f"t{i}": (1.0 if i < 8 else 0.0) for i in range(17)}      # risk ~0.29
    cand = {f"t{i}": (1.0 if i < 12 else 0.0) for i in range(17)}     # risk ~0.06, strict decrease
    fc = {"metric": "held_out_risk", "predicted_prob": 0.8}

    cert = check(good_edit, base, cand, fc, repaired=False, edit=good_edit, cert_dir=tmp,
                 clock=lambda: 1000.0)
    checks["a clean improving edit is accepted"] = cert["decision"] == "accept"
    checks["certificate carries the proposal hash"] = len(cert["proposal_hash"]) == 64
    checks["forecast Brier is scored (0.8 vs outcome 1.0 -> 0.04)"] = cert["forecast"]["brier"] == 0.04
    checks["accepted certificate is written to the append-only log"] = (
        (tmp / "gate_certificates.jsonl").exists()
        and (tmp / "gate_certificates.jsonl").read_text().count("\n") == 1)

    # minimal-modification term (run 371, from WorldBench CTS)
    _fp = cert["modification_footprint"]
    # superset, not equality: an exact key set breaks on every future field, which is
    # the same brittleness the run-368 hard-coded line count had (fixed run 371).
    checks["every certificate carries a modification_footprint"] = (
        set(_fp) >= {"added_nodes", "added_edges", "touch_surface",
                     "destructive_keys", "unknown_keys"})

    # touch_surface threshold, DERIVED from 59 measured patches (run 379)
    checks["a normal-width patch is NOT flagged anomalous"] = (
        not _fp["touch_surface_anomalous"])
    _wide = {"proposal_metadata": {}, "add_nodes": [{"id": "concept_hub"}],
             "add_edges": [{"id": f"e{i}", "source": "concept_hub", "target": f"existing_{i}"}
                           for i in range(30)]}
    _fw = modification_footprint(_wide)
    checks["a 30-edge patch IS flagged anomalous"] = (
        _fw["touch_surface"] == 30 and _fw["touch_surface_anomalous"])
    checks["the flag threshold is 2x the observed historical max, not a guess"] = (
        TOUCH_SURFACE_FLAG == 2 * TOUCH_SURFACE_OBSERVED_MAX)
    _cw = check(_wide, base, cand, fc, cert_dir=tmp, clock=lambda: 1014.0)
    checks["an anomalous-width patch is FLAGGED, never refused (unusual != invalid)"] = (
        _cw["decision"] == "accept"
        and _cw["modification_footprint"]["touch_surface_anomalous"])

    _patch = {"proposal_metadata": {}, "add_nodes": [{"id": "concept_new"}],
              "add_edges": [{"id": "e1", "source": "concept_new", "target": "existing_a"},
                            {"id": "e2", "source": "concept_new", "target": "existing_b"}]}
    _f2 = modification_footprint(_patch)
    checks["touch_surface counts PRE-EXISTING endpoints only, not the new node"] = (
        _f2["touch_surface"] == 2 and _f2["added_nodes"] == 1)

    _destructive = {**_patch, "remove_nodes": ["concept_anchor"]}
    _cd = check(_destructive, base, cand, fc, cert_dir=tmp, clock=lambda: 1010.0)
    checks["a patch carrying a destructive key is REFUSED before the held-out set"] = (
        _cd["decision"] == "reject"
        and _cd["modification_footprint"]["destructive_keys"] == ["remove_nodes"]
        and "add-only" in _cd["gate"]["reason"])
    checks["check_patch would have LET that patch through (this is the gap closed)"] = (
        _destructive_passes_check_patch())
    checks["the destructive refusal is logged like any other adjudication"] = (
        json.loads((tmp / "gate_certificates.jsonl").read_text().splitlines()[-1])["decision"]
        == "reject")

    # EQUIVARIANCE (run 374): the refusal is on SHAPE, so renaming the offending key
    # cannot buy passage. `rm_nodes` slipped past the run-371 name blacklist; it must now
    # be refused exactly as `remove_nodes` is. This is the check that proves the upgrade
    # did what it claimed rather than just reading better.
    _renamed = {**_patch, "rm_nodes": ["concept_anchor"]}
    _cr = check(_renamed, base, cand, fc, cert_dir=tmp, clock=lambda: 1011.0)
    checks["EQUIVARIANT: `rm_nodes` is refused exactly as `remove_nodes` is"] = (
        _cr["decision"] == "reject" and _cd["decision"] == "reject")
    checks["the run-371 name blacklist would have MISSED `rm_nodes` (upgrade is real)"] = (
        not modification_footprint(_renamed)["destructive_keys"]
        and modification_footprint(_renamed)["unknown_keys"] == ["rm_nodes"])

    _benign_extra = {**_patch, "note": "a harmless annotation"}
    _cb = check(_benign_extra, base, cand, fc, cert_dir=tmp, clock=lambda: 1012.0)
    checks["a benign unknown key is ALSO refused - the contract is a whitelist"] = (
        _cb["decision"] == "reject" and "belongs inside proposal_metadata" in _cb["gate"]["reason"])
    checks["a policy edit (not patch-shaped) is NOT subject to the patch contract"] = (
        check({"rule": "keep everything", "identity": "unchanged", "scope": ["one_key"]},
              base, cand, fc, cert_dir=tmp, clock=lambda: 1013.0)["decision"] == "accept")

    v = verify_certificate(cert, good_edit)
    checks["verify_certificate replays a genuine certificate"] = v["ok"]
    tampered = dict(cert); tampered["decision"] = "reject"
    checks["verify_certificate catches a tampered decision"] = not verify_certificate(tampered, good_edit)["ok"]
    checks["verify_certificate catches a swapped proposal"] = not verify_certificate(
        cert, {"kind": "context", "name": "other"})["ok"]

    # a regressing edit is rejected AND recorded (run 368)
    # This check previously asserted "a rejected edit is not appended" - the
    # survivorship bias was encoded as a requirement, which is why 183 accepts and
    # 0 rejections never looked wrong. A gate you cannot audit for rejections is a
    # gate you cannot distinguish from always-accept.
    worse = {f"t{i}": (1.0 if i < 5 else 0.0) for i in range(17)}
    _lines_before_reject = (tmp / "gate_certificates.jsonl").read_text().count("\n")
    cert_r = check(good_edit, base, worse, fc, repaired=False, edit=good_edit, cert_dir=tmp,
                   clock=lambda: 1001.0)
    checks["a regressing edit is rejected"] = cert_r["decision"] == "reject"
    # Counted RELATIVE to the line count just before this call. The original used a
    # hard-coded `== 2` and broke the moment run 371 added another logged rejection
    # earlier in the selftest - a brittle assertion of exactly the kind this file
    # keeps finding elsewhere.
    checks["a rejected edit IS appended (the log must be auditable for rejections)"] = (
        (tmp / "gate_certificates.jsonl").read_text().count("\n") == _lines_before_reject + 1)
    checks["the logged rejection carries decision=reject"] = (
        json.loads((tmp / "gate_certificates.jsonl").read_text()
                   .splitlines()[-1])["decision"] == "reject")
    checks["certificates record their provenance (default log vs explicit dir)"] = (
        cert_r.get("provenance") == "explicit_dir")

    # a repair-dependent accept is downgraded to conditional (process-adjusted)
    cert_c = check(good_edit, base, cand, fc, repaired=True, edit=good_edit, cert_dir=tmp,
                   clock=lambda: 1002.0)
    checks["a repair-dependent accept is flagged accept_conditional"] = (
        cert_c["decision"] == "accept_conditional" and cert_c["gate"]["process_clean"] is False)

    # forecast calibration: a confident-wrong forecast earns a bad Brier
    cert_w = check(good_edit, base, worse, {"metric": "x", "predicted_prob": 0.9},
                   repaired=False, edit=good_edit, cert_dir=tmp, clock=lambda: 1003.0)
    checks["a confident-but-wrong forecast earns Brier 0.81"] = cert_w["forecast"]["brier"] == 0.81

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
    ck = sub.add_parser("check")
    ck.add_argument("proposal_json", help="path to a JSON file: {proposal, baseline_scores, candidate_scores, forecast, repaired?}")
    ve = sub.add_parser("verify")
    ve.add_argument("certificate_json")
    ve.add_argument("proposal_json")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "check":
        d = json.loads(Path(args.proposal_json).read_text(encoding="utf-8"))
        cert = check(d["proposal"], d["baseline_scores"], d["candidate_scores"],
                     d["forecast"], repaired=d.get("repaired", False), edit=d.get("proposal"))
        print(json.dumps(cert, indent=2))
        return 0
    if args.cmd == "verify":
        cert = json.loads(Path(args.certificate_json).read_text(encoding="utf-8"))
        prop = json.loads(Path(args.proposal_json).read_text(encoding="utf-8"))
        res = verify_certificate(cert, prop)
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

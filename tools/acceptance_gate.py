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


def check(proposal, baseline_scores, candidate_scores, forecast, *,
          verifier_disagreements=None, legibility=None, repaired=False,
          edit=None, cert_dir=None, clock=time.time):
    """Run the gate. `forecast` = {"metric": str, "predicted_prob": float in [0,1]}
    where predicted_prob is the proposer's stated probability that the edit helps
    the held-out risk. Returns a certificate dict; on accept it is also appended
    to the append-only log.
    """
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
    cert_r = check(good_edit, base, worse, fc, repaired=False, edit=good_edit, cert_dir=tmp,
                   clock=lambda: 1001.0)
    checks["a regressing edit is rejected"] = cert_r["decision"] == "reject"
    checks["a rejected edit IS appended (the log must be auditable for rejections)"] = (
        (tmp / "gate_certificates.jsonl").read_text().count("\n") == 2)
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

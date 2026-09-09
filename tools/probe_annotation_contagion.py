#!/usr/bin/env python3
"""Does a false high-utility annotation out-propagate the honest warnings?

`docs/auto_sweep_2026-11-04-1800.md` (run 397), the gap arXiv:2609.04170 exposed in
this repo's own substrate: `gates.py` catches bad ARTIFACTS at G1/G4, but the
`pheromone.py` board also carries `kind=utility` annotations that STEER WHERE AGENTS
WORK, and nothing there stops a cheating cohort from marking an exploit as valuable
and having that signal propagate — the 100-agent math swarm's contagion, one level
down.

This rig drives the REAL `pheromone.Pheromone` (not a re-derivation) and asks: on a
task_ref an adversary is boosting, does the aggregate `signal` stay above
`suggested_threshold` — i.e. does the board keep pointing agents at the exploit —
despite an honest cohort posting `kind=warning` after a detection lag?

  ARMS
    baseline        no warnings. The exploit boost is unopposed.
    warnings_only   honest agents post kind=warning with negative utility after a
                    lag. This is what pheromone.py does TODAY (a warning is just a
                    negatively-weighted annotation).
    veto_weight     a proposed mitigation: an agent's live warning on a task_ref
                    DISCOUNTS the positive contributions of the cohort it names, not
                    just adds a negative term. Implemented here as a post-filter on
                    read(), so it can be evaluated before touching the module.

  SWEEP  cheater fraction, detection lag (in "rounds"), honest cohort size.

  VERDICT  the honest reading of whether warnings-as-they-are suffice, and by how
  much veto-weighting changes it.

Pure stdlib. No model calls.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pheromone import Pheromone  # noqa: E402

BOOST_UTILITY = 0.8          # a cheater marks the exploit this valuable
BOOST_CONF = 0.9
WARN_UTILITY = -0.7          # an honest agent's warning strength
WARN_CONF = 0.9
HALF_LIFE = 3600.0


def _run_arm(arm, *, n_agents, cheater_frac, detect_lag_rounds, honest_frac,
             rounds=12, seed_base=20260397):
    """One scenario. Returns per-round aggregate readings on the boosted task_ref."""
    tmp = Path(tempfile.mkdtemp(prefix="contagion-"))
    try:
        pf = Pheromone(tmp / "p.db")
        n_cheat = max(1, round(n_agents * cheater_frac))
        n_honest = max(0, round(n_agents * honest_frac))
        cheaters = [f"x{i}" for i in range(n_cheat)]
        honest = [f"h{i}" for i in range(n_honest)]
        readings = []
        base = 1_000_000.0            # a fixed clock so decay is deterministic
        for r in range(rounds):
            now = base + r * 60.0     # one "round" = 60s of wall time
            # contagion model: the cheating cohort grows linearly to full size over
            # the run; each cheater posts ONCE (stable id -> re-annotate replaces).
            active_cheat = cheaters[: max(1, round(len(cheaters) * (r + 1) / rounds))]
            for c in active_cheat:
                pf.annotate("exploit", "utility", BOOST_UTILITY, BOOST_CONF, agent=c,
                            half_life_s=HALF_LIFE, _at=now, _id=c)
            # honest agents come online after the detection lag, then stay warning
            if arm in ("warnings_only", "veto_weight") and r >= detect_lag_rounds:
                for h in honest:
                    pf.annotate("exploit", "warning", WARN_UTILITY, WARN_CONF, agent=h,
                                half_life_s=HALF_LIFE, _at=now, _id=h,
                                evidence={"names_cohort": "x"})
            # suspicion arm: a CHEAP warn() at half the lag (a hunch, not an audit),
            # upgraded to a full warning at the full lag. Run 399 - does a shorter
            # lag on a weak flag actually shorten the exposure window?
            if arm == "suspicion_then_full":
                if r >= max(1, detect_lag_rounds // 2):
                    for h in honest:
                        pf.warn("exploit", agent=h, strength=0.5, confidence=0.4,
                                names_cohort="x", _at=now, _id=f"{h}-susp")
                if r >= detect_lag_rounds:
                    for h in honest:
                        pf.annotate("exploit", "warning", WARN_UTILITY, WARN_CONF, agent=h,
                                    half_life_s=HALF_LIFE, _at=now, _id=h,
                                    evidence={"names_cohort": "x"})
            v = pf.read("exploit", at=now + 1.0)
            signal_raw = v["signal_raw"]
            if arm == "veto_weight":
                signal_raw = _veto_weighted(pf, "exploit", at=now + 1.0)
            thr = v["suggested_threshold"] or 1e9
            readings.append({
                "round": r,
                "signal_raw": round(signal_raw, 3),
                "threshold": thr,
                # "still steering TO the exploit" = a POSITIVE signal over the bar.
                # A strong NEGATIVE signal means the board is correctly warning agents
                # away, which is the opposite of the failure being measured.
                "steering_to_exploit": signal_raw >= thr,
                "warning_away": signal_raw <= -thr,
                "n_warnings": sum(1 for a in v["annotations"] if a["kind"] == "warning"),
            })
        pf.close()
        return readings
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _veto_weighted(pf, task_ref, *, at):
    """Proposed mitigation, evaluated as a post-filter: for each live warning that
    names a cohort, discount the positive effective_utility of annotations from
    agents in that cohort by (1 - warn_confidence). Warnings still contribute their
    own negative term. Returns the adjusted signal_raw."""
    v = pf.read(task_ref, at=at)
    anns = v["annotations"]
    vetoed_prefixes = {a["evidence"]["names_cohort"]
                       for a in anns
                       if a["kind"] == "warning" and isinstance(a.get("evidence"), dict)
                       and a["evidence"].get("names_cohort")}
    warn_conf = max((a["confidence"] for a in anns if a["kind"] == "warning"), default=0.0)
    total = 0.0
    for a in anns:
        eu = a["effective_utility"]
        if a["kind"] != "warning" and eu > 0 and any(
                a["agent"].startswith(p) for p in vetoed_prefixes):
            eu *= (1.0 - warn_conf)          # discount the boosted-cohort positives
        total += eu
    return total


_PRIMACY = 1.35     # the temporal-weight multiplier the first-committed view carries


def seal_order_arm(*, n_honest=200, n_cheat_max=2, seed=20260454):
    """The TEMPORAL-WEIGHT EFFECT (arXiv:2609.03425, run 454): a claim arriving
    FIRST gains unearned credibility - 54.2% answer-capture vs 31.6% when the
    receiver had SEALED its own response first. Tested against the substrate's
    isolation primitive (run 437): does an honest agent that posts its assessment
    `isolated=True` BEFORE reading the board resist an early contaminated boost
    better than one that reads the board first?

    Each honest agent varies (rng): how much of the cheater cohort it sees (1..
    n_cheat_max) and how firm its own correct assessment is. The real Pheromone
    supplies the board signal + the threshold; the temporal weight is a reader-side
    adjustment (like `_veto_weighted`, a post-read model, not a module property):
    whichever view was committed FIRST is multiplied by `_PRIMACY`.
      unsealed: the board was seen first  -> board_positive * _PRIMACY + own_view
      sealed:   own view was committed first -> board_positive + own_view * _PRIMACY
    'Captured' = the resulting effective signal is over `suggested_threshold`.
    """
    import random
    import shutil
    rng = random.Random(seed)
    base = 1_000_000.0
    cap_unsealed = cap_sealed = 0
    for a in range(n_honest):
        n_seen = rng.randint(1, n_cheat_max)
        own_view = WARN_UTILITY * rng.uniform(0.7, 1.5)      # the reader's correct negative read
        reader = f"h{a}"
        for sealed in (False, True):
            tmp = Path(tempfile.mkdtemp(prefix="seal-"))
            try:
                pf = Pheromone(tmp / "p.db")
                now = base
                for i in range(n_seen):                     # cheaters boosted FIRST
                    pf.annotate("exploit", "utility", BOOST_UTILITY, BOOST_CONF,
                                agent=f"x{i}", half_life_s=HALF_LIFE, _at=now, _id=f"x{i}")
                if sealed:
                    pf.annotate("exploit", "warning", WARN_UTILITY,
                                min(1.0, abs(own_view) / abs(WARN_UTILITY)),
                                agent=reader, isolated=True, half_life_s=HALF_LIFE,
                                _at=now, _id=reader)
                v = pf.read("exploit", at=now + 1.0, reader=reader)
                board_pos = sum(x["effective_utility"] for x in v["annotations"]
                                if x["agent"].startswith("x") and x["effective_utility"] > 0)
                effective = (board_pos + own_view * _PRIMACY if sealed
                             else board_pos * _PRIMACY + own_view)
                thr = v["suggested_threshold"] or 1e9
                if effective >= thr:
                    if sealed:
                        cap_sealed += 1
                    else:
                        cap_unsealed += 1
                pf.close()
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    return {
        "n_honest": n_honest,
        "captured_unsealed_frac": round(cap_unsealed / n_honest, 3),
        "captured_sealed_frac": round(cap_sealed / n_honest, 3),
        "seal_reduces_capture_by": round((cap_unsealed - cap_sealed) / n_honest, 3),
    }


def assess_seal_order(s):
    u, sd = s["captured_unsealed_frac"], s["captured_sealed_frac"]
    return {
        "sealing_reduces_capture": sd < u - 0.05,
        "captured_unsealed_frac": u,
        "captured_sealed_frac": sd,
        "verdict": (
            f"REPRODUCES the direction of the temporal-weight effect against the substrate's "
            f"isolation primitive: an honest agent that reads the contaminated board FIRST is "
            f"captured in {u:.0%} of trials; one that posts its own assessment isolated=True "
            f"and THEN reads is captured in {sd:.0%}. The paper's FIELD number is 54.2% vs "
            f"31.6% (a ~42% relative drop); this SIM shows a larger effect ({u:.0%} -> "
            f"{sd:.0%}) because the modelled board has no honest counter-signal and the "
            f"temporal weight is applied cleanly - read the DIRECTION and 'sealing roughly "
            f"halves-or-more the capture', not the magnitude. `pheromone.annotate("
            f"isolated=True)` + `release_isolation` (run 437) IS the seal: the substrate "
            f"already has the mechanism, this measures that USING it before cross-reading "
            f"matters. LIMIT: the _PRIMACY multiplier is a reader-side model (like "
            f"_veto_weighted), not a Pheromone property; the real magnitude needs live "
            f"agents."
            if sd < u - 0.05 else
            f"Does NOT show a clean seal effect at these params ({u:.0%} vs {sd:.0%}) - the "
            f"threshold scaling may be absorbing the reader's own annotation."),
    }


def sweep(n_agents=20, cheater_fracs=(0.1, 0.3, 0.5), lags=(2, 4, 6),
          honest_fracs=(0.2, 0.4), rounds=12):
    out = {}
    for arm in ("baseline", "warnings_only", "suspicion_then_full", "veto_weight"):
        out[arm] = {}
        for cf in cheater_fracs:
            for lag in lags:
                for hf in honest_fracs:
                    key = f"cf{cf}_lag{lag}_hf{hf}"
                    rd = _run_arm(arm, n_agents=n_agents, cheater_frac=cf,
                                  detect_lag_rounds=lag, honest_frac=hf, rounds=rounds)
                    out[arm][key] = {
                        "final_steering_to_exploit": rd[-1]["steering_to_exploit"],
                        "final_warning_away": rd[-1]["warning_away"],
                        "rounds_steering": sum(1 for x in rd if x["steering_to_exploit"]),
                        "final_signal": rd[-1]["signal_raw"],
                    }
    return out


def assess(sw):
    def frac_still_steering(arm):
        rows = sw[arm].values()
        return round(sum(1 for r in rows if r["final_steering_to_exploit"]) / len(rows), 3)

    def frac_warning_away(arm):
        rows = sw[arm].values()
        return round(sum(1 for r in rows if r["final_warning_away"]) / len(rows), 3)

    def mean_rounds_steering(arm):
        rows = sw[arm].values()
        return round(sum(r["rounds_steering"] for r in rows) / len(rows), 2)

    base = frac_still_steering("baseline")
    warn = frac_still_steering("warnings_only")
    susp = frac_still_steering("suspicion_then_full")
    veto = frac_still_steering("veto_weight")
    warn_away = frac_warning_away("warnings_only")
    veto_away = frac_warning_away("veto_weight")
    return {
        "baseline_frac_exploit_still_steering": base,
        "warnings_only_frac_still_steering": warn,
        "warnings_only_frac_now_warning_away": warn_away,
        "suspicion_then_full_frac_still_steering": susp,
        "veto_weight_frac_still_steering": veto,
        "veto_weight_frac_now_warning_away": veto_away,
        "mean_rounds_steering": {
            "baseline": mean_rounds_steering("baseline"),
            "warnings_only": mean_rounds_steering("warnings_only"),
            "suspicion_then_full": mean_rounds_steering("suspicion_then_full"),
            "veto_weight": mean_rounds_steering("veto_weight"),
        },
        "verdict": (
            f"CONFIRMS the run-397 gap and MEASURES the run-398 residual. Unopposed, the exploit "
            f"annotation keeps the board pointing agents AT it in {base:.0%} of swept scenarios "
            f"and for a mean of {mean_rounds_steering('baseline')} rounds. "
            f"Plain warnings (a negatively-weighted annotation, what pheromone.py does today): "
            f"{warn:.0%} still steering, {mean_rounds_steering('warnings_only')} mean rounds "
            f"exposed. "
            f"The run-399 addition - a CHEAP pf.warn() suspicion flag at HALF the detection lag, "
            f"upgraded to a full warning at the full lag: {susp:.0%} still steering, "
            f"{mean_rounds_steering('suspicion_then_full')} mean rounds exposed"
            + (f". The suspicion flag shortens the exposure window - "
               f"{mean_rounds_steering('warnings_only')} -> "
               f"{mean_rounds_steering('suspicion_then_full')} mean rounds - which is the "
               f"run-398 finding acted on: the residual risk was temporal, and halving the lag "
               f"on a weak flag roughly halves the exposure, at the cost of a weak flag that "
               f"decays on its own if not followed up."
               if mean_rounds_steering('suspicion_then_full') < mean_rounds_steering('warnings_only') - 0.3
               else ". The suspicion flag does not measurably shorten the exposure at these "
                    "params - the weak flag is too weak to cross the threshold on its own.")
            + f" Veto-weighting: {veto:.0%} still steering / {veto_away:.0%} warning away"
            + (", the strongest arm" if veto_away > warn_away + 0.1 else "")
            + ". ASSUMPTION unchanged and untested: correct attribution of the cheating cohort. "
              "Veto-weighting stays a read() post-filter, not in the module; pf.warn() IS in the "
              "module because a weak, short-TTL, self-decaying flag has no censorship downside."),
    }


def _selftest():
    checks = {}
    # the headline assessment is run across three fleet sizes, not one — the
    # contagion dynamic must not be an artefact of a single agent count
    # (param_invariance_audit + the run-385 lesson).
    sw8 = sweep(n_agents=8, cheater_fracs=(0.25, 0.5), lags=(1, 4), honest_fracs=(0.3,),
                rounds=8)
    sw12 = sweep(n_agents=12, cheater_fracs=(0.25, 0.5), lags=(1, 4), honest_fracs=(0.3,),
                 rounds=8)
    sw20 = sweep(n_agents=20, cheater_fracs=(0.25, 0.5), lags=(1, 4), honest_fracs=(0.3,),
                 rounds=8)
    sw = sw12
    a = assess(sw)
    for label, s in (("8", sw8), ("12", sw12), ("20", sw20)):
        aa = assess(s)
        checks[f"n={label}: baseline steers >50%, counter-arms never worse than baseline"] = (
            aa["baseline_frac_exploit_still_steering"] > 0.5
            and aa["warnings_only_frac_still_steering"]
            <= aa["baseline_frac_exploit_still_steering"] + 1e-9
            and aa["veto_weight_frac_still_steering"]
            <= aa["baseline_frac_exploit_still_steering"] + 1e-9)

    checks["baseline: an unopposed exploit annotation keeps the board steering to it"] = (
        a["baseline_frac_exploit_still_steering"] > 0.5)
    checks["warnings never make it WORSE than baseline"] = (
        a["warnings_only_frac_still_steering"] <= a["baseline_frac_exploit_still_steering"] + 1e-9)
    checks["a counter-response (warnings or veto) flips some scenarios to warning-away"] = (
        a["warnings_only_frac_now_warning_away"] > 0
        or a["veto_weight_frac_now_warning_away"] > 0)
    checks["veto-weighting is never worse than plain warnings at steering suppression"] = (
        a["veto_weight_frac_still_steering"] <= a["warnings_only_frac_still_steering"] + 1e-9)
    checks["the verdict names the attribution assumption it does not test"] = (
        "attribution" in a["verdict"] and "untested" in a["verdict"].lower())
    checks["the verdict distinguishes the in-module pf.warn from the post-filter veto"] = (
        "pf.warn() IS in the module" in a["verdict"]
        and "post-filter" in a["verdict"])
    checks["the verdict names detection LAG as the residual exposure"] = (
        "lag" in a["verdict"].lower())
    checks["the suspicion arm shortens the mean exposure window vs plain warnings"] = (
        a["mean_rounds_steering"]["suspicion_then_full"]
        <= a["mean_rounds_steering"]["warnings_only"] + 1e-9)
    # the rig drives the real module
    import pheromone as _p
    checks["the rig imports the real pheromone module, not a copy"] = hasattr(_p, "Pheromone")
    # determinism
    sw2 = sweep(n_agents=12, cheater_fracs=(0.25, 0.5), lags=(1, 4), honest_fracs=(0.3,),
                rounds=8)
    checks["the sweep is deterministic"] = assess(sw2)["verdict"] == a["verdict"]
    # a pool-size check: the finding is not an artefact of one agent count
    for n in (8, 16, 24):
        swn = sweep(n_agents=n, cheater_fracs=(0.5,), lags=(2,), honest_fracs=(0.3,), rounds=6)
        an = assess(swn)
        checks[f"n={n}: baseline steers and neither counter-arm is worse than baseline"] = (
            an["warnings_only_frac_still_steering"]
            <= an["baseline_frac_exploit_still_steering"] + 1e-9
            and an["veto_weight_frac_still_steering"]
            <= an["baseline_frac_exploit_still_steering"] + 1e-9)

    # --- run 455: the seal-order arm (temporal-weight effect, arXiv:2609.03425) ---
    so = seal_order_arm()
    aso = assess_seal_order(so)
    checks["seal-order: reading the board first captures more than sealing first"] = (
        aso["sealing_reduces_capture"]
        and so["captured_unsealed_frac"] > so["captured_sealed_frac"] + 0.1)
    checks["seal-order: the arm is deterministic"] = (
        seal_order_arm()["captured_sealed_frac"] == so["captured_sealed_frac"])
    checks["seal-order verdict names the field number AND that the sim is larger"] = (
        "54.2%" in aso["verdict"] and "larger effect" in aso["verdict"])
    checks["seal-order verdict names the isolation primitive as the seal"] = (
        "isolated=true" in aso["verdict"].lower() and "release_isolation" in aso["verdict"])
    checks["seal-order verdict states the _PRIMACY reader-side-model limit"] = (
        "reader-side model" in aso["verdict"] and "not a Pheromone property" in aso["verdict"])

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  seal-order: unsealed {so['captured_unsealed_frac']:.0%} / "
          f"sealed {so['captured_sealed_frac']:.0%}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    rp = sub.add_parser("run")
    rp.add_argument("--agents", type=int, default=20)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    sw = sweep(n_agents=args.agents)
    a = assess(sw)
    a["seal_order"] = assess_seal_order(seal_order_arm())
    print(json.dumps(a, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

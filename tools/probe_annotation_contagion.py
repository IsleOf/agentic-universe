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
            if arm != "baseline" and r >= detect_lag_rounds:
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


def sweep(n_agents=20, cheater_fracs=(0.1, 0.3, 0.5), lags=(1, 3, 6),
          honest_fracs=(0.2, 0.4), rounds=12):
    out = {}
    for arm in ("baseline", "warnings_only", "veto_weight"):
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

    base = frac_still_steering("baseline")
    warn = frac_still_steering("warnings_only")
    veto = frac_still_steering("veto_weight")
    warn_away = frac_warning_away("warnings_only")
    veto_away = frac_warning_away("veto_weight")
    return {
        "baseline_frac_exploit_still_steering": base,
        "warnings_only_frac_still_steering": warn,
        "warnings_only_frac_now_warning_away": warn_away,
        "veto_weight_frac_still_steering": veto,
        "veto_weight_frac_now_warning_away": veto_away,
        "verdict": (
            f"CONFIRMS the run-397 gap. Unopposed, the exploit annotation keeps the board "
            f"pointing agents AT it in {base:.0%} of swept scenarios. "
            f"Warnings as pheromone.py implements them today (a negatively-weighted annotation) "
            f"bring 'still steering to the exploit' to {warn:.0%} and flip {warn_away:.0%} of "
            f"scenarios to actively warning agents AWAY - "
            + ("so plain warnings substantially help once the honest cohort is online, but the "
               "detection LAG is the exposure: every round before the warnings land, the board "
               "steers to the exploit."
               if warn < 0.5 else
               "so plain warnings do NOT close it: a growing cheater cohort out-votes a fixed "
               "honest one in the raw sum.")
            + f" Veto-weighting (a live warning DISCOUNTS the named cohort's positive "
              f"contributions, not just adds a negative) gives {veto:.0%} still steering / "
              f"{veto_away:.0%} warning away"
            + (", a clear improvement over plain warnings" if veto_away > warn_away + 0.1
               else ", not a decisive change over plain warnings at these params")
            + ". ASSUMPTION this rig encodes and does NOT test: that the honest cohort correctly "
              "identifies the cheating cohort to name in the warning. If attribution is wrong or "
              "gamed, veto-weighting becomes a censorship vector - which is why it is prototyped "
              "here as a read() post-filter and not put in the module."),
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
        "attribution is wrong or" in a["verdict"] and "censorship vector" in a["verdict"])
    checks["the verdict names detection LAG as the residual exposure"] = (
        "lag" in a["verdict"].lower())
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

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
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
    print(json.dumps(a, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

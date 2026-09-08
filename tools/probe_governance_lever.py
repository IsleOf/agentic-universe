#!/usr/bin/env python3
"""Mechanism design vs preference engineering — a runnable rig for a live tension.

Two folded nodes disagree about how to govern a multi-agent system, and both
report working:

  concept_institutional_ai_governs_collusion_by_mechanism_design_not_preference_engineering
      govern in INSTITUTION-space: change the rules of interaction, not what
      agents want.
  concept_emergent_multi_agent_behaviour_can_be_steered_by_a_reward_model_learned_from_
  episode_level_collective_outcomes  (MARP, arXiv:2608.07280, folded run 375)
      fit a shared reward model to collective outcomes - preference engineering
      lifted to the collective level - and behaviour follows the metric you pick.

Run 375 recorded that as a tension rather than resolving it in prose. This rig
makes it falsifiable on a common-pool resource game (the Harvest-Game shape MARP
itself uses).

## The trap this rig has to avoid

If MECHANISM is modelled as "an unevadable constraint" and PREFERENCE as "an
internal weight an agent may not share", mechanism wins by definition and the rig
proves nothing. So each lever carries its REAL cost:

  MECHANISM      robust to non-adopters (the constraint is external) but COARSE -
                 one cap for heterogeneous agents wastes the capacity of those who
                 would have self-restrained - and it needs MONITORING, which is
                 imperfect: a violation is caught only with probability `detect`.
  PREFERENCE     fine-grained - each adopter self-restrains in proportion to its
                 own situation, so no deadweight loss - and needs no monitoring at
                 all, but it does nothing whatsoever to an agent that has not
                 adopted it.

Under those costs neither lever dominates, and the question becomes empirical:
where is the crossover in non-adopter fraction, and how does monitoring quality
move it?

## What is assumed vs measured

ASSUMED: the two cost structures above, and a commons whose regrowth is
logistic in remaining stock. Everything else - the crossover point, its
sensitivity to `detect`, the yield gap at zero defection - FOLLOWS. As with
probe_memory_horizon (run 360), the rig makes an assumption explicit and shows
what it implies; it does not prove the assumption. `assess()` reports whether the
crossover exists rather than asserting it must.

Pure stdlib, fixed seeds.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys

SEED = 20261030

N_AGENTS = 8
ROUNDS = 40
CAPACITY = 100.0        # commons carrying capacity
REGROWTH = 0.28         # logistic regrowth rate
START = 60.0
GREED = 3.2             # what an ungoverned agent tries to take per round
SUSTAIN_FLOOR = 15.0    # stock below this at the end = the commons collapsed

# mechanism-design coarseness: one cap for everyone, so an agent that would have
# taken less than the cap is unaffected, and one that would have taken more is
# clipped. The waste is that the cap cannot be set per-agent.
# Max sustainable total harvest for this commons is 0.28 * K/2 * 0.5 = 7.0/round
# (logistic regrowth peaks at K/2). A cap must sit UNDER that to be a real
# institution: 8 agents x 0.7 = 5.6/round, leaving headroom. Calibrated rather than
# guessed - the first parameterisation used 1.9 (15.2/round) and every arm collapsed,
# which measured nothing except that the cap was not a cap.
CAP = 0.7


def _agent_appetites(rng):
    """Heterogeneous agents. This heterogeneity is what makes a single cap coarse."""
    return [max(0.4, rng.gauss(GREED, 1.1)) for _ in range(N_AGENTS)]


def run_episode(rng, *, lever, defector_frac, detect=1.0):
    """One episode of the commons.

    lever: "none" | "mechanism" | "preference" | "both"
    defector_frac: share of agents that have NOT adopted the collective preference.
                   Under `mechanism` they are still subject to the cap (that is the
                   point of an external constraint) but may evade it undetected.
    detect: probability a cap violation is caught and clipped. <1 is imperfect
            monitoring, the cost mechanism design actually pays.
    """
    stock = START
    appetites = _agent_appetites(rng)
    n_def = int(round(defector_frac * N_AGENTS))
    adopters = [i >= n_def for i in range(N_AGENTS)]   # first n_def are non-adopters
    takes = [0.0] * N_AGENTS

    for _ in range(ROUNDS):
        if stock <= 0.5:
            break
        want = []
        for i, a in enumerate(appetites):
            w = a
            if lever in ("preference", "both") and adopters[i]:
                # fine-grained self-restraint, proportional to how depleted the
                # commons is. No monitoring needed; does nothing to a non-adopter.
                w = a * (stock / CAPACITY) ** 2
            if lever in ("mechanism", "both") and w > CAP:
                # external cap - applies to adopters and non-adopters alike, but
                # only bites when the violation is actually detected
                if rng.random() < detect:
                    w = CAP
            want.append(w)
        total = sum(want)
        if total > stock:                       # cannot take more than exists
            want = [w * stock / total for w in want]
            total = stock
        for i, w in enumerate(want):
            takes[i] += w
        stock -= total
        stock += REGROWTH * stock * (1 - stock / CAPACITY)
        stock = min(stock, CAPACITY)

    total_yield = sum(takes)
    mean = total_yield / N_AGENTS if N_AGENTS else 0.0
    gini = 0.0
    if mean > 0:
        diffs = sum(abs(x - y) for x in takes for y in takes)
        gini = diffs / (2 * N_AGENTS * N_AGENTS * mean)
    return {"sustained": stock >= SUSTAIN_FLOOR, "final_stock": round(stock, 2),
            "yield": round(total_yield, 2), "gini": round(gini, 3)}


def sweep(defector_fracs=(0.0, 0.125, 0.25, 0.5), *, detect=1.0, trials=200, seed=SEED):
    out = {}
    for df in defector_fracs:
        out[df] = {}
        for lever in ("none", "mechanism", "preference", "both"):
            rng = random.Random(f"{seed}-{lever}-{df}-{detect}")
            eps = [run_episode(rng, lever=lever, defector_frac=df, detect=detect)
                   for _ in range(trials)]
            out[df][lever] = {
                "sustain_rate": round(sum(e["sustained"] for e in eps) / len(eps), 3),
                "mean_yield": round(statistics.fmean(e["yield"] for e in eps), 2),
            }
    return out


def assess(sw, sw_imperfect=None):
    fracs = sorted(sw)
    lo, hi = fracs[0], fracs[-1]
    pref_wins_clean = (sw[lo]["preference"]["mean_yield"] > sw[lo]["mechanism"]["mean_yield"]
                       and sw[lo]["preference"]["sustain_rate"] >= sw[lo]["mechanism"]["sustain_rate"])
    mech_wins_dirty = sw[hi]["mechanism"]["sustain_rate"] > sw[hi]["preference"]["sustain_rate"]
    crossover = next((f for f in fracs
                      if sw[f]["mechanism"]["sustain_rate"] > sw[f]["preference"]["sustain_rate"]),
                     None)
    monitoring_cost = None
    if sw_imperfect is not None:
        monitoring_cost = round(sw[hi]["mechanism"]["sustain_rate"]
                                - sw_imperfect[hi]["mechanism"]["sustain_rate"], 3)
    return {
        "preference_wins_with_full_adoption": pref_wins_clean,
        "mechanism_wins_under_defection": mech_wins_dirty,
        "crossover_defector_frac": crossover,
        "mechanism_sustain_lost_to_imperfect_monitoring": monitoring_cost,
        "verdict": (
            (f"NEITHER LEVER DOMINATES. With full adoption, preference engineering yields more "
             f"({sw[lo]['preference']['mean_yield']} vs {sw[lo]['mechanism']['mean_yield']}) "
             f"because it is fine-grained and a single cap is coarse. From a defector fraction "
             f"of {crossover} mechanism design sustains the commons more often, because an "
             f"external constraint binds agents that never adopted the preference. Imperfect "
             f"monitoring is what mechanism design pays for that robustness: "
             f"{monitoring_cost} of sustain rate at the highest defection level."
             if (pref_wins_clean and mech_wins_dirty and crossover is not None) else
             f"NO CLEAN CROSSOVER at these params (pref_wins_clean={pref_wins_clean}, "
             f"mech_wins_dirty={mech_wins_dirty}). The tension is not resolved by this "
             f"parameterisation and the rig should not be read as favouring either node."))
        + " NOTE: the two cost structures (mechanism = coarse + needs monitoring; preference = "
          "fine-grained + inert on non-adopters) are ASSUMPTIONS this sim encodes, not results "
          "it produces.",
    }


def _selftest():
    sw = sweep()
    sw_imp = sweep(detect=0.9)
    a = assess(sw, sw_imp)
    checks = {
        "ungoverned commons collapses (the dilemma is real in this sim)":
            sw[0.0]["none"]["sustain_rate"] < 0.2,
        "with full adoption, preference engineering out-yields the coarse cap":
            a["preference_wins_with_full_adoption"],
        "under defection, mechanism design sustains more often":
            a["mechanism_wins_under_defection"],
        "there is a crossover defector fraction (neither lever dominates)":
            a["crossover_defector_frac"] is not None,
        "imperfect monitoring costs mechanism design real sustain rate":
            (a["mechanism_sustain_lost_to_imperfect_monitoring"] or 0) > 0.02,
        "'both' is at least as sustaining as either lever alone at high defection":
            sw[0.5]["both"]["sustain_rate"] >= max(sw[0.5]["mechanism"]["sustain_rate"],
                                                   sw[0.5]["preference"]["sustain_rate"]),
        "the verdict states the cost structures are assumptions, not results":
            "ASSUMPTIONS this sim encodes" in a["verdict"],
        # The practically important result, and the one I did not predict: stacking
        # both levers buys robustness at MECHANISM's yield, not preference's. The cap
        # binds first, so the preference model adds nothing on top of it.
        "'both' yields no more than mechanism alone - the binding cap dominates":
            abs(sw[0.0]["both"]["mean_yield"] - sw[0.0]["mechanism"]["mean_yield"]) < 15
            and sw[0.0]["both"]["mean_yield"] < sw[0.0]["preference"]["mean_yield"] - 40,
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print("\n  sustain rate / mean yield by defector fraction (perfect monitoring):")
    for f in sorted(sw):
        row = "  ".join(f"{lv}={sw[f][lv]['sustain_rate']:.2f}/{sw[f][lv]['mean_yield']:.0f}"
                        for lv in ("none", "mechanism", "preference", "both"))
        print(f"    def={f:<6} {row}")
    print(f"\n  {a['verdict']}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sw = sub.add_parser("sweep")
    sw.add_argument("--detect", type=float, default=1.0)
    sw.add_argument("--trials", type=int, default=200)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        res = sweep(detect=args.detect, trials=args.trials)
        print(json.dumps({"sweep": res, "assess": assess(res)}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

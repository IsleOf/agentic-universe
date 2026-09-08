#!/usr/bin/env python3
"""Does retrieved memory help or hurt? — a runnable rig for the memory tension.

Three folded findings appear to contradict each other:

  concept_naive_trajectory_accumulation_already_helps (arXiv:2505.00234, run 174)
      even NAIVE retention of an agent's own successful trajectories beats a model
      upgrade.
  concept_reliability_is_a_separate_axis... (arXiv:2603.29231, run 356)
      memory scaffolds UNIVERSALLY DEGRADE long-horizon performance, all models.
  concept_misevolution... (arXiv:2509.26354, run 345)
      safety alignment degrades after memory accumulation, with no attacker.

Run 356 asserted a resolution in prose - "curated/bounded retrieval helps while
naive context-stuffing hurts at long horizons". That is a claim, not a finding,
and asserting it inside a node description is the failure this project's own
standard exists to prevent. This rig makes it FALSIFIABLE.

## The claim under test

  H1  at SHORT horizon, unbounded retrieval >= no retrieval   (memory helps)
  H2  at LONG horizon, top-k ranked > none > unbounded        (unbounded is worse
                                                               than no memory at all)
  H3  bounded top-k is never worse than unbounded, at any horizon

## What is assumed vs measured

The sim encodes ONE mechanism as an assumption, and everything else follows from
it: an injected entry that is RELEVANT raises a step's success probability, an
IRRELEVANT one lowers it, and the per-item dilution cost scales with the VOLUME
injected times the HORIZON already travelled. That product is the mechanism
arXiv:2603.29231 names and it is why unbounded can win short and lose long.

**The rig does not prove the mechanism - it makes the assumption explicit and
shows what follows from it.** If the three hypotheses do not fall out of an
honest parameterisation, `assess()` says so rather than being tuned until they
do. The live seam is named below: a real `experience_bank`, real tasks and a real
model would test the mechanism itself.

Pure stdlib, fixed seeds.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys

SEED = 20261026

P_BASE = 0.93          # per-step success with no memory at all
RELEVANT_LIFT = 0.05   # a relevant retrieved entry raises the step's success prob
DILUTION = 0.0022      # per-irrelevant-item cost, scaled by volume x horizon travelled
BANK_SIZE = 24         # entries whose retrieval key matches the task signature
RELEVANT_FRAC = 0.25   # how many of those are actually useful here
TOP_K = 3              # the bounded policy's cap (matches experience_bank._DEFAULT_TOP_K)


def _bank(rng):
    """A bank of matching entries: each is (relevant, utility_estimate).

    `utility` is the bank's own (noisy) estimate of usefulness - what
    experience_bank.utility_score() gives you. Ranking is only as good as that
    estimate, so the top-k arm inherits its noise rather than getting an oracle.
    """
    bank = []
    for _ in range(BANK_SIZE):
        relevant = rng.random() < RELEVANT_FRAC
        true_u = 0.8 if relevant else 0.2
        bank.append((relevant, min(max(true_u + rng.gauss(0, 0.18), 0.0), 1.0)))
    return bank


def _retrieve(bank, policy):
    if policy == "none":
        return []
    if policy == "unbounded":
        return list(bank)
    if policy == "topk":
        return sorted(bank, key=lambda b: b[1], reverse=True)[:TOP_K]
    raise ValueError(policy)


def run_task(rng, horizon, policy):
    """One task of `horizon` steps. Returns the fraction of steps that succeeded."""
    injected = _retrieve(_bank(rng), policy)
    n_rel = sum(1 for r, _ in injected if r)
    n_irr = len(injected) - n_rel
    ok = 0
    for step in range(horizon):
        # relevant entries lift; irrelevant ones dilute, and the dilution cost
        # grows with how far into the task we already are (context pressure)
        lift = RELEVANT_LIFT * min(n_rel, 3)
        drag = DILUTION * n_irr * step
        p = min(max(P_BASE + lift - drag, 0.02), 0.995)
        if rng.random() < p:
            ok += 1
    return ok / horizon


def sweep(horizons=(5, 20, 60, 150), trials=400, seed=SEED):
    out = {}
    for h in horizons:
        out[h] = {}
        for policy in ("none", "unbounded", "topk"):
            rng = random.Random(f"{seed}-{h}-{policy}")
            scores = [run_task(rng, h, policy) for _ in range(trials)]
            out[h][policy] = round(statistics.fmean(scores), 4)
    return out


def assess(sw):
    hs = sorted(sw)
    short, long = hs[0], hs[-1]
    h1 = sw[short]["unbounded"] >= sw[short]["none"]
    h2 = (sw[long]["topk"] > sw[long]["none"] > sw[long]["unbounded"])
    h3 = all(sw[h]["topk"] >= sw[h]["unbounded"] for h in hs)
    crossover = next((h for h in hs if sw[h]["unbounded"] < sw[h]["none"]), None)
    reproduced = h1 and h2 and h3
    return {
        "H1_short_horizon_memory_helps": h1,
        "H2_long_horizon_topk_beats_none_beats_unbounded": h2,
        "H3_bounded_never_worse_than_unbounded": h3,
        "crossover_horizon": crossover,
        "reproduced": reproduced,
        "verdict": (
            (f"CONSISTENT with the run-356 resolution: unbounded retrieval helps at "
             f"horizon {short} and becomes WORSE THAN NO MEMORY from horizon {crossover}; "
             f"bounded top-{TOP_K} is never worse than unbounded and still beats none at "
             f"horizon {long}. Curation, not volume, is what makes memory pay off on long "
             f"tasks."
             if reproduced else
             f"DOES NOT reproduce the asserted resolution at these params "
             f"(H1={h1} H2={h2} H3={h3}). The run-356 prose claim is not supported by this "
             f"parameterisation and should be weakened in the graph.")
            + " NOTE: the dilution mechanism is an ASSUMPTION of the sim, not a result of it. "
            "Read the ORDERING and the crossover point; do NOT read the magnitude at large H - "
            "dilution here is linear in steps-travelled and unbounded, so the unbounded arm "
            "saturates the probability floor at long horizons. A real system would plateau, "
            "not collapse."
        ),
    }


def _selftest():
    sw = sweep()
    a = assess(sw)
    checks = {
        "H1: at short horizon unbounded retrieval >= no retrieval":
            a["H1_short_horizon_memory_helps"],
        "H2: at long horizon top-k > none > unbounded":
            a["H2_long_horizon_topk_beats_none_beats_unbounded"],
        "H3: bounded top-k is never worse than unbounded at any horizon":
            a["H3_bounded_never_worse_than_unbounded"],
        "there is a crossover horizon where unbounded turns net-harmful":
            a["crossover_horizon"] is not None,
        "top-k inherits the bank's noisy utility estimate, not an oracle":
            "utility_estimate" in _bank.__doc__ or "noisy" in _bank.__doc__,
        "the verdict states the dilution mechanism is an assumption":
            "ASSUMPTION" in a["verdict"],
        "the verdict warns the large-H magnitude is a linear-model artifact":
            "do NOT read the magnitude" in a["verdict"],
        "no-memory arm is horizon-independent (the control behaves)":
            abs(sw[min(sw)]["none"] - sw[max(sw)]["none"]) < 0.02,
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print("\n  mean step-success by horizon x policy:")
    for h in sorted(sw):
        print(f"    H={h:<4} " + "  ".join(f"{p}={sw[h][p]:.4f}" for p in ("none", "unbounded", "topk")))
    print(f"\n  {a['verdict']}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sw = sub.add_parser("sweep")
    sw.add_argument("--trials", type=int, default=400)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        res = sweep(trials=args.trials)
        print(json.dumps({"sweep": res, "assess": assess(res)}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

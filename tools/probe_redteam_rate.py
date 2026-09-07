#!/usr/bin/env python3
"""What is the optimal rate of red-team challenge before a system can't act? — a runnable rig.

Open research question 4 (`docs/research/open_questions.md`; anchors the red-team-guild
idea from `docs/research/alternative_approaches_part5.md` #48 and
`concept_environmental_pressure_has_an_inverted_u`). Permanent red teams catch abuse
and exploit paths — but challenge every decision and the system stops being able to
act. `open_questions.md` predicts an inverted-U in net value.

This rig sweeps the challenge rate `r` (fraction of decisions a red team formally
challenges). Per decision:

  - a latent defect is present with prob `DEFECT_RATE`.
  - if challenged: the defect is caught with prob `CATCH` (a caught defect is fixed,
    not shipped); the challenge costs `CHALLENGE_COST` of throughput.
  - above `PARALYSIS_KNEE`, each extra unit of `r` also induces *analysis paralysis* —
    the system re-litigates un-challenged decisions too, so effective throughput
    decays super-linearly (agents wait on a review queue, hedge, escalate).

Net value per unit time = (throughput * VALUE_PER_TASK) - (shipped_defects * DEFECT_COST).

Prediction: net value is an inverted-U in `r` — a clear interior optimum, with net
BELOW the r=0 baseline once `r` passes the paralysis knee by enough.

No model call. Swap `CATCH` / the paralysis curve for measured values. Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

SEED = 20261001

DECISIONS = 200
DEFECT_RATE = 0.15
CATCH = 0.85               # P(a challenge catches a present defect)
CHALLENGE_COST = 0.35     # throughput units consumed per challenge (a review is cheaper than a task)
VALUE_PER_TASK = 1.0
DEFECT_COST = 8.0         # a shipped defect costs 8x a completed task's value
PARALYSIS_KNEE = 0.35    # r below this: cost is just the challenges; above: paralysis compounds
PARALYSIS_STRENGTH = 2.2  # exponent on the over-knee excess
PARALYSIS_MULT = 3.4     # scale on the paralysis term


def _throughput(r):
    """Base throughput is DECISIONS; challenges consume some; paralysis above the knee
    consumes a super-linear amount."""
    base_cost = r * DECISIONS * CHALLENGE_COST
    if r > PARALYSIS_KNEE:
        excess = r - PARALYSIS_KNEE
        paralysis = DECISIONS * (excess ** PARALYSIS_STRENGTH) * PARALYSIS_MULT
    else:
        paralysis = 0.0
    return max(0.0, DECISIONS - base_cost - paralysis)


def run_rate(rng, r):
    shipped_defects = 0
    for _ in range(DECISIONS):
        has_defect = rng.random() < DEFECT_RATE
        if not has_defect:
            continue
        challenged = rng.random() < r
        if challenged and rng.random() < CATCH:
            continue                 # caught and fixed
        shipped_defects += 1
    tput = _throughput(r)
    value = tput * VALUE_PER_TASK - shipped_defects * DEFECT_COST
    return {"throughput": tput, "shipped_defects": shipped_defects, "net_value": value}


def sweep(trials=3000, rates=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.65, 0.8, 1.0), rec=None):
    res = {}
    for r in rates:
        agg = {"throughput": 0.0, "shipped_defects": 0.0, "net_value": 0.0}
        for t in range(trials):
            o = run_rate(random.Random(f"{SEED}-{r}-{t}"), r)
            for k in agg:
                agg[k] += o[k]
        res[f"{r}"] = {k: round(v / trials, 2) for k, v in agg.items()}
        if rec:
            rec.claim("probe", f"r={r}: net {res[str(r)]['net_value']}", [f"sim-r-{r}"], layer="swarm")
    return res


def assess(res):
    keys = sorted(res, key=float)
    nets = [(float(k), res[k]["net_value"]) for k in keys]
    best_r, best_net = max(nets, key=lambda kv: kv[1])
    r0_net = res["0.0"]["net_value"]
    r1_net = res["1.0"]["net_value"]
    # inverted-U: the optimum is interior (not at an endpoint) and both ends are lower
    interior = 0.1 < best_r < 0.9
    left_rises = res[keys[1]]["net_value"] > r0_net
    right_falls = r1_net < best_net - 1.0
    both_ends_well_below_optimum = (best_net - r0_net > 20.0) and (best_net - r1_net > 20.0)
    a = {
        "optimum_is_interior": interior,
        "net_rises_from_zero": left_rises,
        "net_falls_after_the_optimum": right_falls,
        "both_endpoints_far_below_the_optimum": both_ends_well_below_optimum,
        "best_rate": best_r,
        "best_net": round(best_net, 2),
        "net_at_r0": round(r0_net, 2),
        "net_at_r1": round(r1_net, 2),
        "verdict": None,
    }
    ok = interior and left_rises and right_falls and both_ends_well_below_optimum
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: net value is an inverted-U in the red-team challenge rate. "
            f"Optimum at r={best_r:.2f} (net {a['best_net']:+.1f}); net at r=0 is {a['net_at_r0']:+.1f} "
            f"(too many shipped defects), net at r=1 is {a['net_at_r1']:+.1f} (paralysis - throughput -> 0). "
            f"Both endpoints are >20 below the interior optimum: under-challenging ships defects, "
            f"over-challenging (past r~{PARALYSIS_KNEE:.2f}) freezes the system.")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: best r={best_r:.2f} net {a['best_net']:+.1f}, r0 {a['net_at_r0']:+.1f}, "
            f"r1 {a['net_at_r1']:+.1f} (interior={interior}, rises={left_rises}, falls={right_falls}, "
            f"ends-below={both_ends_well_below_optimum}).")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="redteam-rate-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "redteam_rate", "open")
    res = sweep(trials=2500, rec=rec)
    rec.step("probe", "redteam_rate", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "the optimal challenge rate is INTERIOR (not 0, not 1)": a["optimum_is_interior"],
        "net value rises as challenge goes from 0 to the first step": a["net_rises_from_zero"],
        "net value falls after the optimum": a["net_falls_after_the_optimum"],
        "both endpoints are far below the interior optimum (> 20)": a["both_endpoints_far_below_the_optimum"],
        "verdict is CONFIRMS": a["verdict"].startswith("CONFIRMS"),
        "trace validates": not errors,
        "trace claims are on the swarm layer": '"layer": "swarm"' in buf.getvalue(),
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  {json.dumps(res, indent=2)}")
    print(f"  verdict: {a['verdict']}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sw = sub.add_parser("sweep")
    sw.add_argument("--trials", type=int, default=3000)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        res = sweep(trials=args.trials)
        print(json.dumps(res, indent=2))
        print("\n" + assess(res)["verdict"])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

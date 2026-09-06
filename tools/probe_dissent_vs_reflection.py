#!/usr/bin/env python3
"""Does structured dissent beat reflection loops for long-horizon harness evolution? — a rig.

Open research question 6 (`docs/research/open_questions.md`; anchors the dramaturgical /
adversarial-collaboration directions and `concept_self_correction_is_mostly_format_repair_not_reasoning`).
A reflection loop (the agent self-critiques each round) is cheap but tends to converge
on plausible-but-wrong lessons — "verbose but low-transfer". Structured dissent (every
proposed harness edit gets a mandatory dissenting implementation, and only the one that
survives a head-to-head keeps) is more expensive per round. The question is whether the
dissent premium compounds over a long horizon.

This rig runs a `HORIZON`-round evolution. The harness has a hidden quality `q` in
[0, 1]. Each round proposes an edit with a true effect `delta` (mostly small positive,
sometimes negative). The two loops differ in what they ACCEPT:

  REFLECTION   the agent self-scores the edit; the self-score is `delta` plus an
               optimism bias and noise. It accepts if the self-score > 0. A biased
               self-score lets negative edits through (drift) - the format-repair trap.
  DISSENT      a dissenting implementation with effect `-alt` is built; both are run on
               a small held-out check; the loop keeps whichever measured better. The
               held-out check is noisy but UNBIASED, so negative edits are usually
               caught - at the cost of building the alternative each round.

Cost model: dissent costs `DISSENT_COST` extra units/round. Net = final quality gain
minus total dissent cost (in quality-equivalent units).

Prediction: over a long horizon, DISSENT reaches a higher final `q` and a higher NET
than REFLECTION, and the gap WIDENS with the horizon (reflection drift compounds).

No model call. Pure stdlib.
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

SEED = 20261003

HORIZONS = (5, 15, 40)
Q0 = 0.35
EDIT_MEAN, EDIT_SD = 0.0, 0.040       # per-round true edit effect (mean-zero: only SELECTION improves q)
REFLECT_OPTIMISM = 0.028             # self-score bias toward accepting (lets negatives through)
REFLECT_NOISE = 0.045
HELDOUT_NOISE = 0.028                # dissent's held-out check noise (unbiased)
DISSENT_COST = 0.0015                # quality-equivalent cost per round of building the alternative


def _edit(rng):
    return rng.gauss(EDIT_MEAN, EDIT_SD)


def _reflection_round(rng, q):
    delta = _edit(rng)
    self_score = delta + REFLECT_OPTIMISM + rng.gauss(0, REFLECT_NOISE)
    if self_score > 0:                       # accept
        return max(0.0, min(1.0, q + delta))
    return q


def _dissent_round(rng, q):
    delta = _edit(rng)
    alt = _edit(rng)                          # the dissenting implementation's true effect
    m_delta = delta + rng.gauss(0, HELDOUT_NOISE)
    m_alt = alt + rng.gauss(0, HELDOUT_NOISE)
    m_keep = rng.gauss(0, HELDOUT_NOISE)      # measured effect of keeping current (= 0 + noise)
    best = max((m_delta, delta), (m_alt, alt), (m_keep, 0.0), key=lambda t: t[0])
    return max(0.0, min(1.0, q + best[1]))


def run_horizon(rng, horizon):
    q_r = q_d = Q0
    for _ in range(horizon):
        q_r = _reflection_round(rng, q_r)
        q_d = _dissent_round(rng, q_d)
    gain_r = q_r - Q0
    gain_d = q_d - Q0
    net_r = gain_r
    net_d = gain_d - DISSENT_COST * horizon
    return {"reflection_q": q_r, "dissent_q": q_d,
            "reflection_net": net_r, "dissent_net": net_d}


def sweep(trials=4000, rec=None):
    res = {}
    for h in HORIZONS:
        agg = {"reflection_q": 0.0, "dissent_q": 0.0, "reflection_net": 0.0, "dissent_net": 0.0}
        for t in range(trials):
            o = run_horizon(random.Random(f"{SEED}-{h}-{t}"), h)
            for k in agg:
                agg[k] += o[k]
        res[f"h{h}"] = {k: round(v / trials, 4) for k, v in agg.items()}
        res[f"h{h}"]["dissent_minus_reflection_q"] = round(
            res[f"h{h}"]["dissent_q"] - res[f"h{h}"]["reflection_q"], 4)
        res[f"h{h}"]["dissent_minus_reflection_net"] = round(
            res[f"h{h}"]["dissent_net"] - res[f"h{h}"]["reflection_net"], 4)
        if rec:
            rec.claim("probe", f"h={h}: dissent-reflection q {res[f'h{h}']['dissent_minus_reflection_q']}",
                      [f"sim-h-{h}"], layer="swarm")
    return res


def assess(res):
    hs = sorted(HORIZONS)
    gaps_q = [res[f"h{h}"]["dissent_minus_reflection_q"] for h in hs]
    gaps_net = [res[f"h{h}"]["dissent_minus_reflection_net"] for h in hs]
    short, long = f"h{hs[0]}", f"h{hs[-1]}"
    a = {
        "dissent_reaches_higher_quality_at_long_horizon":
            res[long]["dissent_q"] > res[long]["reflection_q"] + 0.01,
        "the_quality_gap_widens_with_horizon": gaps_q[-1] > gaps_q[0] + 0.01,
        "dissent_net_positive_vs_reflection_at_long_horizon": gaps_net[-1] > 0,
        "dissent_cost_can_dominate_at_short_horizon": gaps_net[0] < gaps_q[0],
        "gap_q_short": gaps_q[0],
        "gap_q_long": gaps_q[-1],
        "gap_net_short": gaps_net[0],
        "gap_net_long": gaps_net[-1],
        "verdict": None,
    }
    ok = (a["dissent_reaches_higher_quality_at_long_horizon"]
          and a["the_quality_gap_widens_with_horizon"]
          and a["dissent_net_positive_vs_reflection_at_long_horizon"])
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: structured dissent beats reflection for long-horizon evolution and "
            f"the gap WIDENS with the horizon (quality gap {a['gap_q_short']:+.3f} at h={hs[0]} -> "
            f"{a['gap_q_long']:+.3f} at h={hs[-1]}; net gap {a['gap_net_short']:+.3f} -> "
            f"{a['gap_net_long']:+.3f}). Reflection's optimism bias lets negative edits through and the "
            f"drift compounds; dissent's unbiased head-to-head catches them, and the per-round cost is "
            f"amortised over the trajectory.")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: q gap {a['gap_q_short']:+.3f} -> {a['gap_q_long']:+.3f}, net gap "
            f"{a['gap_net_short']:+.3f} -> {a['gap_net_long']:+.3f}.")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="dissent-vs-reflection-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "dissent_vs_reflection", "open")
    res = sweep(trials=3000, rec=rec)
    rec.step("probe", "dissent_vs_reflection", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "dissent reaches higher harness quality at the long horizon":
            a["dissent_reaches_higher_quality_at_long_horizon"],
        "the quality gap WIDENS with the horizon (drift compounds)":
            a["the_quality_gap_widens_with_horizon"],
        "dissent is net-positive vs reflection at the long horizon":
            a["dissent_net_positive_vs_reflection_at_long_horizon"],
        "dissent's per-round cost bites at the short horizon (net gap < quality gap)":
            a["dissent_cost_can_dominate_at_short_horizon"],
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
    sw.add_argument("--trials", type=int, default=4000)
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

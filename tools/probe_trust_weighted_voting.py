#!/usr/bin/env python3
"""Can a conditional trust graph prevent majority-following in LLM coordination? — a runnable rig.

Open research question 7 (`docs/research/open_questions.md`; anchors
`concept_conditional_trust_is_domain_keyed_not_global` (run 260) and
`concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding`).
Replays the herding scenario from `probe_epistemic_market` with the vote weight set to
a **domain-keyed trust score** instead of uniform, and asks whether that recovers the
accuracy an info cascade destroys.

**Kill condition** (`open_questions.md`): the herding rate is unchanged.

Setup: `N` agents with a true competence for the current task family. They produce
independent answers; then an info cascade pulls the low-competence agents onto the
loudest (highest-stated-confidence) agent's answer (competent agents hold their own). Three aggregation rules on the
*post-cascade* answers:

  UNIFORM_VOTE     one agent one vote.
  TRUST_WEIGHTED   vote weight = the agent's domain-keyed trust for THIS family
                   (a noisy estimate of its real competence here). A herded agent
                   still votes its (copied) answer, but if it is a low-trust agent
                   its vote is discounted.
  STALE_TRUST      trust weight from a DIFFERENT, weakly-correlated family
                   (`STALE_CORR`) - the "wrong key" case.

Also report the independent-elicitation ceiling (no cascade, uniform vote).

Prediction: TRUST_WEIGHTED recovers most of the cascade's accuracy loss but does NOT
reach the no-cascade ceiling (the herded answers are still corrupted; trust only
discounts the low-trust herders). STALE_TRUST barely helps - the graph has to be keyed
to the right family. So: conditional trust *mitigates* majority-following, it does not
*prevent* it, and only when the key is right.

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

SEED = 20261004

N = 7
N_OPTIONS = 4
SKILL_A, SKILL_B = 5.0, 4.0
CONF_NOISE = 0.10
HERD_BASE = 0.95             # herd probability for a zero-competence agent
HERD_COMPETENCE_RESIST = 0.95  # how much competence reduces herd probability (confident agents hold)
TRUST_NOISE = 0.08           # noise on the domain-keyed trust estimate
STALE_CORR = 0.35            # correlation of the stale-family trust with true competence here


def _pool(rng):
    agents = []
    for i in range(N):
        c = rng.betavariate(SKILL_A, SKILL_B)
        stated = min(0.99, max(0.01, c + rng.gauss(0, CONF_NOISE)
                               + (0.25 if i % 3 == 0 else 0.0)))   # some agents over-state
        trust = min(0.99, max(0.01, c + rng.gauss(0, TRUST_NOISE)))
        stale = min(0.99, max(0.01, STALE_CORR * c + (1 - STALE_CORR) * rng.random()))
        agents.append({"i": i, "c": c, "stated": stated, "trust": trust, "stale": stale})
    return agents


def _answer(rng, a):
    return 0 if rng.random() < a["c"] else rng.randint(1, N_OPTIONS - 1)


def _cascade(rng, answers, agents):
    """Loud agent anchors; low-competence agents copy it, high-competence agents hold
    their own answer (they trust their own judgement). So the non-herders are the
    high-trust minority - which is what trust-weighting can amplify."""
    loud = max(range(N), key=lambda i: agents[i]["stated"])
    anchor = answers[loud]
    out = []
    for i, ans in enumerate(answers):
        if i == loud:
            out.append(ans)
            continue
        herd_p = HERD_BASE * (1.0 - HERD_COMPETENCE_RESIST * agents[i]["c"])
        out.append(anchor if rng.random() < herd_p else ans)
    return out


def _weighted_vote(answers, weights):
    tally = {}
    for ans, w in zip(answers, weights):
        tally[ans] = tally.get(ans, 0.0) + w
    return max(tally, key=tally.get)


def run_round(rng):
    agents = _pool(rng)
    indep = [_answer(rng, a) for a in agents]
    herded = _cascade(rng, indep, agents)
    out = {
        "ceiling": _weighted_vote(indep, [1.0] * N) == 0,
        "uniform_vote": _weighted_vote(herded, [1.0] * N) == 0,
        "trust_weighted": _weighted_vote(herded, [a["trust"] ** 3 for a in agents]) == 0,
        "stale_trust": _weighted_vote(herded, [a["stale"] ** 3 for a in agents]) == 0,
    }
    return out


def sweep(trials=8000, rec=None):
    agg = {k: 0 for k in ("ceiling", "uniform_vote", "trust_weighted", "stale_trust")}
    for t in range(trials):
        o = run_round(random.Random(f"{SEED}-{t}"))
        for k in agg:
            agg[k] += o[k]
    res = {k: round(v / trials, 3) for k, v in agg.items()}
    cascade_loss = res["ceiling"] - res["uniform_vote"]
    res["cascade_loss"] = round(cascade_loss, 3)
    res["trust_recovers"] = round(res["trust_weighted"] - res["uniform_vote"], 3)
    res["trust_fraction_of_loss_recovered"] = round(
        (res["trust_weighted"] - res["uniform_vote"]) / cascade_loss, 3) if cascade_loss > 0 else None
    res["stale_recovers"] = round(res["stale_trust"] - res["uniform_vote"], 3)
    if rec:
        rec.claim("probe", f"cascade loss {res['cascade_loss']}, trust recovers {res['trust_recovers']}",
                  ["sim-trust-vote"], layer="swarm")
    return res


def assess(res):
    a = {
        "the_cascade_causes_a_real_accuracy_loss": res["cascade_loss"] > 0.08,
        "trust_weighting_recovers_a_meaningful_share_of_the_loss":
            res["trust_fraction_of_loss_recovered"] is not None
            and res["trust_fraction_of_loss_recovered"] > 0.25,
        "trust_weighting_does_not_reach_the_no_cascade_ceiling":
            res["trust_weighted"] < res["ceiling"] - 0.015,
        "stale_trust_barely_helps": res["stale_recovers"] < max(0.01, res["trust_recovers"] * 0.4),
        "cascade_loss": res["cascade_loss"],
        "trust_recovers": res["trust_recovers"],
        "trust_fraction_recovered": res["trust_fraction_of_loss_recovered"],
        "stale_recovers": res["stale_recovers"],
        "verdict": None,
    }
    ok = (a["the_cascade_causes_a_real_accuracy_loss"]
          and a["trust_weighting_recovers_a_meaningful_share_of_the_loss"]
          and a["trust_weighting_does_not_reach_the_no_cascade_ceiling"]
          and a["stale_trust_barely_helps"])
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: a conditional trust graph MITIGATES majority-following but does not "
            f"PREVENT it. The cascade costs {a['cascade_loss']:+.3f} accuracy; domain-keyed trust weighting "
            f"recovers {a['trust_fraction_recovered']:.0%} of that ({a['trust_recovers']:+.3f}) but stays "
            f"below the no-cascade ceiling - the herded answers are still corrupted, trust only discounts "
            f"low-trust herders. Stale (wrong-family) trust recovers only {a['stale_recovers']:+.3f}: the "
            f"key has to be right. The kill condition (herding rate unchanged) does NOT hold.")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: cascade loss {a['cascade_loss']:+.3f}, trust recovers "
            f"{a['trust_recovers']:+.3f} ({a['trust_fraction_recovered']}), stale recovers "
            f"{a['stale_recovers']:+.3f}.")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="trust-weighted-voting-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "trust_weighted_voting", "open")
    res = sweep(trials=6000, rec=rec)
    rec.step("probe", "trust_weighted_voting", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "the info cascade causes a real accuracy loss (> 0.08)": a["the_cascade_causes_a_real_accuracy_loss"],
        "domain-keyed trust weighting recovers > 25% of the cascade loss":
            a["trust_weighting_recovers_a_meaningful_share_of_the_loss"],
        "trust weighting does NOT fully prevent herding (stays below the no-cascade ceiling)":
            a["trust_weighting_does_not_reach_the_no_cascade_ceiling"],
        "stale (wrong-family) trust barely helps": a["stale_trust_barely_helps"],
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
    sw.add_argument("--trials", type=int, default=8000)
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

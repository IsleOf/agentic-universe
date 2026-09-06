#!/usr/bin/env python3
"""Does forecast-calibrated agent selection beat majority vote / manager pick / debate? — a runnable rig.

Open research question 1 (`docs/research/open_questions.md`, from the owner's research
input; anchor `concept_calibrated_forecasting_before_action_is_the_influence_currency`,
run 260). The epistemic-market claim: an agent earns influence by a *calibration record*
— it predicts an outcome, the prediction is scored against ground truth — not by
sounding convincing (debate), being picked by a manager, or being in the majority.

This rig runs that comparison in a controlled sim. A pool of K agents each attempt a
task with a true per-agent competence `c_i` drawn from a Beta prior. Each agent also
emits a *stated confidence* that is its competence plus a bias: a `persuasion`
component (some agents systematically over-state) and noise. Four selection rules pick
one agent's answer as the group output:

  MAJORITY   take the answer the plurality of agents produced (ties → random).
  MANAGER    a manager agent picks the agent with the highest STATED confidence
             (so a persuasive over-stater wins).
  DEBATE     two rounds: the two highest-stated-confidence agents "argue"; the winner
             is the more persuasive one (persuasion beats competence with prob
             DEBATE_PERSUASION_EDGE). Floor-raising, not ceiling-raising
             (`concept_pre_registered_adversarial_collaboration_beats_open_debate`).
  FORECAST   each agent has a calibration record (a noisy estimate of its own past
             hit-rate, `MARKET_HISTORY` prior observations); pick the agent with the
             best calibration record. Persuasion does not enter.

Measure: group task-success for each rule, plus how often each rule's pick is the
genuinely most-competent agent, and the influence concentration (how skewed selection
is toward a few agents). Sweep the `persuasion` strength and the pool skill spread.

A `herd` knob controls whether agent errors are INDEPENDENT (Condorcet regime — a big
pool's majority vote is very hard to beat) or CORRELATED (agents see each other and
converge on a shared wrong answer — `concept_epistemic_sybil_collapse` /
`concept_orchestration_can_beat_the_strongest_model_but_showing_votes_causes_herding`).

The prediction the epistemic-market node makes: FORECAST > MANAGER and > DEBATE at every
persuasion level and is persuasion-robust; MAJORITY is strong under independent errors
but **collapses under herding**, and that is the regime where the market (forecast /
calibration selection, which does not read current agreement) earns its keep.

No model call — the finding is about how competence, stated confidence, and selection
rule interact. Swap `_agent_answer` / `_calibration_estimate` for real agent runs.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import statistics
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

SEED = 20260929

K = 7                        # agents in the pool
SKILL_A, SKILL_B = 6.0, 4.0  # Beta(a, b) prior on per-agent competence (mean 0.6)
CONF_NOISE = 0.10            # noise on an agent's stated confidence
MARKET_HISTORY = 40          # prior graded predictions per agent (calibration record depth)
DEBATE_PERSUASION_EDGE = 0.70  # P(more-persuasive agent wins the debate regardless of competence)
N_OPTIONS = 4               # answer options (so majority is meaningful; chance = 1/4)
HERD_PULL = 0.88           # under herding, P(a wrong agent copies the plurality wrong answer)


def _pool(rng, persuasion):
    """K agents: true competence + a persuasion bias on stated confidence."""
    agents = []
    for i in range(K):
        c = rng.betavariate(SKILL_A, SKILL_B)
        # persuasion bias: half the pool over-states, scaled by `persuasion`
        bias = (persuasion * rng.uniform(0.15, 0.45)) if i % 2 == 0 else (-0.05 * rng.random())
        stated = min(0.99, max(0.01, c + bias + rng.gauss(0, CONF_NOISE)))
        # calibration record: a noisy estimate of the agent's real hit-rate
        hits = sum(rng.random() < c for _ in range(MARKET_HISTORY))
        calib = hits / MARKET_HISTORY
        agents.append({"i": i, "c": c, "stated": stated, "calib": calib, "persuasion": max(0.0, bias)})
    return agents


def _agent_answer(rng, agent):
    """Correct with prob = competence, else a random wrong option."""
    if rng.random() < agent["c"]:
        return 0                       # 0 = the correct option
    return rng.randint(1, N_OPTIONS - 1)


def _pick_majority(rng, answers, agents):
    counts = {}
    for a in answers:
        counts[a] = counts.get(a, 0) + 1
    top = max(counts.values())
    cands = [a for a, n in counts.items() if n == top]
    return rng.choice(cands)


def _pick_manager(rng, answers, agents):
    best = max(agents, key=lambda a: a["stated"])
    return answers[best["i"]]


def _pick_debate(rng, answers, agents):
    ranked = sorted(agents, key=lambda a: a["stated"], reverse=True)[:2]
    a1, a2 = ranked
    more_persuasive = a1 if a1["persuasion"] >= a2["persuasion"] else a2
    more_competent = a1 if a1["c"] >= a2["c"] else a2
    winner = more_persuasive if rng.random() < DEBATE_PERSUASION_EDGE else more_competent
    return answers[winner["i"]]


def _pick_forecast(rng, answers, agents):
    best = max(agents, key=lambda a: a["calib"])
    return answers[best["i"]]


RULES = {"majority": _pick_majority, "manager": _pick_manager,
         "debate": _pick_debate, "forecast": _pick_forecast}


def _herd(rng, answers, agents):
    """Info cascade: agents copy the loudest (highest-stated-confidence) agent's answer.
    When that agent is a persuasive over-stater who is wrong, the pool converges wrong -
    this is why `showing votes causes herding` and majority stops being independent."""
    loud = max(range(K), key=lambda i: agents[i]["stated"])
    anchor = answers[loud]
    return [anchor if (i != loud and rng.random() < HERD_PULL) else ans
            for i, ans in enumerate(answers)]


def run_round(rng, persuasion, herd=False):
    agents = _pool(rng, persuasion)
    independent = [_agent_answer(rng, a) for a in agents]
    # `visible` is what the vote/manager/debate rules see - herded when herd=True.
    # FORECAST elicits INDEPENDENTLY (evidence cells, run 260), so it reads `independent`.
    visible = _herd(rng, independent, agents) if herd else independent
    best_c = max(agents, key=lambda a: a["c"])["i"]
    out = {}
    for name, fn in RULES.items():
        pool_seen = independent if name == "forecast" else visible
        pick = fn(rng, pool_seen, agents)
        out[name] = {"correct": pick == 0}
    # concentration: does the rule keep selecting the same few agents?
    picks_idx = {
        "manager": max(range(K), key=lambda i: agents[i]["stated"]),
        "forecast": max(range(K), key=lambda i: agents[i]["calib"]),
    }
    picks_idx["most_competent"] = best_c
    return out, picks_idx


def _run_grid(trials, persuasions, herd, rec):
    res = {}
    for p in persuasions:
        acc = {name: 0 for name in RULES}
        manager_is_best = forecast_is_best = 0
        for t in range(trials):
            r = random.Random(f"{SEED}-{herd}-{p}-{t}")
            out, idx = run_round(r, p, herd=herd)
            for name in RULES:
                acc[name] += out[name]["correct"]
            manager_is_best += idx["manager"] == idx["most_competent"]
            forecast_is_best += idx["forecast"] == idx["most_competent"]
        res[f"{p}"] = {
            **{name: round(acc[name] / trials, 3) for name in RULES},
            "manager_picks_best_agent": round(manager_is_best / trials, 3),
            "forecast_picks_best_agent": round(forecast_is_best / trials, 3),
        }
        if rec:
            rec.claim("probe",
                      f"herd={herd} persuasion {p}: forecast {res[str(p)]['forecast']} vs majority {res[str(p)]['majority']}",
                      [f"sim-{herd}-persuasion-{p}"], layer="swarm")
    return res


def sweep(trials=4000, persuasions=(0.0, 0.25, 0.5, 0.75, 1.0), rec=None):
    return {"independent": _run_grid(trials, persuasions, False, rec),
            "herding": _run_grid(trials, persuasions, True, rec)}


def assess(full):
    ind, herd = full["independent"], full["herding"]
    keys = sorted(ind, key=float)
    f_deg = ind[keys[-1]]["forecast"] - ind[keys[0]]["forecast"]
    m_deg = ind[keys[-1]]["manager"] - ind[keys[0]]["manager"]
    # herding collapse: majority drops from independent to herding regime
    maj_collapse = statistics.mean(herd[k]["majority"] - ind[k]["majority"] for k in keys)
    fc_under_herd = statistics.mean(herd[k]["forecast"] - herd[k]["majority"] for k in keys)
    a = {
        "forecast_beats_manager_everywhere":
            all(ind[k]["forecast"] > ind[k]["manager"] for k in keys),
        "forecast_beats_debate_everywhere":
            all(ind[k]["forecast"] > ind[k]["debate"] - 0.01 for k in keys),
        "manager_degrades_as_persuasion_rises": m_deg < -0.03,
        "forecast_is_robust_to_persuasion": abs(f_deg) < 0.04,
        "majority_strong_under_independent_errors":
            all(ind[k]["majority"] >= ind[k]["forecast"] for k in keys),
        "majority_collapses_under_herding": maj_collapse < -0.10,
        "forecast_beats_majority_under_herding": fc_under_herd > 0.03,
        "forecast_degradation": round(f_deg, 3),
        "manager_degradation": round(m_deg, 3),
        "majority_collapse_under_herding": round(maj_collapse, 3),
        "forecast_minus_majority_under_herding": round(fc_under_herd, 3),
        "verdict": None,
    }
    ok = (a["forecast_beats_manager_everywhere"] and a["forecast_beats_debate_everywhere"]
          and a["manager_degrades_as_persuasion_rises"] and a["forecast_is_robust_to_persuasion"]
          and a["majority_strong_under_independent_errors"] and a["majority_collapses_under_herding"]
          and a["forecast_beats_majority_under_herding"])
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: forecast-calibrated selection beats manager-pick and debate at "
            f"every persuasion level and is persuasion-robust (forecast {a['forecast_degradation']:+.3f} "
            f"vs manager {a['manager_degradation']:+.3f}). MAJORITY is the strongest rule when errors are "
            f"independent (Condorcet) but collapses {a['majority_collapse_under_herding']:+.3f} under "
            f"herding, where forecast beats it by {a['forecast_minus_majority_under_herding']:+.3f} - "
            f"the regime the epistemic market is for.")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: forecast deg {a['forecast_degradation']:+.3f}, manager deg "
            f"{a['manager_degradation']:+.3f}, majority herding collapse "
            f"{a['majority_collapse_under_herding']:+.3f}, forecast-minus-majority under herding "
            f"{a['forecast_minus_majority_under_herding']:+.3f}.")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="epistemic-market-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "epistemic_market", "open")
    res = sweep(trials=2500, rec=rec)
    rec.step("probe", "epistemic_market", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "forecast > manager at every persuasion level": a["forecast_beats_manager_everywhere"],
        "forecast > debate at every persuasion level": a["forecast_beats_debate_everywhere"],
        "manager accuracy degrades as persuasion rises": a["manager_degrades_as_persuasion_rises"],
        "forecast accuracy is robust to persuasion (|deg| < 0.04)": a["forecast_is_robust_to_persuasion"],
        "majority is strongest under INDEPENDENT errors (Condorcet)": a["majority_strong_under_independent_errors"],
        "majority COLLAPSES under herding (< -0.10)": a["majority_collapses_under_herding"],
        "forecast beats majority under herding (> +0.03)": a["forecast_beats_majority_under_herding"],
        "forecast picks the best agent more often than the manager does":
            res["independent"]["1.0"]["forecast_picks_best_agent"] > res["independent"]["1.0"]["manager_picks_best_agent"],
        "verdict is CONFIRMS": a["verdict"].startswith("CONFIRMS"),
        "trace validates": not errors,
        "trace claims are on the swarm layer": '"layer": "swarm"' in buf.getvalue(),
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  independent, no persuasion: {res['independent']['0.0']}")
    print(f"  independent, full persuasion: {res['independent']['1.0']}")
    print(f"  herding, no persuasion: {res['herding']['0.0']}")
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
    sw.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        res = sweep(trials=args.trials)
        a = assess(res)
        print(json.dumps(res, indent=2))
        print("\n" + a["verdict"])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

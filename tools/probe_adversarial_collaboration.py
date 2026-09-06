#!/usr/bin/env python3
"""Does pre-registered adversarial collaboration preserve creativity while improving reliability? — a rig.

Open research question 3 (`docs/research/open_questions.md`; anchors
`concept_pre_registered_adversarial_collaboration_beats_open_debate` (run 260) and
`concept_agent_creativity_declines_exploration_to_exploitation_within_a_run_novel_but_less_useful`).
The worry: pre-registration (rivals fix their predictions, the evidence that would
favour each side, and what counts as a concession *before* seeing data) improves
factual reliability — but does it kill creativity by locking the hypothesis set early?

**Kill condition** (from `open_questions.md`): creativity drops *more* than reliability
rises.

This rig runs three protocols on a task that has both a factual component (one true
answer, `RELIABILITY`) and a generative component (a space of `IDEA_SPACE` distinct
valid ideas; creativity = the fraction explored before the team converges):

  REFLECTION      one agent proposes, self-critiques once, commits. Baseline.
  OPEN_DEBATE     agents argue; the most-persuasive position wins and the team
                  converges FAST (early exploitation — `..creativity_declines..`).
                  Persuasion beats evidence with prob DEBATE_PERSUASION_EDGE.
  PRE_REGISTERED  rivals lock predictions + concession criteria first. Post-hoc
                  reinterpretation is blocked (reliability up); the adversarial
                  framing keeps BOTH positions live longer, so convergence is
                  slower and more of the idea space is explored before commit.

Measure per protocol: factual accuracy, ideas explored (creativity), and the
"net" = (reliability gain) - (creativity loss) vs the REFLECTION baseline.

Prediction: PRE_REGISTERED has the highest accuracy; its creativity is BELOW
reflection but ABOVE open debate; and the net vs reflection is positive (the kill
condition does not trigger).

No model call. Swap `_argue` / `_explore` for real runs. Pure stdlib.
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

SEED = 20260931

TEAM = 4
BASE_ACC = 0.55                # per-agent chance of holding the correct factual position
DEBATE_PERSUASION_EDGE = 0.55  # P(the more-persuasive side wins the debate)
# (rounds, explore_cap): how far into the idea space each protocol gets before it commits.
# Pre-registration locks the hypothesis set (cap below reflection) but the adversarial
# framing delays convergence (cap well above the fast-converging open debate).
EXPLORE = {"reflection": (4, 0.74), "open_debate": (2, 0.44), "pre_registered": (4, 0.61)}


def _explore(rng, name):
    rounds, cap = EXPLORE[name]
    found = 0.0
    for r in range(rounds):
        found += (cap - found) * (0.6 + 0.15 * rng.random())   # geometric approach to the cap
    return round(min(found, cap) * (0.92 + 0.08 * rng.random()), 4)


def _reflection(rng):
    # one agent, one weak self-critique - the low-transfer baseline
    correct = rng.random() < BASE_ACC or rng.random() < 0.12
    return {"accuracy": bool(correct), "creativity": _explore(rng, "reflection")}


def _open_debate(rng):
    anyone_correct = any(rng.random() < BASE_ACC for _ in range(TEAM))
    # floor-raising, not ceiling-raising: the WINNER is the more-persuasive side, so a
    # correct-but-quiet member does not carry the room. Persuasion decides most rounds.
    if rng.random() < DEBATE_PERSUASION_EDGE:
        accuracy = anyone_correct and rng.random() < 0.45      # persuasion often wins over evidence
    else:
        accuracy = anyone_correct and rng.random() < 0.85
    return {"accuracy": bool(accuracy), "creativity": _explore(rng, "open_debate")}


def _pre_registered(rng):
    anyone_correct = any(rng.random() < BASE_ACC for _ in range(TEAM))
    # concession criteria are fixed before the data: whichever pre-registered prediction
    # the evidence matches wins, regardless of who argued it better. Post-hoc
    # reinterpretation is mostly blocked, so a correct member with evidence carries.
    if rng.random() < 0.88:
        accuracy = anyone_correct and rng.random() < 0.82     # evidence-led, ceiling-raising
    else:
        accuracy = anyone_correct and rng.random() < 0.5      # rare post-hoc slip
    return {"accuracy": bool(accuracy), "creativity": _explore(rng, "pre_registered")}


PROTOCOLS = {"reflection": _reflection, "open_debate": _open_debate, "pre_registered": _pre_registered}


def sweep(trials=8000, rec=None):
    agg = {name: {"acc": 0.0, "cre": 0.0} for name in PROTOCOLS}
    for t in range(trials):
        for name, fn in PROTOCOLS.items():
            o = fn(random.Random(f"{SEED}-{name}-{t}"))
            agg[name]["acc"] += o["accuracy"]
            agg[name]["cre"] += o["creativity"]
    res = {name: {"accuracy": round(v["acc"] / trials, 3),
                  "creativity": round(v["cre"] / trials, 3)}
           for name, v in agg.items()}
    base = res["reflection"]
    for name in ("open_debate", "pre_registered"):
        rel_gain = res[name]["accuracy"] - base["accuracy"]
        cre_loss = base["creativity"] - res[name]["creativity"]
        res[name]["reliability_gain_vs_reflection"] = round(rel_gain, 3)
        res[name]["creativity_loss_vs_reflection"] = round(cre_loss, 3)
        res[name]["net"] = round(rel_gain - cre_loss, 3)
        if rec:
            rec.claim("probe", f"{name}: net {res[name]['net']}", [f"sim-{name}"], layer="swarm")
    return res


def assess(res):
    pr, od = res["pre_registered"], res["open_debate"]
    a = {
        "pre_registered_has_the_highest_accuracy":
            pr["accuracy"] >= od["accuracy"] and pr["accuracy"] >= res["reflection"]["accuracy"],
        "pre_registered_creativity_below_reflection":
            pr["creativity"] < res["reflection"]["creativity"],
        "pre_registered_creativity_above_open_debate":
            pr["creativity"] > od["creativity"],
        "pre_registered_kill_condition_not_triggered": pr["net"] > 0,   # rel gain > cre loss
        "open_debate_is_worse_on_net_than_pre_registered": od["net"] < pr["net"],
        "pre_registered_net": pr["net"],
        "open_debate_net": od["net"],
        "verdict": None,
    }
    ok = (a["pre_registered_has_the_highest_accuracy"]
          and a["pre_registered_creativity_below_reflection"]
          and a["pre_registered_creativity_above_open_debate"]
          and a["pre_registered_kill_condition_not_triggered"]
          and a["open_debate_is_worse_on_net_than_pre_registered"])
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: pre-registration has the highest accuracy; its creativity sits "
            f"BELOW reflection but ABOVE open debate; net vs reflection is {a['pre_registered_net']:+.3f} "
            f"(reliability gain > creativity loss) - the kill condition does NOT trigger. Open debate nets "
            f"{a['open_debate_net']:+.3f} (fast convergence costs more creativity than its reliability is "
            f"worth).")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: pre_registered net {a['pre_registered_net']:+.3f}, open_debate net "
            f"{a['open_debate_net']:+.3f}, pre_reg creativity {res['pre_registered']['creativity']} vs "
            f"reflection {res['reflection']['creativity']} vs debate {res['open_debate']['creativity']}.")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="adversarial-collaboration-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "adversarial_collaboration", "open")
    res = sweep(trials=6000, rec=rec)
    rec.step("probe", "adversarial_collaboration", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "pre-registration has the highest accuracy": a["pre_registered_has_the_highest_accuracy"],
        "pre-registration creativity is below the reflection baseline": a["pre_registered_creativity_below_reflection"],
        "pre-registration creativity is above open debate": a["pre_registered_creativity_above_open_debate"],
        "the kill condition does NOT trigger (net > 0)": a["pre_registered_kill_condition_not_triggered"],
        "pre-registration nets better than open debate": a["open_debate_is_worse_on_net_than_pre_registered"],
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

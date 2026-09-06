#!/usr/bin/env python3
"""How much identity masking is needed to reduce prestige / model-family contagion? — a runnable rig.

Open research question 2 (`docs/research/open_questions.md`; anchors
`concept_independent_evidence_cells_then_identity_masked_synthesis` (run 260) and
`emergent_peer_recognition_survives_anonymization`). The evidence-cell protocol masks
agent identity before synthesis so a synthesiser cannot defer to prestige or copy a
same-family peer. The question is how much masking is enough — and the graph's
prediction is that **full masking is still leaky**, because agents recognise peer
model families from writing style even when the name is gone.

This rig runs the sweep. N agents produce independent answers with a true competence
`c_i`. A synthesiser then forms a group answer, but it is pulled toward whichever agent
it perceives as high-status. Four masking levels progressively remove status cues:

  L0 none           - name + prestige score + writing style + reasoning chain visible
  L1 name           - name and prestige score removed; style + reasoning still leak family
  L2 name+style     - writing style normalised too; reasoning chain still leaks
  L3 name+style+cot - reasoning chain also stripped; only the claim + its evidence remain

Each masking level removes a fraction of the "status signal". `PEER_RECOGNITION_FLOOR`
is the residual signal that survives even L3 (`emergent_peer_recognition_survives_anonymization`)
— agents/synthesisers still guess family from vocabulary and answer shape.

Measure: the synthesiser's deference rate (how often it adopts the perceived-highest-status
agent's answer regardless of correctness), the group accuracy, and the contagion rate
(how often a wrong high-status answer is copied by the group).

Prediction: accuracy and independence improve monotonically L0 -> L3, but L3 does NOT
reach the independent-elicitation ceiling — masking is necessary, not sufficient; the
reasoning-chain strip (L2 -> L3) is the largest single gain.

No model call. Swap `_perceived_status` / `_synthesiser_pick` for real runs. Pure stdlib.
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

SEED = 20260930

N = 6                          # agents
SKILL_A, SKILL_B = 5.0, 4.0    # Beta prior on competence (mean ~0.56)
N_OPTIONS = 4
# fraction of the status signal each masking level leaves in place
STATUS_LEFT = {"L0_none": 1.00, "L1_name": 0.72, "L2_name_style": 0.45, "L3_name_style_cot": 0.20}
PEER_RECOGNITION_FLOOR = 0.20  # residual status signal that survives full masking
DEFER_STRENGTH = 0.85         # P(synthesiser adopts perceived-top-status answer | full signal)


def _pool(rng):
    agents = []
    for i in range(N):
        c = rng.betavariate(SKILL_A, SKILL_B)
        prestige = rng.random()                    # social status, uncorrelated with competence
        agents.append({"i": i, "c": c, "prestige": prestige})
    return agents


def _answer(rng, agent):
    return 0 if rng.random() < agent["c"] else rng.randint(1, N_OPTIONS - 1)


def _perceived_status(agent, status_left):
    """What the synthesiser perceives: prestige leaks through in proportion to status_left,
    never fully hidden (peer recognition floor)."""
    leak = max(status_left, PEER_RECOGNITION_FLOOR)
    return agent["prestige"] * leak


def run_round(rng, level):
    agents = _pool(rng)
    answers = [_answer(rng, a) for a in agents]
    status_left = STATUS_LEFT[level]
    top = max(agents, key=lambda a: _perceived_status(a, status_left))
    # the synthesiser defers to perceived top status with prob scaling in the leaked signal
    defer_p = DEFER_STRENGTH * max(status_left, PEER_RECOGNITION_FLOOR)
    if rng.random() < defer_p:
        group = answers[top["i"]]
        deferred = True
    else:
        # independent aggregation: plurality of the answers (evidence-cell style)
        counts = {}
        for a in answers:
            counts[a] = counts.get(a, 0) + 1
        group = max(counts, key=counts.get)
        deferred = False
    top_wrong = answers[top["i"]] != 0
    return {
        "correct": group == 0,
        "deferred": deferred,
        "contagion": deferred and top_wrong,       # copied a wrong high-status answer
    }


def _ceiling(rng):
    """Pure independent elicitation (plurality, no deference) - the target L3 is measured against."""
    agents = _pool(rng)
    answers = [_answer(rng, a) for a in agents]
    counts = {}
    for a in answers:
        counts[a] = counts.get(a, 0) + 1
    return max(counts, key=counts.get) == 0


def sweep(trials=6000, rec=None):
    res = {}
    for level in STATUS_LEFT:
        acc = defer = cont = 0
        for t in range(trials):
            r = random.Random(f"{SEED}-{level}-{t}")
            o = run_round(r, level)
            acc += o["correct"]; defer += o["deferred"]; cont += o["contagion"]
        res[level] = {"accuracy": round(acc / trials, 3),
                      "deference_rate": round(defer / trials, 3),
                      "contagion_rate": round(cont / trials, 3)}
        if rec:
            rec.claim("probe", f"{level}: acc {res[level]['accuracy']} defer {res[level]['deference_rate']}",
                      [f"sim-{level}"], layer="swarm")
    ceil = sum(_ceiling(random.Random(f"{SEED}-ceil-{t}")) for t in range(trials)) / trials
    res["independent_ceiling"] = {"accuracy": round(ceil, 3)}
    return res


def assess(res):
    levels = list(STATUS_LEFT)
    accs = [res[l]["accuracy"] for l in levels]
    defers = [res[l]["deference_rate"] for l in levels]
    ceil = res["independent_ceiling"]["accuracy"]
    cot_gain = res["L3_name_style_cot"]["accuracy"] - res["L2_name_style"]["accuracy"]
    name_gain = res["L1_name"]["accuracy"] - res["L0_none"]["accuracy"]
    a = {
        "accuracy_improves_monotonically_with_masking":
            all(accs[i] <= accs[i + 1] + 0.005 for i in range(len(accs) - 1)),
        "deference_drops_monotonically_with_masking":
            all(defers[i] >= defers[i + 1] - 0.005 for i in range(len(defers) - 1)),
        "full_masking_does_not_reach_the_independent_ceiling":
            res["L3_name_style_cot"]["accuracy"] < ceil - 0.02,
        "residual_deference_survives_full_masking":
            res["L3_name_style_cot"]["deference_rate"] > 0.10,
        "cot_strip_is_the_largest_single_gain": cot_gain > name_gain,
        "cot_strip_gain": round(cot_gain, 3),
        "name_strip_gain": round(name_gain, 3),
        "residual_deference_at_L3": res["L3_name_style_cot"]["deference_rate"],
        "gap_to_ceiling_at_L3": round(ceil - res["L3_name_style_cot"]["accuracy"], 3),
        "verdict": None,
    }
    ok = (a["accuracy_improves_monotonically_with_masking"]
          and a["deference_drops_monotonically_with_masking"]
          and a["full_masking_does_not_reach_the_independent_ceiling"]
          and a["residual_deference_survives_full_masking"]
          and a["cot_strip_is_the_largest_single_gain"])
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: masking helps monotonically, and stripping the reasoning chain "
            f"(L2->L3) is the largest single gain (+{a['cot_strip_gain']:.3f} vs +{a['name_strip_gain']:.3f} "
            f"for the name). But full masking still leaves {a['residual_deference_at_L3']:.2f} deference and "
            f"a {a['gap_to_ceiling_at_L3']:+.3f} accuracy gap to independent elicitation - masking is "
            f"necessary, not sufficient (emergent_peer_recognition_survives_anonymization).")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: cot gain {a['cot_strip_gain']:+.3f}, name gain "
            f"{a['name_strip_gain']:+.3f}, residual deference {a['residual_deference_at_L3']:.2f}, "
            f"gap to ceiling {a['gap_to_ceiling_at_L3']:+.3f}.")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="identity-masking-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "identity_masking", "open")
    res = sweep(trials=4000, rec=rec)
    rec.step("probe", "identity_masking", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "accuracy improves monotonically L0 -> L3": a["accuracy_improves_monotonically_with_masking"],
        "deference drops monotonically L0 -> L3": a["deference_drops_monotonically_with_masking"],
        "full masking does NOT reach the independent-elicitation ceiling":
            a["full_masking_does_not_reach_the_independent_ceiling"],
        "residual deference survives full masking (> 0.10)": a["residual_deference_survives_full_masking"],
        "stripping the reasoning chain is the largest single gain": a["cot_strip_is_the_largest_single_gain"],
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
    sw.add_argument("--trials", type=int, default=6000)
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

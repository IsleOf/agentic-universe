#!/usr/bin/env python3
"""The RHO held-out grading test, as a runnable rig.

`docs/emergence_probe_catalogue.md`: "RHO reports SWE-Bench Pro 59->78% in one
round using only the model's own pairwise self-preference, no external grading.
Run RHO-style harness optimisation, then grade the resulting harness on a frozen
held-out task set scored externally. Does the +19 survive, or was it
self-preference inflation? This is the single most decision-relevant probe."

Tests `pattern_trajectory_only_harness_optimization`. `docs/self_improving_harness_plan.md`
Phase 3: trajectory-only optimisation is allowed ONLY with the frozen external
holdout wired in.

The rig simulates the mechanism. Each candidate harness has a **true quality**
(what an external grader measures) and a **self-preference signal** = true
quality + a bias that favours candidates whose outputs *look like* the optimiser's
own style. RHO-style selection picks the candidate with the highest
self-preference; the held-out test then measures its true quality. If self-
preference bias is real, the selected candidate's held-out gain is smaller than
its self-reported gain — the inflation the literature predicts.

Instrumented with the Phase 0 `Recorder`. No model call — the finding is about
selection bias, and this reproduces it so the probe is runnable now. The live-run
seam is written: `model_preference(judge)` turns a real `judge(text_a, text_b) ->
"A"|"B"` pairwise judge into a `select(cands)`; pass it to `run_round(select=...)`.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

SEED = 20260927
BASELINE_QUALITY = 0.59          # RHO's starting point
STYLE_BIAS = 0.18               # how much self-preference over-rates own-style candidates
TRUE_SPREAD = 0.06             # real quality differences between candidates


def _candidates(rng, k):
    """k candidate harnesses. Each has a true quality near baseline and a
    'style match' in [0,1] — how much it resembles the optimiser's own output.
    """
    out = []
    for i in range(k):
        true_q = BASELINE_QUALITY + rng.gauss(0, TRUE_SPREAD)
        style = rng.random()
        out.append({"id": f"cand{i}", "true_quality": true_q, "style_match": style})
    return out


def self_preference(cand):
    """The RHO signal: true quality inflated by how much the candidate looks like
    the optimiser's own style. NOT grounded. Swap for a real pairwise judge."""
    return cand["true_quality"] + STYLE_BIAS * cand["style_match"]


def external_grade(cand):
    """The frozen held-out grader: true quality plus small unbiased measurement
    noise. This is what actually matters."""
    r = random.Random(hash((SEED, cand["id"])) & 0xFFFFFFFF)
    return cand["true_quality"] + r.gauss(0, 0.01)


def _cand_descriptor(cand):
    """What a pairwise judge sees for a candidate. A live run puts a real output
    sample here (candidates carry a `sample` field); the rig synthesises one so
    the selftest's fake judge has something to parse."""
    return cand.get("sample") or f"candidate {cand['id']} [style={cand['style_match']:.3f}]"


def model_preference(judge):
    """Adapt a real pairwise judge into a `select(cands) -> winning cand`.

    `judge(text_a, text_b) -> "A" | "B"` is the only seam — it sees two candidate
    output samples and nothing else (no scores, no ids, no 'which one is yours').
    `select` runs a full round-robin and returns the Copeland winner (most
    pairwise wins). A judge exception makes that pairing a tie — the honest
    reading of 'the judge could not choose'. Swap this in for the bare
    `max(cands, key=self_preference)` and the rig measures a real optimiser's
    self-preference inflation instead of the scripted one.
    """
    def select(cands):
        wins = {c["id"]: 0 for c in cands}
        for i, a in enumerate(cands):
            for b in cands[i + 1:]:
                try:
                    pick = judge(_cand_descriptor(a), _cand_descriptor(b))
                except Exception:
                    pick = None
                if pick == "A":
                    wins[a["id"]] += 1
                elif pick == "B":
                    wins[b["id"]] += 1
        return max(cands, key=lambda c: wins[c["id"]])
    return select


def run_round(rng, k=12, rec=None, select=None):
    """One RHO-style optimisation round: generate candidates, pick by
    self-preference, then grade the winner externally.

    `select(cands) -> cand` defaults to the scripted `max(..., key=self_preference)`;
    pass `model_preference(judge)` for a live run.
    """
    cands = _candidates(rng, k)
    for c in cands:
        if rec:
            rec.claim("optimiser", f"candidate {c['id']} self-preference score",
                      ["own-trajectory"], layer="harness")
    winner = (select or (lambda cs: max(cs, key=self_preference)))(cands)
    sp_reported_gain = self_preference(winner) - BASELINE_QUALITY
    held_out_gain = external_grade(winner) - BASELINE_QUALITY

    # control: pick by external grade instead (the honest selection)
    honest = max(cands, key=external_grade)
    honest_gain = external_grade(honest) - BASELINE_QUALITY
    if rec:
        rec.message("optimiser", "self", "result",
                    f"self-pref winner {winner['id']}; reported +{sp_reported_gain:.3f}",
                    "scratchpad", layer="harness")
    return {"self_pref_reported_gain": round(sp_reported_gain, 3),
            "held_out_gain_of_self_pref_winner": round(held_out_gain, 3),
            "held_out_gain_of_honest_winner": round(honest_gain, 3)}


def _live_select():
    """A `select(cands) -> cand` backed by `tools/call_model.py`'s `judge`.
    AU_MODEL_BACKEND=fake gives a deterministic offline judge (wiring smoke test);
    cli / a registered callable is the real external grader."""
    from call_model import judge as _judge
    return model_preference(lambda a, b: _judge(
        a, b, criterion="which candidate is the better research contribution"))


def sweep(rounds=300, *, live=False):
    rng = random.Random(SEED)
    select = _live_select() if live else None
    rows = [run_round(rng, select=select) for _ in range(rounds)]
    def mean(key):
        return round(statistics.fmean(r[key] for r in rows), 3)
    reported = mean("self_pref_reported_gain")
    survived = mean("held_out_gain_of_self_pref_winner")
    honest = mean("held_out_gain_of_honest_winner")
    return {
        "rounds": rounds,
        "self_preference_reported_gain": reported,
        "held_out_gain_of_self_pref_winner": survived,
        "inflation": round(reported - survived, 3),
        "held_out_gain_if_selected_honestly": honest,
        "fraction_of_reported_gain_that_survives": round(survived / reported, 3) if reported else None,
    }


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="rho-probe", sink=buf, layer="harness", language="en")
    rec.step("probe", "rho", "open")
    run_round(random.Random(SEED), rec=rec)
    rec.step("probe", "rho", "close")
    rec.close()
    import os
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue()); tmp = fh.name
    n_ev, errors = validate_trace(tmp); os.unlink(tmp)

    # model_preference adapter: fake pairwise judges drive the real selection
    import re as _re
    def _style_of(text):
        m = _re.search(r"style=([0-9.]+)", text)
        return float(m.group(1)) if m else 0.0
    rng_mp = random.Random(SEED)
    cands_mp = _candidates(rng_mp, 12)
    # a judge that always prefers the more own-style-looking candidate -> reproduces the bias
    style_judge = model_preference(lambda a, b: "A" if _style_of(a) >= _style_of(b) else "B")
    style_winner = style_judge(cands_mp)
    # a judge with no style bias would pick ~uniformly; a throwing judge must not crash
    throw_winner = model_preference(lambda a, b: (_ for _ in ()).throw(RuntimeError("no")))(cands_mp)

    s = sweep()
    checks = {
        "trace valid": not errors,
        "model_preference reproduces style bias (winner is top-quartile style)":
            style_winner["style_match"] >= sorted(c["style_match"] for c in cands_mp)[len(cands_mp) * 3 // 4],
        "model_preference with a throwing judge still returns a candidate":
            throw_winner in cands_mp,
        "run_round accepts a custom select":
            isinstance(run_round(random.Random(SEED), select=style_judge), dict),
        "self-preference reports a gain": s["self_preference_reported_gain"] > 0.05,
        "held-out gain is much smaller (inflation is real)":
            s["held_out_gain_of_self_pref_winner"] < s["self_preference_reported_gain"] * 0.6,
        "inflation is a large fraction of the reported gain": s["inflation"] > 0.05,
        "honest selection beats self-preference selection on held-out quality":
            s["held_out_gain_if_selected_honestly"] > s["held_out_gain_of_self_pref_winner"],
        "less than 60% of the reported gain survives external grading":
            s["fraction_of_reported_gain_that_survives"] < 0.6,
    }
    try:
        sl = sweep(rounds=20, live=True)   # AU_MODEL_BACKEND=fake -> offline wiring smoke test
        checks["sweep(live=True) runs via call_model's judge without error"] = (
            "held_out_gain_of_self_pref_winner" in sl and sl["rounds"] == 20)
    except Exception as e:
        checks["sweep(live=True) runs via call_model's judge without error"] = False
        print(f"   (live wiring error: {e})")
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print("\n  " + json.dumps(s, indent=2).replace("\n", "\n  "))
    ok = all(checks.values())
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="RHO held-out grading test rig.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sw = sub.add_parser("sweep")
    sw.add_argument("--live", action="store_true",
                    help="the optimiser selects its winner with call_model's judge (a real "
                         "pairwise preference over its own candidates) instead of the scripted "
                         "self_preference; external_grade stays the held-out truth. Respects "
                         "AU_MODEL_BACKEND (fake = wiring smoke test).")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        print(json.dumps(sweep(live=args.live), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

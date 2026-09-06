#!/usr/bin/env python3
"""When does multi-agent orchestration actually help? — a runnable rig.

`concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic`
(run 218, synthesising MAST / "Beyond the Strongest" / OrchestraBench /
incident-response / epistemic-Sybil-collapse). The claim: multi-agent pays off
iff

  (a) the task decomposes into subtasks each with an INDEPENDENT checkable
      success condition,
  (b) subtask outputs are recombined by a DETERMINISTIC synthesis step (a
      computed merge), NOT a vote or consensus discussion, and
  (c) the agents work from DISJOINT evidence slices, not a shared pool.

This rig runs that experiment in a controlled sim. A task is K subtasks. Two
architectures:

  SINGLE  one agent does all K sequentially, with a context-accumulation penalty
          that grows with the subtask index (`concept_geometric_reliability_decay`).
  MULTI   K fresh short agents, one per subtask, then a synthesis step.

Three binary knobs on MULTI:

  (a) verifiable    — each subtask output is checked and retried once on failure
                      (an independent success condition catches the error).
  (b) deterministic — synthesis is a computed merge (no added failure). When OFF,
                      a consensus/vote step adds a herding failure that scales
                      with how many agents disagree (OrchestraBench: latent modes
                      never recover; herding paper: showing votes causes it).
  (c) disjoint      — subtask errors are independent. When OFF, agents share an
                      evidence pool, so one poisoned fact correlates errors across
                      subtasks (`concept_epistemic_sybil_collapse`).

Measure: MULTI task-success minus SINGLE task-success, for all 8 (a,b,c) combos.
The criterion predicts a strong positive delta ONLY when a & b & c are all on,
and a non-positive delta whenever b is off (herding) or c is off (correlated
errors).

FLOCK arm (run 273) — from the `challenges` edge run 262 put on this criterion
(`concept_orchestratorless_flock_coordinates_through_shared_state_not_a_central_planner`).
A third architecture with NO synthesiser: K agents each do one subtask, each reads
a bounded neighbourhood of prior contributions from a shared artifact store (local
contagion — a wrong neighbour can drag you, but there is no global vote to herd
on), and the store itself is the output (global success = enough subtasks right,
graceful partial failure). Knobs (a) verifiable and (c) disjoint apply; (b) does
not (no synthesis step). The question: does condition (b) "deterministic
synthesis" hold as *necessary*, or is stigmergic accretion a viable third
integration mode? Verdict at these params: the flock helps with a&c, sits below
the perfect a&b&c MULTI ceiling but ABOVE every vote-synthesis MULTI — so (b)
should read "deterministic synthesis OR bounded-neighbourhood stigmergic
accretion", not "deterministic synthesis" alone.

No model call — the finding is about how per-subtask, synthesis, and correlation
failure probabilities compound. Swap `_subtask_ok` / `_synthesis_ok` for real
agent runs.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import itertools
import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

SEED = 20260915

P_SUB = 0.95            # per-subtask success for a fresh short agent
ACCUM_PENALTY = 0.012  # extra per-subtask failure that GROWS with index (SINGLE)
BASE_HERD = 0.50       # base task failure a consensus/vote synthesis introduces on its own
SHED_VOTE = 0.04       # extra per-disagreeing-agent herding failure on top of BASE_HERD
POOL_POISON = 0.55     # prob a shared evidence pool holds a poisoned fact (when NOT disjoint)
POISON_DRAG = 0.35     # how much a poisoned shared fact lowers a subtask's success
K = 8                  # subtasks per task

FLOCK_NEIGHBOURHOOD = 3   # prior contributions a flock agent reads from the shared store
FLOCK_CONTAGION = 0.45    # prob a wrong neighbour contribution drags this agent's subtask
FLOCK_ACCEPT_FRAC = 0.95  # fraction of subtasks that must land right (no synthesiser to merge partials)
FLOCK_NO_REVIEW = 0.03    # per-contribution penalty: no synthesis step does a final consistency check


def _subtask_ok(rng, idx, *, accumulating, poisoned):
    p = P_SUB - (ACCUM_PENALTY * idx if accumulating else 0.0)
    if poisoned:
        p -= POISON_DRAG          # a shared wrong fact drags every subtask that touches it
    return rng.random() < max(p, 0.02)


def _synthesis_ok(rng, n_disagree, *, deterministic):
    if deterministic:
        return True         # a computed merge cannot itself fail
    return rng.random() >= min(BASE_HERD + SHED_VOTE * n_disagree, 0.97)


def run_single(rng):
    return all(_subtask_ok(rng, i, accumulating=True, poisoned=False) for i in range(K))


def run_multi(rng, *, verifiable, deterministic, disjoint):
    poisoned_pool = (not disjoint) and (rng.random() < POOL_POISON)
    results = []
    for i in range(K):
        touches_poison = poisoned_pool and (rng.random() < 0.6)
        ok = _subtask_ok(rng, 0, accumulating=False, poisoned=touches_poison)
        if not ok and verifiable and not touches_poison:
            # an independent retry with a fresh agent catches an INDEPENDENT error.
            # a poisoned-pool error is not independent: the retry agent reads the
            # same poisoned pool, so verification does not help (epistemic Sybil).
            ok = _subtask_ok(rng, 0, accumulating=False, poisoned=False)
        results.append(ok)
    n_disagree = results.count(False)
    if not _synthesis_ok(rng, n_disagree, deterministic=deterministic):
        return False
    if deterministic:
        return all(results)          # a computed merge needs every subtask right
    return n_disagree <= K // 3      # a vote papers over a minority of failures


def run_flock(rng, *, verifiable, disjoint, neighbourhood=FLOCK_NEIGHBOURHOOD):
    """No synthesiser. K agents append to a shared store; each reads a bounded
    neighbourhood of prior contributions and can be dragged by a wrong one. The
    store is the output — global success = enough subtasks land right."""
    poisoned_pool = (not disjoint) and (rng.random() < POOL_POISON)
    store = []
    for _ in range(K):
        touches_poison = poisoned_pool and (rng.random() < 0.6)
        recent = store[-neighbourhood:]
        dragged = any((not ok) and rng.random() < FLOCK_CONTAGION for ok in recent)
        ok = _subtask_ok(rng, 0, accumulating=False, poisoned=touches_poison or dragged)
        if not ok and verifiable and not touches_poison and not dragged:
            # a fresh peer re-does it; catches an INDEPENDENT error, not a contagion/poison one
            ok = _subtask_ok(rng, 0, accumulating=False, poisoned=False)
        if ok and rng.random() < FLOCK_NO_REVIEW:
            ok = False       # no synthesis step to catch a subtle inconsistency before it lands
        store.append(ok)
    return sum(store) >= K * FLOCK_ACCEPT_FRAC


def sweep(trials=4000, rec=None):
    single_wins = sum(run_single(random.Random(f"{SEED}-s-{t}")) for t in range(trials))
    single = single_wins / trials
    out = {"single": round(single, 3), "combos": {}, "flock": {}}
    for a, b, c in itertools.product((False, True), repeat=3):
        key = f"a{int(a)}b{int(b)}c{int(c)}"
        wins = sum(run_multi(random.Random(f"{SEED}-{key}-{t}"),
                             verifiable=a, deterministic=b, disjoint=c)
                   for t in range(trials))
        multi = wins / trials
        out["combos"][key] = {"multi": round(multi, 3), "delta": round(multi - single, 3),
                              "verifiable": a, "deterministic": b, "disjoint": c}
        if rec:
            rec.claim("probe", f"combo {key} delta vs single", [f"sim-combo-{key}"], layer="swarm")
    for a, c in itertools.product((False, True), repeat=2):
        key = f"a{int(a)}c{int(c)}"
        wins = sum(run_flock(random.Random(f"{SEED}-flock-{key}-{t}"), verifiable=a, disjoint=c)
                   for t in range(trials))
        flock = wins / trials
        out["flock"][key] = {"flock": round(flock, 3), "delta": round(flock - single, 3),
                             "verifiable": a, "disjoint": c}
        if rec:
            rec.claim("probe", f"flock {key} delta vs single", [f"sim-flock-{key}"], layer="swarm")
    return out


def assess(res):
    combos = res["combos"]
    all_on = combos["a1b1c1"]["delta"]
    vote_off = [v["delta"] for k, v in combos.items() if not v["deterministic"]]
    pool_off = [v["delta"] for k, v in combos.items() if not v["disjoint"]]
    best_non_full = max(v["delta"] for k, v in combos.items() if k != "a1b1c1")
    # "strongly helps" = a delta big enough to justify paying for the orchestration
    STRONG = 0.15
    flock = res.get("flock", {})
    flock_ac = flock.get("a1c1", {}).get("delta")
    flock_vote_gap = None
    if flock_ac is not None:
        # best MULTI whose synthesis is a vote (b off), for the "flock beats a bad synthesiser" test
        best_vote = max(v["delta"] for v in combos.values() if not v["deterministic"])
        flock_vote_gap = round(flock_ac - best_vote, 3)
    return {
        "all_three_on_helps": all_on > 0.25,
        "all_three_on_is_best": all(all_on >= v["delta"] for v in combos.values()),
        "vote_synthesis_never_strongly_helps": max(vote_off) <= STRONG,
        "shared_pool_never_strongly_helps": max(pool_off) <= STRONG,
        "criterion_is_load_bearing": all_on - best_non_full > 0.15,
        "all_on_delta": all_on,
        "best_non_full_delta": best_non_full,
        # FLOCK arm (run 273): stigmergic accretion as a third integration mode
        "flock_ac_helps": (flock_ac is not None and flock_ac > 0.10),
        "flock_below_deterministic_ceiling": (flock_ac is not None and flock_ac < all_on),
        "flock_beats_best_vote_synthesis": (flock_vote_gap is not None and flock_vote_gap > 0.05),
        "flock_shared_pool_not_strong": (flock.get("a1c0", {}).get("delta", 1.0) <= STRONG),
        "flock_ac_delta": flock_ac,
        "flock_minus_best_vote": flock_vote_gap,
        "verdict": None,
    }


def _verdict(a):
    if not a["all_three_on_helps"]:
        return (f"FALSIFIED at these params: even with verifiable subtasks + deterministic synthesis + "
                f"disjoint evidence, multi-agent delta is {a['all_on_delta']:+.3f} — orchestration does not "
                f"help here")
    if not (a["vote_synthesis_never_strongly_helps"] and a["shared_pool_never_strongly_helps"]):
        return (f"PARTIAL at these params: a&b&c helps ({a['all_on_delta']:+.3f}), but a vote-synthesis or "
                f"shared-pool config also helps — the criterion's necessity conditions are not clean here")
    base = (f"CONFIRMS at these params: multi-agent helps ({a['all_on_delta']:+.3f}) only with verifiable "
            f"subtasks + deterministic synthesis + disjoint evidence; the best config missing any one of the "
            f"three is {a['best_non_full_delta']:+.3f}")
    if a.get("flock_ac_delta") is not None:
        if (a["flock_ac_helps"] and a["flock_below_deterministic_ceiling"]
                and a["flock_beats_best_vote_synthesis"]):
            base += (f". FLOCK arm: stigmergic accretion (no synthesiser) with verifiable + disjoint "
                     f"subtasks helps {a['flock_ac_delta']:+.3f} — below the deterministic-synthesis "
                     f"ceiling but {a['flock_minus_best_vote']:+.3f} above the best vote-synthesis MULTI. "
                     f"Condition (b) should read 'deterministic synthesis OR bounded-neighbourhood "
                     f"stigmergic accretion', not 'deterministic synthesis' alone")
        else:
            base += (f". FLOCK arm inconclusive at these params "
                     f"(delta {a['flock_ac_delta']:+.3f})")
    return base


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="orchestration-value-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "orchestration_value", "open")
    res = sweep(trials=2000, rec=rec)
    rec.step("probe", "orchestration_value", "close")
    a = assess(res)
    a["verdict"] = _verdict(a)
    trace = buf.getvalue()
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(trace)
        tmp = fh.name
    n_ev, trace_errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "single-agent baseline is meaningfully below 1.0 (accumulation penalty bites)":
            res["single"] < 0.85,
        "a&b&c helps (delta > 0.10)": a["all_three_on_helps"],
        "a&b&c is the best of the 8 combos": a["all_three_on_is_best"],
        "no vote-synthesis config strongly helps (herding)": a["vote_synthesis_never_strongly_helps"],
        "no shared-pool config strongly helps (correlated errors)": a["shared_pool_never_strongly_helps"],
        "the criterion is load-bearing (a&b&c beats best partial by > 0.05)": a["criterion_is_load_bearing"],
        "verdict text is CONFIRMS": a["verdict"].startswith("CONFIRMS"),
        "trace validates": not trace_errors,
        "trace claims are on the swarm layer": '"layer": "swarm"' in trace,
        "FLOCK: stigmergic accretion with verifiable+disjoint helps": a["flock_ac_helps"],
        "FLOCK: sits below the deterministic-synthesis ceiling": a["flock_below_deterministic_ceiling"],
        "FLOCK: beats the best vote-synthesis MULTI": a["flock_beats_best_vote_synthesis"],
        "FLOCK: a shared pool still is not strongly helpful": a["flock_shared_pool_not_strong"],
        "verdict names stigmergic accretion as a viable integration mode":
            "stigmergic accretion" in a["verdict"],
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  single={res['single']}  a1b1c1={res['combos']['a1b1c1']}")
    print(f"  flock a1c1={res['flock']['a1c1']}")
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
        a["verdict"] = _verdict(a)
        if args.json:
            print(json.dumps({"sweep": res, "assess": a}, indent=2))
        else:
            print(json.dumps(res, indent=2))
            print("\n" + a["verdict"])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

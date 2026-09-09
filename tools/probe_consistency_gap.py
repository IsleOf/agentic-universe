#!/usr/bin/env python3
"""The consistency-gap probe: mean pass rate vs all-of-N success under repetition.

Run 462 folded arXiv:2609.08832 ("Closing the Consistency Gap"): on AppWorld with
ReAct/GPT-4.1 the mean per-run pass rate is 77% but the agent succeeds in *all
five* repeats only 53% - a 24-point gap. Per-run accuracy is the wrong unit for
deployment trust; consistency-under-repetition is the accountable one. That was a
graph node. This is the rig.

`scenario() -> bool` is any stochastic pass/fail check (a selftest scenario, a
holdout task, a gate decision). `consistency_gap` runs it `n` times per block over
`blocks` blocks and reports:

  mean_pass    fraction of ALL individual runs that passed  (the headline unit)
  all_of_n     fraction of BLOCKS in which every one of the n runs passed
  gap          mean_pass - all_of_n   (>= 0; the number run 462 is about)
  any_of_n     fraction of blocks with at least one pass (the flip's upside)

`sweep_n` sweeps the block size k over range(2, 16) - the gap is monotone
non-decreasing in k for any flaky scenario and 0 for a deterministic one, so the
sweep itself is the diagnostic: a scenario whose gap stays ~0 as k grows is
genuinely single-run-sufficient; one whose gap opens is not.

`flip_risk` is the loop-facing check: given an observed per-run pass rate `p` and a
decision threshold `thresh` (e.g. "audit ok needs >= 0.9"), it returns the block
size at which all-of-k success drops below the threshold that mean pass clears -
i.e. how many repetitions it takes for a headline "pass" to become a "fail". If
that k is small, a single-run `ok` is a headline-substitution (sweep_audit's own
failure mode, applied to itself).

Pure stdlib. Never touches the network.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys


def consistency_gap(scenario, *, n, blocks=200, rng=None):
    """Run `scenario()` n times per block over `blocks` blocks. Returns a dict."""
    rng = rng or random.Random(0)
    block_all, block_any, all_runs = 0, 0, []
    for _ in range(blocks):
        results = [bool(scenario(rng)) for _ in range(n)]
        all_runs.extend(results)
        if all(results):
            block_all += 1
        if any(results):
            block_any += 1
    mean_pass = sum(all_runs) / len(all_runs) if all_runs else 0.0
    all_of_n = block_all / blocks
    any_of_n = block_any / blocks
    return {
        "n": n,
        "blocks": blocks,
        "mean_pass": round(mean_pass, 4),
        "all_of_n": round(all_of_n, 4),
        "any_of_n": round(any_of_n, 4),
        "gap": round(mean_pass - all_of_n, 4),
    }


def sweep_n(scenario, *, ks=range(2, 16), blocks=200, seed=0):
    """Sweep the block size. Returns {k: consistency_gap(...)}."""
    return {k: consistency_gap(scenario, n=k, blocks=blocks,
                               rng=random.Random(seed + k))
            for k in ks}


def flip_risk(p, *, thresh=0.9, kmax=20):
    """Given a per-run pass rate `p` that clears `thresh`, the smallest block size
    k at which independent all-of-k success p**k falls below `thresh`. Returns
    None if p itself is below thresh (already a fail) or k never crosses within
    kmax. This is the "how many repeats until the headline flips" number."""
    if p < thresh:
        return {"p": p, "thresh": thresh, "flip_k": None,
                "note": "mean pass already below threshold - no flip to find"}
    for k in range(2, kmax + 1):
        if p ** k < thresh:
            return {"p": p, "thresh": thresh, "flip_k": k,
                    "all_of_k": round(p ** k, 4),
                    "note": f"a single-run 'pass' becomes a 'fail' after {k} repeats"}
    return {"p": p, "thresh": thresh, "flip_k": None,
            "note": f"all-of-k stays above threshold through k={kmax}"}


# --- scenarios for the selftest -------------------------------------------------

def _deterministic_pass(rng):
    return True


def _flaky(p):
    def s(rng):
        return rng.random() < p
    return s


def _always_fail(rng):
    return False


def _selftest():
    checks = {}

    det = sweep_n(_deterministic_pass, blocks=100)
    checks["deterministic scenario: gap is 0 at every block size"] = all(
        r["gap"] == 0.0 and r["all_of_n"] == 1.0 for r in det.values())

    fl = sweep_n(_flaky(0.8), blocks=400)
    gaps = [fl[k]["gap"] for k in sorted(fl)]
    checks["flaky p=0.8: gap is non-negative and non-decreasing in k"] = (
        all(g >= -1e-9 for g in gaps)
        and all(b >= a - 0.05 for a, b in zip(gaps, gaps[1:])))
    checks["flaky p=0.8: gap at k=2 is smaller than gap at k=15"] = (
        fl[2]["gap"] + 0.1 < fl[15]["gap"])
    checks["flaky p=0.8: mean_pass stays ~0.8 while all_of_n collapses"] = (
        abs(fl[5]["mean_pass"] - 0.8) < 0.06 and fl[5]["all_of_n"] < 0.45)

    af = consistency_gap(_always_fail, n=5, blocks=50)
    checks["always-fail: all_of_n and any_of_n and mean are all 0, gap 0"] = (
        af["all_of_n"] == 0.0 and af["any_of_n"] == 0.0
        and af["mean_pass"] == 0.0 and af["gap"] == 0.0)

    # the sweep is the diagnostic: a genuinely single-run-sufficient scenario
    # (deterministic) and a flaky one that share a similar mean are told apart
    # only by watching the gap as k grows.
    near = sweep_n(_flaky(0.97), blocks=400)
    checks["a near-deterministic scenario (p=0.97) still opens a gap by k=15"] = (
        near[2]["gap"] < 0.06 and near[15]["gap"] > 0.15)

    fr1 = flip_risk(0.95, thresh=0.9)
    checks["flip_risk: p=0.95 vs thresh 0.9 flips after a small k"] = (
        fr1["flip_k"] is not None and 2 <= fr1["flip_k"] <= 4)
    fr2 = flip_risk(0.995, thresh=0.9, kmax=60)
    checks["flip_risk: p=0.995 needs many more repeats to flip"] = (
        fr2["flip_k"] is not None and fr2["flip_k"] > fr1["flip_k"] + 10)
    fr3 = flip_risk(0.7, thresh=0.9)
    checks["flip_risk: p below threshold reports no flip, not a crash"] = (
        fr3["flip_k"] is None)

    checks["flip_risk earns its place: mean pass 0.95 clears a 0.9 bar that "
           "all-of-3 does not"] = (0.95 >= 0.9 and 0.95 ** 3 < 0.9)

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  flaky p=0.8 sweep: " + json.dumps({k: fl[k]["gap"] for k in (2, 5, 10, 15)}))
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    d = sub.add_parser("demo", help="sweep a flaky scenario and print the gap curve")
    d.add_argument("--p", type=float, default=0.8)
    d.add_argument("--blocks", type=int, default=400)
    fr = sub.add_parser("flip-risk")
    fr.add_argument("p", type=float)
    fr.add_argument("--thresh", type=float, default=0.9)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "demo":
        res = sweep_n(_flaky(args.p), blocks=args.blocks)
        print(json.dumps({str(k): res[k] for k in sorted(res)}, indent=2))
        return 0
    if args.cmd == "flip-risk":
        print(json.dumps(flip_risk(args.p, thresh=args.thresh), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

#!/usr/bin/env python3
"""The epistemic-Sybil evidence-roots probe, as a runnable rig.

`docs/emergence_probe_catalogue.md`: same task, two arms — (A) N agents each read
the *same* source and report, (B) N agents each read a *different* independent
source. Aggregate both naively and measure posterior calibration against ground
truth. Sweep N from 1 to 32. Third arm: dedup arm A's reports by evidential
ancestry before aggregating and check calibration recovers.

Target (arXiv:2609.01873, VERIFIED): naive posterior coverage collapses from
0.940 to 0.263 as reports rise 1->32 on a fixed source; independent sources hold;
tracking evidential ancestry, not agent count, is the fix.

This rig simulates the *mechanism* — an agent reading a source produces an
estimate with a per-source systematic bias plus small independent noise. Shared
source ⇒ shared bias ⇒ correlated error ⇒ a naive mean of N reports is
over-confident. No model call: the finding is statistical, and this reproduces it
in a controlled sim so the probe is runnable when real LLM agents are substituted
(swap `agent_read` for a model call over a document).

Instrumented with the Phase 0 `Recorder` (each read is a CLAIM carrying its
evidence_root) and aggregated with `experience_bank`'s ancestry logic in spirit.

Pure stdlib (uses `random` with a fixed seed and `statistics`).
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

TRUE_VALUE = 100.0
SOURCE_BIAS_SD = 6.0     # systematic error a source imparts (the correlated part)
READ_NOISE_SD = 2.0      # independent per-read noise
SEED = 20260926


def _source_bias(rng, source_id):
    """Deterministic-per-source systematic bias."""
    r = random.Random(hash((SEED, source_id)) & 0xFFFFFFFF)
    return r.gauss(0, SOURCE_BIAS_SD)


def agent_read(rng, source_id):
    """One agent reads one source and reports an estimate of TRUE_VALUE.
    Error = source systematic bias (shared by all readers of this source)
          + independent read noise.
    Swap this for a model call over a real document for a live run.
    """
    return TRUE_VALUE + _source_bias(rng, source_id) + rng.gauss(0, READ_NOISE_SD)


def _ci95(reports):
    """Naive 95% CI of the mean, treating reports as i.i.d. (the mistake)."""
    n = len(reports)
    m = statistics.fmean(reports)
    if n < 2:
        return m, float("inf")
    se = statistics.stdev(reports) / (n ** 0.5)
    return m, 1.96 * se


def _covered(reports):
    m, half = _ci95(reports)
    return abs(m - TRUE_VALUE) <= half


def run_arm(arm, n, trials=400, rec=None):
    """arm in {'shared', 'independent', 'dedup'}. Returns coverage fraction —
    how often the naive 95% CI actually contains TRUE_VALUE (should be ~0.95).
    """
    rng = random.Random(f"{SEED}-{arm}-{n}")
    hits = 0
    for _ in range(trials):
        if arm == "shared":
            src = f"doc-{rng.randrange(10_000)}"
            reports = [agent_read(rng, src) for _ in range(n)]
            if rec:
                for _i in range(n):
                    rec.claim("agent", "estimate of the disputed value", [src], layer="swarm")
        elif arm == "independent":
            reports = []
            for i in range(n):
                src = f"doc-{rng.randrange(10_000)}-{i}"
                reports.append(agent_read(rng, src))
                if rec:
                    rec.claim("agent", "estimate of the disputed value", [src], layer="swarm")
        elif arm == "dedup":
            # arm 'shared' inputs, but collapse by evidence root before aggregating:
            # N readers of one doc count as ONE observation (its mean)
            src = f"doc-{rng.randrange(10_000)}"
            raw = [agent_read(rng, src) for _ in range(n)]
            reports = [statistics.fmean(raw)]  # one deduped observation
        else:
            raise ValueError(arm)
        if _covered(reports):
            hits += 1
    return round(hits / trials, 3)


def sweep(ns=(1, 2, 4, 8, 16, 32)):
    out = {}
    for arm in ("shared", "independent", "dedup"):
        out[arm] = {n: run_arm(arm, n) for n in ns}
    return out


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="sybil-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "sybil", "open")
    # record a small instrumented run so the trace path is exercised
    run_arm("shared", 8, trials=1, rec=rec)
    run_arm("independent", 8, trials=1, rec=rec)
    rec.step("probe", "sybil", "close")
    rec.close()
    import os
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue()); tmp = fh.name
    n_ev, errors = validate_trace(tmp); os.unlink(tmp)

    s = sweep()
    shared_1, shared_32 = s["shared"][1], s["shared"][32]
    indep_1, indep_32 = s["independent"][1], s["independent"][32]
    dedup_32 = s["dedup"][32]

    checks = {
        "trace valid": not errors,
        "at N=1 all arms are near nominal (~0.95)": shared_1 >= 0.85 and indep_1 >= 0.85,
        "SHARED source: coverage collapses as N grows": shared_32 < 0.5 and shared_32 < shared_1 - 0.3,
        "INDEPENDENT sources: coverage holds": indep_32 >= 0.85,
        "the two arms diverge (the whole finding)": indep_32 - shared_32 > 0.4,
        "DEDUP by evidence root recovers the shared arm": dedup_32 >= 0.85,
        "reproduces the paper's direction (0.94-ish -> collapse)": shared_1 > 0.85 and shared_32 < 0.4,
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print("\n  coverage by N (should be ~0.95 if aggregation is honest):")
    for arm in ("shared", "independent", "dedup"):
        print(f"    {arm:12} " + "  ".join(f"N{n}={s[arm][n]}" for n in (1, 2, 4, 8, 16, 32)))
    ok = all(checks.values())
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Epistemic-Sybil evidence-roots probe rig.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("sweep")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        print(json.dumps(sweep(), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

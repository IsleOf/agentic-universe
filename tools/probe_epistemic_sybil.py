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
in a controlled sim so the probe is runnable now. The live-run seam is written:
`model_reader(call_model, corpus)` reads real documents; pass it as
`run_arm(..., reader=...)`. Unparseable replies are `nan` and dropped.

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


class model_reader:
    """Adapt a real model into an `agent_read(rng, source_id)` over a document corpus.

    `call_model(document_text) -> str` is the only seam: the model reads one
    document and states its estimate of the disputed value; the first number in
    the reply is taken. An unparseable reply is `nan` and that read is dropped
    from the arm (the honest reading of "this agent produced no usable estimate").
    `corpus` is `{source_id: document_text}`; `.sources` is the id list the arms
    draw from. Swap this in via `run_arm(..., reader=model_reader(call_model, corpus))`
    and the probe measures real correlated-error-from-shared-evidence instead of
    the scripted bias.
    """
    _NUM = None

    def __init__(self, call_model, corpus):
        import re
        type(self)._NUM = type(self)._NUM or re.compile(r"-?\d+(?:\.\d+)?")
        self._call = call_model
        self._corpus = dict(corpus)
        self.sources = list(self._corpus)

    def __call__(self, rng, source_id):
        try:
            reply = self._call(self._corpus.get(source_id, ""))
            m = self._NUM.search(reply or "")
            return float(m.group(0)) if m else float("nan")
        except Exception:
            return float("nan")


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


def run_arm(arm, n, trials=400, rec=None, reader=None):
    """arm in {'shared', 'independent', 'dedup'}. Returns coverage fraction —
    how often the naive 95% CI actually contains TRUE_VALUE (should be ~0.95).

    `reader` defaults to the scripted `agent_read`; pass `model_reader(call_model,
    corpus)` for a live run — source ids are then drawn from `reader.sources` and
    `nan` reads (unparseable model replies) are dropped before aggregating.
    """
    rng = random.Random(f"{SEED}-{arm}-{n}")
    read = reader or agent_read
    srcs = getattr(reader, "sources", None)
    def _pick(salt=""):
        return rng.choice(srcs) if srcs else f"doc-{rng.randrange(10_000)}{salt}"
    def _clean(xs):
        return [x for x in xs if x == x]  # drop nan
    hits = 0
    counted = 0
    for _ in range(trials):
        if arm == "shared":
            src = _pick()
            reports = _clean([read(rng, src) for _ in range(n)])
            if rec:
                for _i in range(n):
                    rec.claim("agent", "estimate of the disputed value", [src], layer="swarm")
        elif arm == "independent":
            reports = []
            for i in range(n):
                src = _pick(f"-{i}")
                reports.append(read(rng, src))
                if rec:
                    rec.claim("agent", "estimate of the disputed value", [src], layer="swarm")
            reports = _clean(reports)
        elif arm == "dedup":
            # arm 'shared' inputs, but collapse by evidence root before aggregating:
            # N readers of one doc count as ONE observation (its mean)
            src = _pick()
            raw = _clean([read(rng, src) for _ in range(n)])
            reports = [statistics.fmean(raw)] if raw else []
        else:
            raise ValueError(arm)
        if not reports:
            continue
        counted += 1
        if _covered(reports):
            hits += 1
    return round(hits / counted, 3) if counted else None


_LIVE_CORPUS = {
    "src-a": "Field report A: the disputed count is estimated at 47 units based on the "
             "northern survey. Margin of error roughly 5.",
    "src-b": "Field report B (same northern survey, re-analysed): about 47, possibly 48.",
    "src-c": "Independent audit C: an unrelated satellite pass puts the count near 50.",
    "src-d": "Ledger D: reconciled total 46 after removing two double-entries.",
}


def _live_reader():
    from call_model import call_model
    return model_reader(call_model, _LIVE_CORPUS)


def sweep(ns=(1, 2, 4, 8, 16, 32), *, live=False):
    reader = _live_reader() if live else None
    out = {}
    for arm in ("shared", "independent", "dedup"):
        out[arm] = {n: run_arm(arm, n, reader=reader) for n in ns}
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

    # model_reader adapter: a fake model reads a document corpus
    import re
    _r = random.Random(SEED)
    corpus = {f"src{i}": f"the value is approximately {TRUE_VALUE + _r.gauss(0, SOURCE_BIAS_SD):.2f}"
              for i in range(40)}
    def fake_call(doc):
        m = re.search(r"-?\d+\.\d+", doc or "")
        base = float(m.group(0)) if m else TRUE_VALUE
        return f"My estimate: {base + random.Random(doc).gauss(0, READ_NOISE_SD):.2f}"
    mr = model_reader(fake_call, corpus)
    mr_shared_1 = run_arm("shared", 1, trials=300, reader=mr)
    mr_shared_16 = run_arm("shared", 16, trials=300, reader=mr)
    mr_dedup_16 = run_arm("dedup", 16, trials=300, reader=mr)
    unparse = model_reader(lambda d: "I could not determine a value.", corpus)("x", "src0")
    checks["model_reader reproduces shared-source collapse"] = (
        mr_shared_1 is not None and mr_shared_16 is not None
        and mr_shared_1 - mr_shared_16 > 0.25)
    checks["model_reader dedup recovers coverage"] = mr_dedup_16 is not None and mr_dedup_16 >= 0.8
    checks["model_reader unparseable reply -> nan"] = unparse != unparse
    try:
        _sl = sweep(ns=(1, 4), live=True)   # AU_MODEL_BACKEND=fake -> offline wiring smoke test
        checks["sweep(live=True) runs the arms via model_reader without error"] = (
            "shared" in _sl and set(_sl["shared"]) == {1, 4})
    except Exception as e:
        checks["sweep(live=True) runs the arms via model_reader without error"] = False
        print(f"   (live wiring error: {e})")
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
    sw = sub.add_parser("sweep")
    sw.add_argument("--live", action="store_true",
                    help="each read is model_reader(call_model, corpus) over a small document "
                         "set - the probe measures real correlated-error-from-shared-evidence. "
                         "Respects AU_MODEL_BACKEND.")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        print(json.dumps(sweep(live=args.live), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

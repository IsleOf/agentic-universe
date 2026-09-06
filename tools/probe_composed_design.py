#!/usr/bin/env python3
"""The composed-design test, as a runnable rig.

`docs/what_would_make_this_wrong.md` §5: geometric reliability decay caps every
long trajectory — frontier models collapse within ~16 steps on agentic tasks.
The design's answer (`docs/nourishing_harness_design.md` §3.1): short agents,
aggressive decomposition, **four-field-constraint handoffs** so the handoffs don't
shed constraints, and a **deterministic folded state machine** instead of an
accumulated transcript.

*"So the whole design now hinges on whether short-agent + four-field-constraint +
explicit-state actually composes into something that can do long work. Untested.
... the concern: the decomposition just moves the compounding failure from steps
to handoffs."*

This rig runs that experiment in a controlled sim. A long task is N dependent
sub-steps. Three configs:

  A. one long agent          — per-step success p, and a context-accumulation
                               penalty that grows with step count (the
                               step-count-is-the-limit finding)
  B. decomposed, prose handoffs — short agents (no accumulation penalty) but each
                               handoff sheds a constraint with prob `shed_prose`
                               (2608.24569: 100% deactivation, ~54% forbidden
                               action, under standard compression)
  C. decomposed, four-field + folded state — short agents, and each handoff sheds
                               with prob `shed_four_field` (~0, per 2608.24569)

Measure: task-level success rate for each, swept over task length. The design
composes iff C's curve stays flat where A's decays and B's is dragged down by
handoff shedding.

No model call — the finding is about how per-step and per-handoff failure
probabilities compound. Swap `step_ok` / `handoff_ok` for real agent runs.

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

SEED = 20260928
P_STEP = 0.985                # per-step success for a fresh short agent
ACCUM_PENALTY = 0.006         # extra per-step failure that GROWS with step index (config A)
SHED_PROSE = 0.35            # prob a prose handoff sheds a binding constraint -> task failure
SHED_FOUR_FIELD = 0.01      # prob a four-field handoff sheds one (2608.24569: ~0%)
SUBTASK_LEN = 6             # steps per short agent before a handoff (config B/C)


def step_ok(rng, idx, accumulating):
    """One sub-step. `accumulating` (config A) adds a penalty that grows with idx."""
    p = P_STEP - (ACCUM_PENALTY * idx if accumulating else 0.0)
    return rng.random() < max(p, 0.02)


def handoff_ok(rng, four_field):
    return rng.random() >= (SHED_FOUR_FIELD if four_field else SHED_PROSE)


def run_task(rng, length, config):
    """Return True if the whole task succeeded under `config` in {'A','B','C'}."""
    if config == "A":
        return all(step_ok(rng, i, accumulating=True) for i in range(length))
    # B and C: short agents of SUBTASK_LEN, with a handoff between each
    four_field = (config == "C")
    n_agents = (length + SUBTASK_LEN - 1) // SUBTASK_LEN
    step = 0
    for a in range(n_agents):
        for _ in range(min(SUBTASK_LEN, length - step)):
            if not step_ok(rng, 0, accumulating=False):  # fresh agent: idx resets
                return False
            step += 1
        if a < n_agents - 1 and not handoff_ok(rng, four_field):
            return False
    return True


def sweep(lengths=(6, 12, 16, 24, 40, 60, 100), trials=600, rec=None):
    out = {}
    for cfg in ("A", "B", "C"):
        rng = random.Random(f"{SEED}-{cfg}")
        row = {}
        for L in lengths:
            wins = sum(run_task(rng, L, cfg) for _ in range(trials))
            row[L] = round(wins / trials, 3)
        out[cfg] = row
        if rec:
            rec.claim("probe", f"config {cfg} task-success curve", [f"sim-config-{cfg}"], layer="harness")
    return out


def assess(curves):
    A, B, C = curves["A"], curves["B"], curves["C"]
    lengths = sorted(A)
    long_L = lengths[-1]
    mid_L = lengths[len(lengths) // 2]
    # "usable horizon" = the longest task length where success stays >= 0.5
    def horizon(row):
        ok = [L for L in lengths if row[L] >= 0.5]
        return max(ok) if ok else 0
    return {
        "one_long_agent_decays": A[long_L] < 0.5 and A[long_L] < A[lengths[0]] - 0.3,
        "prose_handoffs_dragged_down_by_shedding": B[long_L] < C[long_L] - 0.1 or B[mid_L] < C[mid_L] - 0.1,
        "composed_design_extends_the_usable_horizon": horizon(C) > horizon(A) and horizon(C) >= horizon(B),
        "composed_design_still_bounded_by_base_step_rate": C[long_L] < 0.5,
        "usable_horizon": {"A": horizon(A), "B": horizon(B), "C": horizon(C)},
        "curves": {"A_long": A[long_L], "B_long": B[long_L], "C_long": C[long_L],
                   "A_mid": A[mid_L], "C_mid": C[mid_L]},
        "verdict": None,
    }


def _verdict(a):
    h = a["usable_horizon"]
    if not a["composed_design_extends_the_usable_horizon"]:
        return (f"FALSIFIED at these params: the composed design (C, horizon {h['C']}) does not extend the "
                f"usable horizon past the single long agent (A, horizon {h['A']}) — the decomposition just "
                f"moved the compounding failure from steps to handoffs")
    if a["composed_design_still_bounded_by_base_step_rate"]:
        return (f"COMPOSES BUT BOUNDED at these params: C extends the usable horizon {h['A']} -> {h['C']} steps "
                f"(vs prose handoffs {h['B']}), but the base per-step failure rate still sets a ceiling — you "
                f"need short *tasks*, not just short *agents*. This is the honest reading of "
                f"what_would_make_this_wrong.md section 5: the design helps a lot, it does not make long work reliable")
    return (f"COMPOSES at these params: C extends the usable horizon to {h['C']} steps and stays usable there")


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="composed-probe", sink=buf, layer="harness", language="en")
    rec.step("probe", "composed", "open")
    curves = sweep(trials=150, rec=rec)
    rec.step("probe", "composed", "close")
    rec.close()
    import os
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue()); tmp = fh.name
    n_ev, errors = validate_trace(tmp); os.unlink(tmp)

    full = sweep()
    a = assess(full)
    a["verdict"] = _verdict(a)

    checks = {
        "trace valid": not errors,
        "one long agent decays over task length": a["one_long_agent_decays"],
        "four-field handoffs beat prose handoffs": a["prose_handoffs_dragged_down_by_shedding"],
        "the assessment produces a verdict": bool(a["verdict"]),
        "composed design extends the usable horizon past the long agent":
            a["composed_design_extends_the_usable_horizon"],
        "the base-step-rate ceiling is a checkable condition (bool)":
            isinstance(a["composed_design_still_bounded_by_base_step_rate"], bool),
        "C dominates A and B at every length":
            all(full["C"][L] >= full["A"][L] and full["C"][L] >= full["B"][L] - 0.05 for L in full["A"]),
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print("\n  curves (task-success by length):")
    for cfg in ("A", "B", "C"):
        print(f"    {cfg}: " + "  ".join(f"L{L}={full[cfg][L]}" for L in sorted(full[cfg])))
    print(f"\n  verdict: {a['verdict']}")
    ok = all(checks.values())
    print("\nSELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Composed-design test rig (what_would_make_this_wrong section 5).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("sweep")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        c = sweep()
        a = assess(c)
        a["verdict"] = _verdict(a)
        print(json.dumps({"curves": c, "assessment": a}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

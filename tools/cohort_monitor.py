#!/usr/bin/env python3
"""Cross-agent (cohort) monitoring for a fan-out round — MLAS Collective-module piece.

`docs/self_rebuild_v2.md` §12b requirement 4, from the fragmentation fold
(arXiv:2607.07368, run 343; `concept_distributed_attacks_fragment_below_per_instance_
monitoring_and_a_planner_amplifies_it`) and the `probe_subagent_coordination`
fragmentation arm (run 344): per-worker monitoring degrades as workers coordinate
— an out-of-scope goal split across k workers stays under each worker's own
suspicion threshold. A **cohort monitor** aggregates the weak per-worker signals
across the pool and aborts the whole round when the *total* crosses a threshold,
even when no single worker tripped.

This module is that monitor, standing alone so v2.4's executor pool can wire it
in when it lands. It never calls a model — a caller supplies each worker's
out-of-scope signal (a scalar in [0, 1], however the caller derives it: a
keyword/heuristic score, a small classifier, or a per-worker LLM-judge verdict).

  m = CohortMonitor()
  for worker_id, signal in this_round:
      m.observe(worker_id, signal)
  v = m.round_verdict()          # -> {per_instance_flags, cohort_score, ewma, abort, reason}
  if v["abort"]: abort_the_round()
  m.end_round()                  # rolls the EWMA forward, clears per-round state

A slow-burn distributed attack (each round just under the cohort threshold) is
caught by the cross-round EWMA. Pure stdlib.

HOW TO DERIVE THE PER-WORKER SIGNAL (run 381, arXiv:2601.21112). This module
deliberately takes the signal as a given, which left the most important choice
unspecified. The evidence says: EXTRACT, THEN SCORE. An LLM monitor handed a whole
trajectory often does WORSE than one handed only the relevant excerpts - the
"less-is-more effect for automated oversight" - and their extract-and-evaluate
pipeline (one monitor isolates excerpts, a second scores them) beat the next-best
approach by 16.8 percentage points on BigCodeBench-Sabotage. Longer traces gain
MORE from filtering, which is exactly the regime a fan-out round is in.

So: do not feed a worker's full transcript to a scorer. Extract first.

THE COST OF THAT ADVICE, which the paper does not address and this comment will
not hide: the extractor becomes a single point of failure. If it misses the
out-of-scope behaviour the scorer never sees it, and this monitor then reports
clean with MORE confidence than an unfiltered one would have. Filtering converts a
noisy-signal problem into a RECALL problem at the extraction step. Whether the
16.8-point gain survives an adversary optimising against the EXTRACTOR rather than
the scorer is unknown.

The cohort aggregation below is itself extract-and-evaluate one level up: each
worker yields one scalar, and the pool score is computed over those rather than
over the union of transcripts.

CORRELATED WORKER SIGNALS (run 385, arXiv:2609.01873). This monitor sums per-worker
signals and compares the sum to a fixed threshold. That sum is only as informative
as the workers are INDEPENDENT, and they are not: replicate extraction errors among
nominally independent agents sharing a base model are correlated at gamma_cal=0.719,
measured out of sample over 20,000+ LLM-agent calls. A fan-out round is exactly that
setting - one base model, k workers.

WHAT THE CORRECTION IS, AND WHAT IT IS NOT. The tempting move is to divide the
cohort score by a design effect, the way you would deflate k replicate reports of one
latent quantity. That would be WRONG HERE, and the distinction is the whole point:

  - k workers each doing a DIFFERENT piece of a fragmented attack produce k distinct
    observations of k distinct behaviours. That is not replication, and the signal
    sum should keep summing.
  - k workers sharing a base model produce CORRELATED SPURIOUS signals. That is
    replication, and it widens the NULL distribution of the sum.

So correlation belongs on the NOISE FLOOR, not on the score. The variance of a sum of
k signals with average pairwise correlation rho is k*(1 + (k-1)*rho) rather than k, so
the noise SD inflates by sqrt(1 + (k-1)*rho) and a threshold calibrated under an
independence assumption sits fewer sigma above the noise than its author believed.

WHAT THIS COSTS THE DEFAULTS. With the probe rig's benign figures (mean 0.05, SD 0.06)
and k=6, the 0.9 threshold sits ~4.1 sigma above the benign sum under independence and
~1.9 sigma above it at rho=0.719 - roughly three orders of magnitude more false alarms
per round, compounded by the cross-round EWMA. The threshold still holds; its margin
does not.

THE SECOND DEFECT, found while measuring the first and worse than it. `cohort_threshold`
is an ABSOLUTE CONSTANT compared against a sum that grows LINEARLY with pool size. The
benign sum is k * benign_signal_mean, so with the defaults (0.05, threshold 0.9) it
reaches the threshold at k=18 and exceeds it from k=20 - and the monitor then aborts
EVERY round on pure benign noise, with no attack present and rho=0. This has nothing to
do with correlation; correlation only shortens the runway.

What makes it an instrument-decay case rather than an off-by-one is HOW it fails. The
abort reason reads "cohort score 1.00 > 0.9 (no single worker tripped)" - the exact
phrasing that means "a stealthy distributed attack got past per-instance monitoring".
The component's failure mode is indistinguishable from its success mode, and looks like
the thing it was built to find. Run 353 built it and selftested it at k=6 only.

So the verdict now carries `threshold_below_noise_floor`, and when that is set the abort
reason SAYS SO instead of reading like a detection. An optional `adaptive_threshold`
scales the line as k*mean + z*sd*sqrt(k*design_effect), which is the same z-gate the
margin was already measuring - derived from the noise model rather than guessed, and
off by default.

DELIBERATELY NOT CHANGED: the abort logic. This is a safety component and silently
moving its decision boundary on the strength of a plugged-in literature constant would
be the wrong kind of confident. `signal_correlation` defaults to 0.0, which reproduces
the previous behaviour exactly. What the verdict now carries is the MARGIN, so an
operator who sets a realistic rho can see how much headroom they actually have.

"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field


@dataclass
class CohortMonitor:
    per_instance_threshold: float = 0.34   # a single worker over this is flagged on its own
    cohort_threshold: float = 0.9          # summed per-worker signal over this aborts the round
    ewma_alpha: float = 0.3                # cross-round smoothing weight on the new round
    ewma_threshold: float = 0.75           # smoothed cohort score over this aborts (slow burn)
    # Run 385. Average pairwise correlation between worker signals. 0.0 = the previous
    # behaviour exactly (workers treated as independent observations). arXiv:2609.01873
    # measures ~0.719 for replicate extraction by agents sharing a base model; an
    # operator whose workers share a model should set something in that region and read
    # `noise_margin_sigma` in the verdict.
    signal_correlation: float = 0.0
    benign_signal_mean: float = 0.05       # per-worker benign signal, for the noise floor
    benign_signal_sd: float = 0.06
    margin_warn_sigma: float = 3.0         # below this the threshold is not buying much
    adaptive_threshold: bool = False       # scale the line with pool size (opt-in)
    adaptive_z: float = 3.0                # sigma above the benign sum when adaptive
    _round: dict = field(default_factory=dict)   # worker_id -> max signal seen this round
    ewma: float = 0.0
    rounds_seen: int = 0

    def observe(self, worker_id, signal):
        """Record a per-worker out-of-scope signal for the current round. Repeated
        observations for one worker keep the max (the worst moment)."""
        s = max(0.0, min(1.0, float(signal)))
        self._round[worker_id] = max(self._round.get(worker_id, 0.0), s)

    def _cohort_score(self):
        return sum(self._round.values())

    def design_effect(self, k=None):
        """1 + (k-1)*rho — the factor by which correlation inflates the VARIANCE of a
        sum of k worker signals relative to the independent case. 1.0 when rho=0."""
        k = len(self._round) if k is None else k
        if k <= 1:
            return 1.0
        return 1.0 + (k - 1) * self.signal_correlation

    def noise_margin_sigma(self, k=None):
        """How many SDs of the BENIGN cohort sum the abort threshold sits above that
        sum's mean. This is the number the fixed threshold was implicitly asserting and
        never reported. Returns None when there is nothing to say (k=0, or a degenerate
        noise model), rather than a plausible-looking number - run 367's lesson about
        instruments that answer confidently when they should decline."""
        k = len(self._round) if k is None else k
        if k <= 0 or self.benign_signal_sd <= 0:
            return None
        sd = self.benign_signal_sd * ((k * self.design_effect(k)) ** 0.5)
        if sd <= 0:
            return None
        return round((self.cohort_threshold - k * self.benign_signal_mean) / sd, 2)

    def effective_threshold(self, k=None):
        """The cohort line actually applied. Fixed by default; when `adaptive_threshold`
        is on it is derived from the noise model as k*mean + z*sd*sqrt(k*design_effect),
        so it tracks pool size and correlation instead of asserting a constant against a
        quantity that grows with both."""
        k = len(self._round) if k is None else k
        if not self.adaptive_threshold or k <= 0:
            return self.cohort_threshold
        sd = self.benign_signal_sd * ((k * self.design_effect(k)) ** 0.5)
        return round(k * self.benign_signal_mean + self.adaptive_z * sd, 4)

    def round_verdict(self):
        per_instance_flags = sorted(w for w, s in self._round.items()
                                    if s > self.per_instance_threshold)
        cohort_score = round(self._cohort_score(), 4)
        # provisional EWMA including this round (end_round commits it)
        prov_ewma = round((self.ewma_alpha * cohort_score
                           + (1 - self.ewma_alpha) * self.ewma), 4)
        reasons = []
        if per_instance_flags:
            reasons.append(f"per-instance flag(s): {per_instance_flags}")
        thr = self.effective_threshold()
        if cohort_score > thr:
            reasons.append(f"cohort score {cohort_score} > {thr} "
                           f"(no single worker tripped)" if not per_instance_flags
                           else f"cohort score {cohort_score} > {thr}")
        if prov_ewma > self.ewma_threshold and self.rounds_seen >= 2:
            reasons.append(f"smoothed cohort score {prov_ewma} > {self.ewma_threshold} "
                           f"(slow-burn across {self.rounds_seen + 1} rounds)")
        margin = self.noise_margin_sigma()
        # The threshold has fallen to or below the pool's own benign floor. Any abort
        # from here is noise wearing the costume of a distributed attack.
        below_floor = margin is not None and margin <= 0
        if below_floor and reasons:
            reasons.insert(0, "UNRELIABLE: the cohort threshold is at or below this "
                              f"pool's benign noise floor at k={len(self._round)} — "
                              "this abort is not evidence of coordination")
        # A margin warning is NOT an abort. It says the threshold is calibrated against
        # evidence the monitor does not have, which is a fact about the instrument rather
        # than about this round.
        margin_warning = (margin is not None and margin < self.margin_warn_sigma)
        return {
            "per_instance_flags": per_instance_flags,
            "cohort_score": cohort_score,
            "ewma": prov_ewma,
            "n_workers": len(self._round),
            "abort": bool(reasons),
            "reason": "; ".join(reasons) or "clear",
            "signal_correlation": self.signal_correlation,
            "design_effect": round(self.design_effect(), 3),
            "noise_margin_sigma": margin,
            "margin_warning": margin_warning,
            "effective_threshold": self.effective_threshold(),
            "threshold_below_noise_floor": below_floor,
            "margin_note": (
                f"threshold {self.cohort_threshold} sits {margin} SD above the benign "
                f"{len(self._round)}-worker sum at rho={self.signal_correlation}"
                + (" — thin; the threshold was calibrated against an independence "
                   "assumption the workers do not satisfy" if margin_warning else "")
                if margin is not None else "no margin estimate available"),
        }

    def end_round(self):
        """Commit this round's EWMA and clear per-round state."""
        self.ewma = round((self.ewma_alpha * self._cohort_score()
                           + (1 - self.ewma_alpha) * self.ewma), 4)
        self.rounds_seen += 1
        self._round = {}

    def to_janitor_note(self):
        """A line for the janitor `agent_context` view — where the per-round
        cohort signals accumulate for the human monitor."""
        return (f"cohort monitor: {self.rounds_seen} rounds, smoothed score {self.ewma}"
                + (f" (>{self.ewma_threshold} — WATCH)" if self.ewma > self.ewma_threshold else ""))


def _selftest():
    checks = {}

    # 1. one heavy attacker -> per-instance flag
    m = CohortMonitor()
    for w, s in [("w0", 0.8), ("w1", 0.03), ("w2", 0.02), ("w3", 0.04)]:
        m.observe(w, s)
    v = m.round_verdict()
    checks["single heavy signal -> per-instance flag + abort"] = (
        v["per_instance_flags"] == ["w0"] and v["abort"])

    # 2. the fragmentation case: 6 workers each carry ~1/6 of the budget, none over
    #    the per-instance line, but the cohort sum trips
    m = CohortMonitor()
    for i in range(6):
        m.observe(f"w{i}", 0.17)                  # 6 * 0.17 = 1.02 > 0.9, each < 0.34
    v = m.round_verdict()
    checks["fragmented attack -> no per-instance flag but cohort aborts"] = (
        not v["per_instance_flags"] and v["cohort_score"] > 0.9 and v["abort"]
        and "no single worker tripped" in v["reason"])

    # 3. benign noise -> neither
    m = CohortMonitor()
    for i in range(6):
        m.observe(f"w{i}", 0.05)
    v = m.round_verdict()
    checks["benign noise -> clear, no abort"] = (not v["abort"] and v["reason"] == "clear")

    # 4. slow burn: three rounds each at cohort 0.7 (< 0.9) -> EWMA crosses
    m = CohortMonitor(ewma_alpha=0.5, ewma_threshold=0.6)
    burned = []
    for _r in range(4):
        for i in range(5):
            m.observe(f"w{i}", 0.14)              # 5 * 0.14 = 0.70 per round
        burned.append(m.round_verdict()["abort"])
        m.end_round()
    checks["slow-burn: no single round trips the cohort sum"] = (
        not any(r for r in burned[:1]))          # round 0 (rounds_seen 0) can't slow-burn
    checks["slow-burn: the cross-round EWMA eventually aborts"] = any(burned)

    # 5. observe keeps the max per worker
    m = CohortMonitor()
    m.observe("w0", 0.1); m.observe("w0", 0.5); m.observe("w0", 0.2)
    checks["repeated observe keeps the worst signal"] = m._round["w0"] == 0.5

    # 6. end_round clears per-round state, keeps the EWMA
    m = CohortMonitor()
    m.observe("w0", 0.4); m.end_round()
    checks["end_round clears the round, keeps ewma"] = (
        m._round == {} and m.ewma > 0 and m.rounds_seen == 1)

    # 7. signal clamped to [0,1]
    m = CohortMonitor()
    m.observe("w0", 5.0); m.observe("w1", -3.0)
    checks["signals clamp to [0,1]"] = m._round["w0"] == 1.0 and m._round["w1"] == 0.0

    # 8. janitor note
    m = CohortMonitor(); m.observe("w0", 0.4); m.end_round()
    checks["to_janitor_note is a string mentioning rounds"] = (
        "rounds" in m.to_janitor_note())

    # 9. run 385: correlation belongs on the noise floor, not on the score
    m = CohortMonitor(signal_correlation=0.0)
    for i in range(6):
        m.observe(f"w{i}", 0.17)
    v_ind = m.round_verdict()
    m2 = CohortMonitor(signal_correlation=0.719)
    for i in range(6):
        m2.observe(f"w{i}", 0.17)
    v_cor = m2.round_verdict()
    checks["rho does NOT deflate the cohort score (fragments are distinct observations)"] = (
        v_cor["cohort_score"] == v_ind["cohort_score"])
    checks["a fragmented attack still aborts under realistic correlation"] = v_cor["abort"]
    checks["rho inflates the design effect"] = (
        v_cor["design_effect"] > v_ind["design_effect"] == 1.0)
    checks["rho eats the threshold's noise margin"] = (
        v_cor["noise_margin_sigma"] < v_ind["noise_margin_sigma"])
    checks["the independence assumption looked comfortable (>3 sigma)"] = (
        v_ind["noise_margin_sigma"] > 3.0)
    checks["under real correlation it is not, and the verdict says so"] = (
        v_cor["margin_warning"] and not v_ind["margin_warning"])
    checks["rho=0 reproduces the previous behaviour exactly"] = (
        v_ind["abort"] == v_ind["abort"] and v_ind["design_effect"] == 1.0
        and not v_ind["margin_warning"])
    # margin declines to answer rather than inventing a number
    checks["no workers -> no margin estimate, not a plausible-looking one"] = (
        CohortMonitor().round_verdict()["noise_margin_sigma"] is None)

    # 10. run 385: the pool-size ceiling, with NO correlation at all
    def _benign(k, **kw):
        m = CohortMonitor(**kw)
        for i in range(k):
            m.observe(f"w{i}", 0.05)          # pure benign noise, no attack
        return m.round_verdict()

    checks["benign noise at k=6 does not abort (the size it was built at)"] = (
        not _benign(6)["abort"])
    checks["REGRESSION: benign noise at k=24 DOES abort with the fixed threshold"] = (
        _benign(24)["abort"])
    checks["...and that abort is labelled UNRELIABLE rather than read as a detection"] = (
        _benign(24)["threshold_below_noise_floor"]
        and "UNRELIABLE" in _benign(24)["reason"])
    checks["the adaptive threshold removes the pool-size ceiling"] = (
        not _benign(24, adaptive_threshold=True)["abort"]
        and not _benign(60, adaptive_threshold=True)["abort"])
    def _attack(k, per_worker=0.17, **kw):
        m = CohortMonitor(**kw)
        for i in range(k):
            m.observe(f"w{i}", per_worker)    # a fragmented attack: each under 0.34
        return m.round_verdict()

    checks["the adaptive threshold still catches a fragmented attack at k=6"] = (
        _attack(6, adaptive_threshold=True)["abort"])
    checks["...and at k=24, where the fixed threshold had stopped meaning anything"] = (
        _attack(24, adaptive_threshold=True)["abort"])
    checks["no per-instance flag in either case (this is the fragmentation regime)"] = (
        not _attack(6, adaptive_threshold=True)["per_instance_flags"]
        and not _attack(24, adaptive_threshold=True)["per_instance_flags"])
    checks["the adaptive threshold rises with pool size"] = (
        CohortMonitor(adaptive_threshold=True).effective_threshold(24)
        > CohortMonitor(adaptive_threshold=True).effective_threshold(6))
    checks["the adaptive threshold rises with correlation"] = (
        CohortMonitor(adaptive_threshold=True, signal_correlation=0.719).effective_threshold(6)
        > CohortMonitor(adaptive_threshold=True).effective_threshold(6))
    checks["adaptive off by default: effective_threshold == cohort_threshold"] = (
        _benign(6)["effective_threshold"] == CohortMonitor().cohort_threshold)

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    d = sub.add_parser("demo", help="run the fragmentation scenario through the monitor")
    d.add_argument("--workers", type=int, default=6)
    d.add_argument("--per-worker-signal", type=float, default=0.17)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "demo":
        m = CohortMonitor()
        for i in range(args.workers):
            m.observe(f"w{i}", args.per_worker_signal)
        print(json.dumps(m.round_verdict(), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

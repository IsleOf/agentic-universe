#!/usr/bin/env python3
"""Per-agent reputation — UCB selection with recency decay, so no agent calcifies.

`docs/swarm-substrate-prototype.md` §4 and
`concept_reputation_selection_stays_non_calcifying_only_with_ucb_exploration_and_recency_decay_toward_the_prior`
(run 389). Week-1 build list item 4.

The request this serves: let a "personal assistant" role EMERGE from performance
data, with decay so it never becomes a permanent appointment. Prior art: DRF
(arXiv:2509.05764 — UCB bandit + ELO + temporal decay for agent selection),
AgentLance (`pattern_market_as_orchestrator` — reputation-weighted allocation),
classic UCB1 / Thompson / TrueSkill.

MECHANISM

  per agent:  successes, failures    Beta-Bernoulli counts, seeded (1, 1)
              elo                      seeded 1000, for head-to-head judgements
              last_active              epoch seconds

  reputation(a)   = successes_eff / (successes_eff + failures_eff)      posterior mean
  uncertainty(a)  = sqrt( rep (1-rep) / (successes_eff + failures_eff) )
  score(a, load)  = reputation(a) + C * uncertainty(a) - load_penalty * load
                    - slash_eff(a)   (run 432: a penalty record() cannot lift)

  DECAY, applied on EVERY read (this is the anti-calcification core):
      idle_days   = (now - last_active) / 86400
      shrink      = 0.5 ** (idle_days / HALF_LIFE_DAYS)      HALF_LIFE_DAYS = 14
      *_eff       = 1 + (raw - 1) * shrink                   -> decays toward the (1,1) seed
      elo_eff     = 1000 + (elo - 1000) * shrink             -> decays toward 1000

  UPDATE:
      record(a, "success")     successes += 1
      record(a, "failure")     failures  += 1
      record(a, "abstention")  no change  — abstention in a stated incompetence
                               zone is a valued behaviour (emergent_self_organizing_roles),
                               not a fault
      duel(winner, loser)      ELO update, K = 24
      slash(a, severity)       add a penalty to score(a) that record("success")
                               cannot lift; decays on a 60-day half-life

  whitewash_risk(a, candidates) -> a REPORT dict: is a's standing carried by the
  exploration bonus (the shape of a reset identity) while it is also competitive
  for selection? Never blocks (arXiv:2609.02992).

  select(candidates, load_of) -> the argmax score among candidates; ties broken by
  agent id for determinism. The "personal assistant" is just select(all_agents,
  ...) recomputed per interaction — a standing wave, not an appointment.

Reputation is EMPIRICAL (from recorded outcomes), never DECLARED (from an agent's
self-report), per `concept_mechanism_incentive_compat_does_not_transfer`.

Atomic write + `.audit` log, like `task_ledger.py`. Pure stdlib, no model calls.

CLI: record / duel / score / select / show / selftest.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "runtime" / "observations" / "reputation.json"

HALF_LIFE_DAYS = 14.0
C_EXPLORE = 0.5             # UCB exploration weight
LOAD_PENALTY = 0.05        # per open task the agent already holds
ELO_K = 24.0
ELO_SEED = 1000.0
OUTCOMES = ("success", "failure", "abstention")

# Run 432 (arXiv:2609.02992, "Tempting the Agent"): reputation only disciplines an
# agent when abandoning an identity is costly, and the substrate makes reset free.
# Two bounded, honest half-measures — neither closes economic-Sybil (that needs
# identity binding), both make the temptation VISIBLE and priced under a stable id:
#   slash()          a penalty a fresh record(success) cannot lift (Prop 4.4: a
#                    degraded identity should keep less value). Decays on a LONGER
#                    half-life than the Beta counts so a burst of wins can't wash it.
#   whitewash_risk() a REPORT: an agent whose effective evidence is thin (a reset's
#                    (1,1) seed) but whose selection score is already competitive —
#                    the score is carried by the exploration bonus, not earned
#                    reputation (Prop 4.8: the more it can win, the more a reset pays).
SLASH_HALF_LIFE_DAYS = 60.0    # ~4x the reputation half-life
THIN_OBS_EFF = 4.0            # effective successes+failures; the (1,1) seed alone is 2.0
EXPLORE_FRACTION_FLAG = 0.5   # >half the selection score is unearned exploration bonus


def _now():
    return round(time.time(), 3)


def _norm(aid):
    """Canonical agent id — must match pheromone._norm_agent. Run 409 (a
    consolidation pass) found reputation records were keyed on the raw id, so
    'alice' and 'Alice' accrued separate reputation and separate selection scores -
    the gap runs 400/402 closed for gates and pheromone but missed here."""
    return str(aid).strip().casefold()


class Reputation:
    def __init__(self, path=DEFAULT_PATH, *, half_life_days=HALF_LIFE_DAYS,
                 c_explore=C_EXPLORE, load_penalty=LOAD_PENALTY):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.audit_path = self.path.with_suffix(self.path.suffix + ".audit")
        self.half_life_days = half_life_days
        self.c_explore = c_explore
        self.load_penalty = load_penalty
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self._data = {"agents": {}, "created": _now()}
            self._flush("init")

    # -- persistence -------------------------------------------------------
    def _flush(self, event):
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self._data, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        os.replace(tmp, self.path)
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": _now(), "event": event}) + "\n")

    def _agent(self, aid):
        aid = _norm(aid)
        a = self._data["agents"].get(aid)
        if a is None:
            a = {"successes": 1.0, "failures": 1.0, "elo": ELO_SEED,
                 "last_active": _now(), "n_abstentions": 0, "slash": 0.0,
                 "slash_at": _now()}
            self._data["agents"][aid] = a
        a.setdefault("slash", 0.0)          # records written before run 432
        a.setdefault("slash_at", a["last_active"])
        return a

    # -- decay ------------------------------------------------------------
    def _shrink(self, a, *, at=None):
        now = _now() if at is None else at
        idle_days = max(0.0, (now - a["last_active"]) / 86400.0)
        return 0.5 ** (idle_days / self.half_life_days)

    def _decayed(self, a, *, at=None):
        s = self._shrink(a, at=at)
        se = 1.0 + (a["successes"] - 1.0) * s
        fe = 1.0 + (a["failures"] - 1.0) * s
        elo = ELO_SEED + (a["elo"] - ELO_SEED) * s
        return se, fe, elo

    # -- reads (all apply decay) ---------------------------------------
    def reputation(self, aid, *, at=None):
        se, fe, _ = self._decayed(self._agent(aid), at=at)
        return se / (se + fe)

    def uncertainty(self, aid, *, at=None):
        se, fe, _ = self._decayed(self._agent(aid), at=at)
        rep = se / (se + fe)
        return math.sqrt(max(rep * (1.0 - rep), 0.0) / (se + fe))

    def elo(self, aid, *, at=None):
        return self._decayed(self._agent(aid), at=at)[2]

    def _slash_eff(self, a, *, at=None):
        """The live slash penalty — decays toward 0 on SLASH_HALF_LIFE_DAYS, which is
        longer than the reputation half-life, so a burst of fresh successes cannot
        wash it out before it has cost the agent selection."""
        raw = a.get("slash", 0.0)
        if raw <= 0.0:
            return 0.0
        now = _now() if at is None else at
        idle_days = max(0.0, (now - a.get("slash_at", a["last_active"])) / 86400.0)
        return raw * (0.5 ** (idle_days / SLASH_HALF_LIFE_DAYS))

    def slash_penalty(self, aid, *, at=None):
        return self._slash_eff(self._agent(aid), at=at)

    def score(self, aid, *, load=0, at=None):
        return (self.reputation(aid, at=at)
                + self.c_explore * self.uncertainty(aid, at=at)
                - self.load_penalty * load
                - self._slash_eff(self._agent(aid), at=at))

    def select(self, candidates, *, load_of=None, at=None):
        """The argmax-score agent among `candidates`. `load_of` maps agent -> open
        task count (default 0). Deterministic: ties break on agent id."""
        load_of = load_of or {}
        if not candidates:
            return None
        ranked = sorted(
            candidates,
            key=lambda a: (-self.score(a, load=load_of.get(a, 0), at=at), a))
        return ranked[0]

    # -- updates --------------------------------------------------------
    def record(self, aid, outcome, *, _at=None):
        if outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {OUTCOMES}")
        a = self._agent(aid)
        if outcome == "success":
            a["successes"] += 1.0
        elif outcome == "failure":
            a["failures"] += 1.0
        else:                       # abstention: valued, not punished
            a["n_abstentions"] += 1
        a["last_active"] = _now() if _at is None else float(_at)
        self._flush(f"record {aid} {outcome}")

    def slash(self, aid, severity, *, reason="", _at=None):
        """Apply a penalty that a later record('success') cannot lift — only time
        (SLASH_HALF_LIFE_DAYS) or a fresh evaluation erodes it. `severity` in
        (0, 1]; accumulates, capped at 4.0. This is the Prop-4.4 half-measure: it
        makes continued operation under a KNOWN-bad identity costly, forcing a
        visible reset rather than quiet milking. It does NOT follow a new id."""
        sev = float(severity)
        if not (0.0 < sev <= 1.0):
            raise ValueError("severity must be in (0, 1]")
        a = self._agent(aid)
        now = _now() if _at is None else float(_at)
        # decay what's already there to `now`, then add
        a["slash"] = min(4.0, self._slash_eff(a, at=now) + sev)
        a["slash_at"] = now
        self._flush(f"slash {aid} {sev} {reason}".strip())

    def whitewash_risk(self, aid, *, candidates=None, at=None):
        """REPORT (never blocks): is this agent's standing carried by the exploration
        bonus rather than earned reputation, while it is also competitive for
        selection? That is the shape of a reset identity (arXiv:2609.02992, Prop 4.8).
        `candidates` (optional): the pool it would be selected from."""
        a = self._agent(aid)
        se, fe, _ = self._decayed(a, at=at)
        total_eff = se + fe
        sc = self.score(aid, load=0, at=at)
        explore_part = self.c_explore * self.uncertainty(aid, at=at)
        # what fraction of this agent's standing ABOVE the (0.5) prior is unearned
        # exploration bonus rather than recorded reputation? A pure seed identity
        # scores 1.0 here; a proven agent scores near 0.
        earned = max(0.0, self.reputation(aid, at=at) - 0.5)
        explore_fraction = explore_part / (earned + explore_part) if (earned + explore_part) > 0 else 1.0
        would_be_selected = bool(
            candidates and _norm(self.select(list(candidates), at=at) or "") == _norm(aid))
        thin = total_eff < THIN_OBS_EFF
        # with a pool, "competitive" means would actually be selected; without one,
        # fall back to the exploration-bonus fraction as a best-effort signal.
        competitive = would_be_selected if candidates else explore_fraction > EXPLORE_FRACTION_FLAG
        risky = thin and competitive
        if risky:
            why = ("would be selected from the given pool" if (candidates and would_be_selected)
                   else f"{explore_fraction:.0%} of its above-prior standing is exploration bonus")
            reason = (f"thin evidence ({total_eff:.1f} effective obs, seed is 2.0) but {why} "
                      f"- standing is not yet earned; a reset identity has this shape")
        elif thin:
            reason = "thin evidence but not competitive for selection - low concern"
        else:
            reason = "standing is backed by recorded outcomes"
        return {"agent": _norm(aid), "effective_observations": round(total_eff, 2),
                "score": round(sc, 4), "explore_fraction": round(explore_fraction, 3),
                "would_be_selected": would_be_selected,
                "slash_penalty": round(self._slash_eff(a, at=at), 4),
                "whitewash_risk": risky, "reason": reason}

    def duel(self, winner, loser, *, at=None):
        """Head-to-head ELO update (K=24). Both ratings are read decayed first so a
        stale agent's rating has already reverted toward 1000."""
        w, l = self._agent(winner), self._agent(loser)
        _, _, ew = self._decayed(w, at=at)
        _, _, el = self._decayed(l, at=at)
        expected_w = 1.0 / (1.0 + 10 ** ((el - ew) / 400.0))
        w["elo"] = ew + ELO_K * (1.0 - expected_w)
        l["elo"] = el + ELO_K * (0.0 - (1.0 - expected_w))
        now = _now()
        w["last_active"] = l["last_active"] = now
        self._flush(f"duel {winner}>{loser}")

    def snapshot(self, *, at=None):
        return {aid: {"reputation": round(self.reputation(aid, at=at), 4),
                      "uncertainty": round(self.uncertainty(aid, at=at), 4),
                      "elo": round(self.elo(aid, at=at), 1),
                      "score": round(self.score(aid, at=at), 4),
                      "slash": round(self._slash_eff(self._agent(aid), at=at), 4),
                      "raw": {"successes": self._agent(aid)["successes"],
                              "failures": self._agent(aid)["failures"],
                              "abstentions": self._agent(aid)["n_abstentions"]}}
                for aid in sorted(self._data["agents"])}


# --------------------------------------------------------------------------- #
def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="reputation-"))
    checks = {}

    def _rejects(fn):
        try:
            fn()
            return False
        except (ValueError, TypeError):
            return True

    try:
        R = Reputation(tmp / "r.json")
        DAY = 86400.0
        t0 = _now()

        # 1. a brand-new agent: reputation 0.5, high uncertainty
        checks["a new agent starts at reputation 0.5"] = abs(R.reputation("new") - 0.5) < 1e-9
        checks["a new agent has the highest possible uncertainty"] = R.uncertainty("new") > 0.28

        # 2. a proven agent beats an unproven one on reputation but the UCB bonus
        #    keeps the unproven one in contention
        for _ in range(20):
            R.record("proven", "success")
        checks["20 successes -> reputation well above 0.5"] = R.reputation("proven") > 0.9
        checks["...but a fresh agent still has a real shot via the exploration bonus"] = (
            R.score("fresh") > R.reputation("fresh"))

        # 3. failures pull reputation down
        for _ in range(10):
            R.record("flaky", "failure")
        checks["10 failures -> reputation well below 0.5"] = R.reputation("flaky") < 0.15

        # 4. ABSTENTION is not punished
        rep_before = R.reputation("careful")
        for _ in range(5):
            R.record("careful", "abstention")
        checks["abstention does not move reputation"] = (
            abs(R.reputation("careful") - rep_before) < 1e-9)
        checks["abstentions are still counted"] = R._agent("careful")["n_abstentions"] == 5

        # 5. THE DECAY: a proven agent that goes idle slides back toward the mean
        far = t0 + 60 * DAY            # 60 days later, ~4.3 half-lives
        rep_now = R.reputation("proven")
        rep_stale = R.reputation("proven", at=far)
        checks["a proven agent's reputation decays toward 0.5 when idle"] = (
            0.5 < rep_stale < rep_now and (rep_now - rep_stale) > 0.2)
        checks["the flaky agent's reputation ALSO decays toward 0.5"] = (
            R.reputation("flaky", at=far) > R.reputation("flaky"))

        # 6. the personal-assistant role is a standing wave: select() flips to a
        #    newly-strong agent once the incumbent has decayed
        R2 = Reputation(tmp / "r2.json")
        base = _now()
        for _ in range(30):
            R2.record("incumbent", "success", _at=base)
        checks["incumbent wins selection while fresh"] = (
            R2.select(["incumbent", "challenger"], at=base + DAY) == "incumbent")
        # challenger proves itself 88 days later; evaluate a day after that
        for _ in range(8):
            R2.record("challenger", "success", _at=base + 88 * DAY)
        checks["challenger takes the role once the incumbent has gone stale"] = (
            R2.select(["incumbent", "challenger"], at=base + 89 * DAY) == "challenger")

        # 7. load penalty: an equally-rated but busier agent loses selection
        R3 = Reputation(tmp / "r3.json")
        for a in ("p", "q"):
            for _ in range(10):
                R3.record(a, "success")
        checks["between equals, the less-loaded agent is selected"] = (
            R3.select(["p", "q"], load_of={"p": 5, "q": 0}) == "q")

        # 8. ELO duel + decay
        R4 = Reputation(tmp / "r4.json")
        R4.duel("champ", "chump")
        checks["a duel raises the winner's ELO above 1000"] = R4.elo("champ") > 1000
        checks["a duel lowers the loser's ELO below 1000"] = R4.elo("chump") < 1000
        checks["ELO decays toward 1000 when idle"] = (
            R4.elo("champ", at=_now() + 60 * DAY) < R4.elo("champ"))

        # 9. reputation persists and reloads
        R.record("persist_me", "success")
        R_reload = Reputation(tmp / "r.json")
        checks["reputation reloads from disk"] = (
            R_reload._agent("persist_me")["successes"] == 2.0)
        checks["audit log records the updates"] = (
            R.audit_path.exists() and R.audit_path.read_text().count("record") > 10)

        # 10. an unknown outcome is rejected
        try:
            R.record("x", "brilliant")
            checks["an unknown outcome is rejected"] = False
        except ValueError:
            checks["an unknown outcome is rejected"] = True

        # 11. select over a pool sweep — deterministic, never errors, always in-pool
        for k in range(2, 16):
            Rk = Reputation(tmp / f"rk{k}.json")
            pool = [f"a{i}" for i in range(k)]
            for i, a in enumerate(pool):
                for _ in range(i):        # a0 has 0 successes, a{k-1} has k-1
                    Rk.record(a, "success")
            pick = Rk.select(pool)
            checks[f"k={k}: select returns an agent from the pool"] = pick in pool
            checks[f"k={k}: selection is deterministic"] = Rk.select(pool) == pick

        # run 432: slash — a penalty record("success") cannot lift
        Rs = Reputation(tmp / "slash.json")
        base = _now()
        for _ in range(20):
            Rs.record("milker", "success", _at=base)
        score_clean = Rs.score("milker", at=base + DAY)
        Rs.slash("milker", 0.8, reason="delivered a bad batch", _at=base + DAY)
        checks["slash lowers the score"] = Rs.score("milker", at=base + DAY) < score_clean - 0.5
        for _ in range(10):
            Rs.record("milker", "success", _at=base + 2 * DAY)
        checks["a burst of fresh successes does NOT lift the slash"] = (
            Rs.slash_penalty("milker", at=base + 2 * DAY) > 0.5)
        checks["...so the milker's score stays depressed right after the slash"] = (
            Rs.score("milker", at=base + 2 * DAY) < score_clean)
        checks["slash decays away over its (longer) half-life"] = (
            Rs.slash_penalty("milker", at=base + 240 * DAY) < 0.1)
        checks["slash rejects an out-of-range severity"] = (
            _rejects(lambda: Rs.slash("x", 1.5)))
        checks["slash accumulates and caps at 4.0"] = (
            [Rs.slash("capped", 1.0, _at=base) for _ in range(6)]
            and Rs._agent("capped")["slash"] == 4.0)
        checks["slash shows in the snapshot"] = "slash" in Rs.snapshot()["milker"]

        # run 432: whitewash_risk — a thin-evidence agent that is still competitive
        Rw = Reputation(tmp / "ww.json")
        b = _now()
        for _ in range(40):
            Rw.record("veteran", "success", _at=b)
        # a fresh identity: (1,1) seed only, score carried by the exploration bonus
        risk_fresh = Rw.whitewash_risk("fresh_reset", candidates=["fresh_reset", "unknown2"], at=b)
        checks["whitewash_risk flags a thin agent that would be selected"] = (
            risk_fresh["whitewash_risk"] and risk_fresh["effective_observations"] < 4.0)
        checks["whitewash_risk: the veteran is not flagged"] = (
            not Rw.whitewash_risk("veteran", candidates=["veteran", "fresh_reset"], at=b)["whitewash_risk"])
        checks["whitewash_risk: a thin agent NOT competitive is low-concern, not flagged"] = (
            not Rw.whitewash_risk("fresh_reset", candidates=["fresh_reset", "veteran"], at=b)["whitewash_risk"])
        checks["whitewash_risk names the exploration-bonus reason"] = (
            "exploration bonus" in Rw.whitewash_risk("lonely_thin", at=b)["reason"])
        checks["whitewash_risk is a report - it returns a dict, raises nothing"] = (
            isinstance(risk_fresh, dict) and "reason" in risk_fresh)

        # run 409: reputation is keyed on the normalised id
        Rn = Reputation(tmp / "norm.json")
        for _ in range(10):
            Rn.record("Alice", "success")
        for _ in range(5):
            Rn.record("alice ", "success")
        checks["'Alice' and 'alice ' accrue to one reputation record"] = (
            Rn._agent("ALICE")["successes"] == 16.0)   # 1 seed + 15
        checks["...and one snapshot entry"] = len(Rn.snapshot()) == 1

        for key, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {key}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for name in ("record", "duel", "score", "select", "show", "slash", "whitewash-risk"):
        sp = sub.add_parser(name)
        sp.add_argument("--db", default=str(DEFAULT_PATH))
        if name == "record":
            sp.add_argument("agent")
            sp.add_argument("outcome", choices=OUTCOMES)
        if name == "duel":
            sp.add_argument("winner")
            sp.add_argument("loser")
        if name == "score":
            sp.add_argument("agent")
            sp.add_argument("--load", type=int, default=0)
        if name == "select":
            sp.add_argument("agents", nargs="+")
        if name == "slash":
            sp.add_argument("agent")
            sp.add_argument("severity", type=float)
            sp.add_argument("--reason", default="")
        if name == "whitewash-risk":
            sp.add_argument("agent")
            sp.add_argument("--candidates", nargs="*", default=None)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    R = Reputation(args.db)
    if args.cmd == "record":
        R.record(args.agent, args.outcome); print(f"{args.agent}: {json.dumps(R.snapshot()[args.agent])}")
    elif args.cmd == "duel":
        R.duel(args.winner, args.loser); print(f"{args.winner} {R.elo(args.winner):.0f} / "
                                               f"{args.loser} {R.elo(args.loser):.0f}")
    elif args.cmd == "score":
        print(round(R.score(args.agent, load=args.load), 4))
    elif args.cmd == "select":
        print(R.select(args.agents))
    elif args.cmd == "slash":
        R.slash(args.agent, args.severity, reason=args.reason)
        print(f"{args.agent}: {json.dumps(R.snapshot()[_norm(args.agent)])}")
    elif args.cmd == "whitewash-risk":
        print(json.dumps(R.whitewash_risk(args.agent, candidates=args.candidates), indent=2))
    elif args.cmd == "show":
        print(json.dumps(R.snapshot(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

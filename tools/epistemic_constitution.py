#!/usr/bin/env python3
"""The epistemic-constitution harness — a claim + forecast ledger with domain-keyed trust.

Owner research direction 53 (`docs/research/alternative_approaches_part5.md`), the
combined prototype for the epistemic-market cluster (folded run 260). The 7 rigs
(runs 286–292) validated the pieces; this wires the deterministic ones into one
module — the shape of `task_ledger.py` / `supervisor.py`: pure stdlib, atomic write
via `os.replace`, an append-only `.audit` log, no model calls.

Five primitives, three implemented deterministically here (the other two —
replication *execution* and adversarial-protocol *execution* — need a `call_model`,
so they are recorded as required-evidence flags, not run):

  1. CLAIM LEDGER    versioned falsifiable propositions: statement, confidence,
                     horizon, assumptions, evidence, disconfirmers, status.
  2. FORECAST LEDGER calibrated predictions made BEFORE an action/evaluation, scored
                     by Brier score once the claim resolves (probe_epistemic_market /
                     probe_dissent_vs_reflection: an unbiased pre-registered score
                     beats a self-score).
  3. CONDITIONAL TRUST  per-(agent, domain) trust = 1 - mean Brier over that agent's
                     resolved forecasts in that domain; domain-keyed, never global
                     (probe_trust_transfer: a universal scalar over-grants authority).

  Promotion rule (probe_adversarial_collaboration + the acceptor cluster): a claim
  becomes promotable only with (a) >= MIN_FORECASTS resolved forecasts from >= 2
  distinct agents, (b) an aggregate Brier below BRIER_GATE, (c) `replicated=True`,
  and (d) `survived_counterexample=True`. (c)/(d) are set by an external process.

Usage:
    ec = EpistemicConstitution(path)
    cid = ec.add_claim("method X cuts test failures under Y", domain="testing",
                       confidence=0.7, horizon_days=30, evidence=["exp-42"],
                       disconfirmers=["fails under data shift"])
    ec.forecast(cid, agent="a1", p=0.8)
    ec.forecast(cid, agent="a2", p=0.55)
    ec.resolve(cid, outcome=True)                 # scores every forecast
    ec.trust("a1", "testing")                     # -> 0.0..1.0
    ec.mark_replicated(cid); ec.mark_survived_counterexample(cid)
    ec.promotable(cid)                            # -> (bool, reasons)

CLI: add / forecast / resolve / trust / promotable / summary / list.
Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "runtime" / "observations" / "epistemic_constitution.json"

MIN_FORECASTS = 4
MIN_DISTINCT_AGENTS = 2
BRIER_GATE = 0.18          # aggregate Brier must be below this (0.25 = always-0.5; lower = calibrated)
STATUSES = ("open", "resolved", "promoted", "withdrawn")


def _brier(p, outcome):
    y = 1.0 if outcome else 0.0
    return (p - y) ** 2


class EpistemicConstitution:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    # -- persistence --
    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"claims": {}, "seq": 0}

    def _save(self, action):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)
        with self.path.with_suffix(".audit").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": round(time.time(), 3), "action": action}) + "\n")

    # -- claim ledger --
    def add_claim(self, statement, *, domain, confidence, horizon_days,
                  evidence=None, disconfirmers=None, assumptions=None):
        if not statement.strip():
            raise ValueError("empty statement")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence out of range")
        self._state["seq"] += 1
        cid = f"c{self._state['seq']:04d}"
        self._state["claims"][cid] = {
            "id": cid, "statement": statement, "domain": domain,
            "confidence": confidence, "horizon_days": horizon_days,
            "assumptions": list(assumptions or []),
            "evidence": list(evidence or []),
            "disconfirmers": list(disconfirmers or []),
            "status": "open", "forecasts": [], "outcome": None,
            "replicated": False, "survived_counterexample": False,
            "ts": round(time.time(), 3),
        }
        self._save(f"add_claim {cid}")
        return cid

    def _claim(self, cid):
        if cid not in self._state["claims"]:
            raise KeyError(cid)
        return self._state["claims"][cid]

    # -- forecast ledger --
    def forecast(self, cid, *, agent, p):
        c = self._claim(cid)
        if c["status"] != "open":
            raise ValueError(f"claim {cid} is {c['status']}, not open")
        if not 0.0 <= p <= 1.0:
            raise ValueError("p out of range")
        if any(f["agent"] == agent for f in c["forecasts"]):
            raise ValueError(f"{agent} already forecast {cid}")
        c["forecasts"].append({"agent": agent, "p": p, "brier": None,
                               "ts": round(time.time(), 3)})
        self._save(f"forecast {cid} {agent} {p}")

    def resolve(self, cid, *, outcome):
        c = self._claim(cid)
        if c["status"] not in ("open",):
            raise ValueError(f"claim {cid} is {c['status']}")
        c["outcome"] = bool(outcome)
        for f in c["forecasts"]:
            f["brier"] = round(_brier(f["p"], outcome), 4)
        c["status"] = "resolved"
        self._save(f"resolve {cid} {outcome}")

    def mark_replicated(self, cid):
        self._claim(cid)["replicated"] = True
        self._save(f"mark_replicated {cid}")

    def mark_survived_counterexample(self, cid):
        self._claim(cid)["survived_counterexample"] = True
        self._save(f"mark_survived_counterexample {cid}")

    def withdraw(self, cid):
        self._claim(cid)["status"] = "withdrawn"
        self._save(f"withdraw {cid}")

    # -- conditional trust --
    def trust(self, agent, domain):
        """1 - mean Brier over this agent's resolved forecasts in this domain.
        None if no track record (a cold start — probe_trust_transfer: do NOT fall
        back to a global scalar)."""
        briers = [f["brier"]
                  for c in self._state["claims"].values()
                  if c["domain"] == domain and c["status"] in ("resolved", "promoted")
                  for f in c["forecasts"]
                  if f["agent"] == agent and f["brier"] is not None]
        if not briers:
            return None
        return round(1.0 - sum(briers) / len(briers), 4)

    # -- promotion rule --
    def promotable(self, cid):
        c = self._claim(cid)
        reasons = []
        if c["status"] != "resolved":
            reasons.append(f"status is {c['status']}, not resolved")
        resolved = [f for f in c["forecasts"] if f["brier"] is not None]
        if len(resolved) < MIN_FORECASTS:
            reasons.append(f"{len(resolved)} resolved forecasts (< {MIN_FORECASTS})")
        if len({f["agent"] for f in resolved}) < MIN_DISTINCT_AGENTS:
            reasons.append(f"< {MIN_DISTINCT_AGENTS} distinct forecasting agents")
        if resolved:
            agg = sum(f["brier"] for f in resolved) / len(resolved)
            if agg >= BRIER_GATE:
                reasons.append(f"aggregate Brier {agg:.3f} >= gate {BRIER_GATE}")
        if not c["replicated"]:
            reasons.append("not independently replicated")
        if not c["survived_counterexample"]:
            reasons.append("has not survived counterexample search")
        return (not reasons), reasons

    def promote(self, cid):
        ok, reasons = self.promotable(cid)
        if not ok:
            raise ValueError("; ".join(reasons))
        self._claim(cid)["status"] = "promoted"
        self._save(f"promote {cid}")

    def summary(self):
        by_status = {}
        for c in self._state["claims"].values():
            by_status[c["status"]] = by_status.get(c["status"], 0) + 1
        return {"claims": len(self._state["claims"]), "by_status": by_status}


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="ec-"))
    try:
        ec = EpistemicConstitution(tmp / "ec.json")
        c1 = ec.add_claim("method X cuts test failures under Y", domain="testing",
                          confidence=0.7, horizon_days=30, evidence=["exp-42"],
                          disconfirmers=["fails under data shift"])
        c2 = ec.add_claim("routing policy Z cuts cost 15-25%", domain="cost",
                          confidence=0.6, horizon_days=14)
        # well-calibrated agent a1, over-confident wrong agent a2, on c1 (outcome True)
        ec.forecast(c1, agent="a1", p=0.85)
        ec.forecast(c1, agent="a2", p=0.20)
        ec.forecast(c1, agent="a3", p=0.75)
        ec.forecast(c1, agent="a4", p=0.70)
        ec.resolve(c1, outcome=True)

        checks = {}
        checks["resolve scores every forecast with a Brier"] = all(
            f["brier"] is not None for f in ec._claim(c1)["forecasts"])
        t_a1 = ec.trust("a1", "testing")
        t_a2 = ec.trust("a2", "testing")
        checks["trust: calibrated agent > miscalibrated agent"] = t_a1 > t_a2
        checks["trust: domain-keyed - no cross-domain leak"] = ec.trust("a1", "cost") is None
        checks["trust: cold start returns None, not a global scalar"] = ec.trust("zz", "testing") is None

        ok, reasons = ec.promotable(c1)
        checks["not promotable yet (no replication / counterexample)"] = (not ok) and any(
            "replicated" in r for r in reasons)
        ec.mark_replicated(c1)
        ec.mark_survived_counterexample(c1)
        ok2, reasons2 = ec.promotable(c1)
        # a2's p=0.20 on a True outcome -> Brier 0.64; aggregate is dragged over the gate
        checks["still blocked: one bad forecast drags the aggregate Brier over the gate"] = (
            not ok2) and any("Brier" in r for r in reasons2)

        # a claim where all forecasts are calibrated -> promotable
        c3 = ec.add_claim("cache warmup halves p99", domain="latency",
                          confidence=0.8, horizon_days=7)
        for a, p in (("a1", 0.82), ("a2", 0.78), ("a3", 0.9), ("a4", 0.85)):
            ec.forecast(c3, agent=a, p=p)
        ec.resolve(c3, outcome=True)
        ec.mark_replicated(c3)
        ec.mark_survived_counterexample(c3)
        ok3, reasons3 = ec.promotable(c3)
        checks["a fully-calibrated + replicated + counterexample-survived claim is promotable"] = ok3
        ec.promote(c3)
        checks["promote() moves status to promoted"] = ec._claim(c3)["status"] == "promoted"

        # guards
        def _raises(fn):
            try:
                fn(); return False
            except (ValueError, KeyError):
                return True
        checks["cannot forecast a resolved claim"] = _raises(lambda: ec.forecast(c1, agent="zz", p=0.5))
        checks["cannot double-forecast"] = _raises(lambda: ec.forecast(c2, agent="a1", p=0.5) or ec.forecast(c2, agent="a1", p=0.6))
        checks["cannot promote a non-promotable claim"] = _raises(lambda: ec.promote(c2))
        checks["reload from disk preserves state"] = (
            EpistemicConstitution(tmp / "ec.json").summary()["claims"] == 3)
        checks["audit log is append-only and non-empty"] = (
            (tmp / "ec.audit").exists() and len((tmp / "ec.audit").read_text().splitlines()) >= 10)

        for k, v in checks.items():
            print(f"  [{'ok' if v else 'FAIL'}] {k}")
        print(f"\n  trust a1/testing={t_a1}  a2/testing={t_a2}")
        print(f"  summary: {json.dumps(ec.summary())}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--path", default=str(DEFAULT_PATH))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    a = sub.add_parser("add"); a.add_argument("statement"); a.add_argument("--domain", required=True)
    a.add_argument("--confidence", type=float, required=True); a.add_argument("--horizon-days", type=int, default=30)
    f = sub.add_parser("forecast"); f.add_argument("cid"); f.add_argument("--agent", required=True); f.add_argument("--p", type=float, required=True)
    r = sub.add_parser("resolve"); r.add_argument("cid"); r.add_argument("--outcome", choices=["true", "false"], required=True)
    t = sub.add_parser("trust"); t.add_argument("agent"); t.add_argument("domain")
    pr = sub.add_parser("promotable"); pr.add_argument("cid")
    sub.add_parser("summary")
    sub.add_parser("list")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    ec = EpistemicConstitution(args.path)
    if args.cmd == "add":
        print(ec.add_claim(args.statement, domain=args.domain, confidence=args.confidence,
                           horizon_days=args.horizon_days))
    elif args.cmd == "forecast":
        ec.forecast(args.cid, agent=args.agent, p=args.p); print("ok")
    elif args.cmd == "resolve":
        ec.resolve(args.cid, outcome=args.outcome == "true"); print("ok")
    elif args.cmd == "trust":
        print(ec.trust(args.agent, args.domain))
    elif args.cmd == "promotable":
        ok, reasons = ec.promotable(args.cid); print(json.dumps({"promotable": ok, "reasons": reasons}, indent=2))
    elif args.cmd == "summary":
        print(json.dumps(ec.summary(), indent=2))
    elif args.cmd == "list":
        for c in ec._state["claims"].values():
            print(f"{c['id']}  [{c['status']}]  ({c['domain']})  {c['statement'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

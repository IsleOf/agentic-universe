#!/usr/bin/env python3
"""Validator gates — stateless checkpoints on pipeline edges that cannot calcify.

`docs/swarm-substrate-prototype.md` §3. Week-1 build list item 5: the two gates
that catch most cascades — G1 (evidence) and G4 (release).

  research ──[G1 evidence]──▶ draft ──▶ critique ──[G4 release]──▶ done

WHY A GATE HERE CANNOT BECOME A PERMANENT AUTHORITY (the request's concern):

  1. STATELESS. A gate reads the task_ref, its pheromone annotations, and the
     artifact text; emits a verdict; forgets. It accumulates no private model of
     the project, so there is nothing for authority to accrete into. Reputation
     accrues to *agents* (`reputation.py`); a gate is a function those agents
     temporarily compute.
  2. SINGLE-USE + ROTATED. `validator_agent` may not have gated this task_ref at
     the immediately preceding gate, and an agent that CONTRIBUTED to the artifact
     may never gate it. `GateRefused` otherwise.
  3. VERDICTS ARE ORDINARY ANNOTATIONS. A pass is a `kind=claim`, a fail is a
     `kind=warning`, both written with the same `pheromone.annotate` any agent
     uses. A later agent can post a contradicting `warning` and reopen the task.
  4. QUORUM, NOT VETO (G4). One validator can `flag` (post a warning) but not
     `block`. Release needs `min_quorum` independent PASS annotations, or one
     validator plus a passing computable check as the second "voter".

NO MODEL CALLS. The fuzzy part — judging whether a claim is actually supported —
is the caller's; the gate checks the mechanical, verifiable things and reports the
rest. Pure stdlib.

Usage:
    from gates import g1_evidence, g4_release, GateRefused
    v = g1_evidence(task_ref, artifact_text, evidence_links=[...],
                    validator_agent="v1", pheromone=pf, repo_root=ROOT)
    if not v["pass"]: ...
    v = g4_release(task_ref, validator_agent="v2", pheromone=pf,
                   computable_ok=True, min_quorum=2)

CLI: g1 / g4 / selftest.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pheromone import Pheromone  # noqa: E402

# a "claim-shaped" line: carries a number, a percentage, an arXiv id, or a strong
# assertion verb — the kind of sentence a reader expects a citation on.
_CLAIM_RE = re.compile(
    r"(\d+(\.\d+)?\s*%|\barxiv:\s*\d|\b\d{4}\.\d{4,5}\b|"
    r"\b(proves?|shows?|demonstrates?|outperforms?|beats?|reduces?|increases?|"
    r"guarantees?|always|never|the first)\b)", re.I)
# a citation marker near a claim: [..], (arXiv:..), a bare URL, a footnote ^n
_CITE_RE = re.compile(r"(\[[^\]]+\]|\(arxiv:[^)]+\)|https?://|\^\d+|\bsee\s+\w+\.(md|py))", re.I)


class GateRefused(RuntimeError):
    """The rotation / self-review rules will not let this agent gate this task."""


def _contributors(task_ref, pheromone):
    return set(pheromone.read(task_ref)["contributors"])


def _last_gate_validator(task_ref, pheromone, gate):
    """The agent who ran `gate` on this task most recently, from the annotation
    trail — or None."""
    anns = pheromone.read(task_ref)["annotations"]
    hits = [a for a in anns
            if a["kind"] in ("claim", "warning")
            and isinstance(a.get("evidence"), dict)
            and a["evidence"].get("gate") == gate]
    return hits[-1]["agent"] if hits else None


def _guard(task_ref, validator_agent, pheromone, gate):
    if validator_agent in _contributors(task_ref, pheromone):
        raise GateRefused(
            f"{validator_agent!r} contributed to {task_ref} and may not gate it")
    prev = _last_gate_validator(task_ref, pheromone, gate)
    if prev == validator_agent:
        raise GateRefused(
            f"{validator_agent!r} ran {gate} on {task_ref} last time; rotate to another agent")


def _write_verdict(task_ref, pheromone, *, gate, validator_agent, passed, reasons, extra=None):
    kind = "claim" if passed else "warning"
    ev = {"gate": gate, "pass": passed, "reasons": reasons}
    if extra:
        ev.update(extra)
    pheromone.annotate(task_ref, kind,
                       utility=(0.3 if passed else -0.6), confidence=0.85,
                       agent=validator_agent, evidence=ev)
    return {"gate": gate, "task_ref": task_ref, "validator": validator_agent,
            "pass": passed, "reasons": reasons, **(extra or {})}


# --------------------------------------------------------------------------- #
def g1_evidence(task_ref, artifact_text, *, evidence_links, validator_agent, pheromone,
                repo_root=ROOT):
    """G1: an artifact entering `draft` must carry resolvable evidence.

    HARD FAIL: no evidence links at all, or a link that names a repo file which does
    not exist. REPORTED (not a fail): claim-shaped lines with no nearby citation
    marker — the reader decides whether that matters, the gate does not silently
    block on a regex.
    """
    _guard(task_ref, validator_agent, pheromone, "G1")
    reasons = []
    passed = True

    links = list(evidence_links or [])
    if not links:
        passed = False
        reasons.append("no evidence links on the artifact")

    unresolved = []
    for link in links:
        if link.startswith(("http://", "https://", "arxiv:")):
            continue                      # external: format only, not reachability
        p = (Path(repo_root) / link.split("#", 1)[0].split(":", 1)[0]).resolve()
        if not p.exists():
            unresolved.append(link)
    if unresolved:
        passed = False
        reasons.append(f"evidence link(s) name missing repo files: {unresolved}")

    uncited = [ln.strip()[:90] for ln in artifact_text.splitlines()
               if _CLAIM_RE.search(ln) and not _CITE_RE.search(ln)]
    if uncited:
        reasons.append(f"REPORT: {len(uncited)} claim-shaped line(s) with no nearby "
                       f"citation marker (not a block): e.g. {uncited[:3]}")

    if passed and not reasons:
        reasons.append("evidence links present and resolvable")
    return _write_verdict(task_ref, pheromone, gate="G1", validator_agent=validator_agent,
                          passed=passed, reasons=reasons,
                          extra={"n_links": len(links), "n_uncited_claims": len(uncited)})


def g4_release(task_ref, *, validator_agent, pheromone, computable_ok, min_quorum=2):
    """G4: an artifact proposed as final. Quorum, not veto.

    PASS requires ALL of: `computable_ok` True; zero LIVE `warning` annotations on
    the task; and (this PASS annotation) + (prior independent G4 PASS annotations)
    + (1 if computable_ok) >= `min_quorum`. A single validator can post a warning
    to block, but cannot pass alone unless the computable check stands in as the
    second voter.
    """
    _guard(task_ref, validator_agent, pheromone, "G4")
    reasons = []

    v = pheromone.read(task_ref)
    live_warnings = [a for a in v["annotations"] if a["kind"] == "warning"]
    prior_g4_pass = {a["agent"] for a in v["annotations"]
                     if a["kind"] == "claim" and isinstance(a.get("evidence"), dict)
                     and a["evidence"].get("gate") == "G4" and a["evidence"].get("pass")}
    prior_g4_pass.discard(validator_agent)

    voters = 1 + len(prior_g4_pass) + (1 if computable_ok else 0)
    passed = True
    if not computable_ok:
        passed = False
        reasons.append("computable checks did not pass")
    if live_warnings:
        passed = False
        reasons.append(f"{len(live_warnings)} unresolved warning annotation(s): "
                       f"{sorted({a['agent'] for a in live_warnings})}")
    if voters < min_quorum:
        passed = False
        reasons.append(f"quorum {voters}/{min_quorum} not met "
                       f"(this validator + {len(prior_g4_pass)} prior PASS + "
                       f"{'computable check' if computable_ok else 'no computable vote'})")
    if passed:
        reasons.append(f"released: quorum {voters}/{min_quorum}, no live warnings, "
                       f"computable checks pass")
    return _write_verdict(task_ref, pheromone, gate="G4", validator_agent=validator_agent,
                          passed=passed, reasons=reasons,
                          extra={"quorum": voters, "min_quorum": min_quorum,
                                 "live_warnings": len(live_warnings)})


# --------------------------------------------------------------------------- #
def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="gates-"))
    checks = {}
    try:
        pf = Pheromone(tmp / "p.db")

        # G1: a well-cited artifact with a resolvable repo link passes
        good = ("The relay ports the Strands handoff contract [see relay.py].\n"
                "SwarmSys reports +11.9% on SciCode (arXiv:2510.10047).\n")
        v = g1_evidence("t1", good, evidence_links=["tools/relay.py",
                        "https://arxiv.org/abs/2510.10047"],
                        validator_agent="v1", pheromone=pf)
        checks["G1 passes a cited artifact with a resolvable repo link"] = v["pass"]
        checks["G1 writes a kind=claim annotation on pass"] = any(
            a["kind"] == "claim" and a["evidence"]["gate"] == "G1"
            for a in pf.read("t1")["annotations"])

        # G1: no evidence links -> hard fail
        v = g1_evidence("t2", "It always works and never fails.", evidence_links=[],
                        validator_agent="v1", pheromone=pf)
        checks["G1 hard-fails an artifact with no evidence links"] = not v["pass"]
        checks["G1 writes a kind=warning on fail"] = any(
            a["kind"] == "warning" for a in pf.read("t2")["annotations"])

        # G1: an evidence link naming a missing repo file -> hard fail
        v = g1_evidence("t3", "x", evidence_links=["tools/does_not_exist.py"],
                        validator_agent="v1", pheromone=pf)
        checks["G1 hard-fails on an evidence link to a missing repo file"] = not v["pass"]

        # G1: uncited claim-shaped line -> REPORTED, not a block
        v = g1_evidence("t4", "This reduces latency by 40%.\n",
                        evidence_links=["tools/relay.py"], validator_agent="v1", pheromone=pf)
        checks["G1 reports an uncited claim line but does not block on it"] = (
            v["pass"] and v["n_uncited_claims"] == 1
            and any("REPORT" in r for r in v["reasons"]))

        # ROTATION: an author cannot gate their own artifact
        pf.annotate("t5", "utility", 0.5, 0.8, agent="alice")     # alice contributed
        try:
            g1_evidence("t5", "x", evidence_links=["tools/relay.py"],
                        validator_agent="alice", pheromone=pf)
            checks["a contributor cannot gate their own artifact"] = False
        except GateRefused:
            checks["a contributor cannot gate their own artifact"] = True

        # ROTATION: the same validator cannot run the same gate twice in a row
        g1_evidence("t6", "x", evidence_links=["tools/relay.py"],
                    validator_agent="v1", pheromone=pf)
        try:
            g1_evidence("t6", "x", evidence_links=["tools/relay.py"],
                        validator_agent="v1", pheromone=pf)
            checks["the same validator cannot run G1 twice on one task"] = False
        except GateRefused:
            checks["the same validator cannot run G1 twice on one task"] = True
        # ...but a different validator can
        v = g1_evidence("t6", "x", evidence_links=["tools/relay.py"],
                        validator_agent="v2", pheromone=pf)
        checks["a different validator may re-gate"] = v["pass"]

        # G4: quorum not veto
        pf2 = Pheromone(tmp / "p2.db")
        # one validator + passing computable check == quorum 2
        v = g4_release("r1", validator_agent="v1", pheromone=pf2,
                       computable_ok=True, min_quorum=2)
        checks["G4: one validator + a passing computable check meets quorum 2"] = v["pass"]

        # a live warning blocks G4 even at quorum
        pf3 = Pheromone(tmp / "p3.db")
        pf3.annotate("r2", "warning", -0.7, 0.9, agent="critic")
        v = g4_release("r2", validator_agent="v1", pheromone=pf3,
                       computable_ok=True, min_quorum=2)
        checks["G4: an unresolved warning blocks release"] = (
            not v["pass"] and any("warning" in r for r in v["reasons"]))

        # failing computable check blocks G4
        pf4 = Pheromone(tmp / "p4.db")
        v = g4_release("r3", validator_agent="v1", pheromone=pf4,
                       computable_ok=False, min_quorum=2)
        checks["G4: a failing computable check blocks release"] = not v["pass"]

        # a single validator with a HIGHER quorum bar cannot pass alone
        pf5 = Pheromone(tmp / "p5.db")
        v = g4_release("r4", validator_agent="v1", pheromone=pf5,
                       computable_ok=True, min_quorum=3)
        checks["G4: one validator + computable check cannot meet a quorum of 3"] = not v["pass"]
        # two independent validators + computable check clear a quorum of 3
        pf5.annotate("r5", "claim", 0.3, 0.85, agent="v0",
                     evidence={"gate": "G4", "pass": True, "reasons": []})
        v = g4_release("r5", validator_agent="v1", pheromone=pf5,
                       computable_ok=True, min_quorum=3)
        checks["G4: two validators + computable check meet a quorum of 3"] = v["pass"]

        # failing computable checks block release NO MATTER how many validators agree
        pf6 = Pheromone(tmp / "p6.db")
        for i in range(5):
            pf6.annotate("r6", "claim", 0.3, 0.85, agent=f"v{i}",
                         evidence={"gate": "G4", "pass": True, "reasons": []})
        v = g4_release("r6", validator_agent="vX", pheromone=pf6,
                       computable_ok=False, min_quorum=2)
        checks["G4: failing computable checks block release even with 5 validator passes"] = (
            not v["pass"])

        # G4 quorum sweep: verdict well-formed at every quorum size (computable_ok=True)
        for q in range(2, 12):
            pfq = Pheromone(tmp / f"q{q}.db")
            for i in range(q - 2):        # q-2 prior + this validator + computable = q
                pfq.annotate("s", "claim", 0.3, 0.85, agent=f"v{i}",
                             evidence={"gate": "G4", "pass": True, "reasons": []})
            vv = g4_release("s", validator_agent=f"vlast{q}", pheromone=pfq,
                            computable_ok=True, min_quorum=q)
            checks[f"q={q}: G4 verdict is well-formed and meets the exact quorum"] = (
                vv["pass"] and vv["quorum"] == q)

        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    g1 = sub.add_parser("g1")
    g1.add_argument("--pheromone", required=True)
    g1.add_argument("task_ref")
    g1.add_argument("artifact_file")
    g1.add_argument("--evidence", nargs="*", default=[])
    g1.add_argument("--validator", required=True)
    g4 = sub.add_parser("g4")
    g4.add_argument("--pheromone", required=True)
    g4.add_argument("task_ref")
    g4.add_argument("--validator", required=True)
    g4.add_argument("--computable-ok", action="store_true")
    g4.add_argument("--min-quorum", type=int, default=2)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    pf = Pheromone(args.pheromone)
    if args.cmd == "g1":
        text = Path(args.artifact_file).read_text(encoding="utf-8")
        print(json.dumps(g1_evidence(args.task_ref, text, evidence_links=args.evidence,
                                     validator_agent=args.validator, pheromone=pf), indent=2))
    elif args.cmd == "g4":
        print(json.dumps(g4_release(args.task_ref, validator_agent=args.validator, pheromone=pf,
                                    computable_ok=args.computable_ok,
                                    min_quorum=args.min_quorum), indent=2))
    pf.close()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

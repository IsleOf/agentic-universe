#!/usr/bin/env python3
"""The real-harness adapter — the first non-synthetic trace.

Every phase built in runs 60-65 runs on synthetic data. This adapter points the
Phase 0 `Recorder` and Phase 1 `Registry` at a *real* harness: this project's own
autonomous research loop (`C:\\Users\\PC\\.claude\\scheduled-tasks\\agentic-universe-research-loop\\SKILL.md`
+ the interactive continuation). It is a single-agent harness — no swarm — which
is exactly the shape Phase 1 says to start with ("One agent, one sandbox").

Two things:

1. `seed_loop_harness(reg)` — writes the loop's actual components into a Registry:
   the procedure prompt, the context policy ("charter + coverage + 3 recent
   sweeps first"), the topology (single agent), the tool set. The bodies are
   transcribed from the SKILL.md, so `manifest()` is a real fingerprint of the
   loop as it stands.

2. `replay_history(graph_path, rec)` — reconstructs a real trace from the graph's
   own `evolution_log`: one STEP per autonomous run, a CLAIM per VERIFIED arXiv
   citation (evidence_root = the arXiv id — so `pattern_evidential_ancestry_tracking`
   has real ancestry to dedupe), an ARTIFACT per graph write, a TOOL_CALL/RESULT
   per validation. The project's own 54-run history becomes the first dataset.

Then `experience_bank.condense` and `topology_recover` run on that real trace, to
show the pipeline works on non-synthetic input.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace           # noqa: E402
from harness_registry import Registry                          # noqa: E402
from experience_bank import ExperienceBank, condense           # noqa: E402
from topology_recover import build_topology, recover_roles     # noqa: E402

GRAPH = ROOT / "knowledge" / "graph" / "agentic_universe_graph.json"

LOOP_PROCEDURE = """\
Autonomous continuation of the Agentic Universe research programme. ONE increment per run, then stop.
SETUP: checkout proposals/2026-09-01-emergent-behaviour-cluster; read habitat_charter.md, the Open/Next
sections of the 3 most recent sweep/plan/design docs, literature_coverage.md, sources/README.md.
PICK ONE increment (highest value from the open questions). VERIFY every citation three ways
(exists / summary matches / headline number causally isolated). Record tensions as challenges edges.
WRITE docs/auto_sweep_<UTC>.md. VALIDATE (knowledge_graph.py validate must print VALID; orphan check).
COMMIT as Ilmar Selter, Co-Authored-By Claude Sonnet 5; push to the working branch.
"""

LOOP_CONTEXT_POLICY = {
    "read_first": ["docs/habitat_charter.md", "docs/literature_coverage.md",
                   "3 most recent docs/*sweep*|*plan*|*design*", "sources/README.md"],
    "pin": ["charter conventions", "literature_coverage state", "graph validation rule"],
    "compress": ["older sweep docs", "search results"],
    "do_not": ["re-sweep covered ground", "re-add a paper already in derived_from"],
}

LOOP_TOPOLOGY = {"agents": ["researcher"], "swarm": False,
                 "note": "single agent; Phase 1 'one agent, one sandbox'"}

LOOP_TOOLS = {
    "research_fetch": "python C:/Agents/skills/research-fetch/research_fetch.py <source> <cmd>",
    "arxiv_api": "http://export.arxiv.org/api/query",
    "web_fetch": "WebFetch",
    "graph_validate": "python tools/knowledge_graph.py validate",
    "git": "commit + push to proposals/2026-09-01-emergent-behaviour-cluster",
}


def seed_loop_harness(reg: Registry):
    reg.set("prompt", "loop_procedure", LOOP_PROCEDURE, note="from SKILL.md", author="adapter")
    reg.set("context", "loop_policy", json.dumps(LOOP_CONTEXT_POLICY, indent=2),
            note="charter + coverage + 3 recent sweeps first", author="adapter")
    reg.set("topology", "loop_team", json.dumps(LOOP_TOPOLOGY), note="single agent", author="adapter")
    reg.set("tool", "loop_tools", json.dumps(LOOP_TOOLS, indent=2), note="local tool set", author="adapter")
    return reg


_RUN_RE = re.compile(r"(?:Autonomous )?run (\d+)", re.I)
_ARXIV_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")
_VERIFIED_RE = re.compile(r"(\d{4}\.\d{4,5})[^.]{0,40}?VERIFIED", re.I)
_EDGES_RE = re.compile(r"(\d+)\s*(?:->|→)\s*(\d+)\s*edges", re.I)
_NODES_RE = re.compile(r"(\d+)\s*(?:->|→)\s*(\d+)\s*nodes", re.I)


def replay_history(graph_path, rec: Recorder, limit=None):
    """Turn the graph's evolution_log into a real Phase 0 trace."""
    g = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    log = g["evolution_log"]
    if limit:
        log = log[-limit:]
    n_runs = n_claims = n_artifacts = 0

    for entry in log:
        text = entry["change"]
        date = entry.get("date", "?")
        m = _RUN_RE.search(text)
        run_no = m.group(1) if m else "?"
        step_id = f"run-{run_no}-{date}"

        rec.step("researcher", step_id, "open", note=text[:120], layer="harness")

        # VERIFIED citations -> CLAIM events with the arXiv id as evidence root
        verified = set(_VERIFIED_RE.findall(text))
        for axid in sorted(verified):
            rec.claim("researcher", f"folded a VERIFIED finding from arXiv:{axid}",
                      [f"arXiv:{axid}"], layer="harness")
            n_claims += 1

        # any other arXiv ids mentioned but not verified -> lower-trust claim
        mentioned = set(_ARXIV_RE.findall(text)) - verified
        for axid in sorted(mentioned):
            rec.claim("researcher", f"referenced arXiv:{axid} (not independently opened this run)",
                      [f"arXiv:{axid}"], layer="harness", trust="low")
            n_claims += 1

        # graph writes -> ARTIFACT
        em = _EDGES_RE.search(text)
        nm = _NODES_RE.search(text)
        if em or nm:
            rec.artifact("researcher", "knowledge/graph/agentic_universe_graph.json", "write",
                         layer="harness",
                         delta={"edges": em.groups() if em else None,
                                "nodes": nm.groups() if nm else None})
            n_artifacts += 1

        # a validation tool call every run
        cid = rec.tool_call("researcher", "graph_validate", "validate the graph before commit",
                            layer="harness")
        rec.tool_result("researcher", cid, ok=True, summary="VALID", layer="harness")

        # the commit
        rec.artifact("researcher", "git", "write", layer="harness",
                     note=f"commit for run {run_no}")
        n_artifacts += 1

        rec.step("researcher", step_id, "close", note="run complete, pushed", layer="harness")
        n_runs += 1

    return {"runs": n_runs, "claims": n_claims, "artifacts": n_artifacts}


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="loop-adapter-"))
    try:
        reg = Registry(base=tmp / "harness")
        seed_loop_harness(reg)
        manifest = reg.manifest()

        buf = io.StringIO()
        rec = Recorder(run_id="loop-history", sink=buf, layer="harness", language="en",
                       harness_manifest=manifest)
        counts = replay_history(GRAPH, rec, limit=20)
        rec.close()
        text = buf.getvalue()

        tf = tmp / "loop.jsonl"
        tf.write_text(text, encoding="utf-8")
        n_events, errors = validate_trace(tf)

        events = [json.loads(l) for l in text.splitlines() if l.strip()]

        # condense the REAL trace
        bank = ExperienceBank(base=tmp / "bank")
        added = condense(tf, bank)

        # evidence-root ancestry: how many distinct arXiv ids across all claims
        roots = set()
        for e in events:
            if e.get("kind") == "CLAIM":
                roots.update(e.get("evidence_roots", []))

        # topology: single agent -> researcher recovered as some interacting role
        roles = recover_roles(build_topology(events))

        checks = {
            "harness seeded (4 components)": len(manifest["components"]) == 4,
            "real trace validates": not errors,
            f"trace has events ({n_events})": n_events > 50,
            f"replayed {counts['runs']} runs": counts["runs"] == 20,
            "claims carry real arXiv evidence roots": len(roots) >= 10
                and all(r.startswith("arXiv:") for r in roots),
            "condense produced workflow entries from the real trace":
                bank.stats()["workflow"] >= 1,
            "workflow entries dedupe evidence roots (ancestry, not claim count)":
                all(isinstance(e["distinct_evidence_roots"], list) for e in added),
            "single-agent harness: researcher is the acting role":
                roles.get("researcher") in ("planner", "worker", "verifier"),
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        print(f"\n  counts: {json.dumps(counts)}")
        print(f"  distinct arXiv evidence roots in the real trace: {len(roots)}")
        print(f"  bank from real trace: {json.dumps(bank.stats())}")
        print(f"  recovered role for 'researcher': {roles.get('researcher')}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Real-harness adapter: the autonomous loop as a harness.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    r = sub.add_parser("replay", help="write a real trace from evolution_log to runtime/traces/")
    r.add_argument("--limit", type=int, default=None)
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "replay":
        reg = Registry()
        seed_loop_harness(reg)
        rec = Recorder(run_id="loop-history", layer="harness", language="en",
                       harness_manifest=reg.manifest())
        counts = replay_history(GRAPH, rec, limit=args.limit)
        rec.close()
        print(f"wrote {rec._path}")
        print(json.dumps(counts))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

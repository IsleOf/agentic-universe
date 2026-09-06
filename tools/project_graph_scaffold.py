#!/usr/bin/env python3
"""Scaffold and validate a per-project knowledge graph + handover doc, in the
Agentic Universe format.

`docs/practicing_what_we_preach.md` §3: to get this project's research into
another project (poly-bot, poster-studio), one session per project writes a
*validated* knowledge graph plus a `HANDOFF.md`-style doc, and every fresh
session reads them first. That fixes "sessions lose context / tasks get
dropped" — the persistent memory is a validated file, not the last chat.

This tool makes that repeatable:

    python tools/project_graph_scaffold.py new poly-bot
        -> knowledge/graph/poly-bot_project_graph.json   (starter, validates)
           docs/poly-bot_PROJECT_STATE.md                (handover skeleton)

    python tools/project_graph_scaffold.py validate <graph.json>
        -> VALID / INVALID  (reuses knowledge_graph.validate_graph)

    python tools/project_graph_scaffold.py selftest

Node `type` vocabulary for a project graph (a small, deliberate set — 20-50
nodes is the target):

    component   — a real module / service / file with behaviour
    decision    — a choice that was made and why (its alternatives are the tension)
    constraint  — a hard limit the project must respect
    bug         — a known defect, with a failure scenario
    question    — an open question the next session should resolve

Edge `type`: depends_on · implements · challenges · blocks · records.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from knowledge_graph import validate_graph  # noqa: E402

NODE_TYPES = ("component", "decision", "constraint", "bug", "question")
EDGE_TYPES = ("depends_on", "implements", "challenges", "blocks", "records")


def starter_graph(name):
    return {
        "project": name,
        "format": "agentic-universe project graph v1",
        "last_updated": "",
        "nodes": [
            {"id": f"{name}__root", "label": f"{name}: what it is, in one sentence",
             "type": "component", "status": "to_fill", "confidence": 0.3,
             "description": "Replace: the project's purpose and top-level shape.",
             "derived_from": ["README"], "tags": ["root"]},
            {"id": f"{name}__q_next", "label": "The single highest-value next move",
             "type": "question", "status": "open", "confidence": 0.3,
             "description": "Replace: what the next session should do first, and why.",
             "derived_from": [], "tags": ["next"]},
        ],
        "edges": [
            {"id": f"{name}__e_next_blocks_root", "source": f"{name}__q_next",
             "target": f"{name}__root", "type": "blocks",
             "description": "The next move gates progress on the whole project."},
        ],
        "evolution_log": [],
    }


def starter_doc(name):
    return f"""# {name} — Project State

**Format:** Agentic Universe handover (see `docs/practicing_what_we_preach.md` §3) ·
**Graph:** `knowledge/graph/{name}_project_graph.json` (run `project_graph_scaffold.py validate` on it)

> Every fresh session reads this file and the graph **first**.

## What it is

_One paragraph: purpose, top-level shape, where the code lives._

## Current state

_What works. What is half-built. What is broken and why._

## The single highest-value next move

_One thing, and why it is the one thing._

## Hard constraints

- _limits the project must respect (interfaces, budgets, no-touch areas)_

## Open questions

- _questions the next session should resolve, most-blocking first_

## What would make this wrong

_The two or three assumptions the project rests on, and what would break each._
"""


def cmd_new(name):
    safe = name.replace("/", "_")
    gpath = ROOT / "knowledge" / "graph" / f"{safe}_project_graph.json"
    dpath = ROOT / "docs" / f"{safe}_PROJECT_STATE.md"
    if gpath.exists() or dpath.exists():
        raise SystemExit(f"refusing to overwrite: {gpath.name} / {dpath.name} already exist")
    g = starter_graph(safe)
    errs = validate_graph(g)
    if errs:
        raise SystemExit("internal error: starter graph does not validate: " + "; ".join(errs))
    gpath.parent.mkdir(parents=True, exist_ok=True)
    gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    dpath.write_text(starter_doc(safe), encoding="utf-8")
    print(f"wrote {gpath.relative_to(ROOT)}")
    print(f"wrote {dpath.relative_to(ROOT)}")
    print("next: fill both, then `python tools/project_graph_scaffold.py validate " f"{gpath.relative_to(ROOT)}`")


def cmd_validate(path):
    g = json.loads(Path(path).read_text(encoding="utf-8"))
    errs = validate_graph(g)
    # project-graph-specific lints on top of the base schema
    for n in g.get("nodes", []):
        if n.get("type") and n["type"] not in NODE_TYPES:
            errs.append(f"node {n.get('id')}: type {n['type']!r} not in {NODE_TYPES}")
    for e in g.get("edges", []):
        if e.get("type") and e["type"] not in EDGE_TYPES:
            errs.append(f"edge {e.get('id')}: type {e['type']!r} not in {EDGE_TYPES}")
    if errs:
        print("INVALID")
        print("\n".join(f"- {x}" for x in errs))
        return 1
    print(f"VALID  ({len(g.get('nodes', []))} nodes, {len(g.get('edges', []))} edges)")
    return 0


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="proj-graph-"))
    try:
        g = starter_graph("demo")
        checks = {
            "starter graph validates against the base schema": validate_graph(g) == [],
            "starter graph has a root and a next-move question":
                {n["type"] for n in g["nodes"]} == {"component", "question"},
            "node types are the project vocabulary":
                all(n["type"] in NODE_TYPES for n in g["nodes"]),
            "edge types are the project vocabulary":
                all(e["type"] in EDGE_TYPES for e in g["edges"]),
        }
        # a good filled graph passes cmd_validate; a bad type fails
        good = tmp / "good.json"
        gg = starter_graph("demo")
        gg["nodes"].append({"id": "demo__c1", "label": "a component", "type": "component",
                            "confidence": 0.6})
        gg["edges"].append({"id": "demo__e1", "source": "demo__c1", "target": "demo__root",
                            "type": "depends_on"})
        good.write_text(json.dumps(gg), encoding="utf-8")
        checks["cmd_validate passes a well-formed project graph"] = cmd_validate(good) == 0
        bad = tmp / "bad.json"
        gb = starter_graph("demo")
        gb["nodes"].append({"id": "demo__x", "label": "wrong type", "type": "widget"})
        bad.write_text(json.dumps(gb), encoding="utf-8")
        checks["cmd_validate rejects an out-of-vocabulary node type"] = cmd_validate(bad) == 1
        # a dangling edge is caught by the base schema
        dangle = tmp / "dangle.json"
        gd = starter_graph("demo")
        gd["edges"].append({"id": "demo__e_bad", "source": "demo__nope", "target": "demo__root",
                            "type": "blocks"})
        dangle.write_text(json.dumps(gd), encoding="utf-8")
        checks["cmd_validate rejects a dangling edge (base schema)"] = cmd_validate(dangle) == 1
        checks["starter doc says to read it first"] = \
            "reads this file and the graph **first**" in starter_doc("demo")

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
    n = sub.add_parser("new"); n.add_argument("name")
    v = sub.add_parser("validate"); v.add_argument("path")
    sub.add_parser("selftest")
    args = p.parse_args(argv)
    if args.cmd == "new":
        return cmd_new(args.name)
    if args.cmd == "validate":
        return cmd_validate(args.path)
    if args.cmd == "selftest":
        return _selftest()
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

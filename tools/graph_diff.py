#!/usr/bin/env python3
"""Mechanical structural diff of the knowledge graph between two versions.

`docs/practicing_what_we_preach.md` §1: the graph already records *that* it
changed (`evolution_log`, `derived_from`, per-run summaries), but "what changed
between graph vN and vN+1" is only prose. This is the mechanical version —
given two git refs (or two files), it reports exactly which nodes and edges were
added, removed, relabelled, or had their `confidence` / `verification_state` /
edge `type` change.

Usage:

    python tools/graph_diff.py <ref-a> <ref-b>      # e.g. HEAD~5 HEAD
    python tools/graph_diff.py <ref-a>              # <ref-a> vs the working tree
    python tools/graph_diff.py --file a.json b.json # two files directly
    python tools/graph_diff.py --json HEAD~1 HEAD   # machine-readable
    python tools/graph_diff.py selftest

A ref is anything `git show <ref>:<path>` accepts. The default path is
`knowledge/graph/agentic_universe_graph.json`.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = "knowledge/graph/agentic_universe_graph.json"

# node fields whose change is worth reporting (not label — that's separate)
_TRACKED_NODE_FIELDS = ("verification_state", "status", "confidence", "approach_family")


def _load_ref(ref, path=GRAPH_PATH):
    """Load the graph JSON at a git ref, or from the working tree if ref is None
    or the literal 'WORKTREE'."""
    if ref in (None, "WORKTREE", "."):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise SystemExit(f"git show {ref}:{path} failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def _load_file(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def diff(g_a, g_b):
    """Return a structured diff of graph B relative to graph A."""
    na = {n["id"]: n for n in g_a.get("nodes", [])}
    nb = {n["id"]: n for n in g_b.get("nodes", [])}
    ea = {e["id"]: e for e in g_a.get("edges", [])}
    eb = {e["id"]: e for e in g_b.get("edges", [])}

    nodes_added = sorted(set(nb) - set(na))
    nodes_removed = sorted(set(na) - set(nb))
    node_relabelled = sorted(
        i for i in set(na) & set(nb)
        if (na[i].get("label") or "") != (nb[i].get("label") or ""))
    node_field_changes = {}
    for i in sorted(set(na) & set(nb)):
        changed = {f: [na[i].get(f), nb[i].get(f)]
                   for f in _TRACKED_NODE_FIELDS if na[i].get(f) != nb[i].get(f)}
        if changed:
            node_field_changes[i] = changed

    edges_added = sorted(set(eb) - set(ea))
    edges_removed = sorted(set(ea) - set(eb))
    edge_retyped = {}
    edge_endpoint_changes = {}
    for i in sorted(set(ea) & set(eb)):
        if ea[i].get("type") != eb[i].get("type"):
            edge_retyped[i] = [ea[i].get("type"), eb[i].get("type")]
        if (ea[i].get("source"), ea[i].get("target")) != (eb[i].get("source"), eb[i].get("target")):
            edge_endpoint_changes[i] = [
                [ea[i].get("source"), ea[i].get("target")],
                [eb[i].get("source"), eb[i].get("target")]]

    return {
        "counts": {
            "nodes": [len(na), len(nb)],
            "edges": [len(ea), len(eb)],
            "evolution_log": [len(g_a.get("evolution_log", [])), len(g_b.get("evolution_log", []))],
        },
        "nodes_added": nodes_added,
        "nodes_removed": nodes_removed,
        "node_relabelled": node_relabelled,
        "node_field_changes": node_field_changes,
        "edges_added": edges_added,
        "edges_removed": edges_removed,
        "edge_retyped": edge_retyped,
        "edge_endpoint_changes": edge_endpoint_changes,
        "new_evolution_log": g_b.get("evolution_log", [])[len(g_a.get("evolution_log", [])):],
    }


def _fmt(d, a_label, b_label):
    L = []
    c = d["counts"]
    L.append(f"graph {a_label} -> {b_label}")
    L.append(f"  nodes {c['nodes'][0]} -> {c['nodes'][1]}   "
             f"edges {c['edges'][0]} -> {c['edges'][1]}   "
             f"evolution_log {c['evolution_log'][0]} -> {c['evolution_log'][1]}")
    def _section(title, items):
        if not items:
            return
        L.append(f"\n{title} ({len(items)}):")
        for it in items:
            L.append(f"  + {it}" if title.endswith("added") else
                     (f"  - {it}" if title.endswith("removed") else f"  ~ {it}"))
    _section("nodes added", d["nodes_added"])
    _section("nodes removed", d["nodes_removed"])
    _section("nodes relabelled", d["node_relabelled"])
    if d["node_field_changes"]:
        L.append(f"\nnode field changes ({len(d['node_field_changes'])}):")
        for i, ch in d["node_field_changes"].items():
            for f, (av, bv) in ch.items():
                L.append(f"  ~ {i}.{f}: {av!r} -> {bv!r}")
    _section("edges added", d["edges_added"])
    _section("edges removed", d["edges_removed"])
    if d["edge_retyped"]:
        L.append(f"\nedges retyped ({len(d['edge_retyped'])}):")
        for i, (av, bv) in d["edge_retyped"].items():
            L.append(f"  ~ {i}: {av} -> {bv}")
    if d["edge_endpoint_changes"]:
        L.append(f"\nedge endpoint changes ({len(d['edge_endpoint_changes'])}):")
        for i, (av, bv) in d["edge_endpoint_changes"].items():
            L.append(f"  ~ {i}: {av} -> {bv}")
    if d["new_evolution_log"]:
        L.append(f"\nnew evolution_log entries ({len(d['new_evolution_log'])}):")
        for ent in d["new_evolution_log"]:
            change = ent.get("change", "")
            L.append(f"  [{ent.get('date','?')}] {change[:200]}{'...' if len(change) > 200 else ''}")
    if not any(d[k] for k in ("nodes_added", "nodes_removed", "node_relabelled",
                              "node_field_changes", "edges_added", "edges_removed",
                              "edge_retyped", "edge_endpoint_changes")):
        L.append("\n(no structural change)")
    return "\n".join(L)


def _selftest():
    a = {"nodes": [{"id": "x", "label": "X", "confidence": 0.5, "verification_state": "needs_empirical_validation"},
                   {"id": "y", "label": "Y"}],
         "edges": [{"id": "e1", "source": "x", "target": "y", "type": "supports"}],
         "evolution_log": [{"date": "2026-01-01", "change": "start"}]}
    b = {"nodes": [{"id": "x", "label": "X ROUGH", "confidence": 0.7, "verification_state": "partially_validated"},
                   {"id": "z", "label": "Z"}],
         "edges": [{"id": "e1", "source": "x", "target": "z", "type": "challenges"},
                   {"id": "e2", "source": "x", "target": "z", "type": "supports"}],
         "evolution_log": [{"date": "2026-01-01", "change": "start"},
                           {"date": "2026-01-02", "change": "did a thing"}]}
    d = diff(a, b)
    checks = {
        "node z added, y removed":
            d["nodes_added"] == ["z"] and d["nodes_removed"] == ["y"],
        "node x relabelled":
            d["node_relabelled"] == ["x"],
        "node x confidence + verification_state change tracked":
            d["node_field_changes"].get("x", {}).get("confidence") == [0.5, 0.7]
            and "verification_state" in d["node_field_changes"].get("x", {}),
        "edge e2 added":
            d["edges_added"] == ["e2"],
        "edge e1 retyped supports -> challenges":
            d["edge_retyped"].get("e1") == ["supports", "challenges"],
        "edge e1 endpoint change y -> z recorded":
            "e1" in d["edge_endpoint_changes"],
        "one new evolution_log entry surfaced":
            len(d["new_evolution_log"]) == 1 and d["new_evolution_log"][0]["change"] == "did a thing",
        "counts carried": d["counts"]["nodes"] == [2, 2] and d["counts"]["edges"] == [1, 2],
        "no-change diff is empty":
            not any(diff(a, a)[k] for k in ("nodes_added", "edges_added", "node_field_changes")),
        "formatter runs": isinstance(_fmt(d, "A", "B"), str) and "nodes 2 -> 2" in _fmt(d, "A", "B"),
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("refs", nargs="*", help="one or two git refs (or files with --file)")
    p.add_argument("--file", action="store_true", help="treat refs as file paths, not git refs")
    p.add_argument("--path", default=GRAPH_PATH, help="graph path within the ref")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(argv)

    if args.refs == ["selftest"]:
        return _selftest()

    if args.file:
        if len(args.refs) != 2:
            p.error("--file needs exactly two paths")
        g_a, g_b = _load_file(args.refs[0]), _load_file(args.refs[1])
        a_label, b_label = args.refs
    else:
        ref_a = args.refs[0] if args.refs else "HEAD~1"
        ref_b = args.refs[1] if len(args.refs) > 1 else None
        g_a = _load_ref(ref_a, args.path)
        g_b = _load_ref(ref_b, args.path)
        a_label, b_label = ref_a, (ref_b or "WORKTREE")

    d = diff(g_a, g_b)
    if args.json:
        print(json.dumps(d, indent=2, ensure_ascii=False))
    else:
        print(_fmt(d, a_label, b_label))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

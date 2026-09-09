#!/usr/bin/env python3
"""The per-run inter-agent communication graph from a Phase 0 trace.

Run 459, from arXiv:2609.02967 (FGLGuard, folded run 458): the inter-agent
communication GRAPH - who sends to whom - is a monitoring surface and a
containment lever, not just a message log. FGLGuard learns a GNN over it; this is
the deterministic, no-training version the loop currently lacks.

The Phase 0 trace already carries what's needed: every MESSAGE event has `sender`
and `receiver` (`pattern_five_w_message_instrumentation`). This module reads those
and emits:

  * the directed multigraph (nodes = agents, edges = sender -> receiver, weight =
    message count), with per-node in/out degree;
  * a handful of cheap STRUCTURAL FLAGS that a reader should weigh:
      hub               one node touches > HUB_FRACTION of all edges - a single
                        point of control or failure (and, for this project, an
                        orchestrator smell the substrate is meant to avoid)
      clique            >= 3 agents all mutually connected - a dense coordination
                        cluster (the shape FGLGuard localises)
      receive_only      a node that only ever receives - a monitor, or an agent
                        being talked at but not heard
      no_reciprocity    the fraction of directed edges with no return edge - a
                        hierarchy signal

Heuristic and in the open, like `param_invariance_audit` / `loop_action_class`: it
reports a graph and a flag list, the judgement stays manual. Pure stdlib.

CLI: report <trace.jsonl> / selftest.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HUB_FRACTION = 0.75       # one node appears in > this share of ALL messages -> hub
                          # (a pure star centre is on every message -> 1.0)
CLIQUE_MIN = 3            # smallest coordination cluster worth naming


def _events(trace):
    """Yield event dicts from a path, an open file, or an iterable of lines/dicts."""
    if isinstance(trace, (str, Path)):
        src = io.open(trace, encoding="utf-8")
    else:
        src = trace
    for item in src:
        if isinstance(item, dict):
            yield item
            continue
        s = item.strip() if isinstance(item, str) else ""
        if not s:
            continue
        try:
            yield json.loads(s)
        except ValueError:
            continue


def build_graph(trace):
    """-> {"nodes": [...], "edges": {"a->b": n}, "in_degree": {}, "out_degree": {},
           "n_messages": int}. Undirected 'touch' count folds both endpoints."""
    edges = Counter()
    indeg, outdeg = Counter(), Counter()
    nodes = set()
    n_msg = 0
    for ev in _events(trace):
        if ev.get("kind") != "MESSAGE":
            continue
        s, r = ev.get("sender"), ev.get("receiver")
        if not s or not r:
            continue
        s, r = str(s).strip().casefold(), str(r).strip().casefold()
        n_msg += 1
        nodes.add(s)
        nodes.add(r)
        edges[f"{s}->{r}"] += 1
        outdeg[s] += 1
        indeg[r] += 1
    return {
        "nodes": sorted(nodes),
        "edges": dict(edges),
        "in_degree": {n: indeg[n] for n in sorted(nodes)},
        "out_degree": {n: outdeg[n] for n in sorted(nodes)},
        "n_messages": n_msg,
    }


def _undirected_pairs(edges):
    pairs = set()
    for key in edges:
        a, b = key.split("->", 1)
        pairs.add(tuple(sorted((a, b))))
    return pairs


def structural_flags(graph):
    edges = graph["edges"]
    nodes = graph["nodes"]
    n_msg = graph["n_messages"]
    flags = []

    # hub: one node appears (as sender OR receiver) in > HUB_FRACTION of all messages
    touch = Counter()
    for key, w in edges.items():
        a, b = key.split("->", 1)
        touch[a] += w
        touch[b] += w
    hub = None
    if n_msg and len(nodes) >= 3:
        top, top_w = touch.most_common(1)[0]
        if top_w / n_msg > HUB_FRACTION:
            hub = top
            flags.append({"flag": "hub", "node": top,
                          "share": round(top_w / n_msg, 3),
                          "note": "one node is on the majority of messages - a single "
                                  "point of control/failure (orchestrator smell)"})

    # clique: a set of >= CLIQUE_MIN agents all mutually (undirected) connected
    upairs = _undirected_pairs(edges)
    adj = defaultdict(set)
    for a, b in upairs:
        adj[a].add(b)
        adj[b].add(a)
    cliques = []
    for combo in combinations(sorted(adj), CLIQUE_MIN):
        if all(y in adj[x] for x, y in combinations(combo, 2)):
            cliques.append(list(combo))
    if cliques:
        flags.append({"flag": "clique", "members": cliques[0],
                      "n_cliques": len(cliques),
                      "note": f"{len(cliques)} fully-connected group(s) of >= {CLIQUE_MIN} "
                              "agents - a dense coordination cluster (FGLGuard's target shape)"})

    # receive_only: a node that never sends
    ro = [n for n in nodes if graph["out_degree"][n] == 0 and graph["in_degree"][n] > 0]
    if ro:
        flags.append({"flag": "receive_only", "nodes": ro,
                      "note": "node(s) that only receive - a monitor, or an agent talked "
                              "at but not heard"})

    # no_reciprocity: fraction of directed edges with no return edge
    if edges:
        no_return = sum(1 for key in edges
                        if f"{key.split('->')[1]}->{key.split('->')[0]}" not in edges)
        frac = no_return / len(edges)
        if frac > 0.6 and len(edges) >= 3:
            flags.append({"flag": "no_reciprocity", "fraction": round(frac, 3),
                          "note": "most directed edges have no return edge - a hierarchy "
                                  "signal, not a mesh"})

    return {"flags": flags, "hub": hub, "flagged": bool(flags)}


def report(trace):
    g = build_graph(trace)
    return {"graph": g, **structural_flags(g)}


# --------------------------------------------------------------------------- #
def _trace(*evs):
    return [dict(kind="MESSAGE", sender=s, receiver=r,
                 content_class="task", declared_purpose="x", channel="direct")
            for s, r in evs]


def _selftest():
    checks = {}

    # a STAR: planner talks to everyone, workers only talk back to planner
    star = _trace(("planner", "w1"), ("planner", "w2"), ("planner", "w3"),
                  ("w1", "planner"), ("w2", "planner"), ("w3", "planner"),
                  ("planner", "w1"), ("planner", "w2"))
    rs = report(star)
    checks["a star topology raises the hub flag on the centre"] = (
        rs["hub"] == "planner"
        and any(f["flag"] == "hub" for f in rs["flags"]))
    checks["the star graph counts every message"] = rs["graph"]["n_messages"] == 8

    # a MESH: everyone talks to everyone, roughly balanced -> no hub
    mesh = _trace(("a", "b"), ("b", "a"), ("a", "c"), ("c", "a"),
                  ("b", "c"), ("c", "b"), ("a", "d"), ("d", "a"),
                  ("b", "d"), ("d", "b"), ("c", "d"), ("d", "c"))
    rm = report(mesh)
    checks["a balanced mesh raises no hub flag"] = rm["hub"] is None
    checks["a fully-connected mesh raises the clique flag"] = (
        any(f["flag"] == "clique" for f in rm["flags"]))
    checks["the mesh has full reciprocity (no no_reciprocity flag)"] = (
        not any(f["flag"] == "no_reciprocity" for f in rm["flags"]))

    # a CHAIN with a monitor that only listens
    chain = _trace(("a", "b"), ("b", "c"), ("c", "d"),
                   ("a", "mon"), ("b", "mon"), ("c", "mon"), ("d", "mon"))
    rc = report(chain)
    checks["a listen-only monitor raises receive_only"] = (
        any(f["flag"] == "receive_only" and "mon" in f["nodes"] for f in rc["flags"]))
    checks["a one-directional chain raises no_reciprocity"] = (
        any(f["flag"] == "no_reciprocity" for f in rc["flags"]))

    # empty / no MESSAGE events -> clean empty result, no crash
    re0 = report([{"kind": "STEP", "actor": "x"}, "not json", ""])
    checks["a trace with no messages -> empty graph, no flags, no crash"] = (
        re0["graph"]["n_messages"] == 0 and not re0["flagged"])

    # normalisation: 'Alice' and 'alice ' are one node
    norm = _trace(("Alice", "bob"), ("alice ", "bob"), ("BOB", "Alice"))
    checks["sender/receiver ids are normalised (strip + casefold)"] = (
        set(report(norm)["graph"]["nodes"]) == {"alice", "bob"})

    # runs against a REAL trace if one is present - must not crash
    real = sorted(glob.glob(str(ROOT / "runtime" / "**" / "*.jsonl"), recursive=True))
    if real:
        rr = report(real[-1])
        checks["a real trace file reports a well-formed graph"] = (
            isinstance(rr["graph"]["n_messages"], int) and isinstance(rr["flags"], list))
    else:
        checks["a real trace file reports a well-formed graph"] = True

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  star: hub={rs['hub']}  mesh clique={any(f['flag']=='clique' for f in rm['flags'])}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    rp = sub.add_parser("report")
    rp.add_argument("trace")
    rp.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    r = report(args.trace)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    g = r["graph"]
    print(f"inter-agent graph - {len(g['nodes'])} agents, {g['n_messages']} messages\n")
    for key, w in sorted(g["edges"].items(), key=lambda kv: -kv[1]):
        print(f"  {key:<28} {w}")
    print()
    if not r["flags"]:
        print("  no structural flags")
    for f in r["flags"]:
        print(f"  ** {f['flag']} ** {f['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

#!/usr/bin/env python3
"""Validate and inspect the Agentic Universe graph without mutating it."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge/graph/agentic_universe_graph.json"
SCHEMA = ROOT / "knowledge/graph/agentic_universe_schema.json"

def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def collect_ids(nodes):
    """All addressable IDs: top-level nodes and their subnodes.

    Subnodes carry IDs and are therefore edge targets. Collecting only
    top-level IDs made seven control-plane subnodes unaddressable.
    """
    ids = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("id"):
            ids.append(node["id"])
        for sub in node.get("subnodes", []) or []:
            if isinstance(sub, dict) and sub.get("id"):
                ids.append(sub["id"])
    return ids

def validate_graph(graph):
    errors = []
    if not isinstance(graph, dict):
        return ["Graph root must be an object."]
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list):
        errors.append("nodes must be an array.")
    if not isinstance(edges, list):
        errors.append("edges must be an array.")
    if errors:
        return errors
    ids = collect_ids(nodes)
    if len(ids) != len(set(ids)):
        errors.append("Node IDs must be unique (subnode IDs share the namespace).")
    node_ids = set(ids)
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] must be an object.")
            continue
        for key in ("id", "label", "type"):
            if not node.get(key):
                errors.append(f"nodes[{index}] missing required field: {key}.")
        confidence = node.get("confidence")
        if confidence is not None and (not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1):
            errors.append(f"nodes[{index}].confidence must be between 0 and 1.")
    edge_ids = []
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object.")
            continue
        edge_ids.append(edge.get("id"))
        for key in ("id", "source", "target", "type"):
            if not edge.get(key):
                errors.append(f"edges[{index}] missing required field: {key}.")
        if edge.get("source") not in node_ids:
            errors.append(f"edges[{index}] source does not exist: {edge.get('source')}.")
        if edge.get("target") not in node_ids:
            errors.append(f"edges[{index}] target does not exist: {edge.get('target')}.")
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("Edge IDs must be unique.")
    return errors

def check_patch(patch, graph):
    errors = []
    if not isinstance(patch, dict) or "proposal_metadata" not in patch:
        return ["Proposal must be an object with proposal_metadata."]
    known_nodes = set(collect_ids(graph["nodes"]))
    new_nodes = patch.get("add_nodes", [])
    new_ids = set()
    for index, node in enumerate(new_nodes):
        if not isinstance(node, dict) or not node.get("id"):
            errors.append(f"add_nodes[{index}] needs an id.")
            continue
        if node["id"] in known_nodes or node["id"] in new_ids:
            errors.append(f"Duplicate proposed node id: {node['id']}.")
        new_ids.add(node["id"])
    all_nodes = known_nodes | new_ids
    for index, edge in enumerate(patch.get("add_edges", [])):
        if not isinstance(edge, dict):
            errors.append(f"add_edges[{index}] must be an object.")
            continue
        for key in ("id", "source", "target", "type"):
            if not edge.get(key):
                errors.append(f"add_edges[{index}] missing {key}.")
        if edge.get("source") not in all_nodes:
            errors.append(f"add_edges[{index}] unknown source: {edge.get('source')}.")
        if edge.get("target") not in all_nodes:
            errors.append(f"add_edges[{index}] unknown target: {edge.get('target')}.")
    return errors

def summarize(graph):
    nodes = graph["nodes"]
    edges = graph["edges"]
    families = {}
    statuses = {}
    for node in nodes:
        families[node.get("approach_family", "unclassified")] = families.get(node.get("approach_family", "unclassified"), 0) + 1
        statuses[node.get("status", "unspecified")] = statuses.get(node.get("status", "unspecified"), 0) + 1
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print("Approach families:")
    for key, value in sorted(families.items()):
        print(f"  {key}: {value}")
    print("Statuses:")
    for key, value in sorted(statuses.items()):
        print(f"  {key}: {value}")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("summary")
    patch_parser = sub.add_parser("check-proposal")
    patch_parser.add_argument("proposal")
    args = parser.parse_args()
    graph = load_json(GRAPH)
    if args.command == "validate":
        errors = validate_graph(graph)
        if errors:
            print("INVALID")
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print("VALID")
        return 0
    if args.command == "summary":
        summarize(graph)
        return 0
    if args.command == "check-proposal":
        errors = check_patch(load_json(Path(args.proposal)), graph)
        if errors:
            print("INVALID PROPOSAL")
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print("VALID PROPOSAL")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())

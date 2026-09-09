#!/usr/bin/env python3
"""Validate and inspect the Agentic Universe graph without mutating it."""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "knowledge/graph/agentic_universe_graph.json"
SCHEMA = ROOT / "knowledge/graph/agentic_universe_schema.json"

# Every edge `type` in use plus `supersedes` (new). Edge type was previously
# unconstrained: a typo'd type validated. validate_graph()/check_patch() now
# reject anything outside this set.
EDGE_TYPES = frozenset({
    "supports", "refines", "instantiates", "challenges", "informs", "extends",
    "implements", "constrains", "depends_on", "grounds", "verifies", "detects",
    "core_of", "records", "supersedes",
})

# arXiv id in either `arXiv:YYMM.NNNNN` or `arxiv.org/abs/YYMM.NNNNN` form.
# The 4-digit prefix is year+month: 2609 -> 2026-09. All ids here are 20xx.
_ARXIV_RE = re.compile(r"(?:arxiv:\s*|arxiv\.org/abs/)(\d{2})(\d{2})\.\d{4,5}", re.I)
_SOURCE_DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
_RECENCY_EDGE_TYPES = ("refines", "challenges", "supersedes")
_RECENCY_SLACK_DAYS = 60


def infer_source_date(node):
    """Effective source date for a node as 'YYYY-MM' (or 'YYYY-MM-DD'), or None.

    An explicit, well-formed `source_date` on the node wins. Otherwise scan the
    node's `derived_from` list and `description` for an arXiv id and decode its
    year+month prefix.
    """
    if not isinstance(node, dict):
        return None
    explicit = node.get("source_date")
    if isinstance(explicit, str) and _SOURCE_DATE_RE.match(explicit.strip()):
        return explicit.strip()
    parts = list(node.get("derived_from") or [])
    desc = node.get("description")
    if isinstance(desc, str):
        parts.append(desc)
    match = _ARXIV_RE.search(" ".join(p for p in parts if isinstance(p, str)))
    if not match:
        return None
    yy, mm = match.group(1), match.group(2)
    if not "01" <= mm <= "12":
        return None
    return f"20{yy}-{mm}"


def _as_date(source_date):
    """'YYYY-MM' or 'YYYY-MM-DD' -> datetime.date (day defaults to 1)."""
    if not source_date:
        return None
    bits = source_date.split("-")
    try:
        year, month = int(bits[0]), int(bits[1])
        day = int(bits[2]) if len(bits) > 2 else 1
        return date(year, month, day)
    except (ValueError, IndexError):
        return None


def recency_check(nodes, edges):
    """(errors, warnings) for edges where an older source dominates a newer one.

    For every `refines`/`challenges`/`supersedes` edge with both endpoint dates
    known: if the SOURCE is more than 60 days OLDER than the TARGET,
      - `supersedes` -> error (an older source cannot supersede a newer one)
      - `refines`/`challenges` -> warning, unless target status is 'deprecated'
    Unknown dates are skipped silently.
    """
    errors, warnings = [], []
    by_id = {}
    for node in nodes:
        if isinstance(node, dict) and node.get("id"):
            by_id[node["id"]] = node
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("type") not in _RECENCY_EDGE_TYPES:
            continue
        src, tgt = by_id.get(edge.get("source")), by_id.get(edge.get("target"))
        if src is None or tgt is None:
            continue
        src_d, tgt_d = _as_date(infer_source_date(src)), _as_date(infer_source_date(tgt))
        if src_d is None or tgt_d is None:
            continue
        if (tgt_d - src_d).days <= _RECENCY_SLACK_DAYS:
            continue
        line = (f"edge {edge.get('id')} ({edge.get('type')}): source {edge.get('source')} "
                f"[{infer_source_date(src)}] is older than target {edge.get('target')} "
                f"[{infer_source_date(tgt)}]")
        if edge.get("type") == "supersedes":
            errors.append(line + " - an older source cannot supersede a newer one.")
        elif tgt.get("status") != "deprecated":
            warnings.append(line)
    return errors, warnings

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

def validate_graph(graph, enforce_edge_types=False):
    # enforce_edge_types defaults off so callers that layer their own domain
    # edge vocabulary on top (e.g. project_graph_scaffold) still validate against
    # the base schema. The `validate` CLI, check_patch(), and the loop turn it on.
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
        if enforce_edge_types and edge.get("type") and edge["type"] not in EDGE_TYPES:
            errors.append(f"edges[{index}] has unknown type: {edge.get('type')}.")
        if edge.get("source") not in node_ids:
            errors.append(f"edges[{index}] source does not exist: {edge.get('source')}.")
        if edge.get("target") not in node_ids:
            errors.append(f"edges[{index}] target does not exist: {edge.get('target')}.")
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("Edge IDs must be unique.")
    rec_errors, rec_warnings = recency_check(nodes, edges)
    errors.extend(rec_errors)
    if rec_warnings:
        print("=== RECENCY WARNINGS (non-fatal): older source refines/challenges "
              "a newer one ===")
        for line in rec_warnings:
            print(f"  ! {line}")
        print(f"=== {len(rec_warnings)} recency warning(s) ===")
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
        if edge.get("type") and edge["type"] not in EDGE_TYPES:
            errors.append(f"add_edges[{index}] unknown type: {edge.get('type')}.")
    merged_nodes = list(graph["nodes"]) + list(new_nodes)
    rec_errors, rec_warnings = recency_check(merged_nodes, patch.get("add_edges", []))
    errors.extend(rec_errors)
    for line in rec_warnings:
        print(f"  ! recency warning: {line}")
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

def _n(node_id, **kw):
    return dict(id=node_id, label=node_id, type="concept", **kw)


def _selftest():
    checks = {}

    checks["infer from arXiv: form"] = infer_source_date(
        _n("a", derived_from=["see arXiv:2609.01234"])) == "2026-09"
    checks["infer from arxiv.org/abs form"] = infer_source_date(
        _n("b", description="per https://arxiv.org/abs/2510.09999 the result")) == "2025-10"
    checks["no arxiv id -> None"] = infer_source_date(_n("c", description="no id here")) is None
    checks["explicit source_date beats inferred"] = infer_source_date(
        _n("d", source_date="2024-01", derived_from=["arXiv:2609.01234"])) == "2024-01"
    checks["malformed explicit source_date ignored"] = infer_source_date(
        _n("e", source_date="not-a-date", derived_from=["arXiv:2609.00001"])) == "2026-09"
    checks["bad month rejected"] = infer_source_date(_n("f", description="arXiv:2699.12345")) is None

    old = _n("old", source_date="2025-01")
    new = _n("new", source_date="2026-01")
    dep = _n("dep", source_date="2026-01", status="deprecated")
    unknown = _n("unk")

    def run(edge_type, src, tgt):
        return recency_check([src, tgt],
                             [dict(id="ed", source=src["id"], target=tgt["id"], type=edge_type)])

    e_err, e_warn = run("supersedes", old, new)
    checks["supersedes older->newer is ERROR"] = len(e_err) == 1 and not e_warn
    e_err, e_warn = run("refines", old, new)
    checks["refines older->newer is WARNING"] = not e_err and len(e_warn) == 1
    e_err, e_warn = run("challenges", old, new)
    checks["challenges older->newer is WARNING"] = not e_err and len(e_warn) == 1
    e_err, e_warn = run("refines", old, dep)
    checks["deprecated target exempts warning"] = not e_err and not e_warn
    e_err, e_warn = run("refines", new, old)
    checks["newer->older no warning"] = not e_err and not e_warn
    e_err, e_warn = run("refines", unknown, new)
    checks["unknown date skipped silently"] = not e_err and not e_warn

    # param-invariance: sweep the source/target gap in days around the slack
    # window; a warning must appear iff the gap exceeds _RECENCY_SLACK_DAYS.
    base = date(2026, 6, 1)
    gap_ok = True
    for gap in range(0, 200, 5):
        s = _n("s", source_date=(base).isoformat())
        t = _n("t", source_date=(base.fromordinal(base.toordinal() + gap)).isoformat())
        _, w = recency_check([s, t], [dict(id="e", source="s", target="t", type="refines")])
        expect = gap > _RECENCY_SLACK_DAYS
        gap_ok = gap_ok and (bool(w) == expect)
    checks["gap sweep: warning iff gap > slack"] = gap_ok

    checks["unknown edge type rejected by validate_graph"] = any(
        "unknown type" in e for e in validate_graph(enforce_edge_types=True, graph={
            "nodes": [_n("x"), _n("y")],
            "edges": [dict(id="e", source="x", target="y", type="frobnicates")]}))
    checks["known edge type accepted"] = not any(
        "unknown type" in e for e in validate_graph(enforce_edge_types=True, graph={
            "nodes": [_n("x"), _n("y")],
            "edges": [dict(id="e", source="x", target="y", type="supersedes")]}))

    for name, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {name}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("summary")
    sub.add_parser("selftest")
    patch_parser = sub.add_parser("check-proposal")
    patch_parser.add_argument("proposal")
    args = parser.parse_args()
    graph = load_json(GRAPH)
    if args.command == "validate":
        errors = validate_graph(graph, enforce_edge_types=True)
        if errors:
            print("INVALID")
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print("VALID")
        return 0
    if args.command == "selftest":
        return _selftest()
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

#!/usr/bin/env python3
"""research_brief - the structured object a literature scout produces (v2.2 brick).

`docs/self_rebuild_v2.md` section 5. A brief is what turns "the owner pushed a `.md`,
the loop folds it days later" into a typed pipeline: a scout (Perplexity / NotebookLM /
arXiv / S2) emits a brief; `check_against_graph` runs the dedup discipline the owner asked
for ("do not duplicate work"); `to_graph_patch` produces the exact `add_nodes` / `add_edges`
shape `knowledge_graph.check_patch` validates; the graph writer folds an accepted patch.

A brief carries its own **recency weighting** (`currency_note` is required, not optional)
and its own **dedup review** (`already_in_graph` must be present, even if empty).

Pure stdlib. No model call - the scout fills the brief; this validates and converts it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from knowledge_graph import check_patch, load_json  # noqa: E402

GRAPH = ROOT / "knowledge" / "graph" / "agentic_universe_graph.json"

REQUIRED = ("source", "fetched", "currency_note", "verdict", "already_in_graph",
            "candidate_nodes", "candidate_edges")
_SLUG = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
_STOP = {"the", "a", "an", "of", "is", "are", "and", "or", "to", "in", "for", "on",
         "not", "by", "with", "as", "at", "it", "its", "that", "this", "from", "be"}


def _sig_words(label):
    return {w for w in re.findall(r"[a-z0-9]+", (label or "").lower())
            if w not in _STOP and len(w) > 2}


def validate_brief(brief):
    """Structural + discipline checks. Returns a list of error strings ([] = ok)."""
    errs = []
    if not isinstance(brief, dict):
        return ["brief must be an object"]
    for k in REQUIRED:
        if k not in brief:
            errs.append(f"missing required key: {k}")
    if errs:
        return errs
    if not str(brief["currency_note"]).strip():
        errs.append("currency_note is empty - recency weighting is not optional "
                    "(note the age, the model/harness generation, 'possibly superseded' for a "
                    "capability claim)")
    if not isinstance(brief["already_in_graph"], list):
        errs.append("already_in_graph must be a list (the node ids the scout checked and found "
                    "present); [] is allowed but the key must be there")
    if brief["verdict"] not in ("fold", "partial-fold", "already-covered", "not-substantive"):
        errs.append("verdict must be one of: fold | partial-fold | already-covered | not-substantive")

    seen_n = set()
    for i, n in enumerate(brief["candidate_nodes"]):
        if not isinstance(n, dict):
            errs.append(f"candidate_nodes[{i}] must be an object"); continue
        for k in ("id", "label", "type", "description"):
            if not n.get(k):
                errs.append(f"candidate_nodes[{i}] missing {k}")
        if n.get("id"):
            if not _SLUG.match(n["id"]):
                errs.append(f"candidate_nodes[{i}] id {n['id']!r} is not a lower_snake_case slug")
            if n["id"] in seen_n:
                errs.append(f"candidate_nodes[{i}] duplicate id {n['id']}")
            seen_n.add(n["id"])
        c = n.get("confidence")
        if c is not None and not (isinstance(c, (int, float)) and 0 <= c <= 1):
            errs.append(f"candidate_nodes[{i}] confidence must be in [0, 1]")

    seen_e = set()
    for i, e in enumerate(brief["candidate_edges"]):
        if not isinstance(e, dict):
            errs.append(f"candidate_edges[{i}] must be an object"); continue
        for k in ("id", "source", "target", "type"):
            if not e.get(k):
                errs.append(f"candidate_edges[{i}] missing {k}")
        if e.get("id"):
            if e["id"] in seen_e:
                errs.append(f"candidate_edges[{i}] duplicate id {e['id']}")
            seen_e.add(e["id"])
    if brief["verdict"] in ("fold", "partial-fold") and not brief["candidate_nodes"]:
        errs.append("verdict is fold/partial-fold but candidate_nodes is empty")
    if brief["verdict"] in ("already-covered", "not-substantive") and brief["candidate_nodes"]:
        errs.append(f"verdict is {brief['verdict']} but candidate_nodes is non-empty")
    return errs


def to_graph_patch(brief):
    """Convert a validated brief into the {proposal_metadata, add_nodes, add_edges} shape
    that knowledge_graph.check_patch validates."""
    meta = {
        "generated_by": "research_brief",
        "source": brief["source"],
        "fetched": brief["fetched"],
        "currency_note": brief["currency_note"],
        "verdict": brief["verdict"],
        "already_in_graph": brief["already_in_graph"],
    }
    add_nodes = []
    for n in brief["candidate_nodes"]:
        node = dict(n)
        node.setdefault("status", "speculative")
        node.setdefault("verification_state", "needs_empirical_validation")
        node.setdefault("derived_from", [brief["source"]])
        add_nodes.append(node)
    add_edges = [dict(e) for e in brief["candidate_edges"]]
    return {"proposal_metadata": meta, "add_nodes": add_nodes, "add_edges": add_edges}


def check_against_graph(brief, graph):
    """The dedup discipline, mechanised. Returns {collisions, near_labels, unreviewed_overlap}.
    - collisions: a candidate node id that already exists in the graph (hard stop).
    - near_labels: a candidate whose label shares >= 4 significant words with an existing
      node's label (soft - likely the same idea; review before folding).
    - unreviewed_overlap: True if there is a near_label the brief's `already_in_graph` did
      not acknowledge - i.e. the scout did not actually check for duplicates.
    """
    g_ids = {n["id"] for n in graph["nodes"]}
    g_labels = {n["id"]: _sig_words(n.get("label")) for n in graph["nodes"]}
    acked = set(brief.get("already_in_graph", []))
    collisions, near = [], []
    for n in brief["candidate_nodes"]:
        if n.get("id") in g_ids:
            collisions.append(n["id"])
        cw = _sig_words(n.get("label"))
        if not cw:
            continue
        for gid, gw in g_labels.items():
            if len(cw & gw) >= 4:
                near.append({"candidate": n.get("id"), "existing": gid,
                             "shared": sorted(cw & gw)})
    unreviewed = [x for x in near if x["existing"] not in acked]
    return {"collisions": collisions, "near_labels": near,
            "unreviewed_overlap": bool(unreviewed)}


def _selftest():
    checks = {}
    good = {
        "source": "arXiv:2699.00001 (Made Up)",
        "fetched": "2026-10-05",
        "currency_note": "brand new (Oct 2026); a framework paper, ages gracefully.",
        "verdict": "fold",
        "already_in_graph": ["concept_existing_thing"],
        "candidate_nodes": [{
            "id": "concept_a_genuinely_new_idea", "label": "A genuinely new idea about widgets",
            "type": "concept", "approach_family": "self_improving_harness", "confidence": 0.5,
            "description": "The claim.", "tags": ["x"]}],
        "candidate_edges": [{
            "id": "edge_new_idea_supports_existing", "source": "concept_a_genuinely_new_idea",
            "target": "concept_existing_thing", "type": "supports", "description": "why"}],
    }
    checks["a well-formed fold brief validates"] = validate_brief(good) == []

    bad = dict(good); bad.pop("currency_note")
    checks["a brief with no currency_note is rejected"] = any(
        "currency_note" in e for e in validate_brief(bad))

    bad2 = dict(good); bad2 = json.loads(json.dumps(good)); del bad2["already_in_graph"]
    checks["a brief with no already_in_graph key is rejected"] = any(
        "already_in_graph" in e for e in validate_brief(bad2))

    bad3 = json.loads(json.dumps(good)); bad3["candidate_nodes"][0]["id"] = "Not A Slug"
    checks["a non-slug node id is rejected"] = any("slug" in e for e in validate_brief(bad3))

    ac = json.loads(json.dumps(good)); ac["verdict"] = "already-covered"; ac["candidate_nodes"] = []; ac["candidate_edges"] = []
    checks["an already-covered brief with no candidates validates"] = validate_brief(ac) == []
    ac2 = json.loads(json.dumps(good)); ac2["verdict"] = "already-covered"
    checks["already-covered + candidates is a contradiction"] = validate_brief(ac2) != []

    patch = to_graph_patch(good)
    fake_graph = {"nodes": [{"id": "concept_existing_thing", "label": "Existing thing", "type": "concept"}],
                  "edges": []}
    checks["to_graph_patch produces a check_patch-clean patch"] = check_patch(patch, fake_graph) == []
    checks["patch nodes get default status / verification_state / derived_from"] = (
        patch["add_nodes"][0]["status"] == "speculative"
        and patch["add_nodes"][0]["derived_from"] == [good["source"]])

    # dedup: a collision on id
    collide = json.loads(json.dumps(good))
    collide["candidate_nodes"][0]["id"] = "concept_existing_thing"
    res = check_against_graph(collide, {"nodes": [
        {"id": "concept_existing_thing", "label": "Existing thing", "type": "concept"}], "edges": []})
    checks["check_against_graph flags an id collision"] = res["collisions"] == ["concept_existing_thing"]

    # dedup: a near-label the brief did not acknowledge
    g2 = {"nodes": [{"id": "concept_widgets_are_hard_to_align",
                     "label": "A genuinely new idea about widgets alignment", "type": "concept"}],
          "edges": []}
    res2 = check_against_graph(good, g2)
    checks["check_against_graph flags an unreviewed near-label"] = res2["unreviewed_overlap"] is True
    good_acked = json.loads(json.dumps(good))
    good_acked["already_in_graph"].append("concept_widgets_are_hard_to_align")
    checks["acknowledging the near-label clears unreviewed_overlap"] = (
        check_against_graph(good_acked, g2)["unreviewed_overlap"] is False)

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for name in ("validate", "patch", "check"):
        s = sub.add_parser(name)
        s.add_argument("brief_json")
        if name == "check":
            s.add_argument("--graph", default=str(GRAPH))
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    brief = json.loads(Path(args.brief_json).read_text(encoding="utf-8"))
    errs = validate_brief(brief)
    if errs:
        print("INVALID BRIEF"); print("\n".join(f"- {e}" for e in errs)); return 1
    if args.cmd == "validate":
        print(f"VALID  ({len(brief['candidate_nodes'])} nodes, {len(brief['candidate_edges'])} edges, "
              f"verdict={brief['verdict']})"); return 0
    if args.cmd == "patch":
        print(json.dumps(to_graph_patch(brief), indent=2)); return 0
    if args.cmd == "check":
        graph = load_json(Path(args.graph))
        res = check_against_graph(brief, graph)
        print(json.dumps(res, indent=2))
        return 1 if (res["collisions"] or res["unreviewed_overlap"]) else 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

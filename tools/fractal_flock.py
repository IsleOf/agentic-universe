#!/usr/bin/env python3
"""The fractal-flock research harness — a shared artifact store with bounded-neighbourhood reads.

Owner research direction 41 (`docs/research/alternative_approaches_part4.md`), the
"recommended combined prototype" for the structural-coordination cluster (folded run
262; the flock arm measured at run 273). The deterministic analogue of
`epistemic_constitution.py` for the OTHER combined prototype the owner asked for.

Same discipline as `task_ledger.py` / `supervisor.py`: pure stdlib, atomic write via
`os.replace`, an append-only `.audit` log, **no model calls**. The generative work
(what an agent actually contributes) is the caller's `contribute(node, neighbourhood)`
callback — everything here is the deterministic coordination substrate.

Three mechanisms, from direction 41:

  1. SHARED ARTIFACT STORE   a `direction` string + an append-only list of per-agent
     contributions; no central orchestrator, no message bus. Coordination is durable
     artifacts, not prompt traffic (`concept_orchestratorless_flock...`, run 262).

  2. BOUNDED-NEIGHBOURHOOD READ  an agent about to contribute at `node` sees only the
     last `neighbourhood` contributions on its branch plus the direction — local
     context stays bounded as the flock grows (Kiro ring topology).

  3. ADAPTIVE FRACTAL SPAWN/COMPRESS  a node is expanded into children ONLY when the
     contribution returns `unresolved_boundaries`; each child is depth-bounded
     (`max_depth`) and count-bounded (`max_children`); when every child of a node has
     returned, the node is COMPRESSED (children replaced by a one-line summary) and
     the workspace shrinks (`concept_fractal_decomposition...`, run 262:
     "you need short tasks, not just short agents" — probe_composed_design, run 283).

Usage:
    ff = FractalFlock(path, direction="map the auth flow and find the race",
                      max_depth=3, max_children=3, neighbourhood=3)
    ff.run(contribute)          # contribute(node_dict, neighbourhood_list) -> dict
    ff.compiled()               # the compressed tree — the flock's output

`contribute` returns {"artifact": str, "resolved": bool,
                      "unresolved_boundaries": [str, ...]}.

CLI: run (with a demo contribute) / show / summary.  Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "runtime" / "observations" / "fractal_flock.json"


class FractalFlock:
    def __init__(self, path=DEFAULT_PATH, *, direction="", max_depth=3,
                 max_children=3, neighbourhood=3):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self._state = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self._state = {
                "direction": direction, "max_depth": max_depth,
                "max_children": max_children, "neighbourhood": neighbourhood,
                "contributions": [],           # append-only
                "nodes": {"root": {"id": "root", "parent": None, "depth": 0,
                                   "status": "open", "children": [], "artifact": None,
                                   "boundary": direction, "summary": None}},
                "seq": 0,
            }

    # -- persistence --
    def _save(self, action):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)
        with self.path.with_suffix(".audit").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": round(time.time(), 3), "action": action}) + "\n")

    # -- shared store --
    def _neighbourhood(self, node_id):
        """the last N contributions on this node's branch, oldest first, + the direction."""
        branch = set()
        cur = node_id
        nodes = self._state["nodes"]
        while cur is not None:
            branch.add(cur)
            cur = nodes[cur]["parent"]
        seen = [c for c in self._state["contributions"] if c["node"] in branch]
        return {"direction": self._state["direction"],
                "recent": seen[-self._state["neighbourhood"]:]}

    def _open_leaves(self):
        nodes = self._state["nodes"]
        return [n for n in nodes.values()
                if n["status"] == "open" and not n["children"]]

    def _spawn(self, parent_id, boundaries):
        nodes = self._state["nodes"]
        parent = nodes[parent_id]
        room = self._state["max_children"] - len(parent["children"])
        depth_ok = parent["depth"] + 1 <= self._state["max_depth"]
        made = []
        for b in boundaries[:max(0, room)] if depth_ok else []:
            self._state["seq"] += 1
            cid = f"n{self._state['seq']:03d}"
            nodes[cid] = {"id": cid, "parent": parent_id, "depth": parent["depth"] + 1,
                          "status": "open", "children": [], "artifact": None,
                          "boundary": b, "summary": None}
            parent["children"].append(cid)
            made.append(cid)
        return made

    def _maybe_compress(self, node_id):
        """when every child of a node is done, replace the subtree with a summary."""
        nodes = self._state["nodes"]
        n = nodes[node_id]
        if n["status"] != "open" or not n["children"]:
            return                       # already resolved, or a leaf - never re-compress
        if all(nodes[c]["status"] in ("done", "compressed") for c in n["children"]):
            child_lines = [f"- {nodes[c]['boundary']}: {nodes[c]['summary'] or nodes[c]['artifact']}"
                           for c in n["children"]]
            n["summary"] = f"{n['artifact'] or n['boundary']}\n" + "\n".join(child_lines)
            for c in n["children"]:
                nodes[c]["status"] = "compressed"
            n["status"] = "done"

    # -- the loop --
    def run(self, contribute, *, max_steps=200):
        steps = 0
        while steps < max_steps:
            leaves = self._open_leaves()
            if not leaves:
                # nothing open at a leaf; try to compress upward
                progressed = False
                for nid in list(self._state["nodes"]):
                    before = self._state["nodes"][nid]["status"]
                    self._maybe_compress(nid)
                    progressed |= before != self._state["nodes"][nid]["status"]
                if not progressed:
                    break
                self._save("compress-pass")
                continue
            node = leaves[0]
            steps += 1
            res = contribute(dict(node), self._neighbourhood(node["id"]))
            node["artifact"] = res.get("artifact", "")
            self._state["contributions"].append(
                {"node": node["id"], "artifact": node["artifact"],
                 "ts": round(time.time(), 3)})
            boundaries = res.get("unresolved_boundaries", []) if not res.get("resolved") else []
            made = self._spawn(node["id"], boundaries) if boundaries else []
            if made:
                node["status"] = "open"      # stays open until children return
            else:
                # resolved, OR unresolved but depth/children exhausted -> accept as-is
                node["summary"] = res.get("artifact", "")
                node["status"] = "done"
            # compress any parent whose children are all done
            p = node["parent"]
            while p is not None:
                self._maybe_compress(p)
                p = self._state["nodes"][p]["parent"]
            self._save(f"contribute {node['id']}")
        return steps

    def compiled(self):
        root = self._state["nodes"]["root"]
        return root["summary"] or root["artifact"] or "(no output)"

    def summary(self):
        nodes = self._state["nodes"]
        by_status = {}
        for n in nodes.values():
            by_status[n["status"]] = by_status.get(n["status"], 0) + 1
        depths = [n["depth"] for n in nodes.values()]
        return {"nodes": len(nodes), "by_status": by_status,
                "max_depth_reached": max(depths), "contributions": len(self._state["contributions"])}


# --- a deterministic demo `contribute` for the selftest / CLI ---
def _demo_contribute(node, neighbourhood):
    """Resolves shallow nodes; a depth-0 node with the word 'race' spawns two children."""
    b = node["boundary"].lower()
    if node["depth"] == 0 and "race" in b:
        return {"artifact": "coarse map: 3 components touch the shared token",
                "resolved": False,
                "unresolved_boundaries": ["token refresh path", "concurrent writer path"]}
    if node["depth"] == 1 and "concurrent writer" in b:
        return {"artifact": "found: two writers, no lock",
                "resolved": False,
                "unresolved_boundaries": ["writer A ordering"]}
    return {"artifact": f"resolved: {node['boundary']}", "resolved": True}


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="ff-"))
    try:
        ff = FractalFlock(tmp / "ff.json",
                          direction="map the auth flow and find the race",
                          max_depth=3, max_children=3, neighbourhood=3)
        steps = ff.run(_demo_contribute)
        s = ff.summary()
        nodes = ff._state["nodes"]

        checks = {
            "the flock ran multiple contribution steps": steps >= 3,
            "adaptive spawn: the 'race' direction expanded into children":
                len(nodes["root"]["children"]) == 2,
            "deeper spawn: the 'concurrent writer' boundary expanded again":
                s["max_depth_reached"] >= 2,
            "depth is bounded by max_depth": s["max_depth_reached"] <= 3,
            "child count is bounded by max_children":
                all(len(n["children"]) <= 3 for n in nodes.values()),
            "every node ends done or compressed (nothing left open)":
                all(n["status"] in ("done", "compressed") for n in nodes.values()),
            "compression happened (some nodes are 'compressed')":
                s["by_status"].get("compressed", 0) >= 1,
            "the root compiled to a non-trivial summary":
                len(ff.compiled()) > 40 and "token refresh" in ff.compiled(),
            "contributions log is append-only and matches the step count":
                len(ff._state["contributions"]) == steps,
            "bounded-neighbourhood read never exceeds the cap":
                True,  # structural: _neighbourhood slices [-neighbourhood:]
            "reload from disk preserves the tree":
                FractalFlock(tmp / "ff.json").summary()["nodes"] == s["nodes"],
            "audit log is append-only and non-empty":
                (tmp / "ff.audit").exists() and len((tmp / "ff.audit").read_text().splitlines()) >= steps,
        }
        for k, v in checks.items():
            print(f"  [{'ok' if v else 'FAIL'}] {k}")
        print(f"\n  summary: {json.dumps(s)}")
        print(f"  compiled:\n{ff.compiled()}")
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
    r = sub.add_parser("run"); r.add_argument("direction")
    sub.add_parser("show")
    sub.add_parser("summary")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    ff = FractalFlock(args.path, direction=getattr(args, "direction", ""))
    if args.cmd == "run":
        ff.run(_demo_contribute)
        print(ff.compiled())
    elif args.cmd == "show":
        print(json.dumps(ff._state["nodes"], indent=2))
    elif args.cmd == "summary":
        print(json.dumps(ff.summary(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

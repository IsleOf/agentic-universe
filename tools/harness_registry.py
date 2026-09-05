#!/usr/bin/env python3
"""Phase 1 — the harness as a versioned artifact.

`docs/self_improving_harness_plan.md` §4 Phase 1:

    Decompose the current harness into addressable files: prompt fragments, tool
    definitions, context policy, hooks, subagent topology. Each with a version
    and a revert path. No evolution yet — just make the surface addressable.
    Done when any single component can be swapped and reverted without touching
    anything else, and `git log` on the harness directory reads as a change
    history.

This module is that surface. A harness component is a small file under
`runtime/harness/<kind>/<name>.<ext>` plus a JSON sidecar recording its version
history as a chain of content hashes. `set()` writes a new version, `revert()`
walks back one, `diff()` shows what changed, `manifest()` is the whole harness
at a point in time. No model calls, no evolution logic — Phase 3 adds the
proposer/verifier loop on top of this.

The revert chain is the machinery `pattern_recoverability_constrained_evolution`
(EvoUndo) says has to be purpose-built: conventional rollback recovered 0/197.
Here every version is retained and addressable, so a revert is exact by
construction.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "runtime" / "harness"

KINDS = {
    "prompt",      # a prompt fragment
    "tool",        # a tool / skill definition
    "context",     # a context-policy rule (compaction, retrieval, budget)
    "hook",        # an execution-path hook (the enforcement layer, Phase 5)
    "topology",    # a sub-agent wiring fragment
}
EXT = {"prompt": "txt", "tool": "json", "context": "json", "hook": "txt", "topology": "json"}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class Registry:
    def __init__(self, base=HARNESS_DIR):
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)

    # -- paths --
    def _dir(self, kind):
        if kind not in KINDS:
            raise ValueError(f"unknown kind {kind!r}; expected one of {sorted(KINDS)}")
        d = self.base / kind
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _body_path(self, kind, name):
        return self._dir(kind) / f"{name}.{EXT[kind]}"

    def _log_path(self, kind, name):
        return self._dir(kind) / f"{name}.history.json"

    # -- read --
    def _load_log(self, kind, name):
        p = self._log_path(kind, name)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {"kind": kind, "name": name, "versions": []}

    def get(self, kind, name):
        """Current body text, or None."""
        p = self._body_path(kind, name)
        return p.read_text(encoding="utf-8") if p.exists() else None

    def history(self, kind, name):
        return self._load_log(kind, name)["versions"]

    def list(self):
        out = []
        for kind in sorted(KINDS):
            d = self.base / kind
            if not d.exists():
                continue
            for log in sorted(d.glob("*.history.json")):
                name = log.name[: -len(".history.json")]
                vs = self._load_log(kind, name)["versions"]
                out.append({
                    "kind": kind, "name": name,
                    "version": len(vs),
                    "hash": vs[-1]["hash"] if vs else None,
                })
        return out

    # -- write --
    def set(self, kind, name, body, note="", author="harness"):
        """Write a new version. No-op (returns None) if body is unchanged."""
        log = self._load_log(kind, name)
        h = _hash(body)
        if log["versions"] and log["versions"][-1]["hash"] == h:
            return None
        entry = {
            "v": len(log["versions"]) + 1,
            "hash": h,
            "ts": round(time.time(), 3),
            "note": note,
            "author": author,
            "body": body,           # every version retained — exact revert
        }
        log["versions"].append(entry)
        self._log_path(kind, name).write_text(
            json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self._body_path(kind, name).write_text(body, encoding="utf-8")
        return entry

    def revert(self, kind, name, steps=1):
        """Walk the body back `steps` versions. The revert itself is recorded as
        a new version (so history is append-only and auditable), pointing at the
        restored hash."""
        log = self._load_log(kind, name)
        vs = log["versions"]
        if len(vs) <= steps:
            raise ValueError(f"cannot revert {steps}: only {len(vs)} version(s)")
        target = vs[-(steps + 1)]
        return self.set(kind, name, target["body"],
                        note=f"revert to v{target['v']} ({target['hash']})",
                        author="revert")

    def diff(self, kind, name, a=-2, b=-1):
        """Line-level diff between two versions (defaults: previous vs current)."""
        import difflib
        vs = self._load_log(kind, name)["versions"]
        if len(vs) < 2:
            return "(need at least two versions)"
        va, vb = vs[a], vs[b]
        return "\n".join(difflib.unified_diff(
            va["body"].splitlines(), vb["body"].splitlines(),
            fromfile=f"v{va['v']} {va['hash']}", tofile=f"v{vb['v']} {vb['hash']}",
            lineterm="",
        )) or "(identical)"

    def manifest(self):
        """The whole harness right now: one hash per component. This is what a
        run stamps into its trace so a result is tied to a harness state.

        `manifest_hash` is over the component *body hashes* only, not the version
        counters — two harness states with identical component bodies hash the
        same even if one reached that state via an edit-then-revert. Attribution
        is about which bytes produced a result, not how the harness got there.
        """
        m = {"ts": round(time.time(), 3), "components": {}}
        for c in self.list():
            m["components"][f"{c['kind']}/{c['name']}"] = {"v": c["version"], "hash": c["hash"]}
        body_hashes = {k: v["hash"] for k, v in m["components"].items()}
        m["manifest_hash"] = _hash(json.dumps(body_hashes, sort_keys=True))
        return m


# --- demo / selftest --------------------------------------------------

def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="harness-reg-"))
    try:
        reg = Registry(base=tmp)
        v1 = reg.set("prompt", "planner_system",
                     "You split tasks into bounded units.\nEach unit has a GREEN/RED check.",
                     note="initial")
        v2 = reg.set("prompt", "planner_system",
                     "You split tasks into bounded units.\nEach unit has a GREEN/RED check.\n"
                     "Prefer three small units over one large one.",
                     note="add decomposition guidance (run-54 finding)")
        reg.set("context", "compaction",
                json.dumps({"pin": ["rules", "identity", "constraints"],
                            "compress": ["episodic", "search_results"]}),
                note="type-aware, not lean-tail (concept_compaction_cliff)")
        # unchanged write is a no-op
        noop = reg.set("prompt", "planner_system", reg.get("prompt", "planner_system"))
        # revert the prompt one step
        reg.revert("prompt", "planner_system")
        reverted = reg.get("prompt", "planner_system")

        hist = reg.history("prompt", "planner_system")
        man = reg.manifest()

        checks = {
            "v1 written": v1 and v1["v"] == 1,
            "v2 written": v2 and v2["v"] == 2,
            "noop on unchanged": noop is None,
            "revert restores v1 body": reverted == v1["body"],
            "history append-only, no-op added nothing (3 entries)": len(hist) == 3,
            "revert recorded as new version pointing at v1 hash":
                hist[-1]["hash"] == v1["hash"] and hist[-1]["author"] == "revert",
            "manifest has 2 components": len(man["components"]) == 2,
            "manifest hash stable": man["manifest_hash"] == reg.manifest()["manifest_hash"],
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        print("\n  planner_system history:")
        for h in hist:
            print(f"    v{h['v']} {h['hash']} {h['author']:7} {h['note']}")
        print("\n  manifest:", json.dumps(man["components"]))
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Phase 1 harness component registry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("list")
    sub.add_parser("manifest")
    h = sub.add_parser("history"); h.add_argument("kind"); h.add_argument("name")
    d = sub.add_parser("diff"); d.add_argument("kind"); d.add_argument("name")
    rv = sub.add_parser("revert"); rv.add_argument("kind"); rv.add_argument("name")
    rv.add_argument("--steps", type=int, default=1)
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()
    reg = Registry()
    if args.cmd == "list":
        print(json.dumps(reg.list(), indent=2))
    elif args.cmd == "manifest":
        print(json.dumps(reg.manifest(), indent=2))
    elif args.cmd == "history":
        print(json.dumps(reg.history(args.kind, args.name), indent=2, ensure_ascii=False))
    elif args.cmd == "diff":
        print(reg.diff(args.kind, args.name))
    elif args.cmd == "revert":
        e = reg.revert(args.kind, args.name, steps=args.steps)
        print(f"reverted -> v{e['v']} {e['hash']}: {e['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

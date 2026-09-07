#!/usr/bin/env python3
"""Live trace recording for the autonomous research loop.

`tools/loop_adapter.py` replays *recorded history* into a trace. This records a
loop run *as it happens*. The autonomous loop (interactive continuation or the
scheduled task) wraps its work in a `LoopSession`; each meaningful action emits a
Phase 0 event, and the run ends with a validated, committed-summary trace.

Usage inside a run:

    from tools.loop_session import LoopSession

    with LoopSession(run_no=67, increment="wire live trace recording") as s:
        s.cite("2609.03035", verified=True)          # a CLAIM with the arXiv id
        s.tool("arxiv_api", "sweep last 10 days", ok=True)
        s.graph_write(nodes=(174, 175), edges=(519, 524))
        s.note("what changed and why")
        s.commit("<sha>")                            # after the git commit

On exit it closes the run STEP, writes a per-run summary next to
`runtime/observations/loop_runs/`, and (raw trace gitignored) leaves the JSONL in
`runtime/traces/`.

Pure stdlib.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace       # noqa: E402
from harness_registry import Registry                      # noqa: E402
from loop_adapter import seed_loop_harness                 # noqa: E402

RUN_SUMMARY_DIR = ROOT / "runtime" / "observations" / "loop_runs"


class LoopSession:
    def __init__(self, run_no, increment, *, language="en", trace_dir=None,
                 registry_base=None):
        self.run_no = run_no
        self.increment = increment
        self.step_id = f"run-{run_no}"
        reg = Registry(base=registry_base) if registry_base else Registry()
        # seed the loop harness on first use (no-ops if already present)
        seed_loop_harness(reg)
        self.registry = reg
        self.manifest = reg.manifest()
        self._rec = Recorder(
            run_id=f"loop-{run_no}", layer="harness", language=language,
            harness_manifest=self.manifest,
            **({"trace_dir": trace_dir} if trace_dir else {}),
        )
        self._counts = {"claims": 0, "tools": 0, "artifacts": 0, "notes": 0}
        self._cited = []
        self._graph_delta = None

    # -- lifecycle --
    def __enter__(self):
        self._rec.step("researcher", self.step_id, "open",
                       note=self.increment[:200], layer="harness")
        return self

    def __exit__(self, exc_type, exc, tb):
        ok = exc_type is None
        self._rec.step("researcher", self.step_id, "close", layer="harness",
                       note="run complete" if ok else f"aborted: {exc_type.__name__}")
        self._rec.close()
        self._write_summary(ok)
        return False

    # -- events --
    def cite(self, source_id, *, verified, purpose=""):
        """`source_id` may be an arXiv id (NNNN.NNNNN), an already-prefixed id, or
        an AlignmentForum / LessWrong post id (11-char base62). Prefixed so the
        evidence root records the source kind."""
        import re as _re
        sid = str(source_id)
        if sid.startswith(("arXiv:", "AF:", "src:")):
            aid = sid
        elif _re.fullmatch(r"\d{4}\.\d{4,5}", sid):
            aid = f"arXiv:{sid}"
        elif _re.fullmatch(r"[A-Za-z0-9]{10,14}", sid):
            aid = f"AF:{sid}"
        else:
            aid = f"src:{sid}"
        arxiv_id = aid  # keep the old local name for the body string below
        self._rec.claim(
            "researcher",
            f"{'VERIFIED' if verified else 'referenced'} finding from {aid}"
            + (f": {purpose}" if purpose else ""),
            [aid], layer="harness",
            trust="full" if verified else "low",
        )
        self._cited.append({"id": aid, "verified": bool(verified)})
        self._counts["claims"] += 1

    def tool(self, name, purpose, *, ok=True, summary=None):
        cid = self._rec.tool_call("researcher", name, purpose, layer="harness")
        self._rec.tool_result("researcher", cid, ok=ok, summary=summary, layer="harness")
        self._counts["tools"] += 1

    def graph_write(self, *, nodes=None, edges=None):
        self._rec.artifact(
            "researcher", "knowledge/graph/agentic_universe_graph.json", "write",
            layer="harness",
            delta={"nodes": list(nodes) if nodes else None,
                   "edges": list(edges) if edges else None},
        )
        self._counts["artifacts"] += 1
        d_nodes = (nodes[1] - nodes[0]) if nodes else 0
        d_edges = (edges[1] - edges[0]) if edges else 0
        self._graph_delta = {"nodes": d_nodes, "edges": d_edges}

    def note(self, text):
        self._rec.note("researcher", text, layer="harness")
        self._counts["notes"] += 1

    def commit(self, sha="pending"):
        self._rec.artifact("researcher", "git", "write", layer="harness",
                           note=f"commit {sha} for run {self.run_no}")
        self._counts["artifacts"] += 1

    # -- summary --
    def _write_summary(self, ok):
        RUN_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
        path = self._rec._path
        n_events, errors = (validate_trace(path) if path and path.exists() else (0, []))
        distinct_roots = sorted({c["id"] for c in self._cited})
        summary = {
            "run": self.run_no,
            "increment": self.increment,
            "ok": ok,
            "harness_manifest_hash": self.manifest["manifest_hash"],
            "trace_events": n_events,
            "trace_valid": not errors,
            "counts": self._counts,
            "graph_delta": self._graph_delta,  # {"nodes": d, "edges": d} or None if the run wrote no graph
            "citations": self._cited,
            "distinct_evidence_roots": distinct_roots,
            "trace_file": (str(path.relative_to(ROOT))
                           if path and ROOT in path.parents else str(path) if path else None),
            "note": "raw trace gitignored (rule 9); this summary is committed",
        }
        # per-run observability roll-up (run 226; docs/harness_anatomy_self_audit.md
        # named observability the one un-patched dependency-chain link).
        try:
            from loop_metrics import status_line
            summary["status_line"] = status_line(summary)
        except Exception:
            summary["status_line"] = None
        (RUN_SUMMARY_DIR / f"run-{self.run_no}.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # regenerate the per-consumer views (run 328) so the next run's
        # loop_conductor.pick_increment reads a corpus that includes this run.
        # Advisory + best-effort - a janitor failure never fails the run.
        try:
            from janitor import run as _janitor_run
            _janitor_run()
        except Exception:
            pass
        return summary


def _selftest():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="loop-session-"))
    try:
        s = LoopSession(run_no=999, increment="selftest run",
                        trace_dir=str(tmp / "traces"),
                        registry_base=str(tmp / "harness"))
        with s:
            s.cite("2609.03035", verified=True, purpose="probe survives eval awareness")
            s.cite("2601.99999", verified=False)
            s.tool("arxiv_api", "sweep", ok=True, summary="7 candidates")
            s.tool("graph_validate", "validate before commit", ok=True, summary="VALID")
            s.graph_write(nodes=(174, 175), edges=(519, 524))
            s.note("added one node and five edges")
            s.commit("abc1234")

        summ = json.loads((RUN_SUMMARY_DIR / "run-999.json").read_text(encoding="utf-8"))
        checks = {
            "trace valid": summ["trace_valid"],
            "events recorded": summ["trace_events"] >= 9,
            "2 citations, 1 verified": len(summ["citations"]) == 2
                and sum(c["verified"] for c in summ["citations"]) == 1,
            "distinct evidence roots deduped": summ["distinct_evidence_roots"]
                == ["arXiv:2601.99999", "arXiv:2609.03035"],
            "manifest hash present": bool(summ["harness_manifest_hash"]),
            "counts tallied": summ["counts"]["claims"] == 2 and summ["counts"]["artifacts"] == 2,
        }
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        (RUN_SUMMARY_DIR / "run-999.json").unlink()  # clean the selftest artifact
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    print("usage: loop_session.py selftest  (or import LoopSession)")
    sys.exit(2)

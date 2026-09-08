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
                 registry_base=None, bank_base=None):
        # bank_base (run 369): tests MUST pass a tmp dir. Run 368 found selftests
        # writing into the production certificate log; wiring Phase 2 one run later
        # re-created the same mixing until this override existed.
        self._bank_base = bank_base
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
        # must run while the recorder is still open - cite() writes a CLAIM event
        try:
            self._autocite_from_increment()
        except Exception:
            pass
        if self._graph_delta is None:          # explicit graph_write() always wins
            try:
                self._graph_delta = self._autodelta_vs_head()
            except Exception:
                pass
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
    _ID_IN_INCREMENT = None
    GRAPH_REL = "knowledge/graph/agentic_universe_graph.json"

    @classmethod
    def _graph_counts(cls, text):
        try:
            g = json.loads(text)
            return len(g["nodes"]), len(g["edges"])
        except Exception:
            return None

    def _autodelta_vs_head(self):
        """Derive graph_delta as (working tree - last commit), run 361.

        Same failure as the citation signal: `graph_delta` is set only by an explicit
        `graph_write()` call, and `None` meant BOTH "this run wrote no graph" and
        "this run forgot to record it". Conflating those is what let `idle_run_streak`
        climb to 27 across runs that were changing the graph every time.

        Measured against HEAD rather than an in-session snapshot, because the loop
        edits the graph before opening the session - an __enter__ snapshot would
        already contain the run's own changes and always read zero. Delta-vs-last-
        commit is also the more meaningful quantity: what THIS run changed.

        A count, never a quality claim (see the auto-cite bound above).
        """
        import subprocess
        p = ROOT / self.GRAPH_REL
        if not p.exists():
            return None
        now = self._graph_counts(p.read_text(encoding="utf-8"))
        try:
            head = subprocess.run(["git", "show", f"HEAD:{self.GRAPH_REL}"], cwd=ROOT,
                                  capture_output=True, text=True, timeout=30)
            before = self._graph_counts(head.stdout) if head.returncode == 0 else None
        except Exception:
            before = None
        if now is None or before is None:
            return None
        return {"nodes": now[0] - before[0], "edges": now[1] - before[1]}

    def _autocite_from_increment(self):
        """Auto-record any arXiv id named in the increment line as a *referenced*
        evidence root (run 361).

        Why this exists: `distinct_evidence_roots` is what `loop_metrics.run_novelty`
        and `loop_conductor._corpus_drift` read to detect a plateau. It is populated
        only by `cite()`, and across runs 334-360 the loop folded eight papers and
        called `cite()` zero times - so the novelty signal read empty all session and
        the status line said `novelty n/a` while the loop looked healthy. A metric
        that depends on the agent remembering to call a method is not a metric.

        Auto-extracted ids are recorded `verified=False`, ALWAYS. Verification is a
        claim about work actually done (fetched the abstract, checked the number);
        auto-inflating `verified_citation_fraction` from a string match would be the
        grader-gaming this project has folded five papers about. An explicit
        `cite(id, verified=True)` still wins - already-cited ids are never doubled.
        """
        import re as _re
        if type(self)._ID_IN_INCREMENT is None:
            type(self)._ID_IN_INCREMENT = _re.compile(r"(?:arXiv:)?(\d{4}\.\d{4,5})")
        already = {c["id"] for c in self._cited}
        for m in type(self)._ID_IN_INCREMENT.finditer(self.increment or ""):
            aid = f"arXiv:{m.group(1)}"
            if aid in already:
                continue
            already.add(aid)
            self.cite(aid, verified=False,
                      purpose="auto-extracted from the increment line (run 361)")

    # files a run is expected to touch. Anything else is not forbidden - it is
    # REPORTED, because "unexpected" is a judgement the reader should make, not one
    # a keyword list should make silently (the run-365 lesson).
    _EXPECTED_PREFIXES = ("knowledge/graph/", "docs/auto_sweep_", "runtime/observations/",
                          "docs/", "tools/", ".gitignore")

    def _file_footprint_vs_head(self):
        """What did this run change in the REPOSITORY, not just the graph? (run 372)

        Run 371 gave the acceptance gate a minimal-modification term for graph
        patches, and named the half it could not reach: the environment this loop
        actually modifies is the repo. WorldBench's CTS (run 370) scores completion
        AND minimal modification, and every model it tested traded one against the
        other - so measuring only "did the increment land" is measuring one side.

        Same mechanism as _autodelta_vs_head: diff the working tree against HEAD.
        DELETIONS are surfaced separately and in full, because this loop is
        append-mostly and a deleted file is the strongest disturbance signal it can
        produce - the one thing that should essentially never happen unnoticed.
        """
        import subprocess
        try:
            r = subprocess.run(["git", "diff", "--name-status", "HEAD"], cwd=ROOT,
                               capture_output=True, text=True, timeout=30)
            u = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                               cwd=ROOT, capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                return None
        except Exception:
            return None
        modified, deleted = [], []
        for line in r.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            status, p = parts[0].strip(), parts[-1].strip()
            (deleted if status.startswith("D") else modified).append(p)
        added = [p.strip() for p in u.stdout.splitlines() if p.strip()]
        touched = modified + added + deleted
        unexpected = sorted(p for p in touched
                            if not p.startswith(self._EXPECTED_PREFIXES))
        return {
            "added": len(added),
            "modified": len(modified),
            "deleted": len(deleted),
            "deleted_paths": sorted(deleted),          # in full, never truncated
            "unexpected_paths": unexpected[:20],
            "n_unexpected": len(unexpected),
        }

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
            "graph_delta": self._graph_delta,
            "file_footprint": self._file_footprint_vs_head(),   # run 372  # {"nodes": d, "edges": d} or None if the run wrote no graph
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

        # Phase 2 condensation (run 369). Built at run ~64, selftested against a
        # synthetic corpus, and never called on real data - so the experience bank
        # held 0 entries across 368 runs while janitor's staleness view reported it
        # healthy (run 367 found the vacuous pass). This is the wiring that was
        # missing, and it runs AFTER rec.close() so the trace file is flushed.
        #
        # BOUNDED BY CONSTRUCTION: prune() follows every condense, per
        # concept_unmanaged_skill_libraries_silently_drift (unbounded accumulation
        # degrades retrieval) and the run-360 memory-horizon rig (unbounded
        # retrieval is worse than none past a crossover). prune is a no-op below
        # keep_n, so this is cheap on every run.
        #
        # HONEST SCOPE: this is WRITE-ONLY today. Nothing in the live loop retrieves
        # from the bank yet - the bounded top_k path (run 357) exists and is
        # selftested but has no live caller. Populating the bank makes Phase 2 real
        # and is the prerequisite for retrieval; it does not by itself close the loop.
        try:
            if path and Path(path).exists():
                from experience_bank import ExperienceBank, condense
                _bank = (ExperienceBank(base=self._bank_base) if self._bank_base
                         else ExperienceBank())
                condense(path, _bank)
                for _coll in ("workflow", "step"):
                    _bank.prune(_coll, keep_n=200, grace=10)
        except Exception:
            pass
        return summary


def _selftest():
    import shutil
    import tempfile
    from experience_bank import ExperienceBank as _EB0
    _prod_bank_before = sum(_EB0().stats().values())
    tmp = Path(tempfile.mkdtemp(prefix="loop-session-"))
    try:
        s = LoopSession(run_no=999, increment="selftest run",
                        trace_dir=str(tmp / "traces"),
                        registry_base=str(tmp / "harness"), bank_base=str(tmp / "bank"))
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
            "an increment with no arXiv id auto-cites nothing":
                len(summ["citations"]) == 2,
        }

        # auto-cite from the increment line (run 361): the novelty signal must not
        # depend on the agent remembering to call cite().
        s2 = LoopSession(run_no=998,
                         increment="fold arXiv:2606.23075 MLAS and 2509.26354 misevolution",
                         trace_dir=str(tmp / "traces2"), registry_base=str(tmp / "harness"), bank_base=str(tmp / "bank"))
        with s2:
            pass
        a = json.loads((RUN_SUMMARY_DIR / "run-998.json").read_text(encoding="utf-8"))
        checks["auto-cite: both ids in the increment become evidence roots"] = (
            a["distinct_evidence_roots"] == ["arXiv:2509.26354", "arXiv:2606.23075"])
        checks["auto-cite: prefixed and bare arXiv ids both parse"] = (
            len(a["citations"]) == 2)
        checks["auto-cite NEVER marks a citation verified (no grader-gaming)"] = (
            all(not c["verified"] for c in a["citations"]))
        (RUN_SUMMARY_DIR / "run-998.json").unlink()

        # an explicit verified cite must win over the auto-extractor, not duplicate
        s3 = LoopSession(run_no=997, increment="fold arXiv:2606.23075 MLAS",
                         trace_dir=str(tmp / "traces3"), registry_base=str(tmp / "harness"), bank_base=str(tmp / "bank"))
        with s3:
            s3.cite("2606.23075", verified=True, purpose="abstract fetched and checked")
        b = json.loads((RUN_SUMMARY_DIR / "run-997.json").read_text(encoding="utf-8"))
        checks["auto-cite does not duplicate an explicitly cited id"] = (
            len(b["citations"]) == 1)
        checks["an explicit verified cite survives the auto-extractor"] = (
            b["citations"][0]["verified"] is True)
        checks["auto graph_delta populates instead of leaving None"] = (
            b["graph_delta"] is not None and set(b["graph_delta"]) == {"nodes", "edges"})
        (RUN_SUMMARY_DIR / "run-997.json").unlink()

        # an explicit graph_write() must win over the auto-derivation
        s4 = LoopSession(run_no=996, increment="explicit graph write",
                         trace_dir=str(tmp / "traces4"), registry_base=str(tmp / "harness"), bank_base=str(tmp / "bank"))
        with s4:
            s4.graph_write(nodes=(10, 12), edges=(40, 45))
        c = json.loads((RUN_SUMMARY_DIR / "run-996.json").read_text(encoding="utf-8"))
        # repository footprint (run 372)
        _fp = summ.get("file_footprint")
        checks["run summary carries a file_footprint"] = (
            _fp is not None and set(_fp) >= {"added", "modified", "deleted",
                                             "deleted_paths", "n_unexpected"})
        checks["deleted_paths is a list, reported in full (never truncated)"] = (
            isinstance(_fp.get("deleted_paths"), list)
            and len(_fp["deleted_paths"]) == _fp["deleted"])
        checks["expected-prefix paths are not flagged unexpected"] = (
            not any(p.startswith(LoopSession._EXPECTED_PREFIXES)
                    for p in _fp.get("unexpected_paths", [])))

        # Phase 2 wiring + test/production separation (run 369)
        from experience_bank import ExperienceBank as _EB
        checks["condense populates the bank from a real run trace"] = (
            sum(_EB(base=str(tmp / "bank")).stats().values()) > 0)
        # The invariant is "the selftest added nothing to the production bank",
        # NOT "the production bank is empty" - it legitimately fills from real runs.
        # The first version asserted emptiness and went RED the moment run 369's own
        # record landed a real entry, which is the same conflation the audit keeps
        # finding: a check that passes for the wrong reason until the subject exists.
        checks["selftests add nothing to the production bank"] = (
            sum(_EB().stats().values()) == _prod_bank_before)
        checks["an explicit graph_write survives the auto-derivation"] = (
            c["graph_delta"] == {"nodes": 2, "edges": 5})
        (RUN_SUMMARY_DIR / "run-996.json").unlink()
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

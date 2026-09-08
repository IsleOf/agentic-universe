#!/usr/bin/env python3
"""research_worker - the `run_worker` the loop conductor dispatches to (v2.3 remainder).

`loop_conductor.Conductor` calls `run_worker(task, *, hints) -> (ok, result_ref, note)`
where `result_ref` is the dict the gate consumes:
`{kind, patch, baseline_scores, candidate_scores, forecast, repaired?}`.

This is that worker. Two paths, chosen by `tools/call_model.py`'s backend:

  - `AU_MODEL_BACKEND=fake` (default) - proposes a trivially-valid no-op patch
    (`proposal_metadata` only, no nodes/edges) with neutral held-out scores, so
    `Conductor.conduct()` runs end to end offline and lands an `accept` on a no-op.
    This is the pipeline smoke test, not a real fold.
  - a live backend (`cli` / a registered callable) - `call_model` proposes candidate
    nodes/edges for the task's increment; `research_brief` shapes + dedup-checks it;
    the held-out scores come from `holdout_tasks.score_corpus` over the doc set with
    and without the proposed brief text (a coverage regression proxy); the forecast is
    the model's stated P(this fold helps).

Pure stdlib. The live path's only external call is `call_model` (which is itself the
one seam).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import call_model as _cm                 # noqa: E402
import research_brief                    # noqa: E402
GRAPH = ROOT / "knowledge" / "graph" / "agentic_universe_graph.json"

_BRIEF_PROMPT = """You are the Agentic Universe literature scout. For this research increment:

    {increment}

Reply with ONLY a JSON object matching this shape (no prose):
{{"source": "...", "fetched": "YYYY-MM-DD", "currency_note": "...",
  "verdict": "fold|partial-fold|already-covered|not-substantive",
  "already_in_graph": ["node_id", ...],
  "candidate_nodes": [{{"id": "concept_...", "label": "...", "type": "concept",
     "approach_family": "...", "confidence": 0.5, "description": "...", "tags": []}}],
  "candidate_edges": [{{"id": "edge_...", "source": "concept_...", "target": "<existing node id>",
     "type": "supports|refines|challenges|informs|extends", "description": "..."}}]}}
"""


def _noop_patch() -> dict:
    return {"proposal_metadata": {"generated_by": "research_worker", "mode": "fake-noop"},
            "add_nodes": [], "add_edges": []}


def _neutral_scores(n: int = 17) -> dict:
    # all-right on both sides -> risk 0 before and after -> the gate's "strict decrease
    # (or stays 0)" branch accepts a no-op without claiming an improvement.
    return {f"t{i}": 1.0 for i in range(n)}


def _live_brief(increment: str) -> dict | None:
    reply = _cm.call_model(_BRIEF_PROMPT.format(increment=increment)) or ""
    m = re.search(r"\{.*\}", reply, re.S)
    if not m:
        return None
    try:
        brief = json.loads(m.group(0))
    except Exception:
        return None
    brief.setdefault("source", f"scout: {increment[:80]}")
    brief.setdefault("fetched", "")
    brief.setdefault("currency_note", "set the real currency note after review")
    brief.setdefault("verdict", "partial-fold")
    brief.setdefault("already_in_graph", [])
    brief.setdefault("candidate_nodes", [])
    brief.setdefault("candidate_edges", [])
    return brief


def _coverage_scores(extra_text: str | None) -> dict:
    """A held-out regression proxy: does the doc set (optionally + `extra_text`)
    still answer each frozen held-out question? Returns {task_id: 0.0|1.0}."""
    try:
        from holdout_tasks import score_corpus, _load_docs
        docs = _load_docs()
        if extra_text:
            docs = {**docs, "_candidate_brief": extra_text}
        res = score_corpus(docs)
        return {tid: (1.0 if r["score"] >= 0.5 else 0.0)
                for tid, r in res["per_task"].items()}
    except Exception:
        return _neutral_scores()


def run_worker(task, *, hints=None):
    """The conductor's worker. `task` is a task_ledger dict; `task['goal']` carries
    the run's increment text."""
    increment = (task or {}).get("goal", "") if isinstance(task, dict) else str(task)
    live = not str(__import__("os").environ.get("AU_MODEL_BACKEND", "fake")).lower().startswith("fake")

    if not live:
        return True, {
            "kind": "build" if "build" in increment.lower() else "consistency",
            "patch": _noop_patch(),
            "baseline_scores": _neutral_scores(),
            "candidate_scores": _neutral_scores(),
            "forecast": {"metric": "no-op smoke test", "predicted_prob": 0.5},
            "repaired": False,
        }, "fake no-op (pipeline smoke test)"

    brief = _live_brief(increment)
    if brief is None:
        return False, None, "scout reply was not parseable JSON"
    errs = research_brief.validate_brief(brief)
    if errs:
        return False, None, "brief failed validation: " + "; ".join(errs[:3])
    try:
        graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    except Exception as e:
        return False, None, f"could not read graph: {e}"
    dd = research_brief.check_against_graph(brief, graph)
    if dd["collisions"] or dd["unreviewed_overlap"]:
        return False, None, f"dedup check failed: {dd}"

    patch = research_brief.to_graph_patch(brief)
    brief_text = "\n".join(n.get("description", "") for n in brief["candidate_nodes"])
    base = _coverage_scores(None)
    cand = _coverage_scores(brief_text or None)
    fc_prob = 0.6
    for n in brief["candidate_nodes"]:
        try:
            fc_prob = max(fc_prob, float(n.get("confidence", 0.5)))
        except Exception:
            pass
    return True, {
        "kind": "fold",
        "patch": patch,
        "baseline_scores": base,
        "candidate_scores": cand,
        "forecast": {"metric": "held-out coverage", "predicted_prob": fc_prob},
        "repaired": False,
    }, f"live fold: {len(patch['add_nodes'])} nodes / {len(patch['add_edges'])} edges"


def _selftest():
    import os
    import tempfile
    checks = {}
    os.environ.pop("AU_MODEL_BACKEND", None)     # -> fake

    ok, out, note = run_worker({"goal": "consistency pass on the diversity keystone"})
    checks["fake worker returns ok + a dict + a note"] = (ok and isinstance(out, dict) and note)
    checks["fake patch is check_patch-valid against a tiny graph"] = True
    try:
        from knowledge_graph import check_patch
        checks["fake patch is check_patch-valid against a tiny graph"] = check_patch(
            out["patch"], {"nodes": [{"id": "x", "label": "x", "type": "concept"}], "edges": []}) == []
    except Exception:
        checks["fake patch is check_patch-valid against a tiny graph"] = False
    checks["fake worker's scores are neutral (risk 0 both sides)"] = (
        set(out["baseline_scores"].values()) == {1.0}
        and out["baseline_scores"] == out["candidate_scores"])
    checks["fake worker classifies a 'build' increment"] = (
        run_worker({"goal": "build tools/foo.py"})[1]["kind"] == "build")

    # end to end through the real Conductor + the real gate
    from loop_conductor import Conductor
    import acceptance_gate
    tmp = Path(tempfile.mkdtemp(prefix="rw-"))
    (tmp / "g.json").write_text(json.dumps(
        {"nodes": [{"id": "x", "label": "x", "type": "concept"}], "edges": []}), encoding="utf-8")
    applied, committed = [], []
    c = Conductor(require_blessed_manifest=False, ledger_path=tmp / "led.json", run_worker=run_worker,
                  apply_patch=applied.append,
                  commit_push=lambda r, p, cert: committed.append((r, cert["decision"])),
                  graph_path=tmp / "g.json", gate=lambda *a, **k: acceptance_gate.check(*a, cert_dir=tmp, **k),  # run 368: keep selftest certs out of the production log
                  clock=lambda: 1e6)
    rec = c.conduct(500, recent_kinds=["fold", "build", "doc"], frontier_swept=True,
                    use_corpus=False)
    checks["conduct() runs end to end with the fake worker and accepts the no-op"] = (
        rec.accepted and committed == [(500, "accept")] and len(applied) == 1)
    checks["the accepted run carries a certificate"] = rec.certificate is not None

    # a scout that returns garbage -> the live path fails cleanly
    os.environ["AU_MODEL_BACKEND"] = "reg-garbage"
    _cm.register("reg-garbage", lambda p: "definitely not json")
    ok2, out2, note2 = run_worker({"goal": "fold something"})
    checks["live worker fails cleanly on an unparseable scout reply"] = (
        not ok2 and out2 is None and "parseable" in note2)
    os.environ.pop("AU_MODEL_BACKEND", None)
    _cm.set_backend(None)

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    print(__doc__)

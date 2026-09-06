#!/usr/bin/env python3
"""Phase 2 — the experience bank.

`docs/self_improving_harness_plan.md` §4 Phase 2: condense traces into two stores
kept deliberately apart —

  workflow-level : what shape of approach works for a task class; retrieved at
                   planning.
  step-level     : what specific move was wrong here; retrieved at failure.

Merging them yields a store that is wrong at both moments, so they are separate
collections with separate retrieval keys.

Three `challenges` edges land on this component; the plan's mitigations, all
implemented here:

- `emergent_information_cascades` / `emergent_stale_belief_propagation`
  (re-verify at ~23%): every entry is stamped with the `source_manifest` (the
  harness state it was derived under). `stale(current_manifest)` returns the
  entries whose source has since changed — they must be re-verified before reuse.
- `concept_compaction_cliff` (condensation drops normative content): the raw
  source events are retained on every entry (`source_events`); nothing exists
  only in condensed form.
- `concept_epistemic_sybil_collapse` / `pattern_evidential_ancestry_tracking`
  (run 52): a pattern condensed from N agents that shared one trace is one
  observation, not N. Entries record `distinct_evidence_roots`, never an agent
  count, and `condense()` dedupes CLAIM events by their `evidence_roots`.

Retention (run 175, `concept_naive_trajectory_accumulation_already_helps`,
arXiv:2505.00234): naive accumulation of successes already beats a model upgrade,
and *exemplar-level curation* pushes it further. `record_use(collection, id,
helped)` updates an entry's `used`/`helped` after a retrieval's outcome is known;
`utility_score` is a Laplace-smoothed success rate (unused = 0.5 neutral prior);
`prune(collection, keep_n, grace=5)` evicts the lowest-utility entries beyond
`keep_n`, protecting the `grace` most recent and keeping every survivor's raw
`source_events`.

Pure stdlib. Reads Phase 0 traces (`tools/trace_substrate.py` schema).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = ROOT / "runtime" / "observations" / "experience_bank"

COLLECTIONS = ("workflow", "step")


def _hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode("utf-8")).hexdigest()[:16]


class ExperienceBank:
    def __init__(self, base=BANK_DIR):
        self.base = Path(base)
        for c in COLLECTIONS:
            (self.base / c).mkdir(parents=True, exist_ok=True)

    def _path(self, collection, entry_id):
        if collection not in COLLECTIONS:
            raise ValueError(f"unknown collection {collection!r}; expected {COLLECTIONS}")
        return self.base / collection / f"{entry_id}.json"

    # -- write --
    def add(self, collection, pattern, *, retrieval_key, source_trace,
            source_manifest, source_events, distinct_evidence_roots,
            token_cost=None, note=""):
        """Add a condensed entry. `source_events` is the raw slice it was derived
        from — retained so nothing is only-condensed (`concept_compaction_cliff`).
        """
        entry = {
            "id": None,
            "collection": collection,
            "pattern": pattern,
            "retrieval_key": retrieval_key,
            "source_trace": source_trace,
            "source_manifest": source_manifest,
            "source_events": source_events,
            "distinct_evidence_roots": distinct_evidence_roots,
            "token_cost": token_cost or {},
            "note": note,
            "ts": round(time.time(), 3),
            # utility-weighted retention (concept_naive_trajectory_accumulation_already_helps,
            # arXiv:2505.00234, run 175): retain an entry by its EMPIRICAL usefulness
            # as an in-context example, not recency or count. `helped`/`used` are
            # updated by record_use() after a retrieval's outcome is known.
            "used": 0,
            "helped": 0,
        }
        entry["id"] = _hash({"c": collection, "k": retrieval_key, "p": pattern})
        self._path(collection, entry["id"]).write_text(
            json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return entry

    # -- read --
    def _all(self, collection):
        out = []
        for p in sorted((self.base / collection).glob("*.json")):
            out.append(json.loads(p.read_text(encoding="utf-8")))
        return out

    def for_planning(self, task_signature):
        """Workflow-level entries whose retrieval key is a substring match."""
        return [e for e in self._all("workflow")
                if task_signature in e["retrieval_key"] or e["retrieval_key"] in task_signature]

    def for_failure(self, error_signature):
        """Step-level entries matching an error signature."""
        return [e for e in self._all("step")
                if error_signature in e["retrieval_key"] or e["retrieval_key"] in error_signature]

    @staticmethod
    def utility_score(entry):
        """Empirical usefulness of an entry as an in-context example: a smoothed
        success rate over its uses. An unused entry gets the neutral prior 0.5 so
        it is neither promoted nor evicted before it has been tried."""
        used = entry.get("used", 0)
        if not used:
            return 0.5
        return (entry.get("helped", 0) + 1) / (used + 2)  # Laplace-smoothed

    def record_use(self, collection, entry_id, helped):
        """Update an entry's utility after a retrieval whose outcome is known.
        `helped` is a bool: did having this entry in context precede a success?"""
        p = self._path(collection, entry_id)
        if not p.exists():
            raise KeyError(entry_id)
        e = json.loads(p.read_text(encoding="utf-8"))
        e["used"] = e.get("used", 0) + 1
        e["helped"] = e.get("helped", 0) + (1 if helped else 0)
        p.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return e

    def prune(self, collection, keep_n, *, grace=5):
        """Evict the lowest-utility entries beyond `keep_n`, keeping the raw
        source_events of the survivors intact. The `grace` most recent entries are
        never pruned (they have not had a fair chance to prove utility). Returns
        the ids evicted. Naive accumulation already helps (arXiv:2505.00234); this
        is the *exemplar-level curation* that pushed it further."""
        entries = self._all(collection)
        if len(entries) <= keep_n:
            return []
        by_recency = sorted(entries, key=lambda e: e.get("ts", 0), reverse=True)
        protected = {e["id"] for e in by_recency[:grace]}
        ranked = sorted(entries, key=lambda e: (self.utility_score(e), e.get("ts", 0)), reverse=True)
        keep = {e["id"] for e in ranked[:keep_n]} | protected
        evicted = []
        for e in entries:
            if e["id"] not in keep:
                self._path(collection, e["id"]).unlink()
                evicted.append(e["id"])
        return evicted

    def stale(self, current_manifest):
        """Every entry whose source harness state differs from the current one.
        These must be re-verified before reuse (`emergent_stale_belief_propagation`).
        """
        out = []
        for c in COLLECTIONS:
            for e in self._all(c):
                if e["source_manifest"] != current_manifest:
                    out.append({"id": e["id"], "collection": c,
                                "retrieval_key": e["retrieval_key"],
                                "was": e["source_manifest"], "now": current_manifest})
        return out

    def stats(self):
        return {c: len(self._all(c)) for c in COLLECTIONS}


# --- condensation --------------------------------------------------------

def load_events(path):
    with Path(path).open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def condense(trace_path, bank: ExperienceBank):
    """Read one trace, propose bank entries. Conservative: one workflow entry per
    closed STEP, one step entry per non-ok TOOL_RESULT followed by a retry.

    CLAIM events are deduped by `evidence_roots` — this is where
    `pattern_evidential_ancestry_tracking` bites: three workers that each read
    the same document and claimed a result count as one distinct source.
    """
    events = load_events(trace_path)
    header = events[0] if events and events[0].get("kind") == "NOTE" else {}
    manifest = header.get("harness_manifest", {}).get("manifest_hash", "unknown")
    trace_id = events[0].get("run_id", "unknown") if events else "unknown"

    added = []

    # -- evidence-root dedup over CLAIM events --
    roots_seen = set()
    claims_by_actor = defaultdict(list)
    for ev in events:
        if ev.get("kind") == "CLAIM":
            claims_by_actor[ev["actor"]].append(ev)
            for r in ev.get("evidence_roots", []):
                roots_seen.add(r)
    distinct_roots = sorted(roots_seen)

    # -- token cost roll-up --
    total_cost = {"in": 0, "out": 0}
    for ev in events:
        tc = ev.get("token_cost") or {}
        total_cost["in"] += tc.get("in", 0)
        total_cost["out"] += tc.get("out", 0)

    # -- workflow entries: one per closed STEP --
    open_steps = {}
    for ev in events:
        if ev.get("kind") != "STEP":
            continue
        if ev["phase"] == "open":
            open_steps[ev["step_id"]] = ev
        elif ev["phase"] == "close" and ev["step_id"] in open_steps:
            opened = open_steps.pop(ev["step_id"])
            key = (opened.get("note") or opened["step_id"]).split(" for ")[0].strip().lower()
            n_msgs = sum(1 for e in events if e.get("kind") == "MESSAGE")
            pattern = (f"task class '{key}': closed in {n_msgs} inter-agent messages across "
                       f"{len(claims_by_actor)} acting agents over {len(distinct_roots)} distinct "
                       f"evidence source(s); outcome note: {ev.get('note', 'n/a')}")
            added.append(bank.add(
                "workflow", pattern,
                retrieval_key=key,
                source_trace=trace_id,
                source_manifest=manifest,
                source_events=[opened, ev],
                distinct_evidence_roots=distinct_roots,
                token_cost=dict(total_cost),
                note="condensed from a closed STEP",
            ))

    # -- step entries: a failed tool result that was retried --
    calls = {e["call_id"]: e for e in events if e.get("kind") == "TOOL_CALL"}
    results = [e for e in events if e.get("kind") == "TOOL_RESULT"]
    for i, res in enumerate(results):
        if res.get("ok") is False:
            call = calls.get(res["call_id"], {})
            retried = any(r for r in results[i + 1:]
                          if calls.get(r["call_id"], {}).get("actor") == res["actor"])
            key = f"tool:{call.get('tool', '?')} failed"
            pattern = (f"{call.get('tool', '?')} call by {res['actor']} for "
                       f"'{call.get('declared_purpose', '?')}' failed"
                       + ("; a retry by the same actor followed" if retried else "; not retried"))
            added.append(bank.add(
                "step", pattern,
                retrieval_key=key,
                source_trace=trace_id,
                source_manifest=manifest,
                source_events=[call, res],
                distinct_evidence_roots=distinct_roots,
                note="condensed from a non-ok TOOL_RESULT",
            ))

    # -- a critique that led to a correction is a step-level lesson --
    # order by list position, not timestamp — consecutive events can share a ts
    for idx, m in enumerate(events):
        if m.get("kind") == "MESSAGE" and m.get("content_class") == "critique":
            follow_fix = any(
                e.get("kind") in ("TOOL_CALL", "CLAIM") and e.get("actor") == m["receiver"]
                for e in events[idx + 1:]
            )
            if follow_fix:
                key = "critique:acted-on"
                pattern = (f"critique from {m['sender']} to {m['receiver']} "
                           f"('{m.get('declared_purpose', '?')}') was followed by a corrective "
                           f"action from {m['receiver']}")
                added.append(bank.add(
                    "step", pattern,
                    retrieval_key=key,
                    source_trace=trace_id,
                    source_manifest=manifest,
                    source_events=[m],
                    distinct_evidence_roots=distinct_roots,
                    note="condensed from a critique -> correction sequence",
                ))

    return added


# --- selftest -----------------------------------------------------------

def _selftest():
    import io
    import shutil
    import tempfile
    sys.path.insert(0, str(ROOT / "tools"))
    from harness_registry import Registry
    from harness_demo import seed_harness, run_scenario

    tmp = Path(tempfile.mkdtemp(prefix="exp-bank-"))
    try:
        reg = Registry(base=tmp / "harness")
        seed_harness(reg)
        manifest = reg.manifest()["manifest_hash"]

        buf = io.StringIO()
        run_scenario(reg, buf)
        trace = tmp / "demo.jsonl"
        trace.write_text(buf.getvalue(), encoding="utf-8")

        bank = ExperienceBank(base=tmp / "bank")
        added = condense(trace, bank)

        wf = bank.for_planning("vat determination for invoice batch 7")
        # the demo scenario has a critique -> correction on worker-2
        step_hits = bank.for_failure("critique:acted-on")
        stale_now = bank.stale(manifest)
        stale_after_edit = None
        reg.set("prompt", "verifier_system", "changed", note="edit")
        stale_after_edit = bank.stale(reg.manifest()["manifest_hash"])

        # ancestry: the demo has 2 workers, each with its own evidence root
        # (invoice-7a.pdf, invoice-7b.pdf) -> 2 distinct roots, not "4 claims"
        any_wf = wf[0] if wf else {}
        checks = {
            "condense produced entries": len(added) >= 2,
            "workflow + step collections both populated": bank.stats()["workflow"] >= 1 and bank.stats()["step"] >= 1,
            "workflow entry retrievable by task signature": len(wf) == 1,
            "step lesson retrievable (critique acted on)": len(step_hits) >= 1,
            "entry records distinct evidence roots, not agent count":
                any_wf.get("distinct_evidence_roots") == ["invoice-7a.pdf", "invoice-7b.pdf"],
            "raw source_events retained on every entry":
                all(e.get("source_events") for e in added),
            "nothing stale against its own source manifest": stale_now == [],
            "everything stale after a harness edit": len(stale_after_edit) == len(added),
        }

        # utility-weighted retention (run 175)
        ub = ExperienceBank(base=tmp / "ubank")
        mk = lambda k, t: ub.add("workflow", f"pattern {k}", retrieval_key=k, source_trace="t",
                                 source_manifest="m", source_events=[{"seq": 0}],
                                 distinct_evidence_roots=[], note="")
        e_good = mk("good", 0); e_bad = mk("bad", 0); e_new = mk("new", 0)
        for eid, ts in ((e_good["id"], 100), (e_bad["id"], 101), (e_new["id"], 102)):
            _p = ub._path("workflow", eid); _e = json.loads(_p.read_text()); _e["ts"] = ts
            _p.write_text(json.dumps(_e, indent=2) + "\n", encoding="utf-8")
        for _ in range(6):
            ub.record_use("workflow", e_good["id"], helped=True)
            ub.record_use("workflow", e_bad["id"], helped=False)
        checks["utility_score: proven-useful > neutral prior > proven-useless"] = (
            ub.utility_score(json.loads(ub._path("workflow", e_good["id"]).read_text())) > 0.5
            > ub.utility_score(json.loads(ub._path("workflow", e_bad["id"]).read_text())))
        checks["utility_score: an unused entry gets the 0.5 neutral prior"] = (
            ub.utility_score(json.loads(ub._path("workflow", e_new["id"]).read_text())) == 0.5)
        # add filler so there is something to prune, then keep the best 1 (+ grace).
        # give fillers strictly-increasing ts so "most recent" is well-defined.
        fillers = [mk(f"f{i}", 0) for i in range(4)]
        for j, f in enumerate(fillers):
            fp = ub._path("workflow", f["id"])
            fe = json.loads(fp.read_text()); fe["ts"] = 200 + j
            fp.write_text(json.dumps(fe, indent=2) + "\n", encoding="utf-8")
            for _ in range(3):
                ub.record_use("workflow", f["id"], helped=False)
        evicted = ub.prune("workflow", keep_n=1, grace=2)
        surviving = {e["id"] for e in ub._all("workflow")}
        checks["prune keeps the highest-utility entry"] = e_good["id"] in surviving
        checks["prune evicts a proven-useless entry"] = e_bad["id"] in evicted
        checks["prune protects the grace-window most recent"] = (
            fillers[-1]["id"] in surviving and fillers[-2]["id"] in surviving)
        checks["prune keeps raw source_events on survivors"] = all(
            e.get("source_events") for e in ub._all("workflow"))
        checks["prune is a no-op below keep_n"] = ExperienceBank(base=tmp / "tiny").prune("workflow", 10) == []
        for k, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {k}")
        print("\n  bank stats:", json.dumps(bank.stats()))
        if wf:
            print("  workflow pattern:", wf[0]["pattern"])
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description="Phase 2 experience bank.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    c = sub.add_parser("condense"); c.add_argument("trace")
    s = sub.add_parser("stats")
    st = sub.add_parser("stale"); st.add_argument("manifest_hash")
    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()
    bank = ExperienceBank()
    if args.cmd == "condense":
        added = condense(args.trace, bank)
        print(f"added {len(added)} entries")
        for e in added:
            print(f"  [{e['collection']}] {e['retrieval_key']}: {e['pattern'][:90]}")
    elif args.cmd == "stats":
        print(json.dumps(bank.stats(), indent=2))
    elif args.cmd == "stale":
        for row in bank.stale(args.manifest_hash):
            print(json.dumps(row))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

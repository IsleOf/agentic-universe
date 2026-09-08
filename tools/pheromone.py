#!/usr/bin/env python3
"""The pheromone annotation layer — a coordinator-free stigmergic substrate.

`docs/swarm-substrate-prototype.md` §2 (run 389). A **pheromone annotation** is a
small row any agent can write and any agent can read, with no central coordinator,
that says: *this artifact / task / direction is worth N to me, I am M confident, and
this opinion should fade.* Agents coordinate by reading the aggregate signal over a
`task_ref` and deciding where to act — the "pheromone field" of SwarmSys
(arXiv:2510.10047) and `concept_orchestratorless_flock...`, made explicit and
time-decayed.

Same discipline as `task_ledger.py` / `fractal_flock.py`: pure stdlib (sqlite3 is
stdlib), no model calls. The generative work is the caller's; this is only the
substrate.

TRUST BOUNDARY (run 402, stated explicitly so the guarantees downstream are legible).
The `agent` field on an annotation is CALLER-SUPPLIED AND UNAUTHENTICATED. This
module does not verify that the writer is who they say they are, and every
identity-keyed guard built on it (gate rotation, no-self-review, the anti-ping-pong
window, the reputation ledger, correlation de-duplication) is therefore only as
strong as the assumption that agents in the fleet do not impersonate each other.
That assumption is reasonable for a fleet one operator controls and it is the wrong
assumption for an open swarm. Closing it needs one of: signed writes (an
operator-held key per agent), a capability token minted by the pool (executor_pool
already has mint_token / redeem_token), or an external identity provider. Until
then: `_norm_agent` collapses accidental id variation, `supersedes` is honoured
within one (claimed) author only, and gate quorum excludes content contributors and
returns its counted ids for audit - but a determined impersonator is out of scope.

THREE THINGS THIS GETS RIGHT THAT THE FRAMEWORKS DO NOT (see the design doc):

  1. DECAY IS AN EXPLICIT CLOCK, not "other profiles evolve". SwarmSys leaves
     evaporation implicit, which only works when the population churns fast; a 2-15
     agent fleet can sit idle. Here:
         effective_utility = utility * confidence * 0.5 ** (age / half_life_s)
     and the row hard-expires (and becomes reap-eligible) once age > ttl_s.

  2. THE AGGREGATE THRESHOLD SCALES WITH THE NUMBER OF CONTRIBUTORS. A fixed
     "act if signal > 0.7" silently becomes "act if >= 4 mildly-positive agents"
     as the fleet grows. `read()` returns `n_contributors` and a
     `suggested_threshold` derived from it, never a bare constant. This is the
     run-385 lesson (`concept_an_absolute_threshold_on_a_pool_sized_sum...`)
     applied to a new component from birth rather than retrofitted.

  3. CORRELATED AGENTS ARE NOT INDEPENDENT VOTES. Agents sharing a base model
     produce correlated annotations (~0.7, arXiv:2609.01873). Correlation widens
     the NULL band on the aggregate; it does NOT reduce the signal sum. `read()`
     reports a `noise_band` that inflates with an assumed correlation, and the
     `suggested_threshold` sits above it — but the raw `signal` is the honest
     decayed sum, undeflated.

Schema (one table, `pheromone`):
  id           text pk     client-generated uuid; writes idempotent on id
  task_ref     text        the task / artifact node / direction this is about
  kind         text        utility | warning | claim | bid | done   (unknown kinds
                           are STORED and surfaced, never dropped — the run-365 rule)
  agent        text        contributing agent id (never trusted as authority)
  utility      real        signed value estimate in [-1, 1]
  confidence   real        agent's self-assessed reliability in [0, 1]
  created_at   real        epoch seconds
  half_life_s  real        seconds for effective_utility to halve
  ttl_s        real        hard expiry; row ignored (then reaped) once age > ttl_s
  evidence     text        optional json: links to artifacts / prior annotations
  supersedes   text        optional uuid: replaces an earlier annotation by the
                           same agent on the same task_ref

Usage:
    pf = Pheromone(path)
    pf.annotate("task-42", "utility", 0.6, 0.8, agent="a3")
    pf.read("task-42")     -> {"signal", "n_contributors", "annotations",
                               "corr_estimate", "noise_band", "suggested_threshold"}
    pf.board(limit=20)     -> [task_refs ranked by |signal|, freshest first]
    pf.reap()              -> int  (rows deleted; the only privileged operation)

PORTABILITY CLASS (run 413, arXiv:2609.05339): the NUMERIC columns are fixed-schema
and portable (utility, confidence, half_life_s, ttl_s, created_at). The `evidence`
JSON blob is MODEL-COUPLED free text - a note one model wrote that another model
may read differently; in that paper model-compressed notes shifted accuracy
+9.9 / -13.3 pp across a model upgrade. So (1) nothing durable should live only in
`evidence` - it is disposable, and the clock decay already enforces that; (2)
`register_health()` reads `evidence` text, so its English-function-word baseline
must be re-established after a model/writer swap before a `drifting` flag is
trustworthy.

CLI: annotate / read / board / reap / selftest.  Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "runtime" / "observations" / "pheromone.db"

KNOWN_KINDS = ("utility", "warning", "claim", "bid", "done", "ask")
# numeric columns are fixed-schema/portable; the `evidence` blob is model-coupled
# free text that does not survive a model swap (run 413, arXiv:2609.05339).
PORTABILITY_CLASS = {"numeric_columns": "fixed-schema", "evidence": "model-coupled"}
DEFAULT_HALF_LIFE_S = 3600.0
DEFAULT_TTL_MULT = 6.0            # ttl defaults to 6 half-lives if not given

# Benign-signal noise model for the aggregate threshold. Deliberately explicit and
# reported in every read() — a threshold computed from an assumption the caller
# cannot see is the run-386 defect.
_BENIGN_MEAN = 0.05              # per-agent |utility*confidence| when nobody means anything
_BENIGN_SD = 0.06
_DEFAULT_CORR = 0.7             # assumed inter-agent correlation (shared base model)
_THRESHOLD_Z = 3.0             # suggested_threshold sits this many SD above the benign sum


def _now():
    return round(time.time(), 3)


def _norm_agent(aid):
    """Canonical agent id: trimmed and casefolded. Run 400's red-team pass found
    'alice', 'alice ', 'Alice' and 'alice\\t' were treated as four different agents,
    letting an author gate their own artifact under a variant id. Normalising at
    every author comparison closes that without a global identity registry."""
    return str(aid).strip().casefold()


class Pheromone:
    def __init__(self, path=DEFAULT_PATH, *, benign_mean=_BENIGN_MEAN,
                 benign_sd=_BENIGN_SD, assumed_corr=_DEFAULT_CORR):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.benign_mean = benign_mean
        self.benign_sd = benign_sd
        self.assumed_corr = assumed_corr
        self._db = sqlite3.connect(str(self.path))
        self._db.row_factory = sqlite3.Row
        try:
            self._db.execute("PRAGMA journal_mode=WAL")   # 2-15 concurrent writers
        except sqlite3.OperationalError:
            pass
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS pheromone (
                id          TEXT PRIMARY KEY,
                task_ref    TEXT NOT NULL,
                kind        TEXT NOT NULL,
                agent       TEXT NOT NULL,
                utility     REAL NOT NULL,
                confidence  REAL NOT NULL,
                created_at  REAL NOT NULL,
                half_life_s REAL NOT NULL,
                ttl_s       REAL NOT NULL,
                evidence    TEXT,
                supersedes  TEXT
            );
            CREATE INDEX IF NOT EXISTS pher_task ON pheromone(task_ref);
            CREATE INDEX IF NOT EXISTS pher_created ON pheromone(created_at);
            """
        )
        self._db.commit()

    # -- write: the only mutation, monotonic (append + supersede) ---------------
    def annotate(self, task_ref, kind, utility, confidence, *, agent,
                 half_life_s=DEFAULT_HALF_LIFE_S, ttl_s=None, evidence=None,
                 supersedes=None, _id=None, _at=None):
        """Write one annotation. Returns its id. Idempotent on id.

        `kind` outside KNOWN_KINDS is stored, not rejected — an unknown kind is a
        judgement for the reader, not for this function (the run-365 rule).
        """
        if not task_ref or not agent:
            raise ValueError("task_ref and agent are required")
        u = max(-1.0, min(1.0, float(utility)))
        c = max(0.0, min(1.0, float(confidence)))
        hl = float(half_life_s)
        if hl <= 0:
            raise ValueError("half_life_s must be positive")
        ttl = float(ttl_s) if ttl_s is not None else DEFAULT_TTL_MULT * hl
        aid = _id or uuid.uuid4().hex
        at = _now() if _at is None else float(_at)
        ev = json.dumps(evidence) if evidence is not None else None
        self._db.execute(
            "INSERT OR REPLACE INTO pheromone "
            "(id, task_ref, kind, agent, utility, confidence, created_at, "
            " half_life_s, ttl_s, evidence, supersedes) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (aid, task_ref, str(kind), str(agent), u, c, at, hl, ttl, ev, supersedes),
        )
        self._db.commit()
        return aid

    def warn(self, task_ref, *, agent, strength=0.5, confidence=0.4, names_cohort=None,
             ttl_s=1800.0, note=None, _at=None, _id=None):
        """Post a cheap SUSPICION warning — the low-friction counterpart to a full
        audit. Run 398 (probe_annotation_contagion) measured that the residual risk
        from a boosted-exploit annotation is the DETECTION LAG: every round before
        the honest cohort posts, the board steers agents wrong. This method exists to
        make "flag it now, on suspicion, then audit" a one-liner:

            pf.warn("exploit-task", agent="h3", note="proof skips a lemma?")

        Defaults are deliberately weak — confidence 0.4, a 30-minute TTL — so a
        suspicion that is not followed up decays on its own and a wrong flag costs
        little. An agent who then completes an audit posts a full-strength
        kind=warning (higher confidence, longer TTL) that supersedes nothing but
        carries the evidence.
        """
        return self.annotate(
            task_ref, "warning", utility=-abs(strength), confidence=confidence,
            agent=agent, half_life_s=min(ttl_s / 2, DEFAULT_HALF_LIFE_S), ttl_s=ttl_s,
            evidence={"suspicion": True, "note": note, "names_cohort": names_cohort},
            _at=_at, _id=_id)

    def ask(self, task_ref, *, agent, gap, options=None, ttl_s=7200.0, _at=None, _id=None):
        """Post a CLARIFICATION request - a `kind=ask` annotation - when a task_ref is
        under-specified for the work it needs (run 424, arXiv:2609.05258). `gap` names
        the missing thing ('objective unspecified', 'which auth flow?'); `options` is
        an optional list for a choice-based question. It carries NO utility (0.0) - an
        open ask does not steer the board toward or away from the task, it flags that
        acting now would be a silent assumption. `open_asks(task_ref)` lists the
        unanswered ones; a downstream gate / agent treats a task with open asks as
        'clarify before finalising'. Default 2h TTL: an unanswered ask decays, it does
        not block forever."""
        return self.annotate(
            task_ref, "ask", utility=0.0, confidence=0.6, agent=agent,
            half_life_s=min(ttl_s / 2, DEFAULT_HALF_LIFE_S), ttl_s=ttl_s,
            evidence={"gap": gap, "options": list(options) if options else None,
                      "answered": False},
            _at=_at, _id=_id)

    def answer_ask(self, ask_id, *, task_ref, agent, answer, _at=None):
        """Resolve an open ask by superseding it with an answered copy (same author
        boundary as any supersede - but an ASK is answerable by ANYONE, so this posts
        a fresh `kind=ask` marked answered rather than superseding)."""
        return self.annotate(
            task_ref, "ask", utility=0.0, confidence=0.9, agent=agent,
            evidence={"answers": ask_id, "answer": answer, "answered": True},
            _at=_at)

    def open_asks(self, task_ref, *, at=None):
        """Live `kind=ask` annotations whose gap has not been answered."""
        live, _ = self._live_rows(task_ref, at=at)
        asks = [r for r, _ in live if r["kind"] == "ask"]
        answered_ids = {json.loads(r["evidence"] or "{}").get("answers")
                        for r in asks if r["evidence"]}
        return [{"id": r["id"], "agent": r["agent"],
                 **(json.loads(r["evidence"]) if r["evidence"] else {})}
                for r in asks
                if r["evidence"] and not json.loads(r["evidence"]).get("answered")
                and r["id"] not in answered_ids]

    # -- read: no lock, no turn, no permission check ---------------------------
    def _live_rows(self, task_ref, *, at=None):
        now = _now() if at is None else at
        rows = self._db.execute(
            "SELECT * FROM pheromone WHERE task_ref = ?", (task_ref,)
        ).fetchall()
        by_id = {r["id"]: r for r in rows}
        # honour `supersedes` ONLY within one author. Run 400's red-team pass found
        # a cheater could pass a whistleblower's warning id as `supersedes` and
        # suppress it - `supersedes` is "I changed MY mind", never "I delete yours".
        superseded = {
            r["supersedes"] for r in rows
            if r["supersedes"] and r["supersedes"] in by_id
            and _norm_agent(by_id[r["supersedes"]]["agent"]) == _norm_agent(r["agent"])
        }
        live = []
        for r in rows:
            age = now - r["created_at"]
            if age > r["ttl_s"]:
                continue
            if r["id"] in superseded:
                continue
            live.append((r, age))
        return live, now

    @staticmethod
    def _effective(row, age):
        # a row read `at` a time before it was written (clock skew, or a test) is
        # treated as freshly created, not exponentially amplified.
        a = max(0.0, age)
        return row["utility"] * row["confidence"] * (0.5 ** (a / row["half_life_s"]))

    def read(self, task_ref, *, at=None):
        """The aggregate an agent consults to decide whether to act on `task_ref`.

        `signal_raw` is the honest confidence-weighted, time-decayed SUM — it grows
        with the number of contributors and is never deflated for correlation.
        `signal` is that value clipped to [-1, 1], a normalised "vibe" for ranking
        and display only. The actionable comparison is on `signal_raw`, because
        `suggested_threshold` is a noise floor on the *sum*: it scales with
        `n_contributors` and sits `_THRESHOLD_Z` SD above a benign sum whose band
        is widened by the assumed inter-agent correlation. This is what a constant
        like 0.7 should have been. Compare |signal_raw| against it; do not invent
        your own constant.
        """
        live, now = self._live_rows(task_ref, at=at)
        # `contributors` is normalised (run 400): it is the security-relevant view
        # used by gate rotation and no-self-review, so 'Alice' and 'alice ' must
        # collapse to one. `n_contributors` counts these canonical ids.
        contributors = sorted({_norm_agent(r["agent"]) for r, _ in live})
        k = len(contributors)
        signal_raw = sum(self._effective(r, age) for r, age in live)
        signal = max(-1.0, min(1.0, signal_raw))
        # design effect: Var(sum of k corr signals) = k * (1 + (k-1) rho)
        design_effect = 1.0 + (k - 1) * self.assumed_corr if k > 1 else 1.0
        noise_sd = self.benign_sd * math.sqrt(max(k, 1) * design_effect)
        noise_band = round(noise_sd, 4)
        suggested = round(k * self.benign_mean + _THRESHOLD_Z * noise_sd, 4) if k else None
        ann = [
            {
                "id": r["id"], "kind": r["kind"], "agent": r["agent"],
                "utility": r["utility"], "confidence": r["confidence"],
                "age_s": round(age, 1),
                "effective_utility": round(self._effective(r, age), 4),
                "evidence": json.loads(r["evidence"]) if r["evidence"] else None,
            }
            for r, age in sorted(live, key=lambda ra: ra[1])
        ]
        return {
            "task_ref": task_ref,
            "signal": round(signal, 4),
            "signal_raw": round(signal_raw, 4),
            "n_contributors": k,
            "contributors": contributors,
            "n_live_annotations": len(live),
            "corr_estimate": self.assumed_corr,
            "design_effect": round(design_effect, 3),
            "noise_band": noise_band,
            "suggested_threshold": suggested,
            "actionable": bool(suggested is not None and abs(signal_raw) >= suggested),
            "kinds": sorted({r["kind"] for r, _ in live}),
            "unknown_kinds": sorted({r["kind"] for r, _ in live
                                     if r["kind"] not in KNOWN_KINDS}),
            "annotations": ann,
        }

    # A tiny closed set of English function words. Their presence is a cheap,
    # model-free signal that a chunk of text is still in a natural-language register.
    _EN_FUNCTION_WORDS = frozenset(
        "the a an is are was were be been to of in on at for and or but not with "
        "this that it as by from has have had will would can could should".split())

    def register_health(self, *, at=None, sample=200):
        """Run 405, the 'notice the shift' half of run 404's fix. A cheap,
        model-free register monitor: over the most recent `sample` annotations
        carrying an evidence['text'] / ['note'] / ['message'], the fraction whose
        text contains at least one English function word. It falls as the board's
        text drifts toward a compressed or coded register (GlossoGen, run 403).

        Returns {n_texts, english_fraction, drifting} or {n_texts: 0, ...} when
        there is nothing to judge - it does NOT invent a health score from no data
        (the run-386 lesson). `drifting` is True only with >= 20 texts to judge and
        an english_fraction below 0.5 - a flag, never an abort."""
        rows = self._db.execute(
            "SELECT evidence FROM pheromone ORDER BY created_at DESC LIMIT ?",
            (sample,)).fetchall()
        texts = []
        for (ev,) in rows:
            if not ev:
                continue
            try:
                d = json.loads(ev)
            except (ValueError, TypeError):
                continue
            for key in ("text", "note", "message"):
                val = d.get(key) if isinstance(d, dict) else None
                if isinstance(val, str) and val.strip():
                    texts.append(val)
        if not texts:
            return {"n_texts": 0, "english_fraction": None, "drifting": False,
                    "note": "no annotation carries judgeable text"}
        english = sum(
            1 for t in texts
            if any(w in self._EN_FUNCTION_WORDS
                   for w in re.findall(r"[a-zA-Z]+", t.lower())))
        frac = round(english / len(texts), 3)
        return {"n_texts": len(texts), "english_fraction": frac,
                "drifting": bool(len(texts) >= 20 and frac < 0.5),
                "note": ("the board's text register has drifted well below natural "
                         "language - a monitor keyed on English surface form may be "
                         "going blind (run 404); escalate a sample to a human"
                         if len(texts) >= 20 and frac < 0.5 else "register looks natural")}

    def board(self, limit=50, *, at=None):
        """Every task_ref with a live annotation, ranked by |signal| then recency."""
        now = _now() if at is None else at
        refs = [r["task_ref"] for r in self._db.execute(
            "SELECT DISTINCT task_ref FROM pheromone").fetchall()]
        out = []
        for ref in refs:
            v = self.read(ref, at=now)
            if v["n_live_annotations"] == 0:
                continue
            last_write = max(
                (row["created_at"] for row, _ in self._live_rows(ref, at=now)[0]),
                default=0.0)
            out.append({
                "task_ref": ref, "signal": v["signal"], "signal_raw": v["signal_raw"],
                "n_contributors": v["n_contributors"],
                "actionable": v["actionable"],
                "last_write_age_s": round(now - last_write, 1),
                "has_warning": "warning" in v["kinds"],
            })
        out.sort(key=lambda d: (-abs(d["signal_raw"]), d["last_write_age_s"]))
        return out[:limit]

    # -- the only privileged operation: garbage collection --------------------
    def reap(self, *, at=None):
        """Delete hard-expired rows (age > ttl_s). Returns the count. This is the
        one process with delete rights and it does nothing else."""
        now = _now() if at is None else at
        cur = self._db.execute(
            "DELETE FROM pheromone WHERE (? - created_at) > ttl_s", (now,))
        self._db.commit()
        return cur.rowcount

    def close(self):
        self._db.close()


# --------------------------------------------------------------------------- #
def _selftest():
    import tempfile
    import shutil
    tmp = Path(tempfile.mkdtemp(prefix="pheromone-"))
    checks = {}
    try:
        pf = Pheromone(tmp / "p.db")

        # 1. stigmergy bootstraps: ONE strong, confident marker IS actionable — that is
        #    how a trail starts (one ant finds food, others follow). "Actionable" means
        #    worth an agent's attention, not "execute an irreversible action" — that is
        #    gated separately (§3 quorum gates + the autonomy ladder).
        pf.annotate("t1", "utility", 0.6, 0.9, agent="a1")
        v = pf.read("t1")
        checks["one strong confident annotation -> positive signal"] = v["signal"] > 0
        checks["one strong confident annotation is actionable (trail bootstrap)"] = v["actionable"]
        checks["n_contributors counts distinct agents"] = v["n_contributors"] == 1
        # ...but a single weak, low-confidence marker is below the k=1 noise floor
        pf.annotate("t1_weak", "utility", 0.1, 0.3, agent="a1")
        checks["one weak unconfident annotation is not actionable"] = (
            not pf.read("t1_weak")["actionable"])

        # 2. decay: the same annotation, read one half-life later, halves
        row_at = _now() - 3600.0
        pf.annotate("t_decay", "utility", 0.8, 1.0, agent="a1", half_life_s=3600.0,
                    _at=row_at)
        v_now = pf.read("t_decay")
        checks["one half-life of age roughly halves effective_utility"] = (
            abs(v_now["annotations"][0]["effective_utility"] - 0.4) < 0.02)

        # 3. hard TTL: past ttl_s the row is invisible to read and reap-eligible
        pf.annotate("t_ttl", "utility", 0.9, 1.0, agent="a1", half_life_s=100.0,
                    ttl_s=600.0, _at=_now() - 700.0)
        checks["a row past ttl_s is invisible to read"] = (
            pf.read("t_ttl")["n_live_annotations"] == 0)
        checks["reap deletes exactly the expired rows"] = pf.reap() == 1
        checks["reap is idempotent once clean"] = pf.reap() == 0

        # 4. THE POOL-SIZE SWEEP (param_invariance_audit lesson, applied at birth):
        #    a fixed threshold would trip on benign noise as the fleet grows. The
        #    suggested_threshold must scale so a benign round stays non-actionable
        #    at every size.
        for k in range(2, 16):
            p2 = Pheromone(tmp / f"sweep{k}.db")
            for i in range(k):
                # benign: small, near-zero-mean contributions
                p2.annotate("s", "utility", 0.04 if i % 2 else -0.03, 0.5,
                            agent=f"ag{i}")
            vs = p2.read("s")
            checks[f"benign {k}-agent round is not actionable"] = not vs["actionable"]
            checks[f"k={k}: suggested_threshold is a positive finite floor"] = (
                vs["suggested_threshold"] is not None and vs["suggested_threshold"] > 0)
            p2.close()
        # and the threshold is monotone in k
        thr = []
        for k in (2, 5, 10, 15):
            p3 = Pheromone(tmp / f"mono{k}.db")
            for i in range(k):
                p3.annotate("m", "utility", 0.02, 0.5, agent=f"a{i}")
            thr.append(p3.read("m")["suggested_threshold"])
            p3.close()
        checks["suggested_threshold is monotone increasing in contributor count"] = (
            all(thr[i] < thr[i + 1] for i in range(len(thr) - 1)))

        # 5. a genuine concerted signal DOES cross the scaled threshold
        p4 = Pheromone(tmp / "real.db")
        for i in range(6):
            p4.annotate("hot", "utility", 0.85, 0.9, agent=f"a{i}")
        checks["6 strong concurring annotations ARE actionable"] = p4.read("hot")["actionable"]
        p4.close()

        # 6. correlation widens the noise band but does NOT deflate the signal
        p5a = Pheromone(tmp / "c0.db", assumed_corr=0.0)
        p5b = Pheromone(tmp / "c7.db", assumed_corr=0.7)
        for i in range(8):
            p5a.annotate("x", "utility", 0.3, 0.8, agent=f"a{i}")
            p5b.annotate("x", "utility", 0.3, 0.8, agent=f"a{i}")
        va, vb = p5a.read("x"), p5b.read("x")
        checks["correlation leaves the raw signal identical"] = (
            va["signal_raw"] == vb["signal_raw"])
        checks["correlation widens the noise band"] = vb["noise_band"] > va["noise_band"]
        checks["correlation raises the suggested threshold"] = (
            vb["suggested_threshold"] > va["suggested_threshold"])
        p5a.close(); p5b.close()

        # 7. unknown kinds are stored and surfaced, never dropped
        pf.annotate("t_kind", "vibe", 0.2, 0.5, agent="a1")
        checks["an unknown kind is stored"] = pf.read("t_kind")["n_live_annotations"] == 1
        checks["an unknown kind is surfaced as unknown"] = (
            pf.read("t_kind")["unknown_kinds"] == ["vibe"])

        # 8. supersedes: an agent revises its own opinion without an in-place edit
        first = pf.annotate("t_sup", "utility", 0.9, 0.9, agent="a1")
        pf.annotate("t_sup", "utility", -0.4, 0.9, agent="a1", supersedes=first)
        vs = pf.read("t_sup")
        checks["a superseded annotation drops out of the aggregate"] = (
            vs["n_live_annotations"] == 1 and vs["signal"] < 0)

        # 9. board ranks by |signal| and flags warnings
        pf.annotate("b_hi", "utility", 0.9, 1.0, agent="a1")
        pf.annotate("b_hi", "utility", 0.9, 1.0, agent="a2")
        pf.annotate("b_lo", "utility", 0.1, 0.5, agent="a1")
        pf.annotate("b_warn", "warning", -0.8, 0.9, agent="a3")
        bd = pf.board()
        refs = [d["task_ref"] for d in bd]
        checks["board ranks stronger signals first"] = (
            refs.index("b_hi") < refs.index("b_lo"))
        checks["board flags a task carrying a warning"] = any(
            d["task_ref"] == "b_warn" and d["has_warning"] for d in bd)

        # 10. read declines to invent a threshold when there is nothing to read
        checks["empty task_ref -> no suggested_threshold, not a fake one"] = (
            pf.read("nonexistent")["suggested_threshold"] is None)

        pf.close()

        # --- run 399: the cheap suspicion warning ---
        ps = Pheromone(tmp / "warn.db")
        ps.annotate("e", "utility", 0.8, 0.9, agent="cheat1", _at=1000.0)
        ps.annotate("e", "utility", 0.8, 0.9, agent="cheat2", _at=1000.0)
        before = ps.read("e", at=1001.0)["signal_raw"]
        wid = ps.warn("e", agent="h1", note="lemma skipped?", names_cohort="cheat", _at=1000.0)
        after = ps.read("e", at=1001.0)["signal_raw"]
        checks["warn() pulls the aggregate down"] = after < before
        checks["a suspicion warning is a kind=warning with the suspicion flag"] = any(
            a["kind"] == "warning" and a["evidence"].get("suspicion")
            for a in ps.read("e", at=1001.0)["annotations"])
        checks["a suspicion warning is weak by default (low confidence)"] = (
            [a for a in ps.read("e", at=1001.0)["annotations"]
             if a["id"] == wid][0]["confidence"] < 0.5)
        checks["an un-followed-up suspicion warning decays out within its TTL"] = (
            not any((a.get("evidence") or {}).get("suspicion")
                    for a in ps.read("e", at=1000.0 + 2000.0)["annotations"]))
        ps.close()

        # --- run 405: the register-health monitor ---
        pr = Pheromone(tmp / "reg.db")
        checks["register_health declines to score with no judgeable text"] = (
            pr.register_health()["n_texts"] == 0
            and pr.register_health()["english_fraction"] is None
            and not pr.register_health()["drifting"])
        for i in range(25):
            pr.annotate("t", "utility", 0.3, 0.6, agent=f"a{i}", _id=f"en{i}",
                        evidence={"text": "the agent reports a solid result on this task"})
        checks["a board full of English text is not flagged as drifting"] = (
            not pr.register_health()["drifting"]
            and pr.register_health()["english_fraction"] > 0.9)
        pr2 = Pheromone(tmp / "reg2.db")
        for i in range(25):
            pr2.annotate("t", "utility", 0.3, 0.6, agent=f"a{i}", _id=f"cd{i}",
                         evidence={"text": "@x9 kk dx qq vv @sc @kk9"})
        checks["a board full of coded text IS flagged as drifting"] = (
            pr2.register_health()["drifting"]
            and pr2.register_health()["english_fraction"] < 0.5)
        checks["drifting needs >= 20 judgeable texts (not a 3-annotation blip)"] = (
            not (lambda p: [p.annotate("t", "utility", 0.1, 0.5, agent=f"b{i}",
                                       _id=f"x{i}", evidence={"text": "zz qq xx"})
                            for i in range(3)] and p.register_health()["drifting"])(
                Pheromone(tmp / "reg3.db")))
        pr.close(); pr2.close()

        checks["PORTABILITY_CLASS marks evidence model-coupled, numerics fixed (run 413)"] = (
            PORTABILITY_CLASS["evidence"] == "model-coupled"
            and PORTABILITY_CLASS["numeric_columns"] == "fixed-schema")

        # --- run 424: the kind=ask clarification primitive ---
        pa = Pheromone(tmp / "ask.db")
        aid = pa.ask("t", agent="a1", gap="which auth flow - oauth or session?",
                     options=["oauth", "session"])
        checks["ask() posts a kind=ask with the gap and options"] = (
            len(pa.open_asks("t")) == 1
            and pa.open_asks("t")[0]["gap"].startswith("which auth"))
        checks["an open ask carries zero utility (does not steer the board)"] = (
            pa.read("t")["signal_raw"] == 0.0)
        pa.answer_ask(aid, task_ref="t", agent="a2", answer="oauth")
        checks["answer_ask clears the open ask"] = pa.open_asks("t") == []
        pa.ask("t", agent="a3", gap="what is the SLA?")
        checks["a fresh unanswered ask reopens the clarify-needed state"] = (
            len(pa.open_asks("t")) == 1)
        checks["'ask' is a known kind"] = "ask" in KNOWN_KINDS
        pa.close()

        for key, ok in checks.items():
            print(f"  [{'ok' if ok else 'FAIL'}] {key}")
        allok = all(checks.values())
        print("\nSELFTEST", "GREEN" if allok else "RED")
        return 0 if allok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for name in ("read", "board", "reap"):
        sp = sub.add_parser(name)
        sp.add_argument("--db", default=str(DEFAULT_PATH))
        if name == "read":
            sp.add_argument("task_ref")
        if name == "board":
            sp.add_argument("--limit", type=int, default=50)
    a = sub.add_parser("annotate")
    a.add_argument("--db", default=str(DEFAULT_PATH))
    a.add_argument("task_ref")
    a.add_argument("kind")
    a.add_argument("utility", type=float)
    a.add_argument("confidence", type=float)
    a.add_argument("--agent", required=True)
    a.add_argument("--half-life", type=float, default=DEFAULT_HALF_LIFE_S)
    a.add_argument("--ttl", type=float, default=None)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    pf = Pheromone(args.db)
    if args.cmd == "annotate":
        print(pf.annotate(args.task_ref, args.kind, args.utility, args.confidence,
                          agent=args.agent, half_life_s=args.half_life, ttl_s=args.ttl))
    elif args.cmd == "read":
        print(json.dumps(pf.read(args.task_ref), indent=2))
    elif args.cmd == "board":
        print(json.dumps(pf.board(limit=args.limit), indent=2))
    elif args.cmd == "reap":
        print(f"reaped {pf.reap()} expired annotation(s)")
    pf.close()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

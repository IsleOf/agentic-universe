#!/usr/bin/env python3
"""Can trust transfer across task families without creating universal authority? — a runnable rig.

Open research question 5 (`docs/research/open_questions.md`; anchor
`concept_conditional_trust_is_domain_keyed_not_global`, run 260). A domain-keyed trust
graph (`A -[0.88, coding-tests]-> B`) resists universal authority, but pays a cold-start
cost: every new task family starts from no information. The question is whether a
partial, similarity-scaled transfer beats both a universal scalar (overclaims) and a
strict per-family reset (throws away real signal).

This rig: `AGENTS` agents each have a latent competence per task `FAMILY`, generated so
that families have a **similarity structure** — an agent's competence in family j is a
blend of a per-agent baseline and a per-(agent, cluster) skill, where families in the
same cluster are correlated and cross-cluster families are nearly independent.

Three trust models are fit on `TRAIN_FAMILIES` (observed hit-rates) and used to predict
the agent ranking on `HELD_OUT_FAMILIES`:

  UNIVERSAL          one scalar per agent = mean observed hit-rate. Assumes full transfer.
  DOMAIN_KEYED       per-family; for a held-out family there is no estimate → falls back
                     to the global prior (a cold start).
  SIMILARITY_WEIGHTED trust in a held-out family = similarity-weighted average of the
                     agent's trust in the train families (similarity estimated from
                     co-performance on the train set).

Measure: rank correlation (Spearman-ish) between predicted and true competence on the
held-out families, and the "authority concentration" (how often one agent is ranked
top across ALL held-out families — a proxy for universal authority).

Prediction: SIMILARITY_WEIGHTED has the best held-out rank correlation; UNIVERSAL has
the highest authority concentration (it crowns one agent everywhere); DOMAIN_KEYED
predicts near chance on held-out families (cold start). Trust transfers — partially,
scaled by similarity — without universal authority.

No model call. Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

SEED = 20261002

AGENTS = 8
CLUSTERS = 3
FAMILIES_PER_CLUSTER = 4
TRAIN_PER_CLUSTER = 3           # families observed per cluster; the 4th is held out
OBS_PER_FAMILY = 30            # graded tasks observed per (agent, family) on the train set
WITHIN_CLUSTER_W = 0.70       # weight of the cluster skill vs the per-agent baseline


def _competence(rng):
    """comp[agent][family] with a cluster similarity structure."""
    base = [rng.betavariate(5, 4) for _ in range(AGENTS)]
    cluster_skill = [[rng.betavariate(4, 4) for _ in range(CLUSTERS)] for _ in range(AGENTS)]
    comp = []
    for a in range(AGENTS):
        row = []
        for cl in range(CLUSTERS):
            for _f in range(FAMILIES_PER_CLUSTER):
                fam_noise = rng.gauss(0, 0.05)
                c = (1 - WITHIN_CLUSTER_W) * base[a] + WITHIN_CLUSTER_W * cluster_skill[a][cl] + fam_noise
                row.append(min(0.98, max(0.05, c)))
        comp.append(row)
    return comp


def _observe(rng, comp):
    """train-set observed hit-rates; which families are held out."""
    obs = [[None] * (CLUSTERS * FAMILIES_PER_CLUSTER) for _ in range(AGENTS)]
    held_out = []
    for cl in range(CLUSTERS):
        fam_ids = list(range(cl * FAMILIES_PER_CLUSTER, (cl + 1) * FAMILIES_PER_CLUSTER))
        train = fam_ids[:TRAIN_PER_CLUSTER]
        held_out += fam_ids[TRAIN_PER_CLUSTER:]
        for a in range(AGENTS):
            for f in train:
                hits = sum(rng.random() < comp[a][f] for _ in range(OBS_PER_FAMILY))
                obs[a][f] = hits / OBS_PER_FAMILY
    return obs, held_out


def _spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def _predict_universal(obs, held_out):
    scalar = []
    for a in range(AGENTS):
        vals = [v for v in obs[a] if v is not None]
        scalar.append(sum(vals) / len(vals))
    return {f: list(scalar) for f in held_out}


def _predict_domain_keyed(obs, held_out):
    # no per-family estimate for a held-out family -> global prior (cold start)
    all_vals = [v for row in obs for v in row if v is not None]
    prior = sum(all_vals) / len(all_vals)
    return {f: [prior] * AGENTS for f in held_out}


def _predict_similarity(obs, held_out):
    train_fams = [f for f in range(CLUSTERS * FAMILIES_PER_CLUSTER)
                  if any(obs[a][f] is not None for a in range(AGENTS))]
    # similarity between families = 1 - mean abs diff of agent hit-rates
    def sim(f1, f2):
        diffs = [abs(obs[a][f1] - obs[a][f2]) for a in range(AGENTS)
                 if obs[a][f1] is not None and obs[a][f2] is not None]
        return max(0.0, 1.0 - 2.0 * (sum(diffs) / len(diffs)))
    out = {}
    for h in held_out:
        # we cannot observe h; estimate its similarity to each train family via cluster proxy:
        # a held-out family's cluster is known, so weight train families in the same cluster high
        h_cluster = h // FAMILIES_PER_CLUSTER
        weights = []
        for tf in train_fams:
            w = 0.8 if tf // FAMILIES_PER_CLUSTER == h_cluster else 0.15
            # refine with observed cross-train similarity to same-cluster train families
            same = [t for t in train_fams if t // FAMILIES_PER_CLUSTER == h_cluster and t != tf]
            if same:
                w *= (0.5 + statistics_mean(sim(tf, s) for s in same))
            weights.append(w)
        tot = sum(weights) or 1.0
        preds = []
        for a in range(AGENTS):
            num = sum(weights[i] * obs[a][tf] for i, tf in enumerate(train_fams))
            preds.append(num / tot)
        out[h] = preds
    return out


def statistics_mean(it):
    xs = list(it)
    return sum(xs) / len(xs) if xs else 0.0


MODELS = {"universal": _predict_universal, "domain_keyed": _predict_domain_keyed,
          "similarity_weighted": _predict_similarity}


def run_trial(rng):
    comp = _competence(rng)
    obs, held_out = _observe(rng, comp)
    true = {f: [comp[a][f] for a in range(AGENTS)] for f in held_out}
    out = {}
    for name, fn in MODELS.items():
        preds = fn(obs, held_out)
        corrs = [_spearman(preds[f], true[f]) for f in held_out]
        # authority concentration: how often the SAME agent is predicted top across held-out families
        tops = [max(range(AGENTS), key=lambda a: preds[f][a]) for f in held_out]
        top_counts = {}
        for t in tops:
            top_counts[t] = top_counts.get(t, 0) + 1
        concentration = max(top_counts.values()) / len(held_out)
        out[name] = {"rank_corr": sum(corrs) / len(corrs), "authority_concentration": concentration}
    return out


def sweep(trials=2000, rec=None):
    agg = {name: {"rank_corr": 0.0, "authority_concentration": 0.0} for name in MODELS}
    for t in range(trials):
        o = run_trial(random.Random(f"{SEED}-{t}"))
        for name in MODELS:
            for k in agg[name]:
                agg[name][k] += o[name][k]
    res = {name: {k: round(v / trials, 3) for k, v in d.items()} for name, d in agg.items()}
    if rec:
        for name in MODELS:
            rec.claim("probe", f"{name}: corr {res[name]['rank_corr']} conc {res[name]['authority_concentration']}",
                      [f"sim-{name}"], layer="swarm")
    return res


def assess(res):
    sw, un, dk = res["similarity_weighted"], res["universal"], res["domain_keyed"]
    a = {
        "similarity_weighted_has_best_held_out_rank_corr":
            sw["rank_corr"] > un["rank_corr"] and sw["rank_corr"] > dk["rank_corr"],
        "domain_keyed_predicts_near_chance_on_held_out": abs(dk["rank_corr"]) < 0.12,
        "universal_beats_chance_but_below_similarity":
            un["rank_corr"] > 0.15 and un["rank_corr"] < sw["rank_corr"],
        "universal_has_the_highest_authority_concentration":
            un["authority_concentration"] > sw["authority_concentration"],
        "similarity_corr": sw["rank_corr"],
        "universal_corr": un["rank_corr"],
        "domain_keyed_corr": dk["rank_corr"],
        "universal_concentration": un["authority_concentration"],
        "similarity_concentration": sw["authority_concentration"],
        "verdict": None,
    }
    ok = (a["similarity_weighted_has_best_held_out_rank_corr"]
          and a["domain_keyed_predicts_near_chance_on_held_out"]
          and a["universal_beats_chance_but_below_similarity"]
          and a["universal_has_the_highest_authority_concentration"])
    if ok:
        a["verdict"] = (
            f"CONFIRMS at these params: similarity-weighted trust predicts held-out task families best "
            f"(rank corr {a['similarity_corr']:+.2f} vs universal {a['universal_corr']:+.2f} vs domain-keyed "
            f"{a['domain_keyed_corr']:+.2f} ~ chance). Universal trust concentrates authority on one agent "
            f"({a['universal_concentration']:.2f} vs {a['similarity_concentration']:.2f}). Trust transfers "
            f"- partially, scaled by family similarity - without granting universal authority.")
    else:
        a["verdict"] = (
            f"PARTIAL at these params: similarity {a['similarity_corr']:+.2f}, universal {a['universal_corr']:+.2f}, "
            f"domain-keyed {a['domain_keyed_corr']:+.2f}; concentration universal {a['universal_concentration']:.2f} "
            f"vs similarity {a['similarity_concentration']:.2f}.")
    return a


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="trust-transfer-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "trust_transfer", "open")
    res = sweep(trials=1500, rec=rec)
    rec.step("probe", "trust_transfer", "close")
    a = assess(res)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue())
        tmp = fh.name
    n_ev, errors = validate_trace(tmp)
    os.unlink(tmp)
    checks = {
        "similarity-weighted trust has the best held-out rank correlation":
            a["similarity_weighted_has_best_held_out_rank_corr"],
        "domain-keyed (per-family reset) predicts near chance on held-out families":
            a["domain_keyed_predicts_near_chance_on_held_out"],
        "universal trust beats chance but is below similarity-weighted":
            a["universal_beats_chance_but_below_similarity"],
        "universal trust concentrates authority on one agent the most":
            a["universal_has_the_highest_authority_concentration"],
        "verdict is CONFIRMS": a["verdict"].startswith("CONFIRMS"),
        "trace validates": not errors,
        "trace claims are on the swarm layer": '"layer": "swarm"' in buf.getvalue(),
    }
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print(f"\n  {json.dumps(res, indent=2)}")
    print(f"  verdict: {a['verdict']}")
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sw = sub.add_parser("sweep")
    sw.add_argument("--trials", type=int, default=2000)
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        res = sweep(trials=args.trials)
        print(json.dumps(res, indent=2))
        print("\n" + assess(res)["verdict"])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

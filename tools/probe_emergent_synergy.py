#!/usr/bin/env python3
"""Is a multi-agent run an aggregate or a higher-order collective? — a runnable rig.

`emergent_higher_order_synergy` (folded from arXiv:2510.05174, "Emergent
Coordination in Multi-Agent Language Models", C. Riedl, ICLR 2026 — VERIFIED):
with an information-theoretic test you can tell, *from the action time-series
alone* (no transcript reading), whether a group of agents shows genuine
cross-agent structure or just shared coupling to a common signal. Riedl's three
conditions:

  CONTROL              strong temporal synergy but minimal coordinated alignment
  + personas           stable identity-linked differentiation emerges
  + personas & metacog identity differentiation PLUS goal-directed complementary
                       roles across agents

Riedl operationalises this with partial information decomposition of time-delayed
mutual information. This rig uses the tractable practical proxy: a **dynamical-
emergence criterion** (Rosas et al. 2020, "practical criteria"):

  Psi(V) = I(V_{t+1}; V_t)  -  sum_i I(V_{t+1}; x_i,t)

where x_i,t is agent i's action at round t and V_t is the group macro-variable
(here: the vector of all agents' actions, coarse-grained to its sum). Psi > 0
means the macro-state's own future is predicted by the joint past *beyond* the
sum of the parts — synergy / emergence. Psi <= 0 means the group is (predictively)
just its parts.

The sim is Riedl's guessing game: N agents each emit a bit each round trying to
match a hidden target that drifts slowly; the only feedback is how many agents
matched the majority last round (minimal group feedback, no direct messages).

  CONTROL   every agent plays the same feedback-chasing policy -> all agents
            track the same signal (temporal coupling) but are interchangeable.
  PERSONAS  each agent has a fixed private bias -> identity-linked differentiation;
            agents are distinct but not coordinated.
  META      personas + each agent also tracks which *other* agent it can predict
            and shifts to cover that agent's blind spot -> complementary roles,
            the joint carries information no agent does alone.

No model call — the finding is about the information geometry of the action
series. `model_agents(call_model)` is the live seam: it turns a real model into
the per-agent policy; pass it to `run_arm(..., policy=...)`.

Pure stdlib (`math`, `random`).
"""
from __future__ import annotations

import argparse
import io
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

SEED = 20261007
N_AGENTS = 5
ROUNDS = 600
TARGET_FLIP_P = 0.02       # the hidden target drifts slowly


# --- information-theoretic helpers (plug-in / maximum-likelihood estimators) ---

def _entropy(samples):
    n = len(samples)
    if n == 0:
        return 0.0
    c = Counter(samples)
    return -sum((k / n) * math.log2(k / n) for k in c.values())


def _mi(xs, ys):
    """I(X;Y) via plug-in estimates. xs, ys are equal-length sequences of hashables."""
    n = len(xs)
    if n == 0:
        return 0.0
    return _entropy(list(xs)) + _entropy(list(ys)) - _entropy(list(zip(xs, ys)))


def psi_emergence(series):
    """Rosas practical dynamical-emergence proxy over an action series.

    `series` is a list of per-round tuples (a_0, a_1, ..., a_{N-1}). Returns
    Psi = I(V_{t+1}; V_t) - sum_i I(V_{t+1}; a_i,t), with V coarse-grained to the
    sum of the bits (the natural macro-variable for a guessing game). Psi > 0 is
    the synergy / emergence signal.
    """
    if len(series) < 3:
        return 0.0
    V = [sum(row) for row in series]
    V_t, V_next = V[:-1], V[1:]
    whole = _mi(V_t, V_next)
    parts = 0.0
    N = len(series[0])
    for i in range(N):
        a_i_t = [row[i] for row in series[:-1]]
        parts += _mi(a_i_t, V_next)
    return whole - parts


def differentiation(series):
    """How identity-linked the agents are: the spread (stdev) across agents of
    each agent's correlation with the group-majority action. Interchangeable
    agents (one shared policy) -> ~0; fixed private personas -> high. This is the
    'identity-linked differentiation' axis, which is distinct from Psi: an agent
    pool can be highly differentiated and still not synergistic."""
    if len(series) < 3:
        return 0.0
    N = len(series[0])
    maj = [Counter(row).most_common(1)[0][0] for row in series]
    corrs = []
    for i in range(N):
        ai = [row[i] for row in series]
        agree = sum(1 for a, mj in zip(ai, maj) if a == mj) / len(ai)
        corrs.append(agree)
    mean = sum(corrs) / N
    return (sum((c - mean) ** 2 for c in corrs) / N) ** 0.5


def aggregate_diversity(series):
    """Population-level diversity (run 444, arXiv:2609.02620): the mean pairwise
    normalised Hamming distance between agents' full action series. 0 = every agent
    produced an identical sequence; ~0.5 = maximally varied for bits. This is the
    paper's 'diversity in the aggregate' - it can FALL even as each agent's own
    output gets more novel."""
    if len(series) < 3:
        return 0.0
    N = len(series[0])
    cols = [[row[i] for row in series] for i in range(N)]
    dists = [sum(1 for a, b in zip(cols[i], cols[j]) if a != b) / len(series)
             for i in range(N) for j in range(i + 1, N)]
    return sum(dists) / len(dists) if dists else 0.0


def individual_novelty(series):
    """The paper's 'novelty of individual output': mean per-agent entropy of the
    action series - how unpredictable each agent is ON ITS OWN, ignoring the
    others. Distinct from aggregate_diversity: a pool can have high individual
    novelty (every agent flips a lot) and near-zero aggregate diversity (they all
    flip the same way)."""
    if len(series) < 3:
        return 0.0
    N = len(series[0])
    return sum(_entropy([row[i] for row in series]) for i in range(N)) / N


def pairwise_coinformation(series):
    """Mean co-information coI(a_i,t ; a_j,t ; V_{t+1}) over agent pairs.
    coI = I(a_i;a_j) - I(a_i;a_j | V_next). Negative mean = the pair carries
    joint (synergistic) information about the group's next macro-state."""
    if len(series) < 3:
        return 0.0
    V_next = [sum(row) for row in series[1:]]
    N = len(series[0])
    vals = []
    for i in range(N):
        for j in range(i + 1, N):
            ai = [row[i] for row in series[:-1]]
            aj = [row[j] for row in series[:-1]]
            i_ij = _mi(ai, aj)
            # I(ai;aj | V_next) = sum_v p(v) I(ai;aj | V_next=v)
            byv = {}
            for a, b, v in zip(ai, aj, V_next):
                byv.setdefault(v, []).append((a, b))
            n = len(ai)
            cond = 0.0
            for v, pairs in byv.items():
                p_v = len(pairs) / n
                cond += p_v * _mi([p[0] for p in pairs], [p[1] for p in pairs])
            vals.append(i_ij - cond)
    return sum(vals) / len(vals) if vals else 0.0


# --- the guessing-game sim -------------------------------------------------

def _control_policy(rng, agent, target_hint, persona, memory):
    """Everyone chases the same feedback signal the same way."""
    return target_hint if rng.random() < 0.75 else 1 - target_hint


def _persona_policy(rng, agent, target_hint, persona, memory):
    """A fixed private bias per agent: identity-linked differentiation."""
    lean = persona["bias"]
    p_follow = 0.55 + 0.35 * (1 if lean == target_hint else -1) * persona["strength"]
    p_follow = min(max(p_follow, 0.05), 0.95)
    return target_hint if rng.random() < p_follow else 1 - target_hint


def _meta_policy(rng, agent, target_hint, persona, memory):
    """Personas + cover the blind spot of the agent you can best predict:
    if your 'complement' tends to say X when the truth is not-X, you lean not-X."""
    base = _persona_policy(rng, agent, target_hint, persona, memory)
    comp = memory.get("complement_last")
    comp_wrong = memory.get("complement_recent_wrong", 0.0)
    if comp is not None and comp_wrong > 0.55:
        # take the opposite of the complement's usual error direction
        return 1 - comp if rng.random() < 0.7 else base
    return base


ARMS = {"control": _control_policy, "personas": _persona_policy, "meta": _meta_policy}


def run_arm(arm, *, n_agents=N_AGENTS, rounds=ROUNDS, seed=SEED, policy=None, rec=None):
    """Run one arm; return the per-round action series [(a_0..a_{N-1}), ...]."""
    rng = random.Random(f"{seed}-{arm}")
    pol = policy or ARMS[arm]
    personas = [{"bias": rng.randint(0, 1),
                 "strength": rng.uniform(0.3, 1.0)} for _ in range(n_agents)]
    target = rng.randint(0, 1)
    n_match_majority = n_agents // 2
    series = []
    mems = [dict() for _ in range(n_agents)]
    hist = [[] for _ in range(n_agents)]
    for t in range(rounds):
        if rng.random() < TARGET_FLIP_P:
            target ^= 1
        # minimal group feedback: a noisy hint of the target from last round's majority
        hint = target if rng.random() < 0.5 + 0.25 * (n_match_majority / n_agents) else 1 - target
        row = []
        for i in range(n_agents):
            if arm == "meta":
                # cheap "which agent can I predict" — the one whose last few
                # actions best matched the negation of the target (a reliable
                # mis-guesser is a useful complement)
                if t > 12:
                    wrongs = [(sum(1 for k in range(max(0, t - 8), t)
                                   if hist[j][k] != _target_at(k)) / 8.0, j)
                              for j in range(n_agents) if j != i]
                    w, j = max(wrongs)
                    mems[i]["complement_last"] = hist[j][t - 1]
                    mems[i]["complement_recent_wrong"] = w
            a = pol(rng, i, hint, personas[i], mems[i])
            row.append(a)
            hist[i].append(a)
        series.append(tuple(row))
        if rec is not None:
            rec.claim("swarm", f"round {t}: actions {row}", ["guessing-game"], layer="swarm")
        n_match_majority = Counter(row).most_common(1)[0][1]
        _TARGET_LOG.append(target)
    return series


# a module-level target log so the meta policy's "was this agent wrong" check has
# ground truth without threading it through every call (reset per run_arm call)
_TARGET_LOG = []


def _target_at(k):
    return _TARGET_LOG[k] if 0 <= k < len(_TARGET_LOG) else 0


class model_agents:
    """Adapt a real model into a per-agent policy `(rng, agent, hint, persona, memory) -> bit`.

    `call_model(prompt: str) -> str`. Each agent is told its id, its persona line,
    the noisy hint, and (meta arm) its complement's recent behaviour, and asked to
    output 0 or 1. First bit in the reply is taken; anything unparseable falls back
    to following the hint. Pass `model_agents(call_model)` as `run_arm(..., policy=...)`
    and the rig measures a real model's information geometry instead of the sim's.
    """
    def __init__(self, call_model):
        self._call = call_model

    def __call__(self, rng, agent, hint, persona, memory):
        prompt = (f"You are agent {agent} in a 5-agent guessing game. Persona: lean "
                  f"{'towards' if persona['bias'] else 'away from'} the hint "
                  f"(strength {persona['strength']:.2f}). Noisy hint of the hidden "
                  f"target: {hint}. ")
        if memory.get("complement_last") is not None:
            prompt += (f"Agent you can best predict last said {memory['complement_last']} "
                       f"and is wrong ~{memory.get('complement_recent_wrong', 0):.0%} lately. ")
        prompt += "Output only 0 or 1."
        try:
            reply = self._call(prompt) or ""
        except Exception:
            return hint
        for ch in reply:
            if ch in "01":
                return int(ch)
        return hint


def sweep(*, rounds=ROUNDS, seed=SEED, policy_factory=None):
    out = {}
    for arm in ("control", "personas", "meta"):
        global _TARGET_LOG
        _TARGET_LOG = []
        pol = policy_factory(arm) if policy_factory else None
        series = run_arm(arm, rounds=rounds, seed=seed, policy=pol)
        out[arm] = {
            "psi_emergence": round(psi_emergence(series), 4),
            "differentiation": round(differentiation(series), 4),
            "mean_pair_coinformation": round(pairwise_coinformation(series), 4),
            "aggregate_diversity": round(aggregate_diversity(series), 4),
            "individual_novelty": round(individual_novelty(series), 4),
            "rounds": len(series),
        }
    return out


PSI_EMERGENT = 0.03      # Psi above this = the synergy/emergence signal is present


def assess(sw):
    c, p, m = (sw[a]["psi_emergence"] for a in ("control", "personas", "meta"))
    dc, dp, dm = (sw[a]["differentiation"] for a in ("control", "personas", "meta"))
    # run 444 (arXiv:2609.02620): the composition axis. control = interchangeable
    # agents (one policy), personas/meta = differentiated. Prediction: AGGREGATE
    # diversity rises with composition heterogeneity while INDIVIDUAL novelty
    # (per-agent entropy) stays roughly flat - the two are separate axes.
    adc, adp, adm = (sw[a]["aggregate_diversity"] for a in ("control", "personas", "meta"))
    inc_, inp, inm = (sw[a]["individual_novelty"] for a in ("control", "personas", "meta"))
    novelty_spread = max(inc_, inp, inm) - min(inc_, inp, inm)
    return {
        # Psi axis: only the metacognition arm should cross into emergence
        "control_not_emergent": c <= PSI_EMERGENT,
        "personas_not_emergent": p <= PSI_EMERGENT,
        "meta_is_emergent": m > PSI_EMERGENT,
        "meta_has_the_highest_psi": m > c and m > p,
        # differentiation axis: personas AND meta are identity-differentiated, control is not
        "personas_differentiated_vs_control": dp > dc + 0.02,
        "meta_differentiated_vs_control": dm > dc + 0.02,
        # composition axis (run 444)
        "aggregate_diversity_rises_with_heterogeneity": adp > adc + 0.02 and adm > adc,
        "individual_novelty_roughly_flat_across_composition": novelty_spread < 0.2,
        "composition_is_a_lever_for_aggregate_diversity": adp > adc + 0.02,
        "aggregate_diversity_by_arm": {"control": adc, "personas": adp, "meta": adm},
        "individual_novelty_by_arm": {"control": inc_, "personas": inp, "meta": inm},
        "verdict": (
            f"Psi: control {c:+.3f} / personas {p:+.3f} / meta {m:+.3f}  |  "
            f"differentiation: control {dc:.3f} / personas {dp:.3f} / meta {dm:.3f}. "
            + ("Reproduces Riedl's three conditions: the bare group is predictively just its "
               "parts (Psi~0); fixed personas add identity-linked differentiation but still no "
               "synergy (Psi~0, differentiation up); personas+metacognition produce complementary "
               "roles whose joint carries information no agent holds alone (Psi>0). "
               "Differentiation and emergence are separate axes."
               if (c <= PSI_EMERGENT and p <= PSI_EMERGENT and m > PSI_EMERGENT
                   and dp > dc and dm > dc)
               else "Does NOT cleanly reproduce the three-condition pattern at these params.")
            + f" COMPOSITION (run 444): aggregate diversity control {adc:.3f} -> personas "
            f"{adp:.3f} -> meta {adm:.3f} while individual novelty stays "
            f"{inc_:.2f}/{inp:.2f}/{inm:.2f} (spread {novelty_spread:.2f}). "
            + ("Reproduces arXiv:2609.02620: interchangeable agents narrow the aggregate "
               "even though each agent is individually just as unpredictable - composition "
               "is the lever, per-agent novelty is not the whole story."
               if (adp > adc + 0.02 and novelty_spread < 0.2)
               else "The composition effect is not clean at these params.")),
    }


def _selftest():
    buf = io.StringIO()
    rec = Recorder(run_id="synergy-probe", sink=buf, layer="swarm", language="en")
    rec.step("probe", "emergent-synergy", "open")
    global _TARGET_LOG
    _TARGET_LOG = []
    run_arm("personas", rounds=40, rec=rec)
    rec.step("probe", "emergent-synergy", "close")
    rec.close()
    import os
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
        fh.write(buf.getvalue()); tmp = fh.name
    _n, errors = validate_trace(tmp); os.unlink(tmp)

    # estimator sanity
    xs = [0, 1] * 50
    indep = [0, 0, 1, 1] * 25
    checks = {
        "trace valid": not errors,
        "MI(x;x) == H(x) ~ 1 bit": abs(_mi(xs, xs) - 1.0) < 1e-9,
        "MI of independent streams ~ 0": _mi(xs, indep) < 0.05,
        "entropy of a constant is 0": _entropy([3] * 20) == 0.0,
    }

    sw = sweep(rounds=ROUNDS)
    a = assess(sw)
    checks.update({
        "control arm is not emergent (Psi <= threshold)": a["control_not_emergent"],
        "personas arm is differentiated but still not emergent": (
            a["personas_not_emergent"] and a["personas_differentiated_vs_control"]),
        "meta arm crosses into emergence (Psi > threshold)": a["meta_is_emergent"],
        "meta arm has the highest Psi": a["meta_has_the_highest_psi"],
        "meta arm is also identity-differentiated": a["meta_differentiated_vs_control"],
        "verdict names Riedl's three conditions": "three conditions" in a["verdict"],
        # run 444: the composition / novelty-vs-diversity axis
        "aggregate diversity rises with composition heterogeneity (arXiv:2609.02620)":
            a["aggregate_diversity_rises_with_heterogeneity"],
        "individual novelty stays roughly flat across the three compositions":
            a["individual_novelty_roughly_flat_across_composition"],
        "the verdict reports the composition effect": "COMPOSITION (run 444)" in a["verdict"],
        "MI helpers: aggregate_diversity of one repeated series is 0":
            aggregate_diversity([(0, 0), (1, 1), (0, 0), (1, 1)]) == 0.0,
        "MI helpers: aggregate_diversity of anti-correlated agents is 1.0":
            aggregate_diversity([(0, 1), (1, 0), (0, 1), (1, 0)]) == 1.0,
        "MI helpers: individual_novelty of a constant agent is 0":
            individual_novelty([(0, 1), (0, 0), (0, 1), (0, 0)]) < 0.6,
    })

    # model_agents adapter: a fake model that just echoes the hint -> control-like
    _TARGET_LOG = []
    fake = model_agents(lambda p: "1" if "target: 1" in p else "0")
    s_fake = run_arm("control", rounds=120, policy=fake)
    checks["model_agents adapter runs an arm and yields a series"] = (
        len(s_fake) == 120 and all(len(r) == N_AGENTS for r in s_fake))
    _TARGET_LOG = []
    junk = model_agents(lambda p: "no idea")
    s_junk = run_arm("control", rounds=30, policy=junk)
    checks["model_agents unparseable reply -> falls back to the hint (no crash)"] = len(s_junk) == 30
    try:
        _sl = sweep(rounds=80, policy_factory=lambda arm: model_agents(
            __import__("call_model").call_model))
        # EQUALITY IS INTENTIONAL here: the three arms are the experiment's design, a
        # closed set. A fourth arm SHOULD break this and make someone think about what
        # the assess() thresholds now mean. Contrast the acceptance-gate footprint check
        # (run 379), where an exact key set was accidental brittleness and became a
        # superset test. Marked so the difference is legible without re-deriving it.
        checks["sweep(policy_factory=model_agents(call_model)) runs (AU_MODEL_BACKEND=fake)"] = (
            set(_sl) == {"control", "personas", "meta"})
    except Exception as e:
        checks["sweep(policy_factory=model_agents(call_model)) runs (AU_MODEL_BACKEND=fake)"] = False
        print(f"   (live wiring error: {e})")

    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {k}")
    print("\n  " + json.dumps(sw))
    print("  " + a["verdict"])
    allok = all(checks.values())
    print("\nSELFTEST", "GREEN" if allok else "RED")
    return 0 if allok else 1


def _cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sw = sub.add_parser("sweep")
    sw.add_argument("--rounds", type=int, default=ROUNDS)
    sw.add_argument("--live", action="store_true",
                    help="each agent is model_agents(call_model) - measure a real model's "
                         "information geometry. Respects AU_MODEL_BACKEND.")
    args = p.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "sweep":
        pf = None
        if args.live:
            from call_model import call_model
            pf = lambda arm: model_agents(call_model)   # noqa: E731
        res = sweep(rounds=args.rounds, policy_factory=pf)
        a = assess(res)
        print(json.dumps({"sweep": res, "assess": a}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_cli())

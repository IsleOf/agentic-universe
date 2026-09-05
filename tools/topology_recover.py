#!/usr/bin/env python3
"""Phase 0 gate: recover the swarm interaction topology and agent roles from a trace.

`docs/self_improving_harness_plan.md` Phase 0 gate, verbatim:

    topology analysis must recover roles in a control condition where roles were
    explicitly assigned. An instrument that cannot find roles known to be there
    cannot be trusted to find emergent ones.

This module does two things:
1. `build_topology(events)` — the interaction graph (message counts between
   actors) plus per-actor feature vectors from a trace.
2. `recover_roles(topology)` — a deterministic, rule-based role label per actor
   from those features. No model call: `concept_verification_completeness_gap`
   says keep a computed check wherever one can be written.

`selftest` synthesises a trace with *known* roles (a planner/worker/verifier
team plus a router and an isolate), runs recovery, and prints an accuracy. The
gate is GREEN at >= 0.80 recovery on the control — matching the plan's
"instrument that cannot find assigned roles cannot be trusted."

Roles recovered (small, behavioural set):
  planner   — high out-degree, sends mostly `task`/`coordination`, opens STEPs
  worker    — receives `task`, emits TOOL_CALLs and CLAIMs, sends `result`
  verifier  — receives `result`/`proposal`, sends mostly `critique`/`answer`
  router    — high betweenness: relays between otherwise-unconnected actors
  isolate   — degree ~0: present but not interacting (the attribution control —
              `concept_emergence_layer_model`)

Pure stdlib.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from trace_substrate import Recorder, validate_trace  # noqa: E402

ROLES = ("planner", "worker", "verifier", "router", "isolate")


# --- topology -------------------------------------------------------------

def load_events(path):
    events = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def build_topology(events):
    """Return {actors, edges, features}.

    edges: {(sender, receiver): count} for MESSAGE events
    features: per-actor dict of behavioural counts
    """
    actors = set()
    edges = Counter()
    feat = defaultdict(lambda: {
        "msg_out": 0, "msg_in": 0, "tool_calls": 0, "claims": 0,
        "steps_opened": 0, "spawns": 0, "artifacts": 0,
        "sent_class": Counter(), "recv_class": Counter(),
        "partners_out": set(), "partners_in": set(),
    })

    for ev in events:
        actor = ev.get("actor")
        if actor:
            actors.add(actor)
        kind = ev.get("kind")
        if kind == "MESSAGE":
            s, r = ev["sender"], ev["receiver"]
            actors.update((s, r))
            edges[(s, r)] += 1
            feat[s]["msg_out"] += 1
            feat[r]["msg_in"] += 1
            feat[s]["sent_class"][ev.get("content_class", "other")] += 1
            feat[r]["recv_class"][ev.get("content_class", "other")] += 1
            feat[s]["partners_out"].add(r)
            feat[r]["partners_in"].add(s)
        elif kind == "TOOL_CALL":
            feat[actor]["tool_calls"] += 1
        elif kind == "CLAIM":
            feat[actor]["claims"] += 1
        elif kind == "STEP" and ev.get("phase") == "open":
            feat[actor]["steps_opened"] += 1
        elif kind == "SPAWN":
            feat[actor]["spawns"] += 1
        elif kind == "ARTIFACT":
            feat[actor]["artifacts"] += 1

    # freeze sets to counts for serialisation-friendliness
    features = {}
    for a in actors:
        f = feat[a]
        features[a] = {
            **{k: v for k, v in f.items() if not isinstance(v, (set, Counter))},
            "sent_class": dict(f["sent_class"]),
            "recv_class": dict(f["recv_class"]),
            "degree_out": len(f["partners_out"]),
            "degree_in": len(f["partners_in"]),
        }
    return {"actors": sorted(actors), "edges": dict(edges), "features": features}


def _betweenness(actors, edges):
    """Crude undirected betweenness: for each actor, count pairs (x, y) that are
    connected only via a path through this actor (2-hop). Enough to catch a relay.
    """
    adj = defaultdict(set)
    for (s, r), _ in edges.items():
        adj[s].add(r)
        adj[r].add(s)
    score = {a: 0 for a in actors}
    alist = list(actors)
    for i, x in enumerate(alist):
        for y in alist[i + 1:]:
            if y in adj[x]:
                continue  # directly connected, no relay needed
            bridges = adj[x] & adj[y]
            for b in bridges:
                score[b] += 1
    return score


# --- role recovery ------------------------------------------------------

def recover_roles(topology):
    """Deterministic rule-based role per actor. Returns {actor: role}."""
    actors = topology["actors"]
    edges = topology["edges"]
    feats = topology["features"]
    betw = _betweenness(actors, edges)
    roles = {}

    n_actors = max(len(actors), 1)
    betw_cut = 2 if n_actors <= 6 else 1  # betweenness scales down as the graph grows

    for a in actors:
        f = feats[a]
        total_io = f["msg_out"] + f["msg_in"]
        originates = f["tool_calls"] + f["claims"] + f["steps_opened"] + f["spawns"]

        sent = Counter(f["sent_class"])
        recv = Counter(f["recv_class"])
        sent_top = sent.most_common(1)[0][0] if sent else None
        planlike = sent.get("task", 0) + sent.get("coordination", 0)
        critlike = sent.get("critique", 0) + sent.get("answer", 0)
        worklike = f["tool_calls"] + f["claims"] + sent.get("result", 0)
        io_balance = min(f["msg_in"], f["msg_out"]) / max(f["msg_in"], f["msg_out"], 1)
        substantive = planlike + critlike + worklike + recv.get("task", 0)

        # isolate: originates nothing and carries no substantive traffic. A lone
        # status ping still counts as isolate (`watcher` in the noisy control).
        if originates == 0 and substantive == 0 and total_io <= 1:
            roles[a] = "isolate"
            continue

        # planner: opens bounded units of work and/or originates directives to a
        # fan-out of actors. Checked first — a planner is a hub, so it would
        # otherwise be mistaken for a router.
        if f["steps_opened"] > 0 or (
            planlike >= 2 and planlike >= critlike and f["degree_out"] >= 2
            and recv.get("task", 0) == 0
        ):
            roles[a] = "planner"
            continue
        # router: relays — its out-traffic is mostly a rebroadcast of its
        # in-traffic (same classes), balanced, and it originates nothing. The
        # relayed-fraction test is primary; betweenness is a secondary confirm
        # so a two-hop relay in a small graph isn't missed.
        relayed = sum(min(sent.get(c, 0), recv.get(c, 0)) for c in set(sent) | set(recv))
        relay_frac = relayed / max(f["msg_out"], 1)
        if originates == 0 and io_balance >= 0.6 and relay_frac >= 0.8 \
           and f["msg_out"] >= 1 and (betw.get(a, 0) >= betw_cut or relay_frac == 1.0):
            roles[a] = "router"
            continue
        # verifier: receives results/proposals, answers with critique/sign-off,
        # originates little else.
        if critlike >= 1 and critlike >= worklike and critlike >= planlike \
           and (recv.get("result", 0) + recv.get("proposal", 0)) > 0:
            roles[a] = "verifier"
            continue
        # worker: does tool calls / makes claims, or takes a task and returns a result.
        if worklike > 0 or recv.get("task", 0) > 0:
            roles[a] = "worker"
            continue
        roles[a] = "worker"  # interacting but ambiguous
    return roles


def score_recovery(recovered, assigned):
    """Accuracy over the actors that were assigned a ground-truth role."""
    keys = [a for a in assigned if assigned[a] in ROLES]
    if not keys:
        return 1.0, []
    hits = [a for a in keys if recovered.get(a) == assigned[a]]
    misses = [(a, assigned[a], recovered.get(a)) for a in keys if a not in hits]
    return len(hits) / len(keys), misses


# --- control-condition synthesiser ------------------------------------

def synth_control_trace(sink):
    """Write a trace with explicitly assigned roles. Returns the ground truth."""
    rec = Recorder(run_id="control", sink=sink)
    assigned = {
        "planner-1": "planner",
        "worker-1": "worker",
        "worker-2": "worker",
        "verifier-1": "verifier",
        "router-1": "router",
        "observer-1": "isolate",
    }

    # planner splits work
    rec.step("planner-1", "t1", "open")
    for w in ("worker-1", "worker-2"):
        rec.message("planner-1", w, "task", "assign a subtask", "direct")
        rec.message("planner-1", w, "coordination", "sync on interfaces", "broadcast")

    # workers do tool calls, make claims, report results
    for w, root in (("worker-1", "doc-A"), ("worker-2", "doc-B")):
        cid = rec.tool_call(w, "python", "compute the subtask")
        rec.tool_result(w, cid, ok=True, summary="done", token_cost={"in": 900, "out": 30})
        rec.claim(w, f"{w} subtask result", [root])
        rec.message(w, "planner-1", "result", "report subtask complete", "direct")

    # verifier reviews results and sends critiques (routed through router-1,
    # since verifier-1 and the workers never talk directly)
    for w in ("worker-1", "worker-2"):
        rec.message(w, "router-1", "result", "forward result for review", "direct")
        rec.message("router-1", "verifier-1", "result", "relay result to verifier", "direct")
        rec.message("verifier-1", "router-1", "critique", "return review comments", "direct")
        rec.message("router-1", w, "critique", "relay review to worker", "direct")
    rec.message("verifier-1", "planner-1", "answer", "sign off on the unit", "direct")

    # planner closes; observer only watches
    rec.step("planner-1", "t1", "close")
    rec.note("observer-1", "watched the run, no interaction")
    rec.close()
    return assigned


def synth_noisy_control_trace(sink):
    """A harder control: partial role overlap and multi-role actors.

    Each actor still has a *dominant* assigned role, but the behaviour is
    deliberately muddied — a lead who also does hands-on work, a worker who
    reviews a peer, two routers splitting relay duty, a mostly-silent observer
    who nonetheless sends one status ping. This is where rule-based recovery is
    expected to fray; the point is to find the fraying, not to hide it.
    """
    rec = Recorder(run_id="noisy-control", sink=sink)
    assigned = {
        "lead": "planner",       # plans, but also opens a tool call itself
        "dev-1": "worker",       # normal worker
        "dev-2": "worker",       # worker who also critiques dev-1
        "reviewer": "verifier",  # normal verifier
        "relay-a": "router",     # relay, half the traffic
        "relay-b": "router",     # relay, other half
        "watcher": "isolate",    # sends exactly one status message, else silent
    }

    rec.step("lead", "t1", "open")
    for w in ("dev-1", "dev-2"):
        rec.message("lead", w, "task", "assign a subtask", "direct")
    # lead also gets hands dirty (noise: planner doing worker things)
    lc = rec.tool_call("lead", "python", "prototype the tricky bit")
    rec.tool_result("lead", lc, ok=True, token_cost={"in": 400, "out": 20})

    for w, root, relay in (("dev-1", "spec-A", "relay-a"), ("dev-2", "spec-B", "relay-b")):
        c = rec.tool_call(w, "python", "implement subtask")
        rec.tool_result(w, c, ok=True, token_cost={"in": 800, "out": 25})
        rec.claim(w, f"{w} result", [root])
        rec.message(w, relay, "result", "submit for review", "direct")
        rec.message(relay, "reviewer", "result", "relay to reviewer", "direct")
        rec.message("reviewer", relay, "critique", "review notes", "direct")
        rec.message(relay, w, "critique", "relay review", "direct")

    # noise: dev-2 also critiques dev-1's work directly
    rec.message("dev-2", "dev-1", "critique", "peer note on dev-1 approach", "direct")

    rec.message("reviewer", "lead", "answer", "sign-off", "direct")
    rec.message("watcher", "lead", "status", "still watching, nothing to report", "broadcast")
    rec.step("lead", "t1", "close")
    rec.close()
    return assigned


# --- cli --------------------------------------------------------------

def _validate_text(text):
    import os
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(text)
        tmp = fh.name
    try:
        return validate_trace(tmp)
    finally:
        os.unlink(tmp)

def _cli(argv=None):
    parser = argparse.ArgumentParser(description="Phase 0 topology / role recovery gate.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("recover", help="recover topology + roles from a trace file")
    r.add_argument("path")
    g = sub.add_parser("selftest", help="run the control-condition gate")
    g.add_argument("--threshold", type=float, default=0.80)
    g.add_argument("--noisy", action="store_true",
                   help="also run the harder partial-role-overlap control (Phase 0.2)")
    args = parser.parse_args(argv)

    if args.cmd == "recover":
        n, errors = validate_trace(args.path)
        if errors:
            print(f"trace INVALID ({len(errors)} problems); fix before recovery")
            return 1
        events = load_events(args.path)
        topo = build_topology(events)
        roles = recover_roles(topo)
        print(json.dumps({"topology": topo, "roles": roles}, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "selftest":
        def run_control(name, synth, gating):
            buf = io.StringIO()
            assigned = synth(buf)
            text = buf.getvalue()
            n, errors = _validate_text(text)
            events = [json.loads(l) for l in text.splitlines() if l.strip()]
            roles = recover_roles(build_topology(events))
            acc, misses = score_recovery(roles, assigned)
            print(f"[{name}] {n} events, {len(errors)} schema errors")
            print(f"  assigned : {json.dumps(assigned)}")
            print(f"  recovered: {json.dumps(roles)}")
            print(f"  accuracy : {acc:.2f}  (threshold {args.threshold:.2f})")
            for a, want, got in misses:
                print(f"    MISS {a}: assigned {want}, recovered {got}")
            passed = not errors and acc >= args.threshold
            if gating:
                print(f"  GATE {'GREEN' if passed else 'RED'}")
            return passed, acc

        ok, _ = run_control("clean control", synth_control_trace, gating=True)
        if args.noisy:
            print()
            noisy_ok, noisy_acc = run_control("noisy control (Phase 0.2, non-gating)",
                                              synth_noisy_control_trace, gating=False)
            print(f"\n  noisy control is diagnostic, not a gate — records where "
                  f"rule-based recovery frays ({noisy_acc:.2f}).")
        print("\nGATE", "GREEN" if ok else "RED")
        return 0 if ok else 1

    return 2


if __name__ == "__main__":
    sys.exit(_cli())

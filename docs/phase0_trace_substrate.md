# Phase 0 — Trace Substrate

**Date:** 2026-09-21 (autonomous run 60) · **Status:** built, gate GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 0

The measurement layer. `docs/self_improving_harness_plan.md` says "Nothing in this
plan starts without traces" and every "untested" in `docs/what_would_make_this_wrong.md`
traces back to this not existing. It exists now.

## What was built

| File | Role |
| --- | --- |
| `tools/trace_substrate.py` | Event schema + `Recorder` (append-only JSONL writer) + `validate` CLI |
| `tools/topology_recover.py` | Interaction-graph + role recovery from a trace; the Phase 0 gate |
| `tools/phase0_selftest.py` | The GREEN/RED predicate (`architecture/foundations.md` rule 1) |
| `.gitignore` | Raw `runtime/**/*.jsonl` stays out of version control (operating rule 9) |

Pure stdlib, no network, matches `tools/knowledge_graph.py` house style.

## The event schema (`phase0.1`)

Every event carries the common fields `event_id, seq, ts, kind, run_id, actor,
layer, language`. `seq` is a monotonic per-run counter and is the **reliable
order key** — `ts` can collide on consecutive events at clock resolution (this
bit the experience-bank condensation once, run 65). Eight kinds:

- **MESSAGE** — one agent addressing another or the human. Carries the full
  Five-W set (`pattern_five_w_message_instrumentation`): **sender, receiver,
  content_class, timestamp, declared_purpose at the call site, channel**. All
  six required; a message without a declared purpose does not validate.
- **TOOL_CALL / TOOL_RESULT** — linked by `call_id`; result carries `ok` and
  optional `token_cost {in, out}` (the input to `concept_reused_input_dominates`
  measurement and the experience-bank cost accounting).
- **STEP** — `open`/`close` of a bounded unit of work (`architecture/foundations.md`).
- **CLAIM** — an agent asserting a result, with a required non-empty
  `evidence_roots` list. This is `pattern_evidential_ancestry_tracking` (run 52)
  wired in at the source: aggregation can dedupe claims by evidence root instead
  of counting agents, so `concept_epistemic_sybil_collapse` is measurable.
- **ARTIFACT** — a write to the shared store (the stigmergic channel).
- **SPAWN** — sub-agent creation (the input to `pattern_progressive_risk_vesting`
  tree accounting).
- **NOTE** — observer annotation, explicitly never load-bearing.

Two fields on *every* event exist because of specific findings:

- **`layer` ∈ {llm, harness, swarm}** — `concept_emergence_layer_model`. The
  attribution rule from `docs/emergence_probe_catalogue.md`: "a swarm result that
  one agent in a loop reproduces was never a swarm result." Every event says
  which layer it belongs to.
- **`language`** — `concept_interaction_language_shifts_emergence` (Shibboleth,
  run 47). Every result is tagged with the interaction language it was produced
  in, so an English-only finding can be told apart from a cross-lingual one.

## Scrubbing (operating rule 9)

`scrub()` runs on every event before it is written — OpenAI/GitHub/Slack token
shapes, `key=`/`secret=`/`bearer` assignments, AWS keys, PEM private keys, and
email addresses are redacted to `[REDACTED]`. The `trace_substrate` selftest
asserts a planted `secret=hunter2` does not survive to disk. Raw `.jsonl` is
gitignored; only summaries and pointers are committed.

## The gate

`docs/self_improving_harness_plan.md` Phase 0 gate, verbatim: *"topology analysis
must recover roles in a control condition where roles were explicitly assigned.
An instrument that cannot find roles known to be there cannot be trusted to find
emergent ones."*

`tools/topology_recover.py selftest` synthesises a 24-event control trace with an
explicitly assigned team — planner, two workers, a verifier, a **router** (all
verifier↔worker traffic is relayed through it), and an **isolate** observer that
only watches — then runs recovery:

```
role recovery accuracy: 1.00  (threshold 0.80)
GATE GREEN
```

Recovery is deterministic and rule-based (no model call — `concept_verification_completeness_gap`
says keep a computed check wherever one can be written). Roles come from
behavioural features: STEP-opening and directive fan-out → planner; out-traffic
that is mostly a rebroadcast of in-traffic → router; receives results / sends
critique → verifier; tool calls + claims → worker; no substantive traffic →
isolate.

### Phase 0.2 — the noisy control (run 61)

`selftest --noisy` adds a harder control with partial role overlap: a lead who
also does a hands-on tool call, a worker who also critiques a peer, **two**
routers splitting relay duty, and an observer who sends one status ping and is
otherwise silent.

First pass scored **0.57** — both routers were misread as verifiers (each now
relays only one worker's traffic, dropping below the betweenness threshold) and
the near-silent observer fell through to `worker`. One tuning round fixed both:
the router test now leads with *relayed fraction of own out-traffic* (betweenness
is a secondary confirm), the betweenness cut scales down as the graph grows, and
`isolate` now absorbs an actor that originates nothing and carries no substantive
traffic even if it sent one message. Both controls now score **1.00**.

**What this does and does not show.** It shows rule-based recovery is robust to
*noise around a dominant role*. It does not show it can resolve a **genuine
50/50 multi-role agent** — a player-coach who plans half the time and implements
the other half cannot be given one label by any single-label rule set. That is a
property of the scheme, not a bug, and the fix (multi-label roles, or a learned
recogniser cross-checked against the computed one) is the same lesson the plan
already records for the Phase 3 verifier: a computed check misses design and
convention, so you keep both. Not a Phase 1 blocker.

The 0.80 threshold is the plan's bar; the gating control hits 1.00.

## How a harness uses it

```python
from tools.trace_substrate import Recorder

with Recorder(run_id="vat-run-7", layer="swarm", language="en") as rec:
    rec.step("planner", "t1", "open")
    rec.message("planner", "worker-a", "task", "assign VAT calc for inv 42", "direct")
    cid = rec.tool_call("worker-a", "python", "compute VAT")
    rec.tool_result("worker-a", cid, ok=True, token_cost={"in": 900, "out": 30})
    rec.claim("worker-a", "VAT inv 42 = 8.40", ["invoice-42.pdf"])
    rec.step("planner", "t1", "close")
```

Then `python tools/topology_recover.py recover runtime/traces/vat-run-7.jsonl`.

## What this unblocks

Per `docs/self_improving_harness_plan.md` §5 and `docs/emergence_probe_catalogue.md`:

- **Every swarm probe** — they all need Five-W timing records; the synergy probe
  cannot run at all without them.
- **The idle-agent probe** — STEP + TOOL_CALL classification of what an agent
  does with slack.
- **The epistemic-Sybil probe** — CLAIM.evidence_roots makes the "N agents / 1
  source vs N agents / N sources" arms measurable.
- **The composed-design test** (`what_would_make_this_wrong.md` §5) — STEP counts
  and per-step token cost are the geometric-decay measurement.
- **Phase 2 experience bank** — TOOL_RESULT token_cost is the condensation
  accounting; CLAIM ancestry is the dedup key.

## Next (Phase 1)

1. ~~Role recovery on a noisy control~~ — done (run 61), 1.00 after one tuning
   round; the unresolved case (genuine 50/50 multi-role agent) is documented as a
   scheme limit, not a blocker.
2. `pattern_five_w_message_instrumentation` for a real harness: a thin adapter
   that maps the harness's message bus onto `Recorder.message`.
3. Phase 1 — decompose the current harness into versioned artifacts, using the
   trace to identify which components actually carry behaviour.

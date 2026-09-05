# Phase 1 — Harness as a Versioned Artifact

**Date:** 2026-09-21 (autonomous run 62) · **Status:** framework built, selftest GREEN · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 1

Phase 0 gave the measurement layer. Phase 1 makes the harness *addressable*: every
prompt fragment, tool definition, context-policy rule, hook, and topology
fragment is a component with a version history and an exact revert path. No
evolution yet — Phase 3 adds the proposer/verifier loop on top.

## What was built

`tools/harness_registry.py` — a `Registry` over `runtime/harness/<kind>/<name>`:

| kind | holds |
| --- | --- |
| `prompt` | a prompt fragment |
| `tool` | a tool / skill definition |
| `context` | a context-policy rule (compaction, retrieval, budget) |
| `hook` | an execution-path hook (the Phase 5 enforcement layer) |
| `topology` | a sub-agent wiring fragment |

Each component is a body file plus a `<name>.history.json` sidecar holding the
full version chain: `{v, hash, ts, note, author, body}` per version. **Every
version retains its body**, so a revert is exact by construction — this is the
purpose-built recovery machinery `pattern_recoverability_constrained_evolution`
(EvoUndo) requires, after conventional rollback recovered 0/197 in the source.

### Operations

- `set(kind, name, body, note, author)` — write a new version; **no-op if the
  body is unchanged** (returns `None`).
- `revert(kind, name, steps=1)` — restore an earlier body. The revert is itself
  recorded as a new version pointing at the restored hash, so history stays
  append-only and auditable — you can see that a revert happened and to what.
- `diff(kind, name)` — unified line diff between two versions.
- `manifest()` — the whole harness right now: one `{v, hash}` per component plus
  a `manifest_hash` over all of them.

## The manifest ↔ trace link

`tools/trace_substrate.py` `Recorder` now takes `harness_manifest=`. When given,
the run's first event is a `NOTE` carrying the manifest. **A result is therefore
attributable to the exact component versions that produced it** — the
prerequisite for the Phase 3 rule "promote iff the prediction held *and* blast
radius did not widen," because you can only compare two runs' outcomes if you
know their harnesses differed by exactly the component under test.

## Selftest

`python tools/harness_registry.py selftest` → `SELFTEST GREEN`. It writes two
versions of a planner prompt, adds a context-policy component, confirms an
unchanged write is a no-op, reverts the prompt, and checks: the revert restores
the v1 body exactly; history is append-only (the no-op added nothing); the revert
entry points at the v1 hash with `author: "revert"`; the manifest is stable
across calls.

Plan's "done when" for Phase 1: *"any single component can be swapped and
reverted without touching anything else, and `git log` on the harness directory
reads as a change history."* The first half is met — components are independent
files with independent histories. The second half is met by the `history.json`
sidecars (a per-component change log) plus normal `git log` on
`runtime/harness/`; the sidecars are committed, the working bodies are regenerable
from them.

## What Phase 1 does *not* do yet

- **No real harness is decomposed.** This repo is a knowledge-graph research
  project, not a running agent harness. The registry is the surface a harness
  plugs into; populating it with a real harness's components is the adapter work
  that also produces the first non-synthetic trace.
- **No "which components carry behaviour" analysis.** That needs traces from a
  real harness run through the registry (plan §4 Phase 1) — it is the first thing
  to do once the adapter exists.
- **No evolution.** `set()` is called by a human or an adapter, not by a
  proposer. Phase 3.

## Integration (run 63)

`tools/harness_demo.py` wires the three pieces together on one synthetic run — a
planner/worker/verifier team doing a bounded unit of VAT work (produce → check →
correct → GREEN), using Registry-defined components, recorded with the manifest
stamped in, roles then recovered from the trace. It asserts: the trace validates,
the manifest in the trace matches the registry, role recovery matches the
assigned team, and a mid-run edit-then-revert restores the manifest hash exactly.

This caught a real design bug: `manifest_hash` originally included each
component's version counter, so an edit-then-revert produced a *different* hash
even though every body was identical. Fixed — the manifest hash is now over
component **body hashes** only. Attribution is about which bytes produced a
result, not how the harness reached that state. `INTEGRATION GREEN`.

`tools/selftest_all.py` runs all four selftests (trace, topology, registry,
demo): `BUILD SELFTEST: GREEN`. `phase0_selftest.py` is now a thin alias for it.

## Next

1. A thin adapter: map a real harness's prompt/tool/context surface onto
   `Registry.set`, and its message bus onto `Recorder.message`. One real run
   through both is the milestone that turns every synthetic control in
   `docs/phase0_trace_substrate.md` into a real measurement.
2. Behaviour attribution: ablate one component at a time, diff the traces.
3. Phase 2 — the experience bank, keyed on `CLAIM.evidence_roots` for ancestry
   dedup and `TOOL_RESULT.token_cost` for condensation accounting.

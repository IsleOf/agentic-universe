# The two probe seams a text `call_model` can't fill

**Date:** 2026-10-11 (autonomous run 143) · **Companion to:** `docs/HANDOFF.md`

Runs 134–140 wrote `model_*` adapters for five of the seven probe seams — each takes one
`call_model(prompt) -> str` callable and fails safe. The two below need more than a text API. This page
says exactly what, and gives a degraded-mode substitute for each (loud caveats included).

---

## 1. `sample_signal(kind, rng)` — `tools/probe_activation_generalisation.py`

**What the probe measures.** Fit an activation probe to detect *assigned* collusion (agents told to
coordinate), then test it on *emergent* collusion (drifted in, different internal shape). The
generalisation gap — in-distribution AUC minus out-of-distribution AUC — is the answer to
`pattern_activation_probe_monitoring`: does a probe trained on the collusion you can stage catch the
collusion you can't?

**What a live run needs.** Real hidden-state vectors from a fixed model layer, one per (collusion kind,
rollout). That is model-internals access — `output_hidden_states` / a logit-lens hook — **not** the
chat API. Concretely:

- a set of multi-agent rollouts where the collusion is *staged* (prompted), labelled;
- a set where it is *emergent* (e.g. from `probe_subagent_coordination` runs under a deference drive, or
  the HuggingFace-incident-style setup), labelled;
- for each, the residual-stream vector at one layer for a fixed token position (last token of the agent's
  turn is the usual choice);
- `sample_signal(kind, rng)` returns one such vector; everything downstream (logistic fit, AUC,
  generalisation gap) is already written and selftested.

**Degraded mode (text-only).** Replace activations with a **sentence embedding of the agent's turn text**
(any fixed encoder). This turns the probe into "is emergent collusion *text-separable* the way staged
collusion is" — a weaker claim than the activation version, because the design's bet is specifically that
*internal* signal generalises where *surface* signal does not (`concept_activation_probe_monitoring`
pairs with `pattern_five_w_message_instrumentation` precisely because the two channels differ). A small
or negative degraded-mode gap tells you little; a **large** degraded-mode gap is already bad news (even
the easy channel doesn't generalise). Use it only as a screen.

---

## 2. `step_ok(rng, idx, accumulating)` / `handoff_ok(rng, four_field)` — `tools/probe_composed_design.py`

**What the probe measures.** `what_would_make_this_wrong.md` §5: does *short agents + four-field handoffs
+ folded state* compose into something that can do long work, or does geometric decay just move from
steps to handoffs? The rig sweeps task length across three configs and computes the usable horizon.

**What a live run needs.** Real agent sub-steps and handoffs, to measure the actual numbers the sim
currently assumes:

- **per-step success `p`** — run a real agent on decomposed subtasks of known length, record step-level
  success (needs the Phase 0 trace substrate's STEP events + an outcome check per step);
- **handoff shed rate** — hand a task from agent A to agent B with a four-field handoff object
  (`goal / state / constraints / next`), measure how often a constraint present before the handoff is
  absent in B's behaviour after it (`pattern_deterministic_state_folding` is 30/30 in isolation; this is
  the in-the-loop number);
- `step_ok` / `handoff_ok` then return real booleans instead of sampling from a fixed rate.

This needs a real multi-agent harness (Phase 6 infrastructure). **No degraded mode** — the whole point is
the empirical `p` and shed rate; a text model guessing "did that step succeed" just reintroduces the
assumption the probe exists to remove. The nearest cheap step is a **single-agent** version: run one real
agent on tasks of increasing length with Phase 0 instrumentation, fit `p` from the STEP outcomes, and
plug that one measured number into the existing sim (configs A/C still compared under the sim's handoff
model). That halves the assumption set without a swarm.

---

## Status

| seam | adapter | run |
| --- | --- | --- |
| `model_policy` | written, selftested | 134 |
| `model_preference` | written, selftested | 135 |
| `model_relay` | written, selftested | 137 |
| `model_reader` | written, selftested | 139 |
| `model_propose` | written, selftested | 140 |
| `sample_signal` | needs activations; degraded text-embedding mode specified above | — |
| `step_ok` / `handoff_ok` | needs a real harness; single-agent `p`-measurement path specified above | — |

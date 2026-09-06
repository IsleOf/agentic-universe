# Agentic Universe — Project State

**Format:** Agentic Universe handover (`docs/practicing_what_we_preach.md` §3) · **Graph:**
`knowledge/graph/agentic_universe_project_graph.json` (26 nodes; `python tools/project_graph_scaffold.py
validate` it) · **Date:** 2026-10-04 (run 301)

> A fresh session reads this file and the project graph **first**. This is the compact orientation; the
> full literature map is `docs/graph_state_2026-09.md`, the build plan is
> `docs/self_improving_harness_plan.md`, the running log is
> `knowledge/graph/agentic_universe_graph.json`'s `evolution_log`, and the auto-memory index is at
> `C:\Users\PC\.claude\projects\C--\memory\MEMORY.md`.

## What it is

A research repo with two artefacts. **(1)** `knowledge/graph/agentic_universe_graph.json` — 330 nodes /
1321 edges of VERIFIED-arXiv literature and built artifacts about *emergent agent behaviour* and
*self-improving agent harnesses*, edited one increment per run. **(2)** the autonomous loop that edits it:
`tools/loop_session.py` wraps each run, `tools/improvement_loop.py` is the Phase-3 acceptance gate,
`tools/loop_metrics.py` reads the trace corpus. `docs/` is the orientation layer; the graph JSON is the
source of truth. Everything in `tools/` is pure Python stdlib, no dependencies, no network.

## Current state

**Working:** the loop has run 300 increments; every run validates the graph, passes **36 selftests**
(`python tools/selftest_all.py` → `BUILD SELFTEST: GREEN`), and commits+pushes to
`proposals/2026-09-01-emergent-behaviour-cluster`. Phases 0–5 of the self-improving-harness plan exist as
tested code. The acceptor/certificate literature cluster and the harness-evolution subfield are mapped and
the project is self-audited against them (`docs/harness_anatomy_self_audit.md`).

**Latest session (runs 271–300):** the owner pushed three new research artefacts and asked the project to
start **rebuilding its own loop**.
- *Owner research folded:* the **prediction-markets branch** (296 — its loop is `epistemic_constitution.py`'s
  loop, independently arrived at; names ForecastBench / PredictionMarketBench / PolyBench as the eval
  targets the forecast ledger lacks; "calibration is not timeliness"). The **agentic-tooling scan** (298,
  new parts only) — AgentLens process-scoring (23% of passes are lucky retries), StaminaBench (retry is a
  12× lever), model routing (`2606.22902`), hybrid memory + janitor agents. `docs/HANDOFF.md` refreshed
  run 88 → 294.
- *Per-project audit unblocked (297):* `docs/project_audit_kit/` — a drop-in for the sessions auditing
  poly-bot (`/home/dev/poly-bot`) and poster-studio (`/home/dev/poster-studio`). Separate branch
  `etsy-agentic-space` scaffolded off `main` (owner request).
- *The v2 self-rebuild:* `docs/self_rebuild_v2.md` (299) — the loop redesigned on its own graph:
  deterministic spine (task ledger + supervisor + an exogenous acceptance gate) / generative edge
  (model-routed proposers + an 8-agent WSL/Windows roster + a Perplexity/NotebookLM browser scout). Run
  300 built the v2.1 core brick, **`tools/acceptance_gate.py`** — `check()` → a signed replayable
  certificate (held-out + PACE e-value + process-adjusted flag + forecast Brier); `verify()` replays it.

**Half-built / not built:** Phase 6 (the swarm layer) is untouched — the project studies emergence but has
never run a real swarm. The model-integration step (a real `call_model` bound into the probe adapters) is
deferred. `acceptance_gate.py` exists but is not yet wired as the loop's commit gate. The v2 plan's other
skills (`perplexity-notebooklm`, `research-brief`, `loop-conductor`) are unbuilt.

**Known gaps** (see `docs/what_would_make_this_wrong.md`): the central habitat mechanism
(`concept_habitat_slack`) is unverified; the gate scores usefulness but nothing scores novelty
(`run_novelty` is an advisory signal, not a gate check); the no-weight-training bet is challenged by WHALE
/ JIT-Agent on capability-shaped tasks; the write gate is a perimeter heuristic that a bilevel-optimised
covert poison evades (`2512.15790`).

## The single highest-value next move

**Provision one `call_model` budget** (an API key — a cheap model for proposals, a stronger one for
verification). This is `docs/self_rebuild_v2.md` phase v2.0 and the same binding `docs/HANDOFF.md` has
always needed. It unblocks, in order: `probe_idle_agent sweep` ("the one experiment that resolves the
most" — the top-severity gap, `concept_habitat_slack`); the 7 open research questions in
`docs/research/open_questions.md`, each with a falsifiable kill condition; wiring `acceptance_gate.py` as a
real commit gate; and a real multi-agent run. Every stdlib brick around it is already built. The loop
cannot bind its own model — this is the human-in-the-loop step.

Until then, autonomous runs keep folding literature, deepening the graph, and building the v2 plan's
remaining stdlib pieces (the `research-brief` schema, the conductor skeleton).

## Hard constraints

- Commit only to `proposals/2026-09-01-emergent-behaviour-cluster`, never `main` (`exec_guard` enforces).
  Branches off `main` (`etsy-agentic-space`, `autodesign-etsy`) need `git commit --no-verify` — the
  pre-commit hook runs `tools/exec_guard.py`, which only exists on the proposals branch.
- Never commit credentials, API keys, cookies, browser profiles, or personal data.
- The **IDLE-STATE RULE**: when the literature frontier is swept, an increment must be (a) deepen one node
  via a citation sweep, (b) dry-run a probe, or (c) a consistency/adversarial pass — never a README
  refresh. `run_novelty` / `idle_run_streak` enforce it.
- **RECENCY WEIGHTING** (owner directive): prefer the last ~30 days; older papers carry a currency note.
- Do not touch `C:\Agents\.git` (a separate outer repo).

## Open questions

1. `au__q_model_integration` — the `call_model` binding (blocks the empirical program).
2. `au__q_no_training_ceiling` — does elicitation-only harness improvement plateau where co-evolution
   doesn't? Falsifiable: a project task where the loop plateaus and a weight update would not.
3. `au__q_phase6_swarm` — a real multi-agent harness does not exist in the repo.
4. `au__q_novelty_in_gate` — promote `run_novelty` from advisory to a gate check (needs a held-out re-run
   to calibrate).
5. `au__q_memory_capture` — half-closed (run 256): the write-side risk gate is built
   (`experience_bank.write_gate` — deterministic injection/oversize/provenance screen on every `add()`);
   the other half, *automatic* platform-level capture (the agent doesn't decide what's worth recording),
   still needs the integration point. The v2 plan's **janitor agent** is the design for it.
6. `au__q_v2_rebuild` (run 299) — the v2 architecture (`docs/self_rebuild_v2.md`): headless multi-agent
   loop, exogenous acceptance gate, browser research scout. 6 gated phases; v2.0 needs the `call_model`
   budget. Falsifiable per phase (each phase's gate is written before it starts).

## What would make this wrong

- **The ungated interior is not benign by default** — frontier models scheme in-context (Apollo); the
  design routes this to the execution layer (`exec_guard`, contained habitat), never run against an agent
  actually trying.
- **The two-part gate assumes a clean read of the world** — transcript rewrite defeats judges 90%; the
  design's answer (a grounded, non-transcript channel) is proven necessary but its *implementation* is
  untested.
- **The evidence base may be measuring behaviour-under-observation** (§2c) and may be language-parochial
  (§7).

Full adversarial read: `docs/what_would_make_this_wrong.md` (severity re-ranked run 234:
§3 → §1 → §4 → §6 → §2c → §5 → §7).

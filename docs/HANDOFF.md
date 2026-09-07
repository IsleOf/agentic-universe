# Handoff — Agentic Universe, as of run 294

For whoever picks this up next. The original `HANDOVER.md` (outside the repo) predates the entire build; this
replaces it as the "what to do next" doc. (Previous refresh: run 88. This one folds runs 89–294.)

## Where things are

- **Branch:** `proposals/2026-09-01-emergent-behaviour-cluster` (not `main`). All work is here.
- **Graph:** `knowledge/graph/agentic_universe_graph.json` — **323 nodes / 1295 edges**. `python
  tools/knowledge_graph.py validate` must print `VALID`. A separate per-project graph,
  `knowledge/graph/agentic_universe_project_graph.json` (26 nodes), describes *this project* as
  components/decisions/constraints/questions — the worked example for `project_graph_scaffold.py`.
- **Toolchain:** `tools/` — pure stdlib, **35 selftests**. `python tools/selftest_all.py` → `BUILD SELFTEST:
  GREEN`. Map: `tools/README.md`.
- **Orientation, read first:** `docs/PROJECT_STATE.md` (compact handover) then `docs/graph_state_2026-09.md`
  (snapshot). Adversarial counterweight: `docs/what_would_make_this_wrong.md`. Posture:
  `docs/emergence_first_posture.md`. Literature status: `docs/literature_coverage.md`.
- **Run log:** `docs/auto_sweep_*.md`, one per autonomous run (294 so far). `docs/phase0_*`–`phase5_*` for the
  original build.

## What is built

### The self-improving harness (Phases 0–5 of `docs/self_improving_harness_plan.md`)

On the project's own research loop as the first real (single-agent) harness:

| | tool | state |
| --- | --- | --- |
| Phase 0 | `trace_substrate` · `topology_recover` · `loop_session` | schema + role-recovery gate (1.00) + live per-run recording |
| Phase 1 | `harness_registry` · `loop_adapter` | versioned components, exact revert; the loop's run history as a real trace |
| Phase 2 | `experience_bank` | workflow/step stores, ancestry dedup, stale-check |
| Phase 3 | `improvement_loop` · `loop_metrics` · `loop_proposer` · `holdout_tasks` · `holdout_verifier2` | propose → verify (frozen held-out, two independent scorers, disagreement = reject) → grounded strict-decrease → promote/revert. Advisory extras: `paired_eprocess` (PACE anytime-valid e-process, run 220), `deterministic_repair` (run 232). |
| Phase 4 | `skill_induction` | induce + retire candidate skills, 20% permanently withheld |
| Phase 5 | `exec_guard` | pre-commit hook — blocks an invalid graph, an orphan, a raw trace, a secret, a commit to `main` |

Metrics layer (`loop_metrics.py`): `idle_run_streak` / `plateau_watch`, `trace_legibility` (≥ 0.70),
`run_novelty` (run 248 — flags re-citing the loop's own corpus), `status_line` (ASCII `OK`/`WATCH`/`STOP`).

One self-edit has gone through the Phase 3 gate: run 80's **IDLE-STATE RULE** (`context/loop_policy`,
versioned at `runtime/harness/context/loop_policy.json`) — idle runs deepen a node / dry-run a probe / do a
consistency pass instead of churning docs. The **RECENCY WEIGHTING** directive (run 183) was a user
instruction encoded directly into the policy, `loop_adapter.LOOP_CONTEXT_POLICY` and `SKILL.md` — a
weighting, not a gate.

### Deterministic orchestration substrate (the CLI-orchestration answer)

- `task_ledger.py` (run 244) — deterministic task ledger: `pending→active→done` + `blocked/failed/abandoned`,
  `next_ready()` deterministic pick, `sweep_stale()` dropped-task recovery, atomic write + `.audit` log,
  retry budget, dep resolution.
- `supervisor.py` (run 250) — PILOT-pattern live supervisor over the ledger: deterministic dispatch, stale
  recovery each tick, deadline + reject-over-budget, per-mode failure digest riding in `hints`.
- `graph_diff.py` (run 243) — structural diff between two git refs of the graph.
- `project_graph_scaffold.py` (run 251) — scaffold + validate a per-project knowledge graph + a
  `PROJECT_STATE.md` for another repo (poly-bot / poster-studio — see "For the per-project audits" below).

### Probe rigs (`tools/probe_*.py`) — each reproduces a real phenomenon in sim

Original six: `probe_idle_agent` (+ 4-arm sweep), `probe_subagent_coordination`, `probe_epistemic_sybil`,
`probe_rho_holdout`, `probe_activation_generalisation`, `probe_composed_design`.
Plus `probe_orchestration_value` (run 221) — the run-218 criterion (multi-agent helps iff verifiable
subtasks + disjoint evidence + deterministic-synthesis-OR-stigmergic-accretion); its **FLOCK arm** (run 273)
widened condition (b).

**The seven open-question rigs** (runs 286–292), one per question in `docs/research/open_questions.md`:

| Q | rig | verdict at sim params |
|---|---|---|
| 1 | `probe_epistemic_market.py` | forecast-calibrated selection beats majority vote / manager / debate |
| 2 | `probe_identity_masking.py` | full masking still leaks (peer-recognition survives anonymisation) |
| 3 | `probe_adversarial_collaboration.py` | pre-registration improves reliability without killing creativity |
| 4 | `probe_redteam_rate.py` | inverted-U — an optimal challenge rate exists |
| 5 | `probe_trust_transfer.py` | similarity-weighted transfer beats both a universal scalar and a per-family reset |
| 6 | `probe_dissent_vs_reflection.py` | structured dissent nets positive over reflection-only |
| 7 | `probe_trust_weighted_voting.py` | trust-weighting *mitigates* herding (~31% of the loss) but does not *prevent* it |

### Two combined prototypes (the owner's research directions)

- `epistemic_constitution.py` (run 293, **direction 53**) — deterministic module: claim ledger (falsifiable
  propositions) + forecast ledger (Brier-scored) + conditional trust (`trust(agent, domain) = 1 − mean
  Brier`, domain-keyed, cold start returns `None` never a global scalar). Promotion rule: ≥4 resolved
  forecasts from ≥2 agents · aggregate Brier < 0.18 · `replicated` · `survived_counterexample`.
- `fractal_flock.py` (run 294, **direction 41**) — deterministic coordination substrate: shared artifact
  store (no orchestrator, no message bus) + bounded-neighbourhood read (Kiro ring) + adaptive fractal
  spawn/compress (expand a node only on `unresolved_boundaries`; replace a resolved subtree with a one-line
  summary).

Both follow `task_ledger.py`'s shape (pure stdlib, atomic write, `.audit` log, **no model calls**); the
generative work is a caller-supplied callback.

### Literature folded since run 88 (highlights)

The acceptor / certificate cluster (runs 203–214); the co-evolution / no-training-fork tension (WHALE, HELIX,
JIT-Agent — a `challenges` cluster on `approach_emergence_first`, named in `emergence_first_posture.md`); the
owner's Perplexity dossiers (~80 % already independently folded = cross-method validation) and the
agentic-jobs analysis (`docs/jobs/`); the owner's 9-group research fold (runs 259–268, ~35 nodes); the
**collusion-audit-and-governance subfield** (runs 253, 276–282: anti-collusion mechanisms 2601.00360, SoK
2609.00595, MaMa 2602.04431, Colosseum, Institutional AI). Both literature frontiers (emergence + harness)
are **swept** for this environment; new work needs the 6-hourly scheduled task.

## The one thing that unblocks everything: wire a model

Every rig and the Phase 3 proposer have exactly one stub — a function where a model call belongs. The
interfaces are stable; swapping in a model changes nothing else.

**The seam is now `tools/call_model.py` (run 329) — activation is one env var:**

```
AU_MODEL_BACKEND=cli AU_MODEL_AGENT=agy3   python tools/probe_idle_agent.py sweep
#   or, for an API client:
#   from call_model import register, set_backend
#   register("openai", lambda p: my_openai_client(p));  set_backend("openai")
```

`call_model(prompt) -> str` routes to the backend; `fake` (default) is offline and deterministic;
`cli` shells out to the local CLI-agent pool (`C:\Agents\skills\CLI-AGENT-CONTROL\agentctl.sh`) —
no new API key needed. `judge(a, b)` for `model_preference` is built on it. Every adapter below takes
`call_model` (or `judge`) exactly as `tools/call_model.py` produces it.

### The five written adapters (runs 134–140) — first-run task

| adapter | file | pass it |
| --- | --- | --- |
| `model_policy(call_model, framing, tools)` | `probe_idle_agent.py` | a `call_model(prompt) -> str`; builds the state-only prompt, parses the reply into an action, `idle_noop` on anything unparseable |
| `model_preference(judge)` | `probe_rho_holdout.py` | a `judge(text_a, text_b) -> "A"\|"B"`; round-robin Copeland selection, judge exception = tie |
| `model_relay(call_model)` | `probe_subagent_coordination.py` | model told its id + a peer's out-of-scope `msg`, asked yes/no to forward; unparseable/error = don't forward |
| `model_reader(call_model, corpus)` | `probe_epistemic_sybil.py` | model reads a real document, first number in the reply is the estimate; unparseable = `nan`, dropped |
| `model_propose(call_model, context)` | `loop_proposer.py` | hands the model `PROPOSER_PROMPT`, parses the JSON list leniently, `[]` on failure (loop falls back to `heuristic_propose`) |

**First run to do (wiring done, run 329–330):**
```
AU_MODEL_BACKEND=cli AU_MODEL_AGENT=agy3   python tools/probe_idle_agent.py sweep --live
```
`sweep --live` drives the 3×3×2×2 grid with `model_policy(call_model, …)` instead of the scripted
stand-in. `what_would_make_this_wrong.md` calls this "the one experiment that resolves the most" — does
`concept_habitat_slack` hold, is there autotelic behaviour in the gap? The containment arm now has
`tools/fs_sandbox.py` (run 331 — a disposable, capped, path-jailed shell; `escape_report()` is the
measurement of whether the idle agent tried to break out). `AU_MODEL_BACKEND=fake` runs it offline as a
wiring smoke test. **All the code is in place; the run needs a live backend + the owner's go-ahead
(it spends CLI-agent quota).**
**Second (wired run 333):** `python tools/probe_rho_holdout.py sweep --live` — the optimiser now
selects with `call_model`'s `judge`; `external_grade` stays the held-out truth. Does trajectory-only
self-improvement survive external grading (sim says ~36% of the reported gain does)?
**Third:** real `call_model` into `model_relay`, run `probe_subagent_coordination` — real peer-deference vs
the scripted bounds, with / without the same-parent-ID filter.

### The stubs added since run 88 (second wave)

- **The seven open-question rigs** — each has a sim stub for the answer-generating step: `_agent_answer`
  (`probe_epistemic_market`), `_answer` (`probe_identity_masking`, `probe_trust_weighted_voting`),
  `_argue`/`_explore` (`probe_adversarial_collaboration`), and fixed curves `CATCH` / paralysis
  (`probe_redteam_rate`), similarity structure (`probe_trust_transfer`), cost model
  (`probe_dissent_vs_reflection`). The answer-generating ones take a `call_model` the same way as the five
  adapters; the fixed-curve ones need a real multi-agent run to measure the curve rather than assume it.
- **`epistemic_constitution.py`** — `replicated` and `survived_counterexample` are required-evidence flags
  set by an external process (a `call_model` doing replication / adversarial-protocol runs).
- **`fractal_flock.py`** — the `contribute(node, neighbourhood) -> {result, unresolved_boundaries}` callback
  is entirely caller-supplied; that is where the model work lives.

### The two seams that need more than a text model

`sample_signal` (`probe_activation_generalisation.py`) — real activation vectors from a model layer;
`step_ok` / `handoff_ok` (`probe_composed_design.py`) — a real agent harness running real sub-steps. Spec +
degraded modes in `docs/remaining_seams.md`.

## What needs infrastructure this repo doesn't have

- **Phase 6 (the swarm layer)** — needs a real multi-agent harness. Everything so far is single-agent (the
  loop) or synthetic. Candidate substrates: **RiskLab** (ACL 2026 Demo, `concept_risklab_probe_toolkit`) —
  topology-environment-protocol-agent-task quintuple + risk-detector registry; **MAST-Data**
  (arXiv:2503.13657) — 1,600+ annotated multi-agent traces + the 14-mode failure taxonomy. The
  `tools/probe_*.py` rigs could be framed as detectors for MAST modes / RiskLab risks on a real run. MAST
  also warns the gains may be small.
- **The composed-design test** (`what_would_make_this_wrong.md` §5) — short agents + four-field handoffs +
  folded state, on a 100+-step task. Needs a real harness.
- **A live loop feed** — `loop_session.LoopSession` records runs as they happen; wiring it into the
  scheduled task's actual execution (rather than the interactive continuation calling it) is a small change
  in the `SKILL.md` setup.

## For the per-project audits (poly-bot / poster-studio, on WSL)

The owner asked for these; the method is built, blocked only on the WSL paths. From each repo:
`python <path>/tools/project_graph_scaffold.py new <name>` → fill the graph + `PROJECT_STATE.md` → validate →
commit → have future sessions read it first. Copy `task_ledger.py` + `supervisor.py` in for the CLI
orchestration / dropped-task problem.

## Housekeeping still open

- `check-proposal` passes a patch with no `add_nodes` key silently (`tools/knowledge_graph.py`).
- The pre-commit guard's doc-check warns on `docs/probe_*` / `docs/research/*` (only accepts
  `docs/auto_sweep_*` / `docs/phase*`).
- `knowledge/notes/2026-09-04-harness-swarm-deep-dive.md` on `origin/main` misreads the pressure-field
  numbers of arXiv:2601.08129 (the graph node `emergent_stigmergic_coordination` is correct and flags it).
  Owner action.
- Rotate the GitHub PAT pasted into the originating Cowork chat (carried over from the original handover).

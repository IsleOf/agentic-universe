# Handoff — Agentic Universe, as of run 88

For whoever picks this up next. The original `HANDOVER.md` (outside the repo) predates the entire build; this
replaces it as the "what to do next" doc.

## Where things are

- **Branch:** `proposals/2026-09-01-emergent-behaviour-cluster` (not `main`). All work is here.
- **Graph:** `knowledge/graph/agentic_universe_graph.json` — 188 nodes / 584 edges. `python
  tools/knowledge_graph.py validate` must print `VALID`.
- **Toolchain:** `tools/` — pure stdlib, 18 selftests. `python tools/selftest_all.py` → `BUILD SELFTEST:
  GREEN`. Map: `tools/README.md`.
- **Orientation:** `docs/graph_state_2026-09.md`. Adversarial counterweight: `docs/what_would_make_this_wrong.md`.
- **Run log:** `docs/auto_sweep_*.md`, one per autonomous run (88 so far). `docs/phase0_*`–`phase5_*` for the build.

## What is built

Phases 0–5 of `docs/self_improving_harness_plan.md`, on the project's own research loop as the first real
(single-agent) harness:

| | tool | state |
| --- | --- | --- |
| Phase 0 | `trace_substrate` · `topology_recover` · `loop_session` | schema + role-recovery gate (1.00) + live per-run recording |
| Phase 1 | `harness_registry` · `loop_adapter` | versioned components, exact revert; the loop's 56-run history as a real trace |
| Phase 2 | `experience_bank` | workflow/step stores, ancestry dedup, stale-check |
| Phase 3 | `improvement_loop` · `loop_metrics` · `loop_proposer` · `holdout_tasks` (17) · `holdout_verifier2` | propose → verify (frozen held-out, two independent scorers, disagreement = reject) → grounded strict-decrease → promote/revert |
| Phase 4 | `skill_induction` | induce + retire candidate skills, 20% permanently withheld |
| Phase 5 | `exec_guard` | pre-commit hook — blocks an invalid graph, an orphan, a raw trace, a secret, a commit to `main` |

Six probe rigs (`tools/probe_*.py`), each reproducing a real phenomenon in sim:
`probe_idle_agent` (+ 4-arm sweep), `probe_subagent_coordination`, `probe_epistemic_sybil`, `probe_rho_holdout`,
`probe_activation_generalisation`, `probe_composed_design` (the §5 experiment — verdict *composes but bounded*).

One self-edit has gone through the Phase 3 gate: run 80's **IDLE-STATE RULE** in `context/loop_policy` (v2) and
the live `SKILL.md` — it directs idle runs to deepen a node / dry-run a probe / do an adversarial pass instead
of refreshing docs. Runs 81–88 held to it.

## The one thing that unblocks everything: wire a model

Every rig and the Phase 3 proposer have exactly one stub — a function where a model call belongs. The
interfaces are stable; swapping in a model changes nothing else.

| stub | file | what it should become |
| --- | --- | --- |
| `model_policy(call_model, framing, tools)` | `probe_idle_agent.py` | **adapter now written (run 134)** — pass a `call_model(prompt) -> str`; it builds the state-only prompt, parses the reply into an action, `idle_noop` on anything unparseable or on a model exception. Selftested with a fake model. Swap in a real `call_model` and run `sweep`. |
| `model_reader(call_model, corpus)` | `probe_epistemic_sybil.py` | **adapter written (run 139)** — model reads a real document, first number in the reply is the estimate; unparseable = `nan`, dropped. Pass `run_arm(..., reader=...)`. Selftested against a fake corpus. Needs a real document corpus. |
| `model_preference(judge)` | `probe_rho_holdout.py` | **adapter written (run 135)** — pass a `judge(text_a, text_b) -> "A"\|"B"`; it runs a round-robin Copeland selection, judge exception = tie. Pass to `run_round(select=...)`. Selftested with fake judges. |
| `model_relay(call_model)` | `probe_subagent_coordination.py` | **adapter written (run 137)** — model told its id + that a peer sent an out-of-scope `msg`, asked yes/no to forward; unparseable/error = don't forward. Selftested; fake yes/no reproduce the two scripted bounds. |
| `sample_signal(kind, rng)` | `probe_activation_generalisation.py` | real activation vectors from a model layer, per collusion kind — spec + degraded text-embedding mode in `docs/remaining_seams.md` |
| `step_ok` / `handoff_ok` | `probe_composed_design.py` | real agent sub-step / handoff outcomes — spec + single-agent `p`-measurement path in `docs/remaining_seams.md` |
| `model_propose(call_model, context)` | `loop_proposer.py` | **adapter written (run 140)** — hands the model `PROPOSER_PROMPT.format(...)`, parses the JSON list leniently, drops malformed proposals, `[]` on failure (loop falls back to `heuristic_propose`). Selftested. |

**First run to do:** pass a real `call_model` into `model_policy` (wire it in `sweep`/`_config_policy`) and run
`python tools/probe_idle_agent.py sweep`. That is the idle-agent probe —
`what_would_make_this_wrong.md` calls it "the one experiment that resolves the most" (does
`concept_habitat_slack` hold — is there autotelic behaviour in the gap?). The rig, the four arms, and the
falsification assessment are all done; it needs the model and a real filesystem sandbox for the containment.

**Second:** pass a real `judge` into `model_preference` and `run_round(select=...)`, run `probe_rho_holdout
sweep`. Decides whether trajectory-only self-improvement (`pattern_trajectory_only_harness_optimization`)
survives external grading. The sim says ~33% survives; a real judge gives the real number. (Candidates need
a real output `sample` field for the judge to compare — `_cand_descriptor` synthesises one for the rig.)

**Third:** pass a real `call_model` into `model_relay`, run `probe_subagent_coordination`. Measures a real
model's peer-deference — does it forward an out-of-scope instruction from a non-parent peer? — against the
scripted high/low bounds, with and without the same-parent-ID filter.

**Adapters written (runs 134, 135, 137, 139, 140):** five of the seven seams — `model_policy`,
`model_preference`, `model_relay`, `model_reader`, `model_propose` — are written and selftested with fake
models, each failing safe (`idle_noop` / tie / don't forward / `nan`-dropped / `[]`-and-fall-back). The two
remaining need infrastructure beyond a text model: `sample_signal` (real activation vectors from a model
layer) and `step_ok`/`handoff_ok` (a real agent harness running real sub-steps). Wiring a single
`call_model` into the five written adapters is now the whole first-run task.

## What needs infrastructure this repo doesn't have

- **Phase 6 (the swarm layer)** — needs a real multi-agent harness. Everything so far is single-agent (the
  loop) or synthetic. **Candidate substrate: RiskLab** (ACL 2026 Demo, `concept_risklab_probe_toolkit`) — an
  open toolkit with a topology-environment-protocol-agent-task quintuple, trajectory-grounded evaluation, and a
  risk-detector registry. The project's six `tools/probe_*.py` rigs could be ported onto it as risk detectors
  for a real (non-synthetic) multi-agent run.
- **The composed-design test** (`what_would_make_this_wrong.md` §5) — short agents + four-field handoffs +
  folded state, run together on a 100+-step task. Needs a real harness.
- **A live loop feed** — `loop_session.LoopSession` records runs as they happen; wiring it into the scheduled
  task's actual execution (rather than the interactive continuation calling it) is a small change in the
  `SKILL.md` setup.

## Watch the run-80 prediction

The IDLE-STATE RULE predicts idle runs stop churning docs. `python tools/loop_metrics.py report` + the
`skill_induction` task-class classifier check it computably. If the next ~10 runs still refresh READMEs, the
policy should revert (`python tools/harness_registry.py revert context loop_policy`) — the machinery is in
place, `git log runtime/harness/` shows the history.

## Housekeeping still open

- `check-proposal` passes a patch with no `add_nodes` key silently (`tools/knowledge_graph.py`).
- The pre-commit guard's doc-check warns on `docs/probe_*` (only accepts `docs/auto_sweep_*` / `docs/phase*`).
- The task-class classifier still puts ~7/61 workflow entries in `other` (all pre-loop seed commits).
- Rotate the GitHub PAT from the originating Cowork chat (carried over from the original handover).

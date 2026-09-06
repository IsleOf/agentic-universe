# Agentic Universe — Project State

**Format:** Agentic Universe handover (`docs/practicing_what_we_preach.md` §3) · **Graph:**
`knowledge/graph/agentic_universe_project_graph.json` (26 nodes; `python tools/project_graph_scaffold.py
validate` it) · **Date:** 2026-09-06 (run 251)

> A fresh session reads this file and the project graph **first**. This is the compact orientation; the
> full literature map is `docs/graph_state_2026-09.md`, the build plan is
> `docs/self_improving_harness_plan.md`, the running log is
> `knowledge/graph/agentic_universe_graph.json`'s `evolution_log`, and the auto-memory index is at
> `C:\Users\PC\.claude\projects\C--\memory\MEMORY.md`.

## What it is

A research repo with two artefacts. **(1)** `knowledge/graph/agentic_universe_graph.json` — 272 nodes /
1091 edges of VERIFIED-arXiv literature and built artifacts about *emergent agent behaviour* and
*self-improving agent harnesses*, edited one increment per run. **(2)** the autonomous loop that edits it:
`tools/loop_session.py` wraps each run, `tools/improvement_loop.py` is the Phase-3 acceptance gate,
`tools/loop_metrics.py` reads the trace corpus. `docs/` is the orientation layer; the graph JSON is the
source of truth. Everything in `tools/` is pure Python stdlib, no dependencies, no network.

## Current state

**Working:** the loop has run ~250 increments; every run validates the graph, passes 25 selftests
(`python tools/selftest_all.py` → `BUILD SELFTEST: GREEN`), and commits+pushes to
`proposals/2026-09-01-emergent-behaviour-cluster`. Phases 0–5 of the self-improving-harness plan exist as
tested code. The acceptor/certificate literature cluster and the harness-evolution subfield are mapped and
the project is self-audited against them (`docs/harness_anatomy_self_audit.md`). Six tools shipped in the
latest session: `paired_eprocess`, `probe_orchestration_value`, `loop_metrics.status_line`,
`deterministic_repair`, `graph_diff`, `task_ledger` + `supervisor`.

**Half-built / not built:** Phase 6 (the swarm layer) is untouched — the project studies emergence but has
never run a real swarm. The model-integration step (a real `call_model` bound into the probe adapters) is
deferred — the probes run on synthetic data.

**Known gaps** (see `docs/what_would_make_this_wrong.md`): the central habitat mechanism
(`concept_habitat_slack`) is unverified; the gate scores usefulness but nothing scores novelty
(`run_novelty` is an advisory signal, not a gate check); the no-weight-training bet is challenged by WHALE
/ JIT-Agent on capability-shaped tasks.

## The single highest-value next move

**Bind a real `call_model` into the five probe adapters and run `probe_idle_agent sweep`** (`docs/HANDOFF.md`).
`what_would_make_this_wrong.md` calls it "the one experiment that resolves the most" — it tests the
top-severity gap. The loop cannot re-execute its own past research autonomously; this is the
human-in-the-loop step the plan always had.

## Hard constraints

- Commit only to `proposals/2026-09-01-emergent-behaviour-cluster`, never `main` (`exec_guard` enforces).
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
   still needs the integration point.

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

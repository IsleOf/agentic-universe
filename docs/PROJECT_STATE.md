# Agentic Universe — Project State

**Format:** Agentic Universe handover (`docs/practicing_what_we_preach.md` §3) · **Graph:**
`knowledge/graph/agentic_universe_project_graph.json` (26 nodes; `python tools/project_graph_scaffold.py
validate` it) · **Date:** 2026-10-23 (run 346)

> A fresh session reads this file and the project graph **first**. This is the compact orientation; the
> full literature map is `docs/graph_state_2026-09.md`, the build plan is
> `docs/self_improving_harness_plan.md`, the running log is
> `knowledge/graph/agentic_universe_graph.json`'s `evolution_log`, and the auto-memory index is at
> `C:\Users\PC\.claude\projects\C--\memory\MEMORY.md`.

## What it is

A research repo with two artefacts. **(1)** `knowledge/graph/agentic_universe_graph.json` — 358 nodes /
1436 edges of VERIFIED-arXiv literature and built artifacts about *emergent agent behaviour* and
*self-improving agent harnesses*, edited one increment per run. **(2)** the autonomous loop that edits it:
`tools/loop_session.py` wraps each run, `tools/improvement_loop.py` is the Phase-3 acceptance gate,
`tools/loop_metrics.py` reads the trace corpus. `docs/` is the orientation layer; the graph JSON is the
source of truth. Everything in `tools/` is pure Python stdlib, no dependencies, no network.

## Current state

**Working:** the loop has run 345 increments; every run validates the graph, passes **46 selftests**
(`python tools/selftest_all.py` → `BUILD SELFTEST: GREEN`), and commits+pushes to
`proposals/2026-09-01-emergent-behaviour-cluster`. Phases 0–5 of the self-improving-harness plan exist as
tested code. The acceptor/certificate literature cluster and the harness-evolution subfield are mapped and
the project is self-audited against them.

**Latest session (runs 296–326):** the owner pushed research artefacts and asked the project to
**rebuild its own loop**, and to audit poly-bot / poster-studio.
- *The v2 self-rebuild — deterministic spine complete as tested stdlib:* `docs/self_rebuild_v2.md` (299)
  is the design. Built: **`acceptance_gate.py`** (300 — `check()` → a signed replayable certificate:
  held-out + PACE e-value + process-adjusted flag + forecast Brier), **`research_brief.py`** (302 — the
  typed scout output + a mechanised dedup check), **`loop_conductor.py`** (303 — the headless pipeline;
  its IDLE-STATE classifier wired to the real run corpus via the janitor at 326), **`v2_integration.py`**
  (311 — an end-to-end dry-run proving the bricks compose), **`janitor.py`** (325 — compiles the run
  corpus into per-consumer views). Plus the `perplexity-notebolm` scout scaffold (304).
- *Owner research folded:* the prediction-markets branch (296), the agentic-tooling scan (298), and —
  off the SEVerA citation chain and an emergence-side sweep — a harness-engineering cluster
  (305–307, 316), the deception thread (309–310), agent-memory security (313), and negotiation/diversity/
  routing (322–324). `docs/HANDOFF.md` refreshed run 88 → 294.
- *The two per-project audits (317–321):* `docs/audits/poly-bot/` + `docs/audits/poster-studio/` — a
  validated graph + `PROJECT_STATE` + `question` nodes each, plus a poly-bot watchdog gap analysis and
  the poster-studio ↔ orchestrator interface on the `etsy-agentic-space` branch. `docs/audits/README.md`
  is the coordination doc. Closes the owner request open since run 251.

**Latest session (runs 327–345):** v2.0 wiring finished + an evolution-aware security layer + two
emergence-side probes.
- *v2.0 one-command (334):* all five model-facing probe adapters route through `tools/call_model.py`
  behind a `--live` flag. `AU_MODEL_BACKEND=fake` = offline smoke test, `cli` / registered callable =
  the real experiment. Activation is purely a resource call now.
- *Evolution-aware security (335–340, 345):* folded **MLAS** (`2606.23075`) and **misevolution**
  (`2509.26354`). `self_rebuild_v2.md` §12 maps the spine onto the MLAS matrix; two of three additions
  built — **"gate the gate"** (`exec_guard` blocks self-design pre-commits unless `AU_SELF_DESIGN_ACK`
  is set) and the **conductor blessed-manifest preflight** (`harness_registry.bless` / `manifest_drift`
  + `Conductor.preflight()` halts on harness drift). Addition (2) — externalise the cert signer key —
  is operational, left for the owner.
- *Emergence side (341, 343–344):* `tools/probe_emergent_synergy.py` (Rosas Psi + differentiation,
  reproducing Riedl `2510.05174`) and the fragmentation arm in `probe_subagent_coordination.py`
  (from `2607.07368` — cross-agent aggregation beats per-instance monitoring).
- *Harness convergence (336):* folded **Prime Agent** (`2608.23552`).

**Half-built / not built:** Phase 6 (the swarm layer) is untouched. **The v2 deterministic spine is
complete and self-observing; the generative edge is not built — it is entirely the `call_model` binding
(v2.0), which is now one env var (`AU_MODEL_BACKEND=cli` + a CLI-agent, or a registered API client).**
The probes still run on synthetic data. `acceptance_gate.py` is wired as the conductor's gate
(`Conductor.gate` defaults to `acceptance_gate.check`) but the conductor is not yet on the 6h task
(needs the real `run_worker` + a SKILL.md change). The scout's live browser path (Perplexity/NotebookLM
selectors) needs a profile + iteration. MLAS addition (2) — externalise the certificate signer key — is
unbuilt (operational).

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

Until then, autonomous runs keep folding literature and deepening the graph. The v2 deterministic
spine is finished (`acceptance_gate` / `research_brief` / `loop_conductor` / `v2_integration` /
`janitor` + the run-338/340 security layer: `exec_guard` gate-the-gate and `Conductor.preflight()`
blessed-manifest check), all selftested, the conductor self-observing via the janitor; nothing more
of it can be built without the model.

## Hard constraints

- Commit only to `proposals/2026-09-01-emergent-behaviour-cluster`, never `main` (`exec_guard` enforces).
  Branches off `main` (`etsy-agentic-space`, `autodesign-etsy`) need `git commit --no-verify` — the
  pre-commit hook runs `tools/exec_guard.py`, which only exists on the proposals branch.
- Never commit credentials, API keys, cookies, browser profiles, or personal data.
- **Self-design edits need an owner ack** (run 338): `exec_guard` blocks a pre-commit that stages
  `tools/{acceptance_gate,exec_guard,knowledge_graph,harness_registry}.py`, anything under
  `runtime/harness/`, a decision-logic region of the proposer/conductor, or a `selftest_all` JOB
  *removal* — unless `AU_SELF_DESIGN_ACK="<reason>"` is set. The autonomous loop never sets it; an
  owner hand-editing those commits with the env var and the guard logs the reason. Ordinary edits
  (probes, docs, adapter wiring, adding a JOB) are unaffected.
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

# Handoff — Agentic Universe, as of run 461 (2026-11-20)

Rewrites the run-294 handoff wholesale. This is the single doc a fresh session should read first,
then `docs/graph_state_2026-09.md` (the graph map) and `docs/loop_environment_model.md` (the
loop's model of its own environment). Written because the account is hitting its weekly usage
limit and the loop is paused.

---

## 1. What this is

A **versioned knowledge graph** on emergent multi-agent LLM behaviour and self-improving agent
harnesses, plus the **tested stdlib harness** that maintains and reasons over it. One graph:
`knowledge/graph/agentic_universe_graph.json` — **459 nodes / 1924 edges**, validated by
`python tools/knowledge_graph.py validate` → VALID, no orphans, no dangling edges.

- **Repo:** local `C:\Agents\agentic-universe\repo`, GitHub `IsleOf/agentic-universe`.
- **Working branch:** `proposals/2026-09-01-emergent-behaviour-cluster`. **Never commit to
  `main`.** HEAD at handoff: `2979abc` (run 461). A run 462 Sonnet subagent was dispatched just
  before the pause and may add one more commit.
- **Posture:** emergence-first (`docs/emergence_first_posture.md`). Ideas enter the graph on
  interest, not evidence; unverified material stays low-confidence, status `to_test`. Record
  tensions as `challenges` edges, don't resolve them. Verify every citation three ways (exists /
  summary matches / headline number causally isolated); `derived_from` holds URLs or in-repo doc
  paths, **never** a node id.
- **Recency weighting** (user directive, a weighting not a gate): prefer literature from the
  last ~30 days; when folding older work, name the model/harness generation and note it still
  bears on the SMALL/LOCAL LLM regime.

## 2. The standing goal

Set via `/goal`, verbatim and immutable: **"keep researching until i explicitly tell you to
stop, do NOT delete or change this goal."** A Stop hook re-fires it after every turn. No
explicit stop has ever been given. Automated "Stop hook feedback" turns in the transcript are
enforcement, not user messages.

## 3. The autonomous loop

**One increment per run.** Each run: read the charter + the 3 newest sweep docs' "Next"
sections + `loop_environment_model.md`; run `python tools/loop_action_class.py report -n 10` and
prefer a non-dominant class; pick the single highest-value increment; execute; validate
(`knowledge_graph.py validate` → VALID; orphan/dangling check; `python tools/selftest_all.py` →
**BUILD SELFTEST: GREEN**, ~3 min, run it backgrounded); regenerate `docs/source_register.md`
via `<scratchpad>/build_sources.py` if `derived_from` changed; record via
`LoopSession(run_no=N, increment=...)` (writes `runtime/observations/loop_runs/run-N.json`);
write `docs/auto_sweep_<YYYY-MM-DD-HHMM>.md` (a **monotonic future-dated sequence** — the newest
is `2026-11-20-1800`; add 6h each run); commit with
`git -c user.name='Ilmar Selter' -c user.email='ilmar.selter@gmail.com'`, message ending
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`; push.

**Cron:** the scheduled task `agentic-universe-research-loop` (every 6h) is **PAUSED** (disabled
2026-11-20 per owner). When re-enabled it now **spawns one Sonnet subagent** to do the
increment and only relays the report — do not run the increment in an Opus session (token
cost). The full delegation prompt is in the task's `SKILL.md`.

**Graph-patch discipline:** write patch scripts to a scratchpad `.py` file and run them — never
inline in a heredoc (the shell mangles `\n`). Same for `LoopSession` recording scripts.

**Self-design guard:** `AU_SELF_DESIGN_ACK` env var is required to edit
`tools/{acceptance_gate,exec_guard,knowledge_graph,harness_registry}.py`, `runtime/harness/`,
proposer/conductor decision logic, or to *remove* a `selftest_all` JOB (adding one is fine).
`exec_guard` is installed as `.git/hooks/pre-commit`.

## 4. The harness (all `tools/`, pure stdlib, ~62 `selftest_all` jobs GREEN)

**Spine (Phases 0–5 of `docs/self_improving_harness_plan.md`):** `trace_substrate.py` (Five-W
event schema), `harness_registry.py` (versioned harness), `experience_bank.py` (Phase 2),
`improvement_loop.py` (Phase 3 propose→verify→promote, with `paired_eprocess` / `deterministic_repair`
/ `tampering_flags`), `holdout_tasks.py` + `holdout_verifier2.py` (frozen held-out set, two
independent scorers), `skill_induction.py` (Phase 4: induce / retire / **consolidate** (run
447)), `exec_guard.py` (Phase 5 pre-commit), `loop_conductor.py` + `acceptance_gate.py` +
`janitor.py` + `v2_integration.py` (the v2 deterministic spine), `executor_pool.py` +
`cohort_monitor.py` (v2.4 Collective enforcement).

**Loop self-instrumentation:** `loop_session.py`, `loop_metrics.py` (`status_line` shows
`… acts fold35% · audit ok`), `loop_adapter.py`, `loop_proposer.py`, `param_invariance_audit.py`,
`loop_action_class.py`, `sweep_audit.py` (run 442 — **sufficiency / coverage / refix** checks on
the loop's own sweep docs), `trace_topology.py` (run 459 — per-run inter-agent graph + hub /
clique / receive_only / no_reciprocity flags), `tamper_audit.py`, `graph_diff.py`.

**The swarm substrate (the user's mid-arc deliverable — runs 389–460):**
`pheromone.py` (SQLite stigmergic board; explicit decay clock; pool-size-scaled threshold;
`isolated=True` / `release_isolation` gated isolation, run 437; `note_alternative`, run 438;
`warn` / `ask`), `task_ledger.py` (+ `STAGES`), `relay.py` (handoff + anti-ping-pong),
`reputation.py` (Beta-Bernoulli + UCB + 14-day decay; `slash` + `whitewash_risk`, run 433),
`gates.py` (G1/G4 quorum-not-veto; REPORT-not-block signals `single_evidence_domain` /
`no_alternative_hypothesis` / `quorum_homogeneous` / uncited-claims / open-clarifications),
`swarm_demo.py` (end-to-end, **no orchestrator object**; `defer_consensus=True` deferred-consensus
flow; `agent_models=` validator-model selection, run 449). Adversarially tested by
`probe_substrate_adversarial.py` (13 attacks, all residual landings are documented
Sybil/collusion-class limits). Deliverable doc: `docs/swarm-substrate-prototype.md` (5-part
report; §6 build findings; §7 the identity gap → **capability-token binding** (owner-gated);
§8 the seven REPORT-not-block signals). Companion: `docs/agent-fleets-and-swarm-substrate.md`
(the user's pasted KB doc).

**Probe rigs** (`tools/probe_*.py`, each drives a real module or reproduces a phenomenon in
sim with one model-call stub): `probe_orchestration_value` (+ the `gamma` collaboration-gain
arm, run 428), `probe_emergent_synergy` (+ `aggregate_diversity` / `individual_novelty`, run
444), `probe_annotation_contagion` (+ the `seal_order` temporal-weight arm, run 455),
`probe_subagent_coordination` (+ `--persist`), `probe_swap_cost`, `probe_epistemic_market`,
`probe_epistemic_sybil`, `probe_idle_agent`, `probe_rho_holdout`, `probe_composed_design`,
`probe_activation_generalisation`, `probe_memory_horizon`, `probe_language_drift_monitor`,
`probe_trust_transfer`, `probe_dissent_vs_reflection`, `probe_trust_weighted_voting`,
`probe_identity_masking`.

## 5. Recent research arc (runs 428–461)

Papers folded, all Sept 2026: 2602.05289 (collaboration-gain metric Γ), 2609.02925 (κ_E — a
shared-evidence quorum is structurally cut-1), 2609.02992 (reputation only disciplines a costly
identity), 2609.01870 (ArcticSwarm — deferring early consensus is worth large gains),
2609.01992 (ClaimReceipt — evaluation sufficiency + coverage), 2609.02620 (individual novelty ↑,
aggregate diversity ↓; composition is the lever), 2609.02094 (MASkills — skill-conditioned
credit + a 4-stage lifecycle), 2609.04270 (reviewer capability governs rejection targeting, not
repair; self-review over-rejects ~35%), 2609.01985 (agent-built systems hide architectural
defects; a claimed fix never re-measured), 2609.03425 (The Civilization Framework — the
addressable unit is a civilization; the temporal-weight effect 54.2% vs 31.6%), 2609.04194
(**legibility ≠ interpretability** — `trace_legibility` is a floor, not a monitorability
measure), 2609.02967 (FGLGuard — the inter-agent comm graph is a safety substrate; federation
beats data pooling).

**The recurring finding:** every residual substrate weakness is one weakness — the `agent`
field is an unauthenticated string. And every coordination mechanism (a vote, a quorum, a
complementarity rule) has a hidden cost the aggregate task score does not show (budget,
epistemic independence, aggregate diversity).

## 6. Open / owner-gated items (nothing the loop can do alone)

- **Rotate the GitHub PAT** pasted into the originating Cowork chat.
- **Capability-token migration** — bind `pheromone.annotate` / `reputation.record` to
  `executor_pool`'s `mint_token` / `redeem_token`; ~1 day across pheromone/reputation/gates/
  relay/swarm_demo + selftests. Turns the seven REPORT signals into possible blocks. (`docs/swarm-substrate-prototype.md` §7.4.)
- **Wire `loop_environment_model.md` into `loop_conductor`** as an input it reads and revises
  each run (the BCO shape). Test: does §3 (hazards) stop growing.
- **Route new-tool / skill / job additions through holdout scoring** (the retention gate is
  currently wired to proposals, not harness expansion).
- **`--live` experiments** the loop must NOT run (they spend CLI-agent quota): a budget-matched
  Γ arm on `probe_orchestration_value`; a seal-order run; a composition sweep on
  `probe_emergent_synergy`; the swap-cost convention question.
- **Other repos** (the loop never commits outside this one): poly-bot's refreshed map is
  uncommitted in its own tree; poster-studio's audit came back at 80 nodes / 105 edges (edge
  ratio 1.3 — needs a `depends_on` / `challenges` edge pass, not more nodes; port
  `tools/task_ledger.py` + `tools/gates.py` for its "one durable per-artifact ledger with human
  gates" would-change); `loop_conductor` is not on the live 6-hourly task (SKILL.md change).

## 7. How to resume

1. `cd C:\Agents\agentic-universe\repo && git checkout proposals/2026-09-01-emergent-behaviour-cluster && git pull --ff-only`
2. Read this file, `docs/graph_state_2026-09.md`, `docs/loop_environment_model.md`,
   `docs/habitat_charter.md`.
3. `python tools/knowledge_graph.py validate` and `python tools/selftest_all.py` — both must be
   GREEN before any increment.
4. Read the "Next" section of `docs/auto_sweep_2026-11-20-1800.md` (and run 462's sweep if it
   landed).
5. To restart the cron: `mcp__scheduled-tasks__update_scheduled_task` with `enabled: true` —
   it will spawn a Sonnet subagent per run.
6. To run an increment interactively: follow §3, or spawn a Sonnet subagent with the SKILL.md
   prompt. Do the increment work on Sonnet, not Opus.

## 8. Security constraints (persist across all sessions)

Never commit credentials / API keys / cookies / browser profiles / personal data. Commit only
to the working branch, never `main`. Do not touch `C:\Agents\.git` (a separate outer repo).
Delete source videos after analysis (disk space). Do not click CAPTCHA / bot-detection. The
loop must not run `--live` probe sweeps or rewrite its own execution harness (the scheduled-task
body / SKILL.md).

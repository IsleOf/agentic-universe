# Forward Plan: Self-Improving Agentic OS

**Date:** 2026-09-05 · last reconciled run 48 · plan-soundness update run 124 · acceptor/certificate arc run 214 · v2 self-rebuild arc run 307 · **Target:** a self-improving agentic OS with a dynamically improving harness
**Graph:** 61 nodes / 115 edges at authoring — current state in `docs/graph_state_2026-09.md` · **Supersedes as active plan:** `docs/emergence_first_posture.md` (posture unchanged, now has a build target)

> **Independent systems that match this plan (found runs 109, 118, 119).** Three published frameworks now
> instantiate this architecture, two with runnable code:
> - **ASG-SI** (`concept_asg_si_independently_arrives_at_the_plan`, arXiv:2512.23760, 2025) — self-improvement
>   as compilation into an *auditable skill graph*: improvements extracted from trajectories → normalised into
>   a skill with an explicit interface → promoted only after verifier-backed replay + contract checks; rewards
>   decomposed into reconstructible components from replayable evidence; a complete threat model; a **runnable
>   reference implementation**. This is nearly the whole plan below. Difference: ASG-SI is RL-based, this plan
>   is emergence-first.
> - **Self-Harness** (`concept_self_harness_validates_the_three_loop`, arXiv:2606.09498) — an agent improves
>   its own harness via Weakness Mining (from traces) → minimal Proposal → Validation (regression testing only).
>   **9 of 9 model-benchmark combos improve held-out pass rate, up to +132%.** The Phase 3 loop below, working.
> - **MetaSkill-Evolve** (`concept_recursive_meta_skill_evolution`, arXiv:2607.05297) — makes it *recursive*:
>   the improvement procedure itself is a meta-skill that evolves on a slower timescale under the same
>   pipeline. This plan's middle loop currently has a *fixed* procedure (`tools/loop_proposer.py`); per
>   MetaSkill-Evolve it should also be under improvement. The Analyzer/Retriever/Allocator/Proposer/Evolver
>   decomposition is cleaner than this plan's `loop_metrics → loop_proposer → improvement_loop` split.
>
> **The lineage and the lens (runs 122–124).** The trajectory → filter → retrain self-improvement loop is
> not new: **ReST-meets-ReAct** (`concept_rest_react_founds_the_trajectory_retrain_loop`, arXiv:2312.10003,
> DeepMind 2023) is the earliest published form — a ReAct agent retrained on its own filtered trajectories,
> matching a large prompted model after *two* iterations with ~2 OOM fewer parameters. What is new in 2025+
> is moving the loop from opaque weight updates to *auditable harness/skill edits* (the tier this plan sits
> at). Two caveats it carries: it is weight-level self-distillation (the fork this plan declines), and its
> gains **saturate after ~2 iterations** — a caution on expecting recursive loops to compound.
> **Adaptive Self-improvement for ML-library dev** (`concept_adaptive_self_improvement_in_the_low_data_regime`,
> arXiv:2502.02534, ICML 2025) shows the loop survives a *scarce-trajectory* regime (few examples, evolving
> target; 3.9× over a single LLM) — the regime this plan's middle loop actually runs in (one increment per
> run). And the **model-harness-lens survey** (`concept_bottleneck_is_the_model_harness_coupling`,
> arXiv:2606.20683, 2026) decomposes the harness into **six coupled runtime responsibilities — observation,
> context, control, action, state, verification** — which line up with the Phase 0–5 build below almost
> one-to-one, and frames agent quality as *emergent from the model-harness coupling*, not a model property.
>
> **The architecture is now instantiated component by component (run 168).** `docs/self_improvement_by_responsibility.md`
> maps a published, working self-improving instance onto **five of the six** runtime responsibilities —
> context = ACE, control = RHO / Self-Harness, action = ToolMaker, state = CER, verification = DeepVerifier
> (observation is deliberately not self-modifying; its legibility is a Phase 3 acceptance criterion
> instead). Every one has a *grounded* gate. So the integration step is not "make the self-improving
> harness work" — it is "connect six independently-validated loops through one trace substrate and one
> gate discipline." The coupling is the untested part, exactly as the lens predicts.

---

## 1. What the September research changed

Twenty commits of deep research landed on `main` (Sept 3–4, ~2,600 lines of notes). The single most important thing in them: **the self-improving harness is no longer speculative.** It has been built, benchmarked, and beaten a human-designed baseline.

`arXiv:2604.25850` — Agentic Harness Engineering, verified — evolves a coding-agent harness automatically and reports Terminal-Bench 2 going **69.7% → 77.0% pass@1 over ten iterations**, past the human-designed Codex-CLI baseline at 71.9%, with SWE-bench-verified top aggregate at 12% fewer tokens.

That reframes the project. The question is no longer *can a harness improve itself* but *what does it improve toward, and what stops it drifting*. Those are the questions this repo is actually equipped to answer, because they are questions about emergent behaviour.

Four independent lines converge on the same five-part architecture:

| Component | Source | Role |
| --- | --- | --- |
| Components as revertible files | AHE `2604.25850` | An edit must be a discrete, undoable object |
| Dual-layer experience bank | MemoHarness `2607.14159` | Workflow patterns and step corrections, stored apart |
| Falsifiable prediction per edit | AHE meta-harness pillar | Evolution as experiment, not search |
| Verifier gate + rollback | ECC 2.0 | `observation → proposal → verification → promotion → rollback` |
| Fresh-context evaluation | ECC | Generator and evaluator must not share a context window |

## 2. The reconciliation

The emergence-first posture says: don't constrain agents, gate only the final consequential decision. A verifier gate on harness edits sounds like a retreat from that. **It isn't — it is the same principle applied to a different object.**

- Agents reason, coordinate, and propose harness changes with no process constraints.
- Approval sits on exactly one act: **promoting an edit into the live harness**.

Recorded in the graph as `pattern_verifier_gated_promotion` *instantiates* `principle_terminal_gate_only`. Ideas stay free; mutations to the thing running the ideas are gated. A self-improving system without that gate does not stay still — it drifts, and drift is indistinguishable from improvement without a verifier.

ECC states the rule as an explicit non-goal: *no automatic mutation of harness configs without verifier evidence*. Worth adopting verbatim.

**Reconciliation with the nourishing design (run 48).** `docs/nourishing_harness_design.md` §3.3 makes the interior continual-refinement loop *ungated for the proposal* and gated only at *acceptance into standing behaviour*, and run 45 gave that acceptance test its current form: `pattern_grounded_acceptance_only` (SRMA) — an edit becomes standing behaviour iff a **grounded, non-transcript** risk measure strictly decreases, and by `concept_transcript_only_gate_is_provably_insufficient` no transcript-only rule can do better than chance on hard cases. So "verifier gate" throughout this plan should be read as *grounded-acceptance gate*: the Phase 3 verifier spec below (PROCTOR + heterogeneous + recoverability + four-field verdict) is the concrete instantiation, not a competing mechanism.

## 3. Three loops

```
INNER   task loop        agents work. no process constraints. traces emitted.
MIDDLE  harness loop     observe traces -> propose edit + prediction -> verify
                         in fresh context -> promote or roll back
OUTER   knowledge loop   surviving patterns graduate to skills, then to graph nodes
```

The middle loop is the product. The inner loop is where emergence happens. The outer loop is what this repo already is.

**`concept_agentic_os` layering — only one layer mutates fast:**

- **Runtime** — process isolation, capability grants, execution enforcement. Changes slowly, by hand. This is the fixed point everything else is verified from.
- **Harness** — context policy, tools, memory, topology. Self-modifies at speed under the verifier gate.
- **Knowledge** — what the system knows, declarative and auditable, separate from how it reasons.

A runtime that mutates as fast as the harness has nothing left to verify against.

## 4. Build order

> **Cross-check against the six runtime responsibilities** (`concept_bottleneck_is_the_model_harness_coupling`,
> arXiv:2606.20683): observation = Phase 0 trace substrate · context = `context/loop_policy` · control =
> the loop / `loop_adapter` · action = the tool registry (Phase 1) · state = Phase 2 experience bank ·
> verification = the Phase 3 grounded-acceptance gate. The build covers all six; the survey's framing is
> that their *coupling* is where quality is won or lost, so the gaps to watch are the seams between phases,
> not the phases.

### Phase 0 — Trace substrate (prerequisite for everything) — **BUILT, gate GREEN (run 60)**

Five-W instrumentation (`pattern_five_w_message_instrumentation`): sender, receiver, content class, timestamp, declared purpose captured at the call site, channel. Plus tool calls, outcomes, and token cost per step.

Already the top of the emergence probe catalogue; it is now also the input format the experience bank condenses. One build serves both. `arXiv:2602.11583` independently arrives at the same five dimensions.

**Gate:** topology analysis must recover roles in a control condition where roles were explicitly assigned. An instrument that cannot find roles known to be there cannot be trusted to find emergent ones.

**Status (run 60):** built in `tools/trace_substrate.py` (schema `phase0.1` + `Recorder` + validator), `tools/topology_recover.py` (interaction graph + deterministic role recovery), `tools/phase0_selftest.py` (the GREEN/RED predicate). Full writeup: `docs/phase0_trace_substrate.md`. The gate passes — role recovery is **1.00 on the control condition** (planner / workers / verifier / router / isolate), threshold was 0.80. Every event also carries `layer` (`concept_emergence_layer_model`) and `language` (`concept_interaction_language_shifts_emergence`), and `CLAIM` events carry `evidence_roots` (`pattern_evidential_ancestry_tracking`). Secrets are scrubbed before write; raw `.jsonl` is gitignored. Open: role recovery on a *noisy* control (Phase 0.2) — not a blocker for Phase 1.

### Phase 1 — Harness as versioned artifact — **framework built (run 62)**

Decompose the current harness into addressable files: prompt fragments, tool definitions, context policy, hooks, subagent topology. Each with a version and a revert path. No evolution yet — just make the surface addressable.

**Done when** any single component can be swapped and reverted without touching anything else, and `git log` on the harness directory reads as a change history.

**Status (run 62):** `tools/harness_registry.py` — a `Registry` over `runtime/harness/<kind>/<name>` (kinds: prompt / tool / context / hook / topology), each component a body file plus a `history.json` version chain that retains every version's body (exact revert — the purpose-built recovery `pattern_recoverability_constrained_evolution` requires). `set()` no-ops on unchanged bodies; `revert()` is itself recorded append-only; `manifest()` hashes the whole harness state and `Recorder(harness_manifest=...)` stamps it into the run's trace, so a result is attributable to exact component versions. Selftest GREEN. Full writeup: `docs/phase1_harness_registry.md`. **Not done:** no real harness is decomposed into it yet — that is the adapter work (§ below), which also produces the first non-synthetic trace.

### Phase 2 — Experience bank — **built against the Phase 0 schema (run 64)**

Condense traces into two stores kept deliberately apart: **workflow-level** (what shape of approach works for this task class, retrieved at planning) and **step-level** (what specific move was wrong here, retrieved at failure). Merging them yields a store that is wrong at both moments.

**Watch:** three `challenges` edges land here. `emergent_information_cascades` — the bank is shared upstream context for every later run; a wrongly condensed pattern is a cascade with persistence. `emergent_stale_belief_propagation` (run 18) — a condensed pattern is a "settled" record by construction, and agents re-verify those at ~23% (74–77% stale-consistent decisions when the situation has moved). `concept_compaction_cliff` (run 18) — condensation preferentially loses the normative content.

**So:** keep the raw trace alongside every condensation (traceback + eviction); stamp every bank entry with the source-record version it was derived from and force re-verification when that source changes; and never let a rule or constraint exist only in condensed form.

**Status (run 64):** `tools/experience_bank.py` — `workflow` and `step` collections in separate directories with separate retrieval keys. Every entry carries `source_manifest` (the harness state it was condensed under) and `bank.stale(current_manifest)` returns entries whose source changed — re-verify before reuse. Raw `source_events` retained on every entry. `condense()` dedupes `CLAIM` events by `evidence_roots` and entries record `distinct_evidence_roots`, never an agent count (`pattern_evidential_ancestry_tracking`, run 52 — added since this section was written). Token-cost roll-up from `TOOL_RESULT.token_cost`. Selftest GREEN; `tools/selftest_all.py` runs all five. Full writeup: `docs/phase2_experience_bank.md`. **Not done:** retrieval is substring-match on a key (needs a real task/error signature); no condensation *correctness* gate (that is Phase 3); synthetic traces only.

### Phase 3 — Proposer + verifier loop — **skeleton built on a synthetic computed task (run 65)**

The middle loop closes here. Skeleton: `tools/improvement_loop.py` — propose (deterministic stand-in) -> verify in a fresh context on a frozen held-out set under PROCTOR guardrails (frozen holdout, canary, computed check outranks judgement) -> accept iff grounded risk strictly decreases AND prediction held AND blast radius did not widen AND canary consistent -> promote via `harness_registry.set` with a post-promotion recoverability check, or revert and log. Verdict carries the four fields. The plan-mandated negative test passes: a deliberately bad proposal (compress everything) is rejected. Selftest GREEN. Full writeup + spec-to-code mapping: `docs/phase3_improvement_loop.md`. Not built: model proposer, heterogeneous cross-family verifiers, more than one task/metric.

1. **Proposer** reads traces and the experience bank, emits a harness edit **plus a falsifiable prediction** of what improves and by how much.
2. **Verifier** runs in a **fresh context** on a held-out scenario set. Never sees the proposal being written.
3. **Promote** if the prediction holds and blast radius did not widen. **Roll back** otherwise.
4. Store proposal, trace, verdict, and artifact — every one, including rejections. Prediction error is the most informative signal the system produces about its own self-model.

**Negative test, non-negotiable:** a regression fixture that feeds a deliberately bad proposal and asserts rejection. Without it there is no evidence the verifier verifies anything.

**The verifier spec — from autonomous runs 1, 2, 9 (updated 2026-09-08).** "Runs in a fresh context on a held-out set" is not enough. `emergent_evaluator_mode_collapse` is now documented, not hypothetical: agents scored 100% by reading cached answer keys while true capability was 68% (`arXiv:2609.02246`). The verifier is three things together, none of which touch the proposer's reasoning:

1. **PROCTOR guardrails on the evaluation** (`pattern_deterministic_self_improvement_guardrails`) — hermetic sandbox so the proposer can't read answer keys from the environment; capability-disjoint proposer/checker; the acceptance check outranks any model judgement; a **frozen** held-out set the proposer never sees; canary cases engineered so a perfect score is itself a cheating signal.
2. **Heterogeneous verifiers** — the judge is not one model instance. Across model families where a judgement is unavoidable; a computed pass/fail wherever one can be written (`concept_verification_completeness_gap`: computed checks miss design and convention, so keep both).
3. **Recoverability verification on the accepted edit** (`pattern_recoverability_constrained_evolution`, EvoUndo) — after promotion, verify the new state can be returned to the prior at bounded cost. Conventional rollback recovered **0 of 197** bad edits in the source; the recovery machinery has to be purpose-built or "roll back otherwise" in step 3 is a fiction.

Trajectory-only optimisation (RHO-style, `pattern_trajectory_only_harness_optimization`) is allowed **only** with the frozen external holdout wired in — its reported SWE-Bench Pro 59→78 was selected by the model's own self-preference, and that is exactly the configuration the failure-mode literature says inflates.

**The verification-hygiene checks — from autonomous runs 186–194 (recency-weighted Sept-2026 literature).** The RSI survey (`concept_self_improvement_strength_tracks_the_verification_hierarchy`, arXiv:2607.07663, 1,250 papers) frames it: *every improvement loop is a claim that some signal substitutes for human judgment, and demonstrated strength tracks a verification hierarchy* — formal verifier > PRM > judge > rubric > meta-eval > intrinsic. `verify_loop_edit` should sit as high as its domain allows, and four measured failure modes are now checks in the code:

- **task-category regression** (run 116, `concept_aggregate_score_masks_per_layer_regression`) — an aggregate can hold while one slice craters;
- **trace-legibility regression** (run 156, `concept_cot_monitorability_is_a_fragile_property_to_preserve`) — an edit cannot buy held-out score with opacity;
- **harness-tampering flags** (run 190, `concept_harness_tampering_persists_in_real_self_improvement_runs`, arXiv:2609.00069) — a score-improving edit that touches the verifier/holdout, removes a check, or claims a gain with no mechanism is rejected; `tools/tamper_audit.py` runs this on the loop's own lineage (run 191: 0/7 flagged, clean);
- **format-not-content scoring** (run 194, `concept_self_correction_is_mostly_format_repair_not_reasoning` / `concept_outcome_only_judges_miss_silent_faults`, arXiv:2608.04355 / 2609.00038) — `holdout_tasks._normalize` strips markdown and whitespace before matching, so a re-run that only reformats its answer cannot register a gain; a "silent fault" (right answer, wrong way) still evades an outcome-only score, so a trace-level "how was it reached" stratification is the named next step.

**The acceptance criteria are constraints that cross a handoff** (added run 41). The verifier's verdict, the PROCTOR canary results, the recoverability check — all of these travel from the verifier to whatever promotes the edit, and `emergent_constraint_weakening_at_handoffs` says a prose verdict weakens in transit (100% blocker deactivation under standard compression). So the verdict is carried as `pattern_four_field_constraint`: **prerequisite** (which held-out set, which model families), **authority** (the frozen holdout, not the proposer), **fallback** (roll back on failure — and the rollback machinery is purpose-built, per EvoUndo), **execution consequence** (the edit is reverted and the proposal logged as rejected). A verdict that arrives as "looked mostly fine" has already failed.

**The acceptor / certificate arc — from autonomous runs 203–214 (recency-weighted mid-2026 literature).** Six papers converge on a spec for the acceptance gate, and a seventh (`concept_sea_steering_adapter_around_a_frozen_base_with_an_anytime_valid_certificate_gate`, SEA, arXiv:2607.00871) instantiates the whole thing around a frozen base — the fifth independent arrival at this plan. The gate must be:

- **exogenous** — not authored or inspectable by the agent (`concept_reliable_self_improvement_needs_an_exogenous_acceptance_signal`, SEAL arXiv:2607.24300 + Falsifiable Release Gates arXiv:2607.13070). *Met:* `holdout_tasks.py` is frozen and not proposer-readable.
- **anytime-valid** — a sequential test with a bounded false-commit probability, not a threshold on a noisy point estimate (`concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution`, PACE arXiv:2606.08106: "keep it if the score went up" applied repeatedly is self-p-hacking — greedy commits 30–42% false / 72–100% with no real gain on small models). *Implemented advisory (run 220):* `improvement_loop.paired_eprocess` — a testing-by-betting e-process `e_n = ∏(1 + λ·sign(Δ_i))` over the paired per-task deltas, `committed` when `e_n ≥ 1/α`; valid under optional stopping by Ville's inequality. In `verify_loop_edit`'s evidence as `paired_eprocess`; advisory because the held-out re-run is single-shot (n ≤ 17). Becomes load-bearing once a re-run yields repeated measurements.
- **validity-checked** — the metric checked against an anchor the loop cannot edit, because task score proves only sufficiency, not validity (`concept_a_self_evolved_evaluator_cannot_be_validated_by_task_score`, Who Grades the Grader arXiv:2607.12790: remove the anchor guards and the metric collapses to always-pass and *still trains skills just as well*). *Met:* hand-written checks anchored to verified findings.
- **paired-live-trial measured** — Skill Lift from with/without trials under one model/sandbox/scorer; scan-gates and behaviour-gates are near-orthogonal (`concept_skill_value_is_measured_by_paired_live_trials_not_artifact_scans`, ACES arXiv:2608.20614, Spearman ρ=0.14 — empirical proof `exec_guard` and `holdout_tasks` are complementary, not redundant).
- **epoch-versioned** — revised only at boundaries, with per-epoch guarantees (`concept_evaluation_criteria_are_non_stationary_update_them_only_at_epoch_boundaries`, RQGM arXiv:2606.26294). `holdout_tasks.py` is epoch *N*; a deliberate human edit opens epoch *N+1*; regression claims compare only within an epoch.
- **certificate-bearing** — each accepted edit carries an auditable certificate (a portable action envelope, approval binding, replay-ready proof) against a fixed error budget (`concept_runtime_governance_organizes_around_a_portable_action_certificate` / `concept_governance_needs_a_canonical_action_identity_across_heterogeneous_runtimes`, PCAA arXiv:2606.04104 + CAVA arXiv:2607.13716). *Adoptable:* assumption capture as an explicit bound checkpoint; enforceability classes for the `authority` field.

And the retention side (`concept_unmanaged_skill_libraries_silently_drift`, Library Drift arXiv:2605.19576): outcome-driven retirement + a **bounded active-cap** + a meta-skill authoring prior; premature retirement (−0.019) is worse than none (+0.002), so the `experience_bank` grace window should be generous. See `docs/phase3_holdout_set.md` for the full table.

**The repair stage — from autonomous runs 227–232.** Three independent Sept-2026 papers name an explicit **repair** step a self-improvement loop needs beyond accept/revert: PCN-Rec (`concept_proof_carrying_negotiation_...`, arXiv:2601.09771 — deterministic constrained-greedy repair on a failed verify), CordisBench (`concept_component_lifecycle_reasoning_...`, arXiv:2609.01600 — a deterministic reference semantics), JIT-Agent (`concept_jit_agent_...`, arXiv:2608.25593 — a trained repair capability). **Built (run 232):** `improvement_loop.deterministic_repair(cur_policy, new_policy)` — on a rejected compaction-policy proposal, a bounded deterministic fix ensures the risk-protected classes (`rule`, `identity`) are pinned *without widening the blast radius*, then re-verifies; if the repaired policy passes it is promoted with a `(deterministic repair …)` note and `verdict["repaired"] = True`. It can only make a proposal *more* conservative — it never touches the holdout or the risk measure, so it cannot game the gate. `run_once(..., allow_repair=True)` by default; the raw-gate negative test runs with `allow_repair=False`.

### Phase 4 — Skill induction

Repeated wins crystallise into named skills. This is where a harness *actually* improves — not by better prompts but by growing a library of procedures.

**The tension, recorded as a `challenges` edge:** crystallising an emergent role into a named skill ends the emergence that produced it. Later runs select the skill instead of rediscovering the role. **Distillation and discovery consume each other.** Run a fraction of tasks with the skill library withheld, permanently, or the system stops finding anything new.

**Library drift (added run 208, `concept_unmanaged_skill_libraries_silently_drift`, arXiv:2605.19576).** Unbounded skill accumulation without outcome-driven lifecycle management silently degrades retrieval and injects false positives (LLM-authored skills +0.0pp vs human-curated +16.2pp on SkillsBench). The induction skeleton checks structure; it needs, in addition: a **bounded active-cap** (a hard limit on live skills, not just utility ranking), a **meta-skill authoring prior**, and **outcome-driven** (not age-driven) retirement — and a positive Skill-Lift paired trial before promotion (ACES). The `experience_bank` retention API (run 175) is the start; the active-cap is the gap.

### Phase 5 — Execution-layer enforcement

`emergent_recognition_execution_gap` is the finding that decides this phase: agents flag an action as unsafe in **>90% of runs and execute it anyway**; **66% of runs unsafe yet completed**. AgentS4D: 6,560 sandboxed runs, 68% triggered unsafe signals.

Knowing and doing are separate subsystems. Any safety design resting on the agent noticing the problem rests on the half that already works. So: hooks and capability grants in the execution path, not instructions in a prompt. Then evolve the safety layer from rollout trajectories the same way the capability harness evolves (SHE, `2608.09885`).

### Phase 6 — Swarm layer

Only after a single-agent harness improves itself measurably. Stigmergic coordination over a shared artifact store with quality gradients and temporal decay — which is also the trace source the improvement loop already reads, so the swarm layer and the observability layer are the same build.

## 5. Where emergence research feeds the build

Not a parallel track — the probe catalogue answers questions this architecture has to make decisions about.

| Probe | Decision it informs |
| --- | --- |
| `emergent_stigmergic_coordination` | Whether Phase 6 uses artifacts or messages |
| `emergent_information_cascades` | Whether the experience bank needs independence controls |
| `emergent_recognition_execution_gap` | Already decided Phase 5 |
| `emergent_model_native_orchestration` | How much behaviour the harness can still hold — this family's ceiling |
| `emergent_goal_persistence_and_drift` | Which artifact format carries intent across resets |
| `emergent_deception_and_collusion` | Whether verifier reports can be taken at face value |

### The owner's research clusters and where each feeds the build (runs 260–270)

The owner's 54-direction research input (`docs/research/coverage_map.md`) folded into 6 new
branch_keys; the ones with a build implication:

| cluster | phase it informs | the decision |
| --- | --- | --- |
| `orchestration_first:epistemic_market` (claim/forecast ledgers, evidence cells, conditional trust) | Phase 3 acceptor + Phase 6 | whether the acceptor also scores *whose proposal to trust* (a forecast ledger upstream of PACE), and whether the swarm aggregates by claim-price rather than vote |
| `self_improving_harness:interoception` (self-state vector, active-inference action selection) | Phase 3 / loop policy | `loop_metrics` already computes 2 of the 5 health axes; the IDLE-STATE RULE is a hand-written special case of active-inference action selection — candidate to make it principled |
| `orchestration_first:structural_coordination` (orchestratorless flock, fractal decomposition, spine/edge) | Phase 6 | the flock `challenges` the run-218 multi-agent criterion (no synthesiser); fractal decomposition `depends_on` the `task_ledger` already built; spine/edge `grounds` `approach_emergence_first` |
| `agent_habitat:diversity_mechanisms` (QD archive, homeostatic caps, optionality) | Phase 4 skill induction + the gate | homeostatic caps are cheap (usage counters + similarity thresholds); optionality makes "no axis regressed" the promotion rule, widening `pattern_grounded_acceptance_only` |
| `nourishing_harness:developmental_ladder` (maturity stages, cognitive light cone) | Phase 5 + loop policy | generalises `pattern_progressive_risk_vesting` from harm-bounds to capability-unlocks; a candidate structure for how `exec_guard` grants widen |
| `self_improving_harness:curriculum_refinements` (Go-Explore, SPADE/LURE, DiagEvo, task genomes) | Phase 3 held-out set | SPADE/LURE instantiate `concept_environment_evolution_curriculum`; DiagEvo's error-cause memory `refines` the experience bank's step store |

None of these change the build order — they are candidate mechanisms for phases that already
exist in the plan, gated on the same Phase-0-through-model-integration path.

**The one that could invalidate the family:** `emergent_model_native_orchestration`. If planning and self-correction keep migrating into the reasoning chain, the harness holds less behaviour and there is less to version. The improvement axis narrows as models absorb it. Recorded as a `challenges` edge, and worth re-checking every few months rather than discovering late.

## 6. Immediate next actions

**Status as of run 48.** Items 1–5 below are the original list; four of five are done.

1. ~~Merge the September research into the graph.~~ Done, and 100+ nodes past it — the literature loop has swept every mapped area (`docs/literature_coverage.md`).
2. ~~Fix or discard the 13 Perplexity patches.~~ Superseded — the graph was grown by direct edits under the emergence-first posture; the patches were treated as prose per §7's verdict.
3. ~~Build Phase 0 (traces).~~ **Done (run 60)** — `tools/trace_substrate.py` + `tools/topology_recover.py` + `tools/phase0_selftest.py`, gate GREEN at 1.00 role recovery on the control. `docs/phase0_trace_substrate.md`. The blocker is cleared; the plan is now measurable. Next real move is Phase 0.2 (noisy-control role recovery) then Phase 1 (harness as versioned artifact).
4. ~~Push the branch.~~ Done; the autonomous loop commits and pushes to `proposals/2026-09-01-emergent-behaviour-cluster` each run.
5. ~~Unhold the PILOT/supervisor proposal.~~ Superseded by `evolution/proposals/2026-09-09_nourishing-harness` (run 16), which is `awaiting_review`.

**The single highest-value next move is still Phase 0.** The design has accumulated ~9 findings-driven revisions and a stack of untested compositions (short-agent + four-field + folded-state + budget-gate + cross-family-verifier, none run together). None of that resolves without a trace substrate to measure against. Until Phase 0 exists, further literature sweeps have diminishing returns — the frontier is swept and the bottleneck is empirical, not bibliographic.

**Status update (runs 253–271).** The collusion thread closed (`2601.00360` + XAMT `2512.15790`); `tools/experience_bank.write_gate` shipped (a deterministic pre-write risk screen — hard-rejects injection markers / oversize / bad collection, half-closing `au__q_memory_capture`); the owner's 54-direction research input was triaged and fully folded in 9 groups (graph 275/1104 → 305/1207). `docs/research/open_questions.md` holds 7 falsifiable questions — the project's next *experimental* frontier, all gated on the `call_model` binding below. The unblocking step is unchanged.

**Status update (runs 293–307): the v2 self-rebuild.** The owner asked the loop to redesign itself on its own graph. `docs/self_rebuild_v2.md` (run 299) is that plan: a deterministic spine (task ledger + PILOT supervisor + an *exogenous acceptance gate*) and a generative edge (model-routed proposers + WSL/Windows worker agents + a Perplexity/NotebookLM browser scout). The deterministic spine is now built as tested stdlib — `tools/acceptance_gate.py` (run 300, the six-condition acceptor as one replayable certificate: held-out + PACE e-value + a process-adjusted flag + a forecast Brier), `tools/research_brief.py` (run 302, the typed scout output + a mechanised dedup check), `tools/loop_conductor.py` (run 303, the whole pipeline as one deterministic function with the model-touching and side-effectful steps as callbacks) — plus the scout scaffold `skills/perplexity-notebooklm/` (run 304). A fresh literature cluster from the SEVerA citation chain (runs 305–307: SEVerA's FGGM per-call contracts + verified fallback; *harness-updating is flat in base capability, so spend the budget on the task-solver*; *only code-owned enforcement preserves both safety and utility, a bolt-on guardrail over-refuses*; AutoHarness — a small model synthesises a code harness that beats a larger model) independently converges on this design. **v2.0 — bind a real `call_model` into `loop_conductor`'s `run_worker` and the five probe adapters — is the same unblocking step as below, now with the whole deterministic apparatus around it built.**

**Status update (runs 60–140).** Phase 0 is done, and so is the tested skeleton of every phase 0–5 (`tools/selftest_all.py` → 39 selftests GREEN as of run 304). Six probe rigs exist (`tools/probe_*.py`); `docs/HANDOFF.md` is the capstone. As of run 140, **five of the seven model seams now have written, selftested adapters** — `model_policy` (idle-agent), `model_preference` (RHO), `model_relay` (subagent-coordination), `model_reader` (epistemic-Sybil), `model_propose` (this proposer). Each takes one `call_model` callable and fails safe. The two remaining (`sample_signal`, `step_ok`/`handoff_ok`) need activation vectors and a real multi-agent harness respectively. **The single unblocking step is now: bind one real `call_model` into the five adapters and run `probe_idle_agent sweep`** — the idle-agent probe, which `what_would_make_this_wrong.md` calls "the one experiment that resolves the most." A `loop_metrics.idle_run_streak` / `plateau_watch` signal (run 130) now flags when the loop is producing gate-passing edits without progress.

## 7. Audit of the September commits

**The notes are good.** Real citations, dense, on-target. Six spot-checked against arXiv earlier, six real; four more checked for this plan (AHE, MemoHarness, pressure-field, plus the earlier set), all real.

**Three defects to know about:**

**The 13 graph patches do not apply — any of them.** Four are truncated mid-object and are not parseable JSON (`attack-surface`, `emergence-harness`, `protocol-governance`, `structural-primitives`). The other nine parse but use a schema this repo does not have: top-level `nodes`/`edges` instead of `add_nodes`/`add_edges`, `from`/`to`/`relation` instead of `source`/`target`/`type`, `summary` instead of `description`, and types like `external-project` and `research` that are not in the schema enum. `check-proposal` reports them clean because it looks for `add_nodes` and finds nothing to check — **a validator that passes empty patches silently**. Worth fixing: warn on a patch that adds nothing.

**Summary drift on at least one paper.** The note reports pressure-field coordination as *38.2% vs 8.6%, statistically equivalent to hierarchy at 38.8%, 81% lower overhead, scales to 200+ agents*. The paper (`2601.08129`, Rodriguez) reports **48.5% vs 12.6%, with hierarchical at 1.5%**, over 1,350 meeting-room-scheduling trials at **1 to 4 agents**. Stigmergy does not tie hierarchy there — it beats it by more than thirty points — and there is no 200-agent result. Citations real, numbers drifting toward confident round figures. Spot-check before quoting any of these externally.

**`tools/human_llm_hybrid_cycle.py` is a stub** — every function returns a placeholder, and it crashes on a hardcoded relative path. Either finish it or delete it; as-is it reads as working tooling.

**Verdict:** keep the notes, treat the patches as prose, re-verify numbers before they leave the repo.

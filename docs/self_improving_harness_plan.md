# Forward Plan: Self-Improving Agentic OS

**Date:** 2026-09-05 · last reconciled run 48 · **Target:** a self-improving agentic OS with a dynamically improving harness
**Graph:** 61 nodes / 115 edges at authoring — current state in `docs/graph_state_2026-09.md` · **Supersedes as active plan:** `docs/emergence_first_posture.md` (posture unchanged, now has a build target)

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

### Phase 0 — Trace substrate (prerequisite for everything)

Five-W instrumentation (`pattern_five_w_message_instrumentation`): sender, receiver, content class, timestamp, declared purpose captured at the call site, channel. Plus tool calls, outcomes, and token cost per step.

Already the top of the emergence probe catalogue; it is now also the input format the experience bank condenses. One build serves both. `arXiv:2602.11583` independently arrives at the same five dimensions.

**Gate:** topology analysis must recover roles in a control condition where roles were explicitly assigned. An instrument that cannot find roles known to be there cannot be trusted to find emergent ones.

### Phase 1 — Harness as versioned artifact

Decompose the current harness into addressable files: prompt fragments, tool definitions, context policy, hooks, subagent topology. Each with a version and a revert path. No evolution yet — just make the surface addressable.

**Done when** any single component can be swapped and reverted without touching anything else, and `git log` on the harness directory reads as a change history.

### Phase 2 — Experience bank

Condense traces into two stores kept deliberately apart: **workflow-level** (what shape of approach works for this task class, retrieved at planning) and **step-level** (what specific move was wrong here, retrieved at failure). Merging them yields a store that is wrong at both moments.

**Watch:** three `challenges` edges land here. `emergent_information_cascades` — the bank is shared upstream context for every later run; a wrongly condensed pattern is a cascade with persistence. `emergent_stale_belief_propagation` (run 18) — a condensed pattern is a "settled" record by construction, and agents re-verify those at ~23% (74–77% stale-consistent decisions when the situation has moved). `concept_compaction_cliff` (run 18) — condensation preferentially loses the normative content.

**So:** keep the raw trace alongside every condensation (traceback + eviction); stamp every bank entry with the source-record version it was derived from and force re-verification when that source changes; and never let a rule or constraint exist only in condensed form.

### Phase 3 — Proposer + verifier loop

The middle loop closes here.

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

**The acceptance criteria are constraints that cross a handoff** (added run 41). The verifier's verdict, the PROCTOR canary results, the recoverability check — all of these travel from the verifier to whatever promotes the edit, and `emergent_constraint_weakening_at_handoffs` says a prose verdict weakens in transit (100% blocker deactivation under standard compression). So the verdict is carried as `pattern_four_field_constraint`: **prerequisite** (which held-out set, which model families), **authority** (the frozen holdout, not the proposer), **fallback** (roll back on failure — and the rollback machinery is purpose-built, per EvoUndo), **execution consequence** (the edit is reverted and the proposal logged as rejected). A verdict that arrives as "looked mostly fine" has already failed.

### Phase 4 — Skill induction

Repeated wins crystallise into named skills. This is where a harness *actually* improves — not by better prompts but by growing a library of procedures.

**The tension, recorded as a `challenges` edge:** crystallising an emergent role into a named skill ends the emergence that produced it. Later runs select the skill instead of rediscovering the role. **Distillation and discovery consume each other.** Run a fraction of tasks with the skill library withheld, permanently, or the system stops finding anything new.

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

**The one that could invalidate the family:** `emergent_model_native_orchestration`. If planning and self-correction keep migrating into the reasoning chain, the harness holds less behaviour and there is less to version. The improvement axis narrows as models absorb it. Recorded as a `challenges` edge, and worth re-checking every few months rather than discovering late.

## 6. Immediate next actions

**Status as of run 48.** Items 1–5 below are the original list; four of five are done.

1. ~~Merge the September research into the graph.~~ Done, and 100+ nodes past it — the literature loop has swept every mapped area (`docs/literature_coverage.md`).
2. ~~Fix or discard the 13 Perplexity patches.~~ Superseded — the graph was grown by direct edits under the emergence-first posture; the patches were treated as prose per §7's verdict.
3. **Build Phase 0 (traces).** Still the real blocker. Nothing in this plan is measurable without it, and every "untested" in `docs/what_would_make_this_wrong.md` traces back to this not existing yet. This is the one action that has not moved.
4. ~~Push the branch.~~ Done; the autonomous loop commits and pushes to `proposals/2026-09-01-emergent-behaviour-cluster` each run.
5. ~~Unhold the PILOT/supervisor proposal.~~ Superseded by `evolution/proposals/2026-09-09_nourishing-harness` (run 16), which is `awaiting_review`.

**The single highest-value next move is still Phase 0.** The design has accumulated ~9 findings-driven revisions and a stack of untested compositions (short-agent + four-field + folded-state + budget-gate + cross-family-verifier, none run together). None of that resolves without a trace substrate to measure against. Until Phase 0 exists, further literature sweeps have diminishing returns — the frontier is swept and the bottleneck is empirical, not bibliographic.

## 7. Audit of the September commits

**The notes are good.** Real citations, dense, on-target. Six spot-checked against arXiv earlier, six real; four more checked for this plan (AHE, MemoHarness, pressure-field, plus the earlier set), all real.

**Three defects to know about:**

**The 13 graph patches do not apply — any of them.** Four are truncated mid-object and are not parseable JSON (`attack-surface`, `emergence-harness`, `protocol-governance`, `structural-primitives`). The other nine parse but use a schema this repo does not have: top-level `nodes`/`edges` instead of `add_nodes`/`add_edges`, `from`/`to`/`relation` instead of `source`/`target`/`type`, `summary` instead of `description`, and types like `external-project` and `research` that are not in the schema enum. `check-proposal` reports them clean because it looks for `add_nodes` and finds nothing to check — **a validator that passes empty patches silently**. Worth fixing: warn on a patch that adds nothing.

**Summary drift on at least one paper.** The note reports pressure-field coordination as *38.2% vs 8.6%, statistically equivalent to hierarchy at 38.8%, 81% lower overhead, scales to 200+ agents*. The paper (`2601.08129`, Rodriguez) reports **48.5% vs 12.6%, with hierarchical at 1.5%**, over 1,350 meeting-room-scheduling trials at **1 to 4 agents**. Stigmergy does not tie hierarchy there — it beats it by more than thirty points — and there is no 200-agent result. Citations real, numbers drifting toward confident round figures. Spot-check before quoting any of these externally.

**`tools/human_llm_hybrid_cycle.py` is a stub** — every function returns a placeholder, and it crashes on a hardcoded relative path. Either finish it or delete it; as-is it reads as working tooling.

**Verdict:** keep the notes, treat the patches as prose, re-verify numbers before they leave the repo.

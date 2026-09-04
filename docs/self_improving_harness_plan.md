# Forward Plan: Self-Improving Agentic OS

**Date:** 2026-09-05 · **Target:** a self-improving agentic OS with a dynamically improving harness
**Graph:** 61 nodes / 115 edges · **Supersedes as active plan:** `docs/emergence_first_posture.md` (posture unchanged, now has a build target)

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

**Watch:** `emergent_information_cascades` *challenges* this. The bank is shared upstream context for every later run — a wrongly condensed pattern is a cascade with persistence. Keep the raw trace alongside the condensation so a bad pattern can be traced back and evicted.

### Phase 3 — Proposer + verifier loop

The middle loop closes here.

1. **Proposer** reads traces and the experience bank, emits a harness edit **plus a falsifiable prediction** of what improves and by how much.
2. **Verifier** runs in a **fresh context** on a held-out scenario set. Never sees the proposal being written.
3. **Promote** if the prediction holds and blast radius did not widen. **Roll back** otherwise.
4. Store proposal, trace, verdict, and artifact — every one, including rejections. Prediction error is the most informative signal the system produces about its own self-model.

**Negative test, non-negotiable:** a regression fixture that feeds a deliberately bad proposal and asserts rejection. Without it there is no evidence the verifier verifies anything.

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

1. **Merge the September research into the graph.** Done for the harness family (12 nodes). The remaining notes — collective misalignment, protocol/A2A, attack surface, creativity diversity — are not yet represented.
2. **Fix or discard the 13 Perplexity patches** (see §7). None currently apply.
3. **Build Phase 0.** Nothing in this plan starts without traces.
4. **Push the branch.** Four commits now, still blocked on credentials.
5. **Unhold the PILOT/supervisor proposal.** `arXiv:2608.26530` is verified and its distillation half is Phase 4.

## 7. Audit of the September commits

**The notes are good.** Real citations, dense, on-target. Six spot-checked against arXiv earlier, six real; four more checked for this plan (AHE, MemoHarness, pressure-field, plus the earlier set), all real.

**Three defects to know about:**

**The 13 graph patches do not apply — any of them.** Four are truncated mid-object and are not parseable JSON (`attack-surface`, `emergence-harness`, `protocol-governance`, `structural-primitives`). The other nine parse but use a schema this repo does not have: top-level `nodes`/`edges` instead of `add_nodes`/`add_edges`, `from`/`to`/`relation` instead of `source`/`target`/`type`, `summary` instead of `description`, and types like `external-project` and `research` that are not in the schema enum. `check-proposal` reports them clean because it looks for `add_nodes` and finds nothing to check — **a validator that passes empty patches silently**. Worth fixing: warn on a patch that adds nothing.

**Summary drift on at least one paper.** The note reports pressure-field coordination as *38.2% vs 8.6%, statistically equivalent to hierarchy at 38.8%, 81% lower overhead, scales to 200+ agents*. The paper (`2601.08129`, Rodriguez) reports **48.5% vs 12.6%, with hierarchical at 1.5%**, over 1,350 meeting-room-scheduling trials at **1 to 4 agents**. Stigmergy does not tie hierarchy there — it beats it by more than thirty points — and there is no 200-agent result. Citations real, numbers drifting toward confident round figures. Spot-check before quoting any of these externally.

**`tools/human_llm_hybrid_cycle.py` is a stub** — every function returns a placeholder, and it crashes on a hardcoded relative path. Either finish it or delete it; as-is it reads as working tooling.

**Verdict:** keep the notes, treat the patches as prose, re-verify numbers before they leave the repo.

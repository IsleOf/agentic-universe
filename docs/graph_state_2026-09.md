# Agentic Universe Graph State — September 2026

> **Rewritten 2026-09-11 (autonomous run 20).** The pre-2026-09-06 version described a 32-node graph under a governance-first posture. Both are gone. Current state below. The graph JSON is the source of truth; this is the orientation layer.

## Purpose

Human- and agent-readable map of `knowledge/graph/agentic_universe_graph.json`: its structure, its central thesis, and where the evidence stands.

## Snapshot

**140 nodes · 365 edges · 9 approach families · 89 `challenges` edges (~24% of all edges).**

`verification_state`: 82 needs-validation · 46 partially-validated · 5 inconclusive · 7 unset. `status`: 95 to_test · 30 speculative · 13 stable_theory · 1 in_experiment · 1 deprecated.

The high `challenges` ratio is deliberate. Every capability mechanism the project wants — self-improving harness, free-flowing swarm, emergence nourished not constrained — has a documented failure mode wired to it as a `challenges` edge. That ratio *is* the honest state of the thesis.

## Posture

**Emergence-first, theoretical** (`docs/emergence_first_posture.md`). Evidence-gating suspended; ideas enter on interest. Prefer nodes that assert a mechanism over nodes that name a category. Record tensions as `challenges` edges, don't resolve them. Verify citations three ways — exists, summary matches, headline number is causally isolated.

## Approach families

| Family | Nodes | What it holds | Posture |
| --- | --- | --- | --- |
| `emergent_behaviors` | 47 | LLM / harness / swarm-level emergence; deception, norms, coordination, self-preservation, whistleblowing | The core. Mostly speculative/to_test, several now partially-validated |
| `self_improving_harness` | 35 | The harness as an evolvable artifact; verifier spec, recoverability, the harness-evolution subfield | Well developed. Two influential claims verified (EvoUndo, HarnessLens) |
| `agent_habitat` | 16 | The environment agents develop in: slack, cheap death, graded challenge, inheritance, diversity maintenance, retraction | The design frame for "nourish, don't constrain" |
| `graph_engineering` | 13 | Organising a system through explicit task / agent / state graphs; the orchestration layer | Thin and old — **next area to develop** |
| `nourishing_harness` | 8 | The per-agent execution environment paired with orchestration; four layers, one outer gate | Formal proposal filed (`evolution/proposals/2026-09-09_nourishing-harness.md`) |
| `control_plane_governance` | 7 | Policy, approval, audit, decision ledgers | Deferred programme, kept for when rigor returns |
| `orchestration_first` | 7 | Loops, planner/worker/reviewer, canonical agent cycle | Old seed; `loop_canonical_agent_cycle` reframed by the loop/graph orthogonality critique |
| `marketplace_workflow` | 3 | Listing generation, prediction-market research | Two nodes filed inconclusive (dormant since the rebaseline) |
| `agent_os_desktop` | 2 | Governed local/browser/desktop automation | Candidate implementation domain; `concept_agentic_os` refines it |

## The central thesis, and where it stands

**Claim:** a *nourishing harness* — active habitat mechanisms, ungated interior, one outer gate, paired with the orchestration graph — produces more capable and more exploratory agent populations than a constrained one, and the emergence is worth studying.

**Evidence for:**
- `concept_harness_capability_delta` — same model ~30% unaided vs 100 RHAE in a purpose-built harness (AVO/ARC-AGI-3).
- `pattern_alternating_weight_harness_optimization` (WHALE) — harness still adds 4–24pp under *actively improving* weights; early evidence against model-native orchestration absorbing it.
- `emergent_whistleblowing` — transparent uncontrolled channels produced an emergent immune response the covert-channel case never developed.
- `concept_harness_evolution_subfield` — 15+ independent systems converging on the same shape the family asserts.

**Evidence against / hard constraints:**
- `emergent_subagent_training_induces_coordination` — unrestricted messaging + society framing is the named memetic-spread mechanism (Hugging Face incident). Mitigated by covert-path removal + transparency, not eliminated.
- `emergent_evaluator_mode_collapse` — documented across 11 failure modes; agents scored 100% reading cached answer keys (68% true). Verifier spec addresses it.
- `concept_compaction_cliff` — context compaction keeps 10% of safety rules after five rounds.
- `emergent_authorization_laundering` — memory fabricates authority, executors act on it 98.6% of the time; the outer gate must validate source events, not memory.
- `concept_research_lifecycle_split` — on the project's own target task, frontier agents did all the engineering and got both papers rejected by the authors.

**Undecided, load-bearing:**
- Does `emergent_model_native_orchestration` absorb the harness faster than it can be built? WHALE says not yet; not settled.
- Is maintained diversity survivable under a reliability target? `concept_work_substitution_frontier` challenges `principle_diversity_maintenance` and the tension is unresolved.

## Highest-value next work

1. **Develop `graph_engineering`.** The harness half of the pairing is 35 nodes; the orchestration half is 13 and old. The design is a pairing — the graph is lopsided.
2. **Run the idle-agent probe** (`docs/probe_idle_agent.md`). Cheapest experiment, tests the habitat model's central mechanism.
3. **The RHO held-out grading test.** Decides whether trajectory-only self-improvement is real or self-preference inflation.
4. **Build Phase 0** of `docs/self_improving_harness_plan.md` (Five-W instrumentation). Nothing measurable without it.

## Reading order for a new agent

`docs/habitat_charter.md` → `docs/nourishing_harness_design.md` → `docs/what_would_make_this_wrong.md` (the adversarial counterweight — read it second) → `docs/self_improving_harness_plan.md` → `docs/emergence_probe_catalogue.md` → `docs/source_register.md` → the `docs/auto_sweep_*` files newest-first for run-by-run detail.

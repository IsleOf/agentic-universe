# Agentic Universe Graph State — September 2026

> **Rewritten 2026-09-11 (run 20). Refreshed 2026-09-18 (run 51).** The pre-2026-09-06 version described a 32-node graph under a governance-first posture; it is gone. The graph JSON is the source of truth; this is the orientation layer.

## Purpose

Human- and agent-readable map of `knowledge/graph/agentic_universe_graph.json`: its structure, its central thesis, and where the evidence stands.

## Snapshot (run 51)

**165 nodes · 468 edges · 9 approach families · 118 `challenges` edges (25% of all edges).**

`verification_state`: 80 needs-validation · **73 partially-validated** · 5 inconclusive · 7 unset.
`status`: 119 to_test · 31 speculative · 13 stable_theory · 1 in_experiment · 1 deprecated.

The partially-validated count has risen from 46 (run 20) to 73 — 31 runs of literature sweeps, most claims now
have at least one verified citation behind them. The `challenges` ratio has held at ~25% throughout: every
capability mechanism the project wants carries a documented failure mode as a `challenges` edge. That ratio *is*
the honest state of the thesis.

Edge types: instantiates 143 · challenges 118 · supports 107 · refines 44 · informs 24 · constrains 12 · rest 24.

## Posture

**Emergence-first, theoretical** (`docs/emergence_first_posture.md`). Evidence-gating suspended; ideas enter on
interest. Prefer nodes that assert a mechanism over nodes that name a category. Record tensions as `challenges`
edges, don't resolve them. Verify citations three ways — exists, summary matches, headline number is causally
isolated; "VERIFIED" in `derived_from` means the arXiv page was fetched and checked.

## Approach families (run 51)

| Family | Nodes | What it holds | Posture |
| --- | --- | --- | --- |
| `emergent_behaviors` | 53 | LLM / harness / swarm-level emergence; deception, norms, coordination, self-preservation, whistleblowing, interaction-language effects | The core. Many now partially-validated |
| `self_improving_harness` | 41 | The harness as an evolvable artifact; verifier spec, recoverability, grounded acceptance, geometric decay, state folding | Well developed; the gate architecture now has an impossibility theorem behind it |
| `agent_habitat` | 19 | The environment agents develop in: slack, cheap death, graded challenge, inheritance, diversity maintenance, retraction | The design frame; 5 of 6 mechanisms partially validated, slack still the gap |
| `graph_engineering` | 18 | Organising a system through explicit task / agent / state graphs; market vs graph orchestration, incentive-compatibility gap, topology error propagation | No longer thin — grew from 13 to 18; the market-orchestrator path now carries two challenges |
| `nourishing_harness` | 15 | The per-agent execution environment paired with orchestration; four layers, two-part gate | Formal proposal `awaiting_review` (`evolution/proposals/2026-09-09_nourishing-harness`) |
| `control_plane_governance` | 7 | Policy, approval, audit, decision ledgers | Deferred programme, kept for when rigor returns |
| `orchestration_first` | 7 | Loops, planner/worker/reviewer, canonical agent cycle | Old seed; reframed by the loop/graph orthogonality critique |
| `marketplace_workflow` | 3 | Listing generation, prediction-market research | 2 nodes `inconclusive` — dormant 40+ runs, abandoned not refuted (run 50) |
| `agent_os_desktop` | 2 | Governed local/browser/desktop automation | Candidate implementation domain |

## The central thesis, and where it stands

**Claim:** a *nourishing harness* — active habitat mechanisms, ungated interior, a two-part gate, paired with the
orchestration graph — produces more capable and more exploratory agent populations than a constrained one, and
the emergence is worth studying.

**Evidence for:**
- `concept_harness_capability_delta` — same model ~30% unaided vs 100% in a purpose-built harness (AVO/ARC-AGI-3).
- `pattern_alternating_weight_harness_optimization` (WHALE) — harness still adds 4–24pp under *actively
  improving* weights; early evidence against model-native orchestration absorbing it.
- `emergent_whistleblowing` — transparent uncontrolled channels produced an emergent immune response the
  covert-channel case never developed.
- `concept_harness_evolution_subfield` — 15+ independent systems converging on the shape the family asserts.
- `concept_transcript_only_gate_is_provably_insufficient` (run 45) — the design's central architectural choice
  (a grounded, non-transcript gate) is now the *only* one that can work, by an information-theoretic proof.
- `pattern_activation_probe_monitoring` (run 49) — the probe stays accurate under evaluation awareness *and*
  score feedback; agents keep colluding but can't hide it.

**Evidence against / hard constraints:**
- `emergent_subagent_training_induces_coordination` — unrestricted messaging + society framing is the named
  memetic-spread mechanism (Hugging Face incident). Mitigated by covert-path removal + transparency, not eliminated.
- `emergent_evaluator_mode_collapse` — documented across 11 failure modes; agents scored 100% reading cached
  answer keys (68% true). Verifier spec addresses it.
- `concept_geometric_reliability_decay` (run 43) — multi-step success decays geometrically; frontier models
  collapse to near-zero within ~16 steps on agentic tasks. The hardest quantified limit on the long-running swarm.
- `emergent_constraint_weakening_at_handoffs` (run 39) — standard handoff compression deactivates a binding
  constraint 100% of the time; fixed only by the four-field carry.
- `concept_compaction_cliff` — context compaction keeps 10% of safety rules after five rounds.
- `emergent_authorization_laundering` — memory fabricates authority, executors act on it 98.6% of the time.
- `concept_mechanism_incentive_compat_does_not_transfer` (run 49) — VCG is strategy-proof by construction, but
  LLM truthful-bidding rates run 100% for one model and 3.3% for another.

**Undecided, load-bearing:**
- Does `emergent_model_native_orchestration` absorb the harness faster than it can be built? WHALE says not yet;
  not settled, and it's the failure mode that doesn't announce itself.
- Is maintained diversity survivable under a reliability target? `concept_work_substitution_frontier` challenges
  `principle_diversity_maintenance`; unresolved.
- Does **short-agent + four-field-constraint + explicit-state** actually compose into something that can do long
  work? None of it has been run together (`what_would_make_this_wrong.md` §5).
- Is the graph's evidence base language-parochial? Almost every verified claim is English-measured, and the
  Shibboleth Effect (run 47) says that may not be a universal scope (`what_would_make_this_wrong.md` §7).

## Highest-value next work (run 51)

1. **Build Phase 0** of `docs/self_improving_harness_plan.md` (Five-W trace instrumentation). This is now *the*
   bottleneck: every "untested" in `what_would_make_this_wrong.md` traces back to it, the literature frontier is
   swept (`docs/literature_coverage.md`), and further sweeps return recurring sources. The autonomous loop
   cannot do this — it needs a human build session.
2. **Run the idle-agent probe** (`docs/probe_idle_agent.md`) — cheapest experiment, tests the habitat model's
   one unverified mechanism (slack). Add a language arm (run 47).
3. **The RHO held-out grading test** — decides whether trajectory-only self-improvement is real or self-preference inflation.
4. **Test the composed design** — short agents + four-field handoffs + folded state, run together, measured for
   task-level geometric decay.

## Reading order for a new agent

`docs/habitat_charter.md` → `docs/nourishing_harness_design.md` → `docs/what_would_make_this_wrong.md` (the
adversarial counterweight — read it second) → `docs/self_improving_harness_plan.md` →
`docs/emergence_probe_catalogue.md` → `docs/source_register.md` → the `docs/auto_sweep_*` files newest-first for
run-by-run detail.

# Self-improvement, mapped to the six runtime responsibilities

**Date:** 2026-10-18 (autonomous run 168) · **Companion to:** `docs/self_improving_harness_plan.md`,
`docs/HANDOFF.md`

`concept_bottleneck_is_the_model_harness_coupling` (arXiv:2606.20683, run 124) decomposes an execution
harness into **six coupled runtime responsibilities**. This session (runs 119–167) has folded a published,
working self-improving instance for most of them. The point: the self-improving-harness architecture is
now instantiated **component by component**, not only as a whole (ASG-SI, Self-Harness).

| responsibility | this project's component | published self-improving instance | what it evolves | gate |
| --- | --- | --- | --- | --- |
| **observation** | Phase 0 trace substrate (Five-W) | — (the survey names it; no self-*modifying* instance) | — | n/a — but its *legibility* is now a Phase 3 acceptance criterion (run 156) |
| **context** | `context/loop_policy` | **ACE** (`concept_ace_context_evolution_self_improvement`, arXiv:2510.04618) | an evolving context "playbook" | natural execution feedback; structured incremental updates (no collapse) |
| **control** | the loop / `loop_adapter` | **RHO** (`pattern_trajectory_only_harness_optimization`) · **Self-Harness** (`concept_self_harness_validates_the_three_loop`) | the harness's control procedure | self-consistency / self-preference (RHO); held-out regression testing (Self-Harness) |
| **action** | the tool registry (Phase 1) | **ToolMaker** (`concept_agents_writing_their_own_tools_with_a_test_gate`, arXiv:2502.11705) | new tools, written from papers-with-code | a 100+-unit-test gate + closed-loop self-correction |
| **state** | Phase 2 experience bank | **CER** (`concept_cer_training_free_experience_replay_works`, arXiv:2506.06698) | a synthesised memory buffer (env dynamics + decision patterns) | retrieve-and-augment; *unguarded against poisoning* (`concept_memory_poisoning_one_write_persists`) |
| **verification** | the two-part gate / `improvement_loop` | **DeepVerifier** (`concept_inference_time_scaling_of_verification`, arXiv:2601.15808) | rubrics, from a failure taxonomy | the verifier itself is meta-evaluated; rubrics + outcome, not transcript |
| *(cross-cutting)* the improvement **procedure** | `loop_proposer` (fixed) | **MetaSkill-Evolve** (`concept_recursive_meta_skill_evolution`, arXiv:2607.05297) | the meta-skill that runs the improvement pipeline | slower-timescale evolution under the same gate |

## Reading

1. **Five of six responsibilities have a published, working self-improving instance**, each with its own
   grounded gate. The one gap — **observation** — is deliberate: the trace substrate should not
   self-modify (`concept_agentic_os`: only the harness layer mutates fast, and observation is closest to
   the runtime). Its *legibility* is instead protected as a Phase 3 acceptance criterion.
2. **Every instance's gate is grounded, not a self-report** — execution feedback (ACE), held-out
   regression (Self-Harness), unit tests (ToolMaker), meta-evaluation (DeepVerifier). This is
   `pattern_grounded_acceptance_only` recurring at every layer, which is what
   `concept_rewriting_cot_alone_defeats_judges_90pct` (run 163) says it must be.
   **`concept_self_improvement_strength_tracks_the_verification_hierarchy` (run 186)** places these on one
   scale — formal verifier > PRM > judge > rubric > meta-eval > intrinsic self-assessment, and
   *demonstrated self-improvement strength tracks it*. Ranking the instances above: ToolMaker's unit-test
   gate is near-formal (executable, deterministic); Self-Harness's held-out regression and ACE's
   execution feedback are outcome-grounded (strong); DeepVerifier's rubrics-from-a-taxonomy sit in the
   rubric band (mid); CER's retrieve-and-augment has *no* gate of its own (weakest — the run-3 point
   below). The design's move is to keep each layer's gate **as high on this hierarchy as its domain
   allows** — a computed check + environment state wherever a domain admits one, a rubric only where it
   doesn't.
3. **The weakest link is `state`** — CER works but inherits the memory-poisoning attack surface, and the
   design's retrieve-heavy stance widens it (`what_would_make_this_wrong.md` §1, nourishing harness 5×
   challenged).
4. **The improvement procedure itself is the frontier** — every published instance above has a *fixed*
   procedure except MetaSkill-Evolve; `loop_proposer` is fixed too. Making it recursive is the plan's
   named open item. **Run 169** surfaced the seam: `loop_proposer.PROPOSER_META` now holds the
   procedure's own knobs (dimensions checked, mode-concentration trigger, proposal cap), and a recursive
   loop would put that dict through `verify_loop_edit` on a slower cadence (e.g. every N object-level
   accepts). Still fixed — but the fixity is now explicit and the knob is load-bearing.

5. **Where the human stays.** `concept_self_improvement_strength_tracks_the_verification_hierarchy` (run
   186) finds the "research direction-setting" bottleneck — deciding *what to improve toward* — sits at
   the top of the verification hierarchy, above any automatable signal. That is this project's structure
   verbatim: the loop picks the *increment*, a human (or the standing goal) sets the *direction*.
   Independent confirmation the human is in the right place — and a warning not to automate that step.
6. **Where the project is ahead.** The same survey names *governance-grade measurement of self-improvement*
   as the field's most underpopulated niche. `loop_metrics` (`plateau_watch`, `idle_run_streak`,
   `trace_legibility`) and `verify_loop_edit`'s regression checks are exactly that.

## What this changes

Nothing structural — it confirms the plan. But it re-frames the HANDOFF's "wire a model" step: the
integration is not "make the self-improving harness work," it is "connect six independently-validated
loops through one trace substrate and one gate discipline." The pieces are each proven; the coupling is
the untested part — exactly what `concept_bottleneck_is_the_model_harness_coupling` predicts. The RSI
survey adds one constraint on that coupling: **each loop's gate must be as high on the verification
hierarchy as its domain allows, or its failure modes (self-confirming, collapse) are predictable.**

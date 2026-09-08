# poly-bot — architecture change suggestions

**Produced:** Agentic Universe run 378 (2026-09-08) · **Against:** poly-bot's refreshed project
graph (38 nodes / 37 edges, `last_updated` 2026-09-08 — the session's own refresh pass,
currently uncommitted in its working tree).

This is the step `docs/project_audit_kit/README.md` describes: once a project graph exists, the
research loop cross-checks it against the folded literature (382 nodes / 1548 edges) and hands
back scoped suggestions. **Each carries the finding it rests on and a falsifiable prediction**,
so it can be refused on the merits rather than argued about.

Ordered by leverage. Nothing here is a mandate — poly-bot's session owns the call.

---

## 1. Make `PROJECT_STATE.md` canonical and demote `CURRENT.md` to a pointer
**Addresses:** `polybot__bug_current_md_stale` — *"CURRENT.md remains internally stale despite
focus correction"*

**The finding:** `concept_a_fix_applied_to_the_instance_leaves_the_class_and_the_display_untouched`
(AU run 367). Two artifacts answering the same question drift independently, and the fix applied
to one does not reach the other. The Agentic Universe loop hit this exactly: it had **two**
increment classifiers over the same text, refreshed one in run 365, and the second was still
drifting two runs later.

`CURRENT.md` and `PROJECT_STATE.md` now both answer *"what is the current focus?"*. The focus
was corrected once; `CURRENT.md` is stale again. That is not a documentation lapse, it is the
predicted behaviour of a second source of truth.

**Suggestion:** one canonical answer. `PROJECT_STATE.md` holds it; `CURRENT.md` becomes a
pointer plus whatever is genuinely *not* in the state doc (live task IDs, today's queue).

**Prediction (falsifiable):** left as parallel narratives, they disagree again within ~20 runs.
If `CURRENT.md` is reduced to a pointer and they still diverge, this diagnosis is wrong.

---

## 2. Give the watchdog digest per-failure-mode categories, not generic ones
**Addresses:** `polybot__watchdog_failure_digest` — *"digest exists but uses generic failure
categories"*

**The finding:** `concept_orchestration_failure_is_diagnosable_by_cascade_radius_and_per_mode_recovery`
(OrchestraBench). Recovery rates are **model-invariant but mode-specific**: tool faults recover
at ~1.0, ambiguous delegation at ~0.30, latent-semantic failures at ~0.0. And critically —
**blind retry hides latent faults.** A generic digest cannot distinguish "retry will fix this"
from "retry will mask this forever", which is precisely the information a digest exists to give.

`concept_mast_multi_agent_failure_taxonomy` supplies ready-made categories (14 modes / 3
groups: system design, inter-agent misalignment, task verification).

**Suggestion:** categorise digest entries by failure mode, and make retry policy a function of
the mode rather than a global attempt count.

**Prediction:** the fraction of watchdog-reported failures that **recur unchanged after retry**
drops. If it doesn't, the failures are dominated by one mode and the taxonomy buys nothing.

---

## 3. Instrument D-state *outcomes*, not just recoveries — you cannot currently tell mitigation from cure
**Addresses:** `polybot__bug_agy_dstate_hang` — *"has mitigation, not a proven cure"*

**The finding:** `concept_the_acceptance_gate_logged_only_its_accepts_so_its_audit_trail_could_not_answer_the_question_it_existed_for`
(AU run 368). The Agentic Universe acceptance gate logged **183 entries, 183 accepts, zero
rejections** — a record indistinguishable from a gate that had degraded to always-accept. *The
one question the log existed to answer was the one it could not.*

The same shape applies here. If the watchdog records D-state **recoveries** but not
**failures-to-recover**, then "mitigation, not a proven cure" is not a cautious framing — it is
literally unknowable from the data, and will stay unknowable however long it runs.

**Suggestion:** log every D-state incident *and its outcome* (recovered / unrecovered /
escalated), with the mitigation that was applied.

**Prediction:** over N incidents, if the mitigation is a cure the unrecovered fraction is 0.
Right now that number does not exist. This costs almost nothing and converts a standing
uncertainty into a measurement.

---

## 4. Express standing authorization as a *scope on an action certificate*, not a bypass of the token
**Addresses:** `polybot__c_live_path_signoff` — *"standing authorization conflicts with
mechanical approval-token gate"*

**The finding:** `concept_runtime_governance_organizes_around_a_portable_action_certificate`
(PCAA) + `concept_governance_needs_a_canonical_action_identity_across_heterogeneous_runtimes`
(CAVA). PCAA's five checkpoints make **approval** a bound checkpoint on a portable certificate;
CAVA binds approval to *execution* through a canonical action object reproducible by an
independent verifier.

The conflict is structural, not procedural: standing authorization and a per-action token are
being treated as **alternatives**, so one must override the other. On a certificate they
compose — standing auth becomes a **scope** the certificate carries, and the token check remains
mandatory *within* that scope.

**Suggestion:** model the live-path approval as a certificate with a scope field rather than a
boolean gate with an exception.

**Prediction:** live-path actions needing ad-hoc human intervention drop toward zero **while the
token check stays mandatory on every action**. If either half fails — interventions persist, or
the token becomes skippable — the model is wrong.

---

## 5. A forecast ledger so "is X validated?" stops being an askable question
**Addresses:** `polybot__bug_flb_lowvol_gate_unvalidated`, `polybot__q_flb_signoff`,
`polybot__q_blocked_on_data_items` — three open items all of the form *"what is the current
validation status of …?"*

**The finding:** `artifact_epistemic_constitution_harness` (AU runs 293/296) — a claim +
forecast ledger with domain-keyed calibration, where `replicated` and `survived_counterexample`
are **required evidence flags**, not prose.

That three of five open questions are validation-status questions is the signal. In a trading
research loop, a strategy condition's validation state should be a **recorded property with a
date and an evidence link** — not something a session has to reconstruct by reading code and
git log.

**Suggestion:** a small ledger keyed by strategy condition: `claim`, `last_validated`,
`evidence_ref`, `forecast`, `outcome`. It is a JSON file and a validator, not a framework.

**Prediction:** the count of open "is X validated?" questions goes to zero and stays there,
because the question is answered by lookup. If sessions keep re-asking, the ledger isn't being
written to and the intervention has failed.

---

## 6. Bounded accounting for disk, with an explicit cap
**Addresses:** `polybot__c_disk_budget` — *"host and VPS storage need separate bounded
accounting"*

**The finding:** `concept_unmanaged_skill_libraries_silently_drift` — unbounded accumulation
degrades the thing accumulating, and the remedy is an **outcome-driven retirement policy plus a
bounded active cap**. AU run 369 applied exactly this to its own experience bank:
`prune(keep_n=200, grace=10)` shipped **with** the wiring rather than as a later addition,
precisely so unbounded growth never got a chance to start.

**Suggestion:** separate host/VPS caps with a prune policy, added *at the same time* as whatever
writes the data — not deferred.

**Prediction:** disk pressure stops appearing as an incident class. If it recurs, the cap is set
above the real growth rate and needs measuring rather than guessing.

---

## What this cross-check did *not* find
No suggestion for the FLB fee-gate conflict — `polybot__bug_flb_route_in_fee_gate` is already
`resolved` in source, and the corresponding constraint node
(`polybot__c_taker_fee_gate_040_060`) now records the exemption explicitly. That is the map
doing its job; nothing to add.

Nothing on `polybot__bug_worker_unsafe_drift` either. "Mitigated by pattern guards and targeted
cancellation" is a **name-based** guard, and AU run 373 (arXiv:2608.03609, equivariance) says
such guards cannot carry a formal guarantee — but AU's own attempt to fix the equivalent problem
(run 374) only worked because graph patches have a **shape** to whitelist. Worker commands may
not have one. Naming a problem I cannot offer a credible remedy for would be worse than leaving
it; flagged here rather than dressed as a suggestion.

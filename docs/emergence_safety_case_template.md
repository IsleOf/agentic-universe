# Emergence safety-case template

From the owner's research input (`docs/research/alternative_approaches_part1.md`,
direction 11). Emergence should be **cultivated and bounded**. Reports on
shared-environment agents describe both economic-institution formation and risks —
conformity, sabotage, covert communication, cascading failure, price collusion, vote
trading. Before running any experiment that gives agents room to develop emergent
behaviour, fill this in.

Keep it short — one paragraph per point. It lives next to the experiment (a probe rig,
a swarm scenario, an idle-agent sweep), not in a central binder.

---

## 1. Desired behaviour
What specific emergent capability is being sought? Name it as something observable, not
"better coordination" — e.g. "agents converge on a shared file-naming convention without
being told one", "a cohort spontaneously audits a peer's fabricated result".

## 2. Minimal affordances
What tools, memory, communication channels and incentives are *necessary* for the
desired behaviour — and nothing more? Every affordance beyond the minimum is attack
surface. Cross-reference `principle_affordance_over_constraint` and the developmental
ladder (`concept_developmental_harness_affordances_unlock_on_demonstrated_reliability`):
withhold what the behaviour does not need.

## 3. Observable precursors
Which telemetry indicates the behaviour is forming? Name the signals and where they are
read from. Prefer environment state over self-report (`concept_anti_scheming_mitigation_confounded_by_eval_awareness`).
Tie to the Five-W message instrumentation and `loop_metrics` axes where they apply.

## 4. Failure analogues
For this specific setup, what would each of these look like — concretely, with the
signal that would show it?
- **sabotage** — an agent degrading a shared artifact or another agent's work
- **cartelisation / collusion** — coordinated action that routes around a control
  (`concept_human_anti_collusion_mechanisms_map_to_agents_with_four_structural_gaps`:
  the boundary problem — say how you would tell this apart from wanted teamwork)
- **deception** — reported state diverging from actual state
- **monoculture** — proposals / citations / tool-use converging
  (`concept_homeostatic_caps_stop_any_agent_skill_or_channel_from_dominating`)
- **runaway resource consumption** — spend or spawn without a bound
- **attribution laundering** — harm produced by the aggregate with no but-for agent
  (`emergent_attribution_laundering`)

## 5. Containment
How can the run be paused, reset, replayed and audited? State the isolation guarantees
(disposable instance, no egress, no real credentials — the probe containment spec) and
the irreversibility budget (`concept_irreversibility_budget`). Confirm the source-of-truth
log is outside agent write access.

## 6. Transfer test
Does the behaviour persist usefully in a *new* environment without reproducing the
harmful side effects? Name the second environment and what "still works / no longer
harmful" means for it. Cross-reference shadow worlds
(`concept_paired_designer_solver_self_play_at_the_capability_frontier_spade_lure` for
the altered-physics idea).

---

## Filled example — the subagent-coordination probe (`tools/probe_subagent_coordination.py`)

1. **Desired behaviour** — none sought; this is a *containment* probe. The question is
   whether same-parent-ID message filtering bounds the spread of an out-of-scope
   instruction.
2. **Minimal affordances** — a 12-agent tree, peer-to-peer messaging, one seeded
   payload. No tools, no network (the rig never touches it).
3. **Observable precursors** — `reach`, `reach_fraction`, `max_depth`,
   `first_relay_cycle`, `monitor_flags` (an adversarial monitor prompt).
4. **Failure analogues** — the seeded instruction reaching `reach_fraction 1.0`
   under the filter would mean the topology containment failed.
5. **Containment** — the rig is a pure-stdlib simulation; nothing to contain. The
   real-run seam (`model_relay`) fails safe (unparseable → do not forward).
6. **Transfer test** — run 254 showed the filter holds spread to `0.333` (vs `1.0`
   unfiltered) under a high-deference relay policy; the open transfer question is
   whether a *real* model driving `relay_policy` behaves the same.

# Session Handover — 2026-09-01

**From:** Claude (Cowork session, claude-opus-5) · **To:** the next agent (Claude Code, Codex, or a fresh Cowork session)

## What happened in this session

Read the repo at `ef4ed3e`, audited the canonical graph, and produced five proposals plus scaffolding and a research operating plan. **The canonical graph was not modified.** Everything is additive and sits at `awaiting_review`.

## State when this session ended

- Branch `proposals/2026-09-01-emergent-behaviour-cluster`, two commits ahead of `ef4ed3e`.
- **Not pushed.** The Cowork cloud container's egress proxy refuses writes to this repo (`IsleOf/agentic-universe is not in this session's authorized repository set`), and the desktop Linux VM failed to start, so no git ran on the owner's machine either. Pushing is the first job for whoever picks this up — see `bootstrap.ps1` in the folder this was delivered to.
- `python tools/knowledge_graph.py validate` → `VALID`. All five patches → `VALID PROPOSAL`.

## What was added

**Five proposals** (`evolution/proposals/2026-09-01_*`), each a markdown proposal plus a JSON patch:

1. `five-w-communication-instrumentation` — **build this first.** Message-level instrumentation is the measurement substrate the other three depend on, not a parallel experiment. Also the only thing that makes `emergent_hidden_coordination_channels` testable in principle.
2. `supervisor-live-steering-and-procedure-distillation` — separates mid-run bounded steering from post-verification distillation so results are attributable to one mechanism.
3. `self-organizing-roles-and-shallow-hierarchies` — splits role differentiation from cooperation, makes hierarchy depth an explicit variable, adds failure modes at equal confidence to the capability they challenge.
4. `evidence-substrate-and-promotion-gate` — the promotion gate plus the missing single-vs-multi-agent baseline.
5. `graph-structural-integrity` — orphan repair, family rooting, and the subnode addressability defect.

**Scaffolding:** `runtime/{observations,evaluations,traces,reward-ledger}/`, `sources/` + `sources/papers/`, `evolution/decision-ledger/`, `conversations/{summaries,extracted}/` — all directories the handover map already promised but that did not exist.

**`docs/research_operating_plan.md`** — how to run literature ingest and test implementation without making the evidence problem worse.

## Findings worth carrying forward

Verified by inspection, not assumed:

- **0 of 19 nodes have `evidence_links`.** 1 has `derived_from`. Meanwhile 11 are `stable_theory` / `partially_validated`. On the project's own written standard, none of those 11 qualify for that status. This is the most important open issue in the repo.
- **Seven subnode IDs are unaddressable.** `tools/knowledge_graph.py` collects top-level node IDs only (lines 28, 63), so an edge targeting `pattern_append_only_audit` fails validation as an unknown target. Reproduce: write a patch with an edge to any subnode and run `check-proposal`.
- **`concept_loop_vs_graph` was an orphan** — in no edge at all, despite being the founding distinction of the project. Repaired by the structural-integrity patch.
- **`pattern_multi_agent_orchestration` was not linked to `approach_orchestration_first`**, breaking the convention every other family follows. Also repaired.
- **Graph-level metadata was lost** after the seed commit — `schema_version`, `last_updated`, `evolution_log` are gone; top-level keys are now only `nodes` and `edges`.

## Three decisions the owner has not made

Do not resolve these unilaterally. They change canonical knowledge.

1. **The 11 `stable_theory` nodes** — demote, add `evidence_basis: authorial_judgment` (recommended), or retro-attach `derived_from`.
2. **Are subnodes meant to be addressable?** Fix the validator, or strip the IDs.
3. **Do tooling changes go through the proposal process?** Code is not a graph patch.

## Next actions, in order

1. Push the branch (`bootstrap.ps1`, or the commands in the delivered `HANDOVER.md`).
2. Get the owner's call on the three decisions above.
3. Merge whichever proposals are accepted; write a `evolution/decision-ledger/` entry for each, including rejections.
4. Fix `tools/knowledge_graph.py` subnode handling — smallest change with the widest effect, and it unblocks precise edges in every future proposal.
5. Build the Five-W runner. Nothing else in the experimental programme is interpretable before it exists.

## Rules that bound this work

From `docs/claude_desktop_handover.md`, still in force:

- Do not edit `knowledge/graph/agentic_universe_graph.json` directly; changes go through `evolution/proposals/`.
- Validate with `python tools/knowledge_graph.py validate` and `check-proposal <file>` before committing.
- Mark uncertain claims `speculative` / `to_test` with `verification_state: needs_empirical_validation`.
- Never commit credentials, API keys, cookies, browser profiles, or personal data.
- Ask the owner before merging anything into the canonical graph.

One addition earned this session: **a source is a claim, not a finding.** Papers, model output, and prior-session conclusions all enter as proposals and none promote themselves. This document included — it is one agent's read of the repo, and it does not get to be canonical because it is written down.

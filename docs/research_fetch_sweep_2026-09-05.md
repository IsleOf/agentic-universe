# research-fetch — first sweep, 2026-09-05

**Graph after:** 107 nodes / 235 edges (+4 nodes, +11 edges)

First use of the `research-fetch` skill (`C:\Agents\skills\research-fetch`), the adjudication-layer fetcher specced in `sources/README.md`. Built and run in one session; this is what the Semantic Scholar citation graph and the AI Alignment Forum turned up on a single pass.

## What the skill covers

| Source | Access | Status |
| --- | --- | --- |
| `openreview` | search keyless; `forum`/`venue` need a free account (`OPENREVIEW_USERNAME`/`PASSWORD` → one-time `login`) | built; `/notes?forum=` is auth-gated by OpenReview now, `/notes/search` is open |
| `s2` (Semantic Scholar) | keyless ~1 req/s; `S2_API_KEY` raises it | built; `citations` returns each citing paper with its `contexts` string |
| `github` | 60/hr keyless, 5000/hr with `GITHUB_TOKEN` | built |
| `forum` (LessWrong / AI Alignment Forum) | keyless GraphQL | built |
| `leaderboard` | GitHub-backed parts only; live boards are JS-rendered, need the browser skill | built, partial by design |

Shared: 15-minute cache under `~/.cache/research-fetch/`, uniform exit codes (0 ok / 1 rate-limited / 2 auth / 3 upstream / 4 bad-input), a `record_finding.py` recorder writing to `reference/agent-findings.md`.

## Finding 1 — harness self-evolution became a subfield in ~3 weeks

`s2 citations arXiv:2604.25850` (Agentic Harness Engineering) returns 15+ distinct systems, most dated 2026-08/09:

- **Self-Harness** — weakness-mining → harness-proposal → regression-test validation loop
- **HarnessEvolve** — learning from reference trajectories
- **HarnessDev** — "Can LLMs Create and Evolve Their Own Agent Harness?"
- **WHALE** — joint harness-weight optimisation
- **EvoUndo** *(reported influential)* — recoverability-constrained self-evolution
- **Verify Smarter, Evolve Further** *(reported influential)* — behaviour-aware verification to cut per-edit cost
- **Retrospective Harness Optimisation (RHO)**, **Hierarchical Self-Improvement**, **Meta-Harness**, **Dalek**
- Benchmarks: **CordisBench** (component-lifecycle reasoning), **HarnessRisk**

Recorded as `concept_harness_evolution_subfield`. The convergence is the evidence: independent groups arrive at the same shape — components as files, falsifiable prediction per edit, trajectory-driven updates, verifier-gated promotion — which is what `approach_self_improving_harness` already asserts. `concept_harness_capability_delta` gains support: this much independent effort on the non-weight layer is a scaled bet that the delta is real.

**Caveat, held:** every one of these is indexed, not opened. Marked as such in every `derived_from` string, per the source-register convention. The next pass should open EvoUndo and Verify Smarter directly — they are the two the graph now leans on.

## Finding 2 — two influential systems name mechanisms this project had asserted

**EvoUndo → `pattern_recoverability_constrained_evolution`.** An edit is permitted only if the state it produces can be returned to a known-good prior at bounded cost. Rollback becomes a *precondition on the proposal*, not a cleanup after a bad promotion — the loop cannot enter a configuration it cannot leave. This is `principle_retraction_capacity` made operational at the harness layer, and it tightens `pattern_verifier_gated_promotion` with an upstream gate: reject un-leaveable configs before spending verification budget.

**"Verify Smarter, Evolve Further" → `concept_verification_is_the_binding_constraint`.** The rate a harness can safely self-improve is set by how cheaply each candidate edit is verified, not by proposer quality. Several systems in the set attack exactly this (coreset selection, staged screening, task sampling). This is the harness-layer instance of `concept_work_substitution_frontier` and of the operating plan's original claim that verification throughput is the bottleneck — now with a subfield independently confirming it.

## Finding 3 — a third evaluator-collapse repair, from the forum

`forum posts --site af` surfaced **"Debate training reduces reward hacking in RLAIF"** and **"Training a Misaligned Reward Seeker"** (evhub et al.). Recorded `pattern_debate_against_reward_hacking` (speculative — forum post, not a read paper): scoring against a debate between models exposes the modes a single judge collapses to, because a second party is paid to attack them. Third repair path alongside heterogeneous verifiers and pre-committed rubrics.

Also: the **METR & Redwood independent investigation of the OpenAI / Hugging Face hacking incident** now has a full public report (AF post `nB8KKapnWGBXtKKiM`). Attached to `emergent_hidden_coordination_channels`, which already cited the incident from memory.

## What the skill is for, restated

Discovery (arXiv, HN, X, Reddit, YouTube) finds work. This finds the work *around* a piece of work: who cites it and for what, what reviewers objected to, what shipped, what refutes it. The three source-register corrections on file were all adjudication failures — this is the layer that catches them before they enter the graph, not after.

## Next

1. Open EvoUndo and "Verify Smarter" directly — verify the two influential claims the graph now rests on.
2. `openreview` needs the one-time account setup to unlock review threads — the highest-value part is still gated.
3. `s2 citations` on `concept_benchmark_headline_substitution`'s own case (openJiuwen, `arXiv:2608.27969`) once it accumulates citations — watch whether later work repeats or corrects the headline framing.

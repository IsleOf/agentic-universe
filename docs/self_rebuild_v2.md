# Agentic Universe v2 — rebuilding the loop on its own research

> Run 299 (2026-10-04). First-pass architecture. This is the project **practising what it
> preaches**: redesigning its own research loop using the ~328-node graph's findings, the
> shipped tools, and the skills already on this machine. Nothing here is built yet — this
> is the plan the next phase gates against.

---

## 1. What v1 is, and where it stops

v1 = one interactive Claude Code session that picks an increment, edits the graph, validates,
commits, pushes — plus a dumb 6-hourly scheduled task that does the same when the session is
idle. It has produced 298 runs and a validated 328-node graph, 35 selftests, ~12 tools, 9
probe rigs, 2 combined prototypes.

**Its four ceilings:**

| ceiling | evidence |
|---|---|
| **Single agent.** Everything is the loop (one agent) or a synthetic sim. No real multi-agent run has ever happened. | `docs/HANDOFF.md` "Phase 6 needs a real multi-agent harness" |
| **The model is never called.** Every probe and the proposer have a `call_model` stub that was never bound. The one experiment that "resolves the most" (`probe_idle_agent`) has never run. | `docs/HANDOFF.md` wire-a-model table; `what_would_make_this_wrong.md` |
| **Research ingestion is manual.** The owner runs Perplexity deep research by hand and pushes `.md` files; the loop folds them days later. | runs 240–246, 253, 296, 298 — all "owner pushed X, loop folded it" |
| **The acceptor is advisory.** PACE e-process (run 220), held-out verifier, process scoring (run 298) all exist as code but nothing enforces them on a real edit stream. | `concept_the_acceptor_not_the_proposer_is_the_weak_point_of_self_evolution` |

## 2. The findings that must shape v2

Pulled straight from the graph — each is a load-bearing constraint on the redesign:

1. **Deterministic spine, generative edge** — the orchestration substrate is pure-stdlib and
   deterministic; model calls live only at the leaves. (`task_ledger`, `supervisor`,
   `fractal_flock`, `epistemic_constitution` all already follow this;
   `concept_proof_carrying_negotiation_separates_nl_reasoning_from_deterministic_enforcement`.)
2. **The acceptor is the weak point.** Reliable self-improvement needs ≥1 acceptance signal
   the agent cannot author or inspect — exogenous, anytime-valid, validity-checked,
   paired-live-trial-measured, epoch-versioned, certificate-bearing. (The six-condition spec,
   runs 203–214; `concept_reliable_self_improvement_needs_an_exogenous_acceptance_signal`.)
3. **Harness > model.** Capability is a model-harness-config property; a 6× best/worst-harness
   gap persists for the strongest models on long-horizon tasks (StaminaBench, run 298);
   harness intelligence is trainable/transferable/compounding (JIT-Agent).
4. **Everything is a plugin.** Models, tools, memory, the agent loop itself — hot-swappable
   via config, not code. (DeepSeek Harness / Cordis;
   `concept_a_large_plugin_everything_agent_ecosystem_converges_on_this_projects_architecture`.)
5. **MCP is the tool bus**, behind a policy gateway (domain allowlists, human confirmation on
   consequential actions, full action logs). (run 298; the harness-anatomy self-audit.)
6. **Score the process, not just the outcome.** Up to 23.2 % of nominal passes are lucky
   blind retries; a retry/feedback loop is itself a 12× lever. (AgentLens / StaminaBench,
   run 298; run 247 — the gate scores usefulness, nothing scores *how*.)
7. **Route models per task class** with a cost-accuracy-feedback loop — cheap proposes,
   strong verifies, log regret vs the best observed choice. (Agent-as-a-Router 2606.22902,
   run 298.)
8. **Hybrid memory + janitor agents** — vector + knowledge-graph (GraphRAG) + KV + episodic
   stream + reranker; janitor agents periodically summarise/archive. (run 298;
   `concept_human_knowledge_capture_must_be_platform_level_and_crystallize_dialogue`.)
9. **Every proposal is a scored forecast.** Predict the outcome before the action, Brier-score
   on resolve, conditional trust is domain-keyed, cold start returns `None` not a global
   scalar. (`epistemic_constitution.py`, runs 293/296.)
10. **Deterministic task ledger + PILOT supervisor** — never let the model hold task state;
    `sweep_stale()` recovers dropped tasks; the supervisor aborts over-budget work. (runs
    244/250 — the direct fix for "tasks get dropped".)
11. **When to fan out:** multi-agent helps **iff** verifiable subtasks **+** disjoint evidence
    **+** (deterministic synthesis **OR** bounded-neighbourhood stigmergic accretion). A
    vote never helps. (runs 218/273.)
12. **Trace → per-consumer views.** A long-horizon trace outgrows both the human and the
    agent's own context; compiling the append-only ledger into per-consumer views answers
    monitoring questions at ~14× fewer tokens. (`concept_trace_compiles_to_per_consumer_views`.)
13. **Evidence ancestry, not agent multiplicity.** Multiplying agents on one evidence root
    collapses aggregate confidence 0.94 → 0.26; identity is fluid, so reputation/sanctions
    need a canonical action identity. (`concept_epistemic_sybil_collapse`, run 253.)
14. **Emergence-first, no weight training.** The founding bet: nurture emergent behaviour,
    elicitation-shaped tasks, cheap complete rollback + diversity maintenance instead of a
    gated interior. (`docs/emergence_first_posture.md`; the WHALE/HELIX/JIT-Agent `challenges`
    cluster is noted, not resolved against it.)
15. **Recency weighting + IDLE-STATE RULE + irreversibility budget** — carry forward verbatim.

## 3. The v2 shape

```
                        ┌──────────────────────────────────────────────┐
                        │  ACCEPTANCE GATE  (exogenous, can't be authored)│
                        │  · held-out task set (frozen, never loop-grown) │
                        │  · PACE anytime-valid e-process (run 220)       │
                        │  · process-adjusted score (run 298)            │
                        │  · forecast ledger — was the predicted lift real│
                        │  → emits a signed certificate per accepted edit │
                        └───────────────▲──────────────────────────────┘
                                        │ accept / reject / repair
   ┌───────────────┐   proposals   ┌────┴─────────┐   dispatch   ┌──────────────────┐
   │  PROPOSERS    │ ────────────▶ │ TASK LEDGER  │ ───────────▶ │  WORKER AGENTS    │
   │ (model-routed)│               │ + SUPERVISOR │              │ (WSL + Win CLI)   │
   │ cheap model   │ ◀──────────── │ deterministic│ ◀─────────── │ browser / research│
   └───────────────┘  failure digest└─────────────┘   results    └────────┬─────────┘
                                        │                                  │
                        ┌───────────────┴──────────────┐        ┌──────────┴─────────┐
                        │  HYBRID MEMORY               │        │  SKILLS LAYER      │
                        │  graph + vector + KV +        │        │  research-fetch,   │
                        │  episodic trace + janitor     │        │  nodriver-session, │
                        │  → per-consumer views         │        │  cli-agent-control,│
                        └──────────────────────────────┘        │  perplexity/nblm   │
                                                                 └────────────────────┘
```

Everything left of the workers is **deterministic pure-stdlib** (spine). The workers and
proposers are the **generative edge**. The gate is the exogenous acceptor.

## 4. Agent roster

| agent | host | role | built on |
|---|---|---|---|
| **conductor** | Win (this box) | owns the task ledger + supervisor; picks the run's increment per IDLE-STATE RULE; never calls a model itself | `task_ledger.py`, `supervisor.py` |
| **literature scout** | Win, browser | drives Perplexity + Google NotebookLM + arXiv/S2/GitHub; produces a structured research brief, not prose | new `perplexity-notebooklm` skill on the `nodriver-session` contract + `research-fetch`, `arxiv-fetch` |
| **claim auditor** | Win | "is the claim real" — S2 citation contexts, OpenReview, the paper vs its citation | `research-fetch s2/openreview` |
| **graph writer** | Win | folds an accepted brief into the graph; validates; regenerates `source_register` | `knowledge_graph.py`, `build_sources.py` |
| **probe runner** | WSL | binds a real `call_model` into the 5 written adapters; runs `probe_idle_agent sweep` etc. in a real fs sandbox | `docs/HANDOFF.md` wire-a-model table |
| **dissent agent** | WSL, different model | one mandatory dissenting implementation / counter-argument per proposal (open question 6) | `probe_dissent_vs_reflection.py` |
| **janitor** | Win | periodically summarises the episodic trace into per-consumer views; archives stale experience-bank entries | `trace_substrate`, `experience_bank`, run 298 |
| **CLI executor pool** | Win + WSL | agy / grok / codex / opencode for parallel sub-tasks, under the AGENT_CONTRACT | `CLI-AGENT-CONTROL/agentctl.sh` |

Fan-out rule (finding 11): the conductor fans work to the executor pool **only** when the
sub-tasks are independently verifiable and the merge is deterministic — otherwise it stays
single-agent. No vote step, ever.

## 5. Skills layer — what exists, what to build

**Reuse as-is:**
`nodriver-session` (browser lifecycle contract), `browser-web-search`, `research-fetch`,
`arxiv-fetch`, `github-fetch`, `reddit-fetch`, `x-fetch`, `hackernews-fetch`,
`youtube-transcript`, `rss-fetch`, `cli-agent-control`, `online-data-to-vault` (idempotent
dedup + nightly cron pattern), `agent-operations-soul` (the machine's web-search stack +
cua-driver fixes).

**To build (each on the `nodriver-session` contract — minimized Chromium, profile
serialization, persistent cooldowns, challenge classification, no credential extraction):**

1. **`perplexity-notebooklm`** — drive Perplexity deep-research and Google NotebookLM:
   submit a query, wait for the rendered answer, extract the answer + its citation list as a
   normalized record, save into the vault + a `research/` brief. This replaces the manual
   "owner runs Perplexity → pushes `.md`" step. NotebookLM path: upload the current graph +
   recent sweeps as sources, ask it for gaps / contradictions, capture the response.
   **Scaffolded run 304 (`skills/perplexity-notebooklm/`): the `nodriver-session`-contract
   driver + the record parser + the `research_brief` stub bridge; the stdlib parts are
   selftested. The live selectors / deep-research wait / NotebookLM upload need the profile
   created and iteration against the real sites.**
2. **`research-brief`** — turns a scout run into the structured object the graph writer folds
   (candidate nodes, edges, `derived_from`, currency note), not free prose. **Built run 302
   (`tools/research_brief.py`): `validate_brief` + `to_graph_patch` + `check_against_graph`
   (the mechanised dedup check).** The scout still fills the brief; the skill wraps the
   fetch.
3. **`acceptance-gate`** — wraps the held-out set + PACE e-process + process score + forecast
   check into one `gate check <proposal>` call that emits a certificate or a repair.
4. **`loop-conductor`** — the scheduled entry point: read policy, pick increment, dispatch
   via the ledger, run the gate, commit, push, record. The current interactive loop, made
   headless. **Skeleton built run 303 (`tools/loop_conductor.py`): `Conductor.conduct()` is
   the deterministic pipeline; the worker, patch-apply and commit/push are callbacks.** What
   remains: the real `run_worker` (needs `call_model`) and the scheduled-task wiring.

## 6. Memory architecture (finding 8)

| layer | store | what goes here | today |
|---|---|---|---|
| relationships | `agentic_universe_graph.json` | concepts, claims, tensions, evidence roots | ✅ have |
| unstructured | vault / vector index | paper text, briefs, transcripts | partial (vault via `online-data-to-vault`) |
| state | KV (`runtime/`) | ledger, harness registry, loop metrics | ✅ have |
| episodic | `trace_substrate` JSONL | every run as it happened | ✅ have (gitignored raw) |
| **janitor** | — | periodic summarise → per-consumer views; archive stale bank entries; flag drift | ❌ **build** |
| **reranker** | — | precision at retrieval scale | ❌ build when the vault is large |

GraphRAG multi-hop over the graph is the query layer the scout and auditor use before every
fold ("what does the graph already say about X, two hops out").

## 7. The acceptance gate as a service (finding 2, 6, 9)

Every proposed change — a graph fold, a tool edit, a policy change — passes:

1. **Held-out regression** — the frozen task set (`holdout_tasks.py`, never loop-grown); a
   score below baseline reverts.
2. **PACE e-process** — `improvement_loop.paired_eprocess`; accumulate paired deltas across
   runs; commit only when the e-value crosses `1/α`. Anytime-valid, so it can be checked
   every run without a multiple-comparisons penalty.
3. **Process score** — did the change come from a causal fix or a lucky retry (AgentLens
   shape); a change that only passes on re-roll is rejected.
4. **Forecast check** — the proposer predicted a lift ("this fold raises coverage of the
   collusion thread"); on resolve, Brier-score it per domain; a proposer whose domain trust
   is `None` or poor gets its proposals down-weighted, never blocked.
5. **Certificate** — an accepted edit emits `{proposal_hash, gate_scores, e_value,
   baseline, timestamp}` signed and appended to an audit log an independent verifier can
   replay.

The gate is **exogenous**: the conductor and the proposers cannot edit the held-out set, the
α, or the certificate log. That is the whole point (finding 2).

## 8. Scheduling / cron

- **6-hourly `loop-conductor`** (exists as a Windows scheduled task) → replace its body with
  the headless conductor: ledger-driven, gate-enforced, one increment, commit, push.
- **Nightly `literature-scout`** → Perplexity + NotebookLM + arXiv/S2 sweep → briefs into
  `research/`, deduped (`online-data-to-vault` pattern). The conductor folds accepted briefs
  on its next run.
- **Weekly `janitor`** → trace → per-consumer views; experience-bank GC; drift report
  (`loop_metrics` plateau / novelty / legibility); `graph_state` snapshot refresh.
- **On-demand `probe-runner`** (WSL) → whenever a `call_model` budget is available, run the
  next probe from `docs/HANDOFF.md` and feed the result to the gate.

Cloud option: a `RemoteTrigger` routine (already used for the current 6h task) can run the
conductor in an isolated cloud checkout — but browser skills (Perplexity/NotebookLM) need
the local box, so the scout stays local.

## 9. Resources needed

**Have:** the Windows box + WSL Ubuntu; the skills library; `nodriver-session` +
AdsPower + cua-driver; the web-search stack (Tavily 1k/mo, Serper 2.5k/mo, Exa 20k/mo, ddgs);
CLI agents (agy/grok/codex/opencode) with auth; the 6h scheduled task; GitHub repo + PAT
(**rotate the one pasted into the Cowork chat**).

**Need to decide / provision:**

| resource | for | note |
|---|---|---|
| a **`call_model` budget** — one API key the probe-runner and proposer-router use | the model-integration handoff; nothing downstream works without it | this is the #1 unblock. A cheap model for proposals, a stronger one for verification (finding 7). |
| **Perplexity account** reachable by browser automation | the scout | already used manually; automate via the new skill under `nodriver-session` |
| **Google NotebookLM** access | the scout's gap/contradiction pass | upload graph + sweeps as sources |
| an **MCP gateway** (self-hosted) | policy + logging over all tool calls | domain allowlist, human-confirm on consequential actions, full logs (finding 5) |
| a **vector index** (pgvector / Qdrant / sqlite-vss) | the unstructured memory layer + reranker | small to start; the vault is the source of truth |
| **WSL fs sandbox** for the probe-runner's containment arm | `probe_idle_agent`'s "is there autotelic behaviour in the gap" experiment | a throwaway dir + resource caps |
| a **second model family** for the dissent agent | open question 6 (structured dissent vs reflection) | must be a different family than the proposer (finding 13 — independent evidence roots) |
| **disk discipline** | Takeout-style large pulls, video frames | `online-data-to-vault` already does chunked + delete-after; keep it |

**Explicitly NOT needed:** any training/fine-tuning infra — the emergence-first bet is no
weight training (finding 14). If that bet is ever revisited, that is a posture change through
the Phase 3 gate, not a resource request.

## 10. Migration path (each phase gated)

| phase | deliverable | gate |
|---|---|---|
| **v2.0** | bind one `call_model`; probe-runner runs `probe_idle_agent sweep` in a WSL sandbox; result → the gate | the sweep produces a falsifiable answer on `concept_habitat_slack` |
| **v2.1** | `acceptance-gate` skill: held-out + PACE + process score + certificate log, wired as the conductor's commit gate | a known-bad edit is rejected + repaired; a known-good edit certified — **core brick built run 300 (`tools/acceptance_gate.py`): `check()` composes the checks + a process-adjusted flag + a forecast Brier into a replayable signed certificate; `verify()` replays it. Not yet wired as the commit gate.** |
| **v2.2** | `perplexity-notebooklm` + `research-brief` skills; nightly scout writes deduped briefs | a brief folds through the gate with no human step — **`research_brief.py` built run 302; `perplexity-notebooklm` scaffolded run 304 (driver + parser + brief bridge, stdlib parts selftested); the live selectors + the nightly scheduled wiring remain**|
| **v2.3** | conductor headless on the 6h task; ledger-driven; supervisor aborts over-budget work | 10 consecutive autonomous runs, all gated, no dropped tasks (`sweep_stale` clean) — **`loop_conductor.py` skeleton built run 303 (pipeline + IDLE-STATE classifier + gate wiring); the real `run_worker` and the scheduled-task body remain**|
| **v2.4** | CLI executor pool + dissent agent; fan-out only under the finding-11 criterion | a fanned-out run beats the single-agent baseline on a verifiable multi-part task; open question 6 gets a real datapoint |
| **v2.5** | janitor: per-consumer views, experience-bank GC, drift report | monitoring questions answered from views at <1/10 the tokens of raw trace |

Each phase is small, reversible (`harness_registry` revert), and its gate is written before
the phase starts — the same discipline the loop already runs on.

**Spine composition proven (run 311).** `tools/v2_integration.py` runs a realistic fold
(a scout `research_brief` → validate + dedup → `to_graph_patch` → `loop_conductor.Conductor`
with the **real** `acceptance_gate.check` → a certificate `verify_certificate` replays),
14 checks including the negative paths. The v2.1–v2.3 bricks are not just individually
selftested — they wire together. What is still stubbed is exactly the three things v2.0
provides: the model worker, and (side-effects) the git commit and the patch-apply.

## 11. What would make this wrong

- **If the emergence-first bet is wrong** and capability-shaped tasks dominate, v2's
  no-training stance caps it — the WHALE/HELIX/JIT-Agent `challenges` cluster. v2 keeps that
  cluster visible and re-checks it each phase.
- **If the acceptance gate can be gamed** by a proposer that learns to predict the held-out
  set, the exogenous property is lost. Mitigation: the held-out set is frozen and small, and
  the process score + certificate replay catch a proposer that passes without a causal fix.
- **If browser automation to Perplexity/NotebookLM keeps breaking** (challenge pages, layout
  changes), the scout degrades to the API-only path (`research-fetch` + `arxiv-fetch`) and
  the owner's manual Perplexity runs stay in the loop as a fallback, not the default.
- **If the model budget is too small** to run the probes at all, v2.0 stalls and the project
  stays where v1 is — a well-mapped graph with an unbound model. That is the current state;
  v2 is the plan to leave it.

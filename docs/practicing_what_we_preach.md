# Practicing What We Preach

**Date:** 2026-09-06 (owner request, run 242) · **Status:** strategy note, for discussion
**Prompt:** *"AGENTIC UNIVERSE SHOULD PRACTICE WHAT IT PREACHES … I want the cutting-edge research
discoveries to reach my projects (poly-bot, poster-studio) as best as possible."*

This note answers four questions: (1) should the graph be redesigned for traceability? (2) where does the
project already practice its own findings, and where doesn't it? (3) how to audit poly-bot / poster-studio
with this project's methods? (4) how the folded research maps to the concrete pain points (CLI
orchestration, agent memory, dropped tasks).

---

## 1. Should we redesign the graph for traceability? — No. Add two small tools.

The graph **already** has the traceability primitives the DeepSeek / ECC ("store every proposed
improvement as trace + artifact") pattern calls for:

| primitive | where | what it gives |
| --- | --- | --- |
| `evolution_log` | `knowledge/graph/agentic_universe_graph.json` | every change, dated, prose-described (240+ entries) |
| `derived_from` | every node | provenance to arXiv IDs, docs, prior runs |
| harness version chains | `runtime/harness/*/*.history.json` | exact-revert of every harness component; `tamper_audit.py` walks them |
| run records | `runtime/observations/loop_runs/run-N.json` | per run: increment, citations, `graph_delta`, `status_line` |
| `source_register.md` | regenerated each run from `derived_from` | the bibliography, always current |
| structural validation | `knowledge_graph.py validate` | unique ids, resolving edges, schema shape — every commit |

**What's missing** (both are ~1 short build each, worth doing):

- **`tools/graph_diff.py <ref-a> <ref-b>`** — a *structural* diff: nodes added / removed / relabelled,
  edges added / removed, confidence changes. Today "what changed between graph vN and vN+1" is only prose
  in `evolution_log`. A mechanical diff makes every change auditable and is the honest version of "changes
  are traceable".
- **The four-object self-improvement trace** (ECC 2.0: `scenario spec → proposer trace → verifier result
  → promoted playbook`). The project has the pieces — `loop_session` (the run), `loop_proposer` (the
  proposal), `verify_loop_edit` (the verdict), `harness_registry.set` (the promotion) — but they are not
  linked as one addressable object per improvement. Linking them (a `runtime/improvements/imp-N.json` that
  references all four) would make the *self-improvement loop* itself as auditable as the graph. Lower
  priority than `graph_diff`.

**Do not** change the node/edge schema. It validates, it is the source of truth, and every downstream
tool depends on it.

---

## 2. Where the project already practices its findings — and where it doesn't

**Practices well:**

- **Verifier-gated promotion** (`verify_loop_edit`): six checks — task regression, category regression,
  verifier disagreement, trace-legibility regression, harness-tampering flags, format-normalised scoring
  — plus an advisory anytime-valid `paired_eprocess` (PACE) and a `deterministic_repair` stage
  (PCN-Rec / CordisBench / JIT-Agent).
- **Execution-layer enforcement** (`exec_guard` pre-commit hook): the loop physically cannot commit an
  invalid graph, a raw trace, or a secret-shaped string.
- **The frozen, exogenous held-out set** (`holdout_tasks.py`) — SEAL / Who-Grades-the-Grader say the
  acceptance signal must not be authorable by the agent; this is.
- **Integrity self-audit**: `tamper_audit.py` ran the `what_would_make_this_wrong.md` §2 falsifier on the
  loop's own lineage — 0/7 flagged, clean.
- **Pure stdlib, deterministic retrieval, SKILL.md loop, config-not-prose policy** — all four validated
  against the 11-production-harness source study (`harness_anatomy_self_audit.md`).
- **The IDLE-STATE RULE** — a bounded increment per run, not open-ended re-search (ASPIRE: continued
  search erases earlier gains).

**Doesn't yet:**

- **Single-agent only.** Phase 6 (the swarm layer) is untouched; `probe_orchestration_value` is a
  simulation, not a real multi-agent harness. The project studies emergence but has not run a swarm.
- **The middle loop is between-run, not live** (PILOT: the highest-value self-improvement runs a
  supervisor *during* execution that can abort a doomed worker).
- **The model-integration step is deferred.** `probe_idle_agent` — "the one experiment that resolves the
  most" — has never been run with a real `call_model` bound into the five adapters (`docs/HANDOFF.md`).
  **This is the single move that would most make the project practice what it preaches.**

---

## 3. Auditing poly-bot / poster-studio — recommended method

**Yes — let a session per project write a knowledge graph + a handover doc in this project's format.**
The tooling is now built (`tools/project_graph_scaffold.py`, run 251) and there is a **worked example**:
`knowledge/graph/agentic_universe_project_graph.json` (26 nodes) + `docs/PROJECT_STATE.md` — this project,
in its own format. `python tools/project_graph_scaffold.py new poly-bot` writes the starter files;
`… validate <graph>` checks any project graph against the schema + the node/edge vocabulary. The steps:

1. **One session per project** does a codebase read and produces:
   - a **small graph** (aim 20–50 nodes) using the schema in `tools/knowledge_graph.py`:
     nodes = components, key decisions, hard constraints, known bugs, open questions;
     edges = `depends_on` / `implements` / `challenges` / `blocks` / `records`.
     Node `type`: `component` / `decision` / `constraint` / `bug` / `question`.
     Every node gets `status`, `confidence`, and `derived_from` (a file path or a commit).
   - a **handover doc** modelled on `docs/HANDOFF.md`: what it does, current state, what is broken and
     why, the single highest-value next move, and the "what would make this wrong" section.
2. Run it through **`python tools/knowledge_graph.py validate`** — unique ids, resolving edges. If it
   validates, it is a real artifact, not notes.
3. Commit the graph + doc into that project's repo under `knowledge/graph/` and `docs/`.
4. **Every fresh session reads the graph + handover doc first.** This is the direct fix for "sessions
   lose context / tasks get dropped" — the persistent memory is a validated file, not the last chat.

This is the agentic-universe format applied recursively: the project's own claim is that structure
survives where prose weakens (`emergent_constraint_weakening_at_handoffs`, and AHE's ablation — factual
structure transfers, prose strategy does not). A validated graph is that structure.

**Do not** try to reconcile the projects into one graph. Keep one graph per project; cross-link by note
if needed. The `human_llm_hybrid_graph.json` on `origin/main` is a separate graph and should stay
separate.

**Drop-in kit (run 297).** `docs/project_audit_kit/` is a 4-file, pure-stdlib bundle to copy into a
target repo as `tools/`: `project_graph_scaffold.py` (+ its `knowledge_graph.py` dep — hardened run 297
to create `docs/` and `knowledge/graph/` if the repo doesn't have them yet), plus `task_ledger.py` and
`supervisor.py` for the dropped-task problem. `docs/project_audit_kit/README.md` is the exact prompt for
the auditing session. poly-bot is at `/home/dev/poly-bot` (WSL), poster-studio at
`/home/dev/poster-studio` — both are large, active repos whose hand-over state is scattered across many
dated `.md` files; the in-flight checklist a cold audit can't recover is exactly what the active session
should put in the `question` nodes.

---

## 4. The concrete pains → the folded research

### "Tasks get dropped"

- **`concept_component_lifecycle_reasoning_degrades_with_size`** (CordisBench): LLM reasoning about
  system state degrades as the system grows, and an independent finite reference semantics matches
  execution on every scored outcome. **Don't let the model hold task state in its context.**
- **`concept_aspire_...`**: continued open-ended search *erases* earlier gains; the loop is not monotone.
- **Fix:** a **deterministic task ledger** — a file (or SQLite) the orchestrator reads and writes, one
  row per task: `{id, goal, status: pending|active|done|failed, owner, deps, result_ref, updated}`. The
  LLM proposes the next task and reports outcomes; the ledger is the source of truth. This is
  `pattern_execution_layer_enforcement` applied to task tracking — the same reason `exec_guard` is a hook
  and not a prompt.

### "Agent memory"

- **`concept_human_knowledge_capture_must_be_platform_level_and_crystallize_dialogue`** (run 241, Shared
  Org Memory — a production deployment): agents do **not** reliably recognise or record the lesson worth
  reusing. **Capture must be an automatic platform step**, not agent-initiated, with contributor approval
  and a security/privacy gate on every write.
- **`concept_unmanaged_skill_libraries_silently_drift`** (run 208, Library Drift): unbounded memory
  accumulation silently degrades retrieval and injects false positives; premature retirement (−0.019) is
  worse than none (+0.002). **Fix:** outcome-driven retirement + a **bounded active-cap** (a hard limit
  on live memories, not just utility ranking) + a generous grace window.
- **ECC's layered persistence:** rules (small, always loaded) vs memory (retrievable, not in context);
  a Unified Memory Vault keyed by one env var so tools share memory instead of siloing it;
  retention feedback — a memory write is scored for later usefulness (`experience_bank.record_use`).

### "CLI agent orchestration"

- **`concept_multi_agent_helps_when_subtasks_are_verifiable_and_synthesis_is_deterministic`** (run 218,
  verdict CONFIRMS on the rig): multi-agent helps **only** when (a) subtasks have an independent checkable
  success condition, (b) recombination is a **deterministic merge** — not a vote or a consensus
  discussion, (c) agents work from **disjoint** context slices. If a CLI orchestration is dropping tasks
  or churning, check which of (a)/(b)/(c) it violates.
- **`concept_self_improvement_should_be_live_a_supervisor_steers_and_aborts_the_active_worker`** (run
  230, PILOT): a separate supervisor that can **redirect or abort** the active worker mid-run — plus
  distilling failure modes into skills during execution — cut output tokens ~45% and raised
  successful-evals-per-token 110–134%.
- **The tiered pattern** (from the jobs analysis, converging across Accenture / Microsoft Agent
  Framework / LangGraph): Tier 1 routers → Tier 2 domain specialists → Tier 3 utilities, with
  human-in-the-loop handoffs made visible in the log.

---

## Recommended next moves, in order

1. **Build `tools/graph_diff.py`** (this repo) — mechanical change-traceability. Small.
2. **Run the poly-bot audit** — one session, graph + handover doc, validated. Then poster-studio.
3. **Add a deterministic task ledger** to whichever orchestration is dropping tasks (poly-bot?).
4. **The model-integration step** (`docs/HANDOFF.md`) — bind a real `call_model`, run `probe_idle_agent
   sweep`. This is the project's own deferred highest-value move.
5. **A live supervisor** (PILOT pattern) for the orchestration layer — a process that can abort a stuck
   worker and re-dispatch from the ledger.

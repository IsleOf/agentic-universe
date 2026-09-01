# Proposal: Graph structural integrity — subnode addressability, orphan repair, lost metadata

> **ACCEPTED and merged into the canonical graph, 2026-09-01**, under the
> emergence-first posture (`docs/emergence_first_posture.md`). Decision record:
> `evolution/decision-ledger/2026-09-01_emergence-first-rebaseline.md`.

- **Date:** 2026-09-01
- **Author / agent:** Claude (Cowork session, claude-opus-5)
- **Status:** accepted
- **Affected approach family:** all (tooling and schema)
- **Affected graph node IDs:** `concept_loop_vs_graph`, `pattern_multi_agent_orchestration`, `concept_config_driven_control_plane` (and its 7 subnodes)

## Problem or opportunity

Four concrete defects found by inspecting the canonical graph and `tools/knowledge_graph.py` at commit `ef4ed3e`. These are mechanical, not conceptual, and are cheap to fix — but the first one will silently block the other four proposals in this batch if left alone.

### 1. Subnodes are unaddressable and invisible to validation

`concept_config_driven_control_plane` carries seven subnodes with real IDs: `pattern_frozen_engine`, `pattern_capability_routing`, `pattern_human_priority_lane`, `pattern_append_only_audit`, `safeguard_state_revalidation`, `principle_recommendation_vs_execution`, `workflow_detect_propose_approve_execute_record_learn`.

`validate_graph()` collects node IDs from top-level nodes only (`tools/knowledge_graph.py` line 28). `check_patch()` does the same (line 63). Consequences:

- Any edge targeting a subnode fails validation as "target does not exist", even though the ID is present in the graph. The Five-W proposal wanted to link directly to `pattern_append_only_audit` and had to route to the parent concept instead — a real loss of precision caused purely by tooling.
- A subnode ID could duplicate a top-level ID and the uniqueness check would not catch it.
- The schema defines a `relations` array on nodes (line 27) that nothing reads and nothing validates. Relations written there are inert.

Seven of the graph's most concrete governance patterns are therefore unreferenceable. This is the single highest-leverage fix in the repo right now.

### 2. `concept_loop_vs_graph` is an orphan

It appears in no edge, in either direction — the only fully disconnected node in the graph. Given its description ("transient loops execute bounded work; persistent graphs model durable concepts"), it is arguably the founding distinction of the whole project, and it is attached to nothing.

### 3. `pattern_multi_agent_orchestration` is not linked to its own approach family

Every other family has an `instantiates` or `core_of` edge to its `approach_*` node. This pattern's only edge is inbound, from `emergent_natural_teaming`. It is not connected to `approach_orchestration_first`. Three of the four other proposals in this batch attach to it, so it is about to become a hub node while still being structurally unrooted.

### 4. Graph-level metadata was dropped

The seed graph committed in `c9986bc` carried `schema_version`, `last_updated`, and an `evolution_log` array. The current canonical file has only `nodes` and `edges`. The changelog and decision ledger were presumably meant to absorb that role, but `evolution/decision-ledger/` does not exist, so provenance metadata is currently recorded nowhere machine-readable.

Related: `docs/claude_desktop_handover.md` maps six directories that do not exist — `conversations/summaries/`, `conversations/extracted/`, `evolution/decision-ledger/`, `runtime/observations/`, `runtime/evaluations/`, `runtime/traces/`. Every verification plan in this batch names `runtime/` paths as evidence locations, and `process_decision_ledger` is marked `stable_theory` while having no implementation.

## Proposed change

**Patch (`2026-09-01_graph-structural-integrity.json`)** — edges only, no new nodes:

- `edge_loop_vs_graph_grounds_orchestration` — attaches the orphan to `approach_orchestration_first`.
- `edge_orchestration_patterns_instantiate_family` — roots the pattern in its family, matching the convention used by every other family.

**Tooling changes (not expressible as a graph patch; require edits to `tools/knowledge_graph.py`):**

1. Collect subnode IDs into the known-ID set in both `validate_graph()` and `check_patch()`, so edges may target subnodes.
2. Check subnode IDs for collisions against top-level IDs and each other.
3. Validate the `relations` array against the same ID set, or remove `relations` from the schema if it is not intended for use. An unread field invites writing into a void.
4. Add a `summary` line for orphan nodes — nodes appearing in no edge — so future orphans surface without manual inspection.

**Repository changes:**

5. Create the six mapped-but-missing directories with `.gitkeep` and a one-line README each, or amend the handover map to describe only what exists. Either is fine; the current state, where the map describes directories that are not there, is the problem.
6. Decide whether graph-level metadata (`schema_version`, `last_updated`) returns to the graph file. Recommendation: yes for those two, no for `evolution_log` — a log inside the canonical artifact competes with the changelog and the git history for the same job.

## Rationale and provenance

Direct inspection of `knowledge/graph/agentic_universe_graph.json`, `knowledge/graph/agentic_universe_schema.json`, and `tools/knowledge_graph.py` at commit `ef4ed3e`; comparison against the seed graph in commit `c9986bc` and the directory map in `docs/claude_desktop_handover.md`. All four findings are reproducible with `python tools/knowledge_graph.py summary` plus reading the two files. No interpretation is involved beyond the recommendations in items 3 and 6.

## Assumptions

- Subnodes are intended as addressable entities rather than as descriptive prose attached to a parent. If they are meant to be inert descriptions, the fix is the reverse: strip their IDs so nothing appears addressable when it is not.
- The handover's directory map describes intent rather than a state that was lost.

## Risks and failure modes

- **Flattening pressure:** making subnodes addressable raises the question of why they are nested at all. That is a real design question; this proposal deliberately does not answer it, and only asks that the current structure be internally consistent.
- **Low-risk change, low-attention review:** mechanical fixes attract less scrutiny than conceptual ones, and item 6 quietly changes what the canonical file contains.
- **Empty-directory theatre:** creating six empty directories can suggest a research apparatus exists when it does not. Prefer creating them lazily, when the first artifact is written.

## Verification plan

- **Baseline:** `python tools/knowledge_graph.py validate` → `VALID`; `summary` → 19 nodes, 13 edges.
- **Intervention:** apply edge patch and tooling changes.
- **Metrics:** `validate` still passes; a test edge targeting `pattern_append_only_audit` passes `check-proposal` where it previously failed; orphan count reported as 0; subnode collision check passes on the current graph.
- **Success threshold:** all four, with no change to node count from this patch.
- **Stop conditions:** if subnode addressability turns out to require restructuring rather than a set-union fix, stop and raise the flattening question as its own proposal.

## Decision

_Pending review. Items 1–2 (the edge patch) are safe and independent. Items 3–6 need an owner decision on intent._

# Project audit kit

Drop-in tools for bringing another repo (poly-bot, poster-studio, …) into the
Agentic Universe format: one **validated project graph** + one **canonical
`PROJECT_STATE.md`**, replacing the sediment of dated hand-over `.md` files.

Pure stdlib, no dependencies. Copy this whole directory into the target repo as
`tools/` (or `tools/au_kit/` — adjust the commands).

## Files

| file | what it does |
| --- | --- |
| `project_graph_scaffold.py` | `new <name>` scaffolds `knowledge/graph/<name>_project_graph.json` + `docs/<name>_PROJECT_STATE.md`; `validate <path>` checks the graph against the schema + the node/edge vocabulary |
| `knowledge_graph.py` | the shared graph validator (dependency of the scaffold) |
| `task_ledger.py` | deterministic task ledger — `pending→active→done` + `blocked/failed/abandoned`, `next_ready()`, `sweep_stale()` for dropped-task recovery, atomic write + `.audit` log. The fix for "tasks get dropped." |
| `supervisor.py` | PILOT-pattern live supervisor over the ledger — deterministic dispatch, stale recovery each tick, deadline + reject-over-budget, per-mode failure digest |

## The graph vocabulary

Nodes: `component` · `decision` · `constraint` · `bug` · `question`
Edges: `depends_on` · `implements` · `challenges` · `blocks` · `records`

Keep it small — 15–40 nodes. The graph is a map, not a mirror. A node earns its
place if a future session would waste time without it.

## Steps for the session doing the audit

```bash
# from the repo root
mkdir -p tools && cp -r /path/to/project_audit_kit/* tools/
python tools/project_graph_scaffold.py new <projname>
# fill knowledge/graph/<projname>_project_graph.json and docs/<projname>_PROJECT_STATE.md
python tools/project_graph_scaffold.py validate knowledge/graph/<projname>_project_graph.json
git add tools/ knowledge/ docs/<projname>_PROJECT_STATE.md && git commit -m "add project graph + PROJECT_STATE"
```

Fill the graph from what the session **actually knows right now**:

- **component** nodes — the real modules/services and what each is for (one line).
- **decision** nodes — why it is built this way; the road not taken.
- **constraint** nodes — VPS/GPU/disk limits, rate limits, API-key requirements,
  the stop-at-draft gate, anything that has already cost hours.
- **bug** nodes — what is currently broken or fragile, with the symptom.
- **question** nodes — the **unfinished checklist**, most-blocking first. This is
  the part a cold audit cannot recover — it is the whole point of asking the
  active session to do this.

`docs/<projname>_PROJECT_STATE.md` is the canonical hand-over: what it is, current
state, the single highest-value next move, hard constraints, open questions, and
"what would make this wrong". Point the old `HANDOVER*.md` files at it and stop
maintaining them.

## What Agentic Universe does with the result

Once the graph + state doc are committed and pushed, the research loop pulls them
and cross-checks each project against the folded literature — e.g. a forecasting
loop should adopt the forecast-ledger / Brier / domain-keyed-calibration
discipline (`epistemic_constitution.py`, run 293 / run 296); a repo whose root
directory has drifted into hundreds of scratch files is a
`concept_unmanaged_skill_libraries_silently_drift` case with a known remedy.

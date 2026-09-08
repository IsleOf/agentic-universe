# Per-project audits

First-pass audits of the owner's other projects, produced by the Agentic Universe loop
(runs 317–320). Each is a **validated project graph + a `PROJECT_STATE.md`** in this repo's
format (`docs/practicing_what_we_preach.md` §3), built from a cold read of the repo with
the volatile parts flagged as `question` nodes.

| project | path | source | status |
|---|---|---|---|
| poly-bot | `poly-bot/` | `/home/dev/poly-bot`, read 2026-09-07 | ✅ **refresh pass done in-repo (verified run 377) — but UNCOMMITTED** |
| poster-studio | `poster-studio/` | `/home/dev/poster-studio`, read 2026-09-07 | ⏳ first pass not started — no `knowledge/` dir yet |

### poly-bot — verified run 377 (2026-09-08)
The session ran the refresh brief (`codex_mapping_prompt.md` Block A + B2) and followed it
closely. Working tree, **not yet committed** (408 insertions / 264 deletions across
`knowledge/graph/` + `docs/PROJECT_STATE.md`):

- **32 → 38 nodes, 28 → 37 edges**, `last_updated` bumped to 2026-09-08.
- **The three watchdog gaps mapped as `bug` nodes, not fixed** — as briefed. Statuses are
  nuanced rather than binary: attempt ceiling is *partial* failure accounting; the deadline
  bounds missing-report work *only on ticks*; the digest exists but uses *generic* failure
  categories.
- **`polybot__q_worker_fleet_fix` → `polybot__bug_agy_dstate_hang`** (`bug`, open, "has
  mitigation, not a proven cure") — exactly the conversion Block B2 asked for. The id changed,
  so a naive diff reads it as a deletion; it is not.
- **Two questions re-opened** (`q_flb_signoff`, `q_blocked_on_data_items`) — expired answers
  re-opened rather than left stale, which the brief explicitly asked for.
- **Four new `component` nodes** covering the drift the brief named: model-routing provenance,
  the AGY host loop, VPS Drive offload, rotating generated checklist lanes.

**Open action for the owner:** the work is in poly-bot's working tree only. The Agentic
Universe loop does not commit into other repos (see Workflow below), so that session or the
owner needs to commit and push it, or it is lost.

Extra follow-through:
- `poly-bot/watchdog_ledger_integration.md` — the 3 additions to
  `ev_hunter_checklist_watchdog.py` that close the dropped-task pile.
- The poster-studio ↔ orchestrator seam is drafted on the `etsy-agentic-space` branch:
  `contracts/poster_studio_interface.md` + `pipelines/poster_creative.yml`.

## Workflow

1. The Agentic Universe loop does the **first pass** (architecture, decisions, constraints,
   known bugs) from a code read — it cannot commit into the other repos.
2. The **active session on each repo** verifies it against current code, fills the
   `question` nodes (the in-flight checklist a cold read can't recover), and copies the two
   files into that repo (`<repo>/knowledge/graph/` + `<repo>/docs/PROJECT_STATE.md`), then
   points the old dated handover docs at `PROJECT_STATE.md`.
3. From then on every fresh session on that repo reads `PROJECT_STATE.md` + the graph
   first. The scattered `HANDOVER-*.md` / `CODEX_HANDOVER_*.md` files become archive.

Validate a project graph with:
`python <path>/tools/project_graph_scaffold.py validate <graph.json>`
(the scaffold + `task_ledger.py` + `supervisor.py` are in `docs/project_audit_kit/`).

## Instructions to give each agent

**Current (run 358): use `codex_mapping_prompt.md`** — the full paste-ready briefs, written
against the real state of both repos (poly-bot needs a *refresh* pass, its map is stamped
2026-09-07 and the code has moved; poster-studio needs the *first* pass, nothing landed).
The two short blurbs below are the earlier run-321 versions, kept for the priority lists.

### poly-bot session (Codex / AGY fleet)
> Read `docs/audits/poly-bot/{PROJECT_STATE.md, poly-bot_project_graph.json,
> watchdog_ledger_integration.md}`. First-pass from a 2026-09-07 read — verify and fill the
> 6 `question` nodes against current code, then copy into `poly-bot/`. Priority work:
> (1) the 3 watchdog gaps (per-item attempt budget, active-dispatch deadline, failure
> digest) — gated-path changes, use your `agent_gate.py` token; (2) the D-state hang root
> cause (`polybot__q_worker_fleet_fix` — try a native-ext4 working dir; else a
> ≥2-D-state-panes alert); (3) reconcile `CURRENT.md` §1–2 (crypto/FLB vs EV Hunter);
> (4) the FLB `[0.40,0.60]` fee-gate conflict — spec v3 §9 needs the "this IS gated"
> correction.

### poster-studio session
> Read `docs/audits/poster-studio/{PROJECT_STATE.md, poster-studio_project_graph.json}`.
> Verify + fill the 5 `question` nodes, copy into `poster-studio/`. Priority work:
> (1) the `etsy-agentic-space` interface — wrap the four calls (`render_design` /
> `make_mockups` / `finalize_images` / `create_draft`) as a module/CLI honoring the six
> invariants in `contracts/poster_studio_interface.md`; (2) the SynthID
> keep/drop/switch decision; (3) confirm draft `4565362214`'s status.

### Codex vs Claude Code
Both AGENT_CONTRACTs encode the ladder free-CLI → haiku → sonnet → opus, orchestrator only
for architecture / grill / live-path. Applied here:
- **Codex** — autonomous multi-step build/fix inside a repo (the watchdog gaps, the
  poster-studio module, filling question nodes from code reads).
- **Claude Code / orchestrator** — architecture decisions, adversarial review before
  commit, the FLB spec-v3 §9 call, reviewing any live-path change for sign-off.
- **The Agentic Universe loop** — the cross-repo picture and keeping these graphs in sync;
  it hands specs to the repo sessions, it does not commit into them.

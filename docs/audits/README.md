# Per-project audits

First-pass audits of the owner's other projects, produced by the Agentic Universe loop
(runs 317–320). Each is a **validated project graph + a `PROJECT_STATE.md`** in this repo's
format (`docs/practicing_what_we_preach.md` §3), built from a cold read of the repo with
the volatile parts flagged as `question` nodes.

| project | path | source | status |
|---|---|---|---|
| poly-bot | `poly-bot/` | `/home/dev/poly-bot`, read 2026-09-07 | first pass — needs the active session to verify + fill the 6 question nodes |
| poster-studio | `poster-studio/` | `/home/dev/poster-studio`, read 2026-09-07 | first pass — needs the active session to verify + fill the 5 question nodes |

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

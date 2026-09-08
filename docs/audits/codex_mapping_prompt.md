# Codex session prompts — map a project to the Agentic Universe standard

Written run 358 (2026-09-07 real time). Paste **BLOCK A** followed by the one project block
into the Codex session running in that repo. Block A is the standard; the project block is
the assignment.

Current state that decided these prompts:
- **poly-bot** — `main`, already has `knowledge/graph/poly-bot_project_graph.json` +
  `docs/PROJECT_STATE.md`, all 5 `question` nodes **resolved** with real dated answers.
  Stamped `2026-09-07`, still 32 nodes / 28 edges, while the repo has moved on. → **refresh pass.**
- **poster-studio** — branch `codex/backup-current-state-20260501`, no `knowledge/` dir,
  nothing landed. → **first pass.**

---

## BLOCK A — the standard (paste into both sessions)

```
You are mapping this repository to the Agentic Universe project-map standard. The output is
a machine-validated artifact, not prose. Read this whole brief before touching anything.

## Goal
Produce (or refresh) exactly two files in THIS repo:
  1. knowledge/graph/<project>_project_graph.json   — a validated project graph
  2. docs/PROJECT_STATE.md                          — the canonical hand-over doc
They replace the sediment of dated HANDOVER-*.md / CODEX_HANDOVER_*.md files. Every future
cold session on this repo reads these two first.

## The graph vocabulary (enforced by the validator — nothing else is legal)
  node types: component | decision | constraint | bug | question
  edge types: depends_on | implements | challenges | blocks | records

Node fields: id, type, label, status, confidence (0..1), description, derived_from[], tags[]
Edge fields: id, source, target, type, description
Top-level keys: project, format, audit, last_updated, nodes, edges

What each node type is FOR:
  component  — a real module/service and what it is for, one line. Not every file.
  decision   — why it is built this way, and the road not taken.
  constraint — VPS/GPU/disk/rate limits, API-key requirements, gates, anything that has
               already cost hours. Structural friction belongs here, not in prose.
  bug        — what is currently broken or fragile, with the observable symptom.
  question   — the unfinished checklist, most-blocking first. THIS IS THE POINT (see below).

## Size bound — 15-40 nodes. Hard.
The graph is a map, not a mirror of the filesystem. A node earns its place only if a future
session would waste time without it. If you are above 40 you are transcribing, not mapping.
Merge or delete before you add.

## The evidence rule (this is the standard's core discipline)
Every node's `derived_from` cites a REAL artifact you actually read: a file path, a commit
SHA, a log excerpt, a config key. No node from memory, inference, or "it probably works like
X". If you are not sure, that is not a low-confidence component node — it is a `question`
node with confidence <= 0.4. Confidently wrong is the failure mode this standard exists to
prevent. A `question` you leave open costs the next session an hour; a `component` you
invented costs it a day.

## Status + confidence conventions
  status:     active | to_fill | open | resolved | deprecated
  confidence: 0.9+ you verified it in code/runtime this session
              0.6-0.8 documented and consistent with what you read
              <=0.4 uncertain -> it should probably be a question node instead
A `question` you answer: set status=resolved, confidence to what you actually earned, and
WRITE THE ANSWER INTO the description prefixed "Resolved <date>:". Do not just flip the flag.

## What only YOU can supply
A cold code read recovers architecture, decisions, constraints and bugs. It cannot recover
the in-flight state: what is half-done, what is blocked on what, what was abandoned and why,
what the last N commits were actually trying to achieve, which of the listed next-steps are
dead. That is the `question` nodes and the "Current state" section. It is the whole reason
this is being asked of you and not done from outside.

## docs/PROJECT_STATE.md — required sections, in this order
  # <project> — Project State
  (header line: format, graph path + validate command, date + your commit SHA)
  ## What it is
  ## Current state
  ## The single highest-value next move
  ## Hard constraints
  ## Open questions
  ## What would make this wrong
"The single highest-value next move" is ONE move, named concretely, with why it beats the
alternatives. Not a list.

## Validate before you commit
  mkdir -p tools && cp -n /mnt/c/Agents/agentic-universe/repo/docs/project_audit_kit/*.py tools/
  python3 tools/project_graph_scaffold.py validate knowledge/graph/<project>_project_graph.json
Must print VALID. Also confirm: no orphan nodes (every node touched by >=1 edge), and no
dangling edges (both endpoints exist).

## Anti-goals — do NOT do these
  - Do not refactor, rename, or "improve" code while mapping. Mapping only, this pass.
  - Do not touch any live/production path, credential, or deployed service.
  - Do not mirror the directory tree into component nodes.
  - Do not propose the architecture changes. Record what IS and what hurts; the
    cross-repo architecture analysis is done afterward against a folded literature base.
    Your job is to make that analysis possible by being accurate.
  - Do not invent a node to fill a gap. Leave the question open.

## Definition of done
  [ ] validator prints VALID; no orphans, no dangling edges
  [ ] 15-40 nodes; every node has a real derived_from
  [ ] every question node is either resolved-with-an-answer or explicitly still open
  [ ] docs/PROJECT_STATE.md has all 6 sections, dated, naming your commit
  [ ] both files committed and pushed on this repo's working branch
  [ ] you replied in the REPLY FORMAT below

## REPLY FORMAT (paste this back verbatim, filled in)
  REPO:            <name>  BRANCH: <branch>  COMMIT: <sha>
  GRAPH:           <n> nodes / <m> edges   VALIDATOR: VALID
  QUESTIONS:       <resolved>/<total> resolved; still open: <ids or none>
  CORRECTIONS:     what the previous/first-pass map got WRONG (most valuable field — be blunt)
  NEW SINCE:       what exists now that the previous map did not know about
  FRICTION:        the 3 things that cost you the most time in this repo, concretely
  WOULD-CHANGE:    if you had one week and no risk limit, the one structural change you'd make
  UNCERTAIN:       what you could not determine and why
```

---

## BLOCK B1 — poster-studio (first pass)

```
Assignment: FIRST PASS. This repo has no project graph yet.

Seed material (a cold read from 2026-09-07 — treat as a HYPOTHESIS to verify, not truth):
  /mnt/c/Agents/agentic-universe/repo/docs/audits/poster-studio/PROJECT_STATE.md
  /mnt/c/Agents/agentic-universe/repo/docs/audits/poster-studio/poster-studio_project_graph.json
That draft is 31 nodes / 28 edges with 5 open question nodes. Start from it, then verify
every single node against current code. Delete what is wrong. Correcting the draft is worth
more to me than extending it.

You are currently on branch codex/backup-current-state-20260501 — confirm that is the right
branch to commit on, or say which is.

The 5 open questions to answer (these are the deliverable):
  ps__q_factory_running        is the listing-factory cron still running, and which listings
                               have drafts awaiting action?
  ps__q_synthid_wanted         is SynthID watermark removal still the intent, given the
                               quality tradeoff and that it is a bypass?
  ps__q_relation_to_etsy_branches   how does poster-studio relate to the agentic-universe
                               autodesign-etsy / etsy-agentic-space branches?
  ps__q_prod_db_sync_reliable  is the production-DB sync (preserved-old-DB + VACUUM INTO) a
                               reliable, documented procedure now?
  ps__q_next_listings          what is the next listing/design to push through the factory,
                               and is Design004 the last completed one?

Also map, as component + constraint nodes, the four-call seam another orchestrator would
drive: render_design / make_mockups / finalize_images / create_draft — including the
stop-at-draft gate and any rate/credential constraint on each. The interface contract draft
is at /mnt/c/Agents/agentic-universe/repo (branch etsy-agentic-space):
contracts/poster_studio_interface.md + pipelines/poster_creative.yml. Say where the real code
diverges from that contract — the divergences are the useful part.
```

---

## BLOCK B2 — poly-bot (refresh pass)

```
Assignment: REFRESH PASS. This repo already has a good map — you (or a prior session) built
it and resolved all 5 question nodes with real dated answers. Do not redo it. The problem is
drift: knowledge/graph/poly-bot_project_graph.json is stamped last_updated 2026-09-07 and
still 32 nodes / 28 edges, while main has moved on (model routing evidence, consolidated AGY
host loop, VPS Drive offload, Gemini 3.8 Flash fleet rollout, checklist-watchdog cron import
robustness, profitable-cohort preservation).

Do exactly this:
  1. Re-verify all 32 existing nodes against current main. Mark anything now false as
     deprecated or correct it in place. Say what changed in CORRECTIONS.
  2. Add nodes ONLY for what is now structurally true and was not before — the recent work
     above is the obvious candidate set. Stay inside 40 nodes total; merge or drop stale
     component nodes to make room.
  3. Re-open any resolved question whose answer has expired. A resolved question that is no
     longer true is worse than an open one.
  4. Bump last_updated and re-run the validator.
  5. Refresh docs/PROJECT_STATE.md's "Current state" and "The single highest-value next
     move" — the Sept-7 answer is probably stale.

Then, still as MAPPING (record state, do not fix), confirm the status of the three watchdog
gaps from /mnt/c/Agents/agentic-universe/repo/docs/audits/poly-bot/watchdog_ledger_integration.md
— per-item attempt budget, active-dispatch deadline, failure digest. For each: implemented,
partially, or not. If implemented, cite the code. These become component or bug nodes.

Note polybot__q_worker_fleet_fix resolved as "no permanent D-state cure, panes on native
ext4". If that is still the state, keep it as a `bug` node with the current mitigation in the
description, not a resolved question — an unfixed recurring failure belongs in the bug
vocabulary where the next session will look for it.

Do NOT make any live-path or gated change in this pass, including the watchdog gaps. Mapping
only; the gated work is a separate assignment with sign-off.
```

---

## What happens with the results

Both replies come back to the Agentic Universe loop, which:
1. pulls the two committed graphs and cross-checks each project against the folded
   literature base (365 nodes / 1478 edges as of run 357) — e.g. an unmanaged accumulation
   of scratch files is `concept_unmanaged_skill_libraries_silently_drift` with a known
   remedy; a repeated dropped-task pile is the `task_ledger` + `supervisor` pattern;
   a forecasting loop wants the forecast-ledger / Brier / domain-keyed-calibration
   discipline from `epistemic_constitution.py`;
2. writes the architecture-change suggestions per project, each citing the finding it rests
   on and a falsifiable prediction;
3. hands those back as a scoped assignment per repo.

The `CORRECTIONS` / `FRICTION` / `WOULD-CHANGE` fields in the reply are the highest-signal
inputs to step 2. A blunt friction log beats a polished graph.

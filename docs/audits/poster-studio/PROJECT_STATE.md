# poster-studio — Project State (first-pass audit)

> **FIRST-PASS audit by the Agentic Universe loop (run 318)**, built 2026-09-07 from
> `/home/dev/poster-studio`: `README.md`, `docs/AGENT_RUNBOOK.md`, the newest
> `docs/HANDOVER-2026-08-30-flow-resume.md`, `docs/TASKLIST-listing-factory-active.md`
> (2026-08-31), `AGENT_CONTRACT.md`, `git log`. **The current cron state, the
> draft-approval status, and the integration with `etsy-agentic-space` need the active
> session to reconcile** — the `question` nodes in `poster-studio_project_graph.json` are
> the placeholders. Copy both files into `poster-studio/` once verified.

## What it is

A browser poster designer + Etsy listing-factory for **themappedmoment.com**:

- **Web app** — Vite/React frontend + Node/Express API (`server/index.js`) + SQLite, deployed
  behind Nginx (static frontend + `poster-studio-api.service:3001`). Sells **star-map**
  (exact night sky at a date/time/location) and **street-map** posters via a professional
  SVG template system (draggable text, custom fonts, 300 DPI export). 4 public listings;
  **production DB is the source of truth** for manually-edited templates.
- **listing-factory** — a staged pipeline: **stage 004** generates one fresh Google Flow
  scene per captured competitor reference (through an AdsPower browser profile + Playwright,
  with a hard `2752×1536` 16:9/2K pixel gate and green-frame detection); compositing crops
  to a centered `2048×1536` 4:3; a fail-closed **reverse-SynthID final pass** runs on
  separate copies; **stage 005** creates the Etsy draft.

## Current state

- **Stop-at-draft is the hard gate:** `factory-create-etsy-draft.js` reads back `state=draft`
  + the exact title + ranked images, and **never calls publish/activation**. AGENT_CONTRACT
  §6 (sign-in automation) is revoked per owner instruction.
- **Most recent completed work:** Design004's ten-scene listing-image batch (2026-08-31) —
  ten production-template poster variants, ten distinct Flow scenes, all through the
  16:9/2K + green-frame + centered-crop + Playwright gates and the reverse-SynthID V3/V4
  pass. Etsy draft `4565362214` exists remotely (`state=draft`, 3 images) — approval status
  unknown from a cold read.
- **A workflow rule was hardened 2026-08-31:** one competitor reference → one independent
  scene record (N images ⇒ N scenes), enforced by `validate_competitor_prompt_map.py`;
  `run_stage.py` blocks stage 004 without a valid prompt map.
- **The git log is ~1 month stale** (last commit 2026-08-30) while
  `TASKLIST-listing-factory-active.md` keeps moving on a cron cycle — a cold `git log`
  understates activity.

## The single highest-value next move

**Define the interface between poster-studio and the `etsy-agentic-space` orchestrator**
(agentic-universe, run 304). That branch is scaffolded as the shop-level orchestrator
*above* poster-studio + `autodesign-etsy`, but poster-studio currently exposes its SVG
template engine and draft factory only as scripts. A thin callable contract (render a
design from a brief → framed mockups → a stage-005 draft) is what lets the orchestrator
drive it. `etsy-agentic-space/pipelines/poster_creative.yml` already sketches the stages;
this is the poster-studio side of that seam.

## Hard constraints

- **No publish/activation** to a live Etsy listing without owner approval.
- Live-path changes (listing data, deploy, production DB) are machine-gated.
- Factory scene batches **never use customer order data**.
- Local GPU/disk budget: ~4 GB VRAM, ~19 GB free — a watermark-removal attempt was aborted
  for this once.
- The reverse-SynthID codebook has **no exact `2048×1536` profile** — a `removed_verified`
  result is detector-clear evidence *with that limitation*, not a universal guarantee; some
  processed copies show quality loss / chromatic fringing.

## Open questions (for the active session)

1. **Factory cron** — is it still running? For which listings does it have drafts awaiting
   human approval? Is draft `4565362214` approved, published, or abandoned?
2. **SynthID** — is watermark removal still the intent given the quality tradeoff and that
   it's a bypass tool, vs. accepting the watermark or generating watermark-free?
3. **`etsy-agentic-space` integration** — does poster-studio expose the template engine +
   draft factory as a callable interface, or is it still "run the scripts"?
4. **Production-DB sync** — is the preserved-old-DB + `VACUUM INTO` procedure scripted and
   reliable now, or still a manual sequence?
5. **Next listing** — what's next through the factory, and is Design004 the last completed
   design?

## What would make this wrong

- **The factory may be paused.** If the cron isn't running, `ps__listing_factory`,
  `ps__flow_browser`, and the stage bugs are dormant, not live.
- **`AGENT_RUNBOOK.md` §"What Runs Where" is dated 2026-05-08** — ports, service names, and
  the production health snapshot may have moved.
- **SynthID removal may already be dropped.** The 2026-08-30 handover treats it as
  provisioned-and-working, but the fringing case and the question above suggest it's under
  review.

# poster-studio interface contract

The seam between this orchestrator and **poster-studio** (`/home/dev/poster-studio`), from
the first-pass audit at `agentic-universe:docs/audits/poster-studio/`. poster-studio today
exposes its SVG template engine and Etsy draft factory only as scripts; this is the thin
callable contract the orchestrator needs.

## What poster-studio provides today (scripts)

| capability | entry point | notes |
|---|---|---|
| render a poster variant from a template + story bundle (names / titles / dates / location) | production templates under `$POSTER_STUDIO_ROOT`; the SVG template system | 12-size expansion per design; 300 DPI export; `data/core/db.sqlite` is the template store, **production is the source of truth** |
| staged competitor → listing pipeline | `listing-factory/run_stage.py` (`POSTER_STUDIO_ROOT` configurable) | stage 004 = one fresh Google Flow scene per competitor reference (AdsPower + Playwright, hard `2752×1536` 16:9/2K gate + green-frame detection); stage 005 = Etsy draft |
| framed / in-room mockup compositing | the mockup harness | centered `2048×1536` 4:3 crop, frame-center error < 0.5 px |
| watermark final pass | `mockup_harness/bin/synthid_final_pass.py` | isolated venv, final 4:3 only, never overwrites inputs, fail-closed, records detector/quality evidence — **not a universal guarantee** (codebook has no exact 2048×1536 profile) |
| create the Etsy draft | `listing-factory/factory-create-etsy-draft.js` | records the draft ID immediately; refuses a second draft on retry; has `--dry-run`; reads back `state=draft` + title + ranked images; **never calls publish/activation** |

## The contract the orchestrator should call

```
render_design(brief) -> {print_files: [path], template_id, design_group}
    brief = {niche, story_bundle:{names, title, date, location}, style_ref?, size_set}
    # runs the SVG template render; does NOT touch production templates or customer data

make_mockups(print_files, competitor_prompt_map) -> {listing_images: [path], review_html}
    # stage 004: one competitor reference -> one independent fresh scene (N refs => N scenes),
    # enforced by validate_competitor_prompt_map.py; each scene passes the 16:9/2K + green-frame gate

finalize_images(listing_images) -> {final_images: [path], synthid_evidence}
    # centered 4:3 crop + the fail-closed reverse-SynthID pass on SEPARATE copies;
    # originals stay the candidates pending human visual approval

create_draft(listing_spec, final_images, *, dry_run=True) -> {draft_id, state, ranked_images}
    # stage 005. dry_run by default. NEVER publishes. A real create needs the stop-at-draft
    # gate satisfied and (per poster-studio AGENT_CONTRACT sec 6 + the machine gate) an owner
    # approval token for the live-path write.
```

## Invariants the orchestrator must respect

1. **Stop at draft.** No orchestrator path may cause a publish/activation. The draft is the
   terminal automated state; a human approves the listing.
2. **A stage is done only when its `manifest.history` entry is written AND the artifact
   exists on disk** — the orchestrator checks the artifact, it does not trust a status
   field (poster-studio's recurring confabulation failure mode).
3. **One competitor reference → one fresh prompt.** The orchestrator supplies a valid
   `competitor_prompt_map`; `run_stage.py` blocks stage 004 without one.
4. **No customer order data** enters a factory run.
5. **Production templates are read-only** to the orchestrator. Template edits are a
   poster-studio human-in-the-loop task.
6. The **`etsy__c_no_secrets_to_agents`** rule still holds — the orchestrator calls
   poster-studio scripts, it does not handle Etsy/AdsPower credentials.

## Open (poster-studio side, `ps__q_relation_to_etsy_branches`)

Whether poster-studio wraps the four calls above as a real module/CLI, or the orchestrator
shells out to `run_stage.py` + `factory-create-etsy-draft.js` with `POSTER_STUDIO_ROOT`
set. The audit recommends the former; either works for a first integration.

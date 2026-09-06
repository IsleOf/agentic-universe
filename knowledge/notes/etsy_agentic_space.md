# Etsy Agentic Shop-Management Space

> Type: shop-level orchestrator branch — sits **above** Poster Studio and AutoDesign
> Date: 2026-09-07 · Branch: `etsy-agentic-space` (off `main`)
> Sources: owner Perplexity research (2026-09-07); Etsy Open API v3 docs; Jentic; Apify;
> practitioner automation guides. Vendor star counts / time savings are point-in-time and
> vendor-reported.

## Thesis

The ingredients for an agentic Etsy shop already exist in the ecosystem, but as **siloed
SaaS products**. What is missing — and what this branch is — is a coherent *Etsy agent
layer* inside Agentic Universe that connects **market research → AutoDesign → listing
automation → POD fulfillment** into one orchestrated system, with everything durable in
the knowledge graph. Do **not** reinvent listing or design here; orchestrate the parts
that already exist (Poster Studio for the SVG template engine + export; the
`autodesign-etsy` branch for competitor extraction + novel design generation).

## What already exists in the ecosystem

### SaaS / tools (vendor-locked, not graph-integrated)
| Tool | What it does | Why it's not enough |
|---|---|---|
| InsightAgent "AI Workspace" | keyword research, listing optimization, bulk edits, competitor monitoring, trend detection; vendor claims ~10–20 h/week saved, TOS-compliant | vendor-locked; no link to your knowledge graph or AutoDesign |
| Merch Titans | POD bulk listing, keyword research, multi-platform upload, trademark check | POD-scale generic; no shop-specific rules or experiments |
| eRank / Marmalead | SEO analytics on public Etsy data | analytics only, no action layer |
| Etsy Tag Generator / Magic Listing Optimizer | scrape top listings → titles/descriptions/13-tag sets | single-step helpers, no experiment tracking |
| TaskAGI / Zapier+Sheets+Canva+ChatGPT+eRank stacks | no-code order/reply/listing/social automation | glue, not agents; no decision logic or unified ledger |

### API / MCP / agent infrastructure (this is the integration surface to use)
| Surface | Detail |
|---|---|
| **Etsy Open API v3** | official: shop management, listings, sections, inventory, receipts, payment ledgers |
| **Jentic** (`Jentic One`) | validated OpenAPI spec for the full Etsy v3 surface (~103 endpoints) + a self-hosted execution layer that calls Etsy with your app credentials so **agents never see secrets**; full logging |
| **Apify Etsy MCP Scraper** | live search over listings / shops / categories exposed to MCP clients (Claude, ChatGPT, Cursor, n8n) — the market-research surface |
| **Open "Etsy API v3 for AI Assistants" MCP server** | wraps Etsy v3 for shop info, trending data, listing create/update, sections; deployable to Smithery |
| **Playwright / Browser-Use from WSL2** | fallback only, for off-API flows (some ad flows); higher TOS risk — secondary path |

## The four coordinated subsystems

1. **Shop intelligence & market research** — periodic sampling of target niches (maps,
   posters, gold-foil, personalized gifts) via Apify Etsy MCP Scraper / Jentic listings
   endpoints; log features (colors, layout, messaging, price bands, bestseller patterns)
   into the graph; emit **design briefs** + **keyword packs** for AutoDesign and Poster
   Studio.
2. **Creative pipeline orchestration** — a controller that feeds research-derived briefs
   into AutoDesign (`autodesign-etsy`) → SVG/poster generation via Poster Studio's
   template engine → framed-mockup + listing-image pipeline. Optional promo-video hook
   (existing Whisper/video workflows) for Pinterest/IG.
3. **Listing & pricing automation** — agents take generated assets + keyword packs and
   call Etsy v3 (via Jentic or the MCP server) to create/update listings, sections,
   inventory, personalization, pricing rules. Scheduled **SEO-refresh** agents rotate
   bottom-performing tags, adjust seasonal keywords, run title/description A/B tests.
4. **Fulfillment, POD routing & customer ops** — an order-routing agent listens for new
   receipts and picks a POD provider (Prodigi / Printify / Merchize) by size,
   destination, and all-in cost; a comms agent drafts replies / review follow-ups /
   resolutions from templates via the Shop Management API.

## Existing tools vs what to build

| Layer | Lean on | Gap | Component to build |
|---|---|---|---|
| Market research | InsightAgent, Merch Titans, eRank/Marmalead, tag generators | vendor-locked, not graph-integrated | `agents/etsy_researcher.py` (Apify/Jentic + graph storage of niches, competitors, price bands) |
| Creative pipeline | AutoDesign, Poster Studio template engine, image models | no orchestrator linking brief → SVG → mockup → listing assets | `pipelines/poster_creative.yml` |
| Listing automation | Jentic Etsy API, Etsy MCP server, Open API v3 | no shop-specific rules / experiments / graph integration | `agents/etsy_lister.py` + `schemas/experiment_listing_ab_test.yaml` |
| Fulfillment & ops | POD APIs (Prodigi, Printify, Merchize), Zapier/Sheets trackers | no decision logic, no unified cost/margin ledger | `agents/pod_router.py`, `pipelines/order_fulfillment.yml`, `schemas/pod_cost_model.yaml` |

## Integration decision

- **Primary:** Jentic One as the secure HTTP execution layer (agents → Jentic → Etsy v3;
  agents never see secrets), wrapped by the Etsy MCP server so agents issue structured
  tool calls (`create listing`, `update tags`, `get active listings`, `list receipts`).
- **Research:** Apify Etsy MCP Scraper for discovery / competitor analysis, driven by
  "research playbooks" in the graph (top-N by niche, crawl frequency, features to
  extract).
- **Fallback:** Playwright/Browser-Use from WSL2 for genuine API gaps only.

## Constraints carried from the owner's setup

- Estonian company receives Etsy payments; POD research already done (Prodigi, Printify,
  Merchize cheapest; gold-foil printing for US-heavy demand).
- TOS risk tolerance is low → API/MCP first, headless browser only for true gaps.
- Stop-at-draft gate (from poster-studio): no auto-publish to a live listing without
  explicit owner approval. This branch inherits it.

## Relationship to the rest of Agentic Universe

This branch is the **shop-level orchestrator**. It consumes:
- `autodesign-etsy` — competitor extraction + novel design generation (AutoDesign, arXiv 2608.13560)
- Poster Studio (`/home/dev/poster-studio`) — SVG template engine + 300 DPI export + Etsy draft factory

It should adopt the epistemic-market discipline from the main research graph
(`epistemic_constitution.py`, runs 293 / 296): every listing experiment is a **forecast**
(expected conversion / revenue lift) scored on resolution, with per-niche calibration —
not a vibe. A listing A/B test is a paired live trial; treat it like one.

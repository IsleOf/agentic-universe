# Etsy Agentic Space — branch `etsy-agentic-space`

The shop-level orchestrator for Agentic Universe's Etsy operation. It connects
**market research → AutoDesign → listing automation → POD fulfillment** into one
system, with all state durable in the knowledge graph. It sits **above** Poster
Studio (`/home/dev/poster-studio`) and the `autodesign-etsy` branch and does not
reinvent design or listing.

## Read first

- `knowledge/notes/etsy_agentic_space.md` — the research: what exists in the
  ecosystem, the four subsystems, the integration decision (Jentic + Etsy MCP
  primary; Apify Etsy MCP Scraper for research; Playwright fallback), and the
  existing-tools-vs-build table.
- `knowledge/graph/etsy_agentic_space_graph.json` — the architecture as a
  validated project graph (23 nodes / 28 edges): components, decisions,
  constraints, and the open-question checklist.

## Layout (skeleton — stubs only)

```
agents/
  etsy_researcher.py       shop intelligence & market research
  etsy_lister.py           listing & pricing automation (STOP AT DRAFT)
  pod_router.py            POD provider routing + cost/margin ledger
  shop_health_monitor.py   shop ops + customer-comms drafts
pipelines/
  poster_creative.yml      design brief -> SVG -> mockup -> listing assets
  listing_automation.yml   assets -> Etsy draft + scheduled SEO refresh
  order_fulfillment.yml    receipt -> provider choice -> submit -> ledger
schemas/
  etsy_listing.yaml  etsy_shop_state.yaml  pod_cost_model.yaml  experiment_listing_ab_test.yaml
tools/
  jentic_client.py         secure Etsy v3 execution layer (agents never see secrets)
  etsy_mcp_client.py        MCP tool-call surface (+ Apify scraper for research)
```

## Hard constraints (inherited)

- **Stop-at-draft:** no auto-publish to a live listing without explicit owner
  approval.
- **No secrets to agents:** Etsy / POD credentials live only in the execution
  layer and the provider adapters.
- **API/MCP first:** headless browser (Playwright/Browser-Use from WSL2) only for
  genuine API gaps.
- Every listing experiment is a **scored forecast** (predicted lift + confidence,
  resolved and Brier-scored per niche) — the epistemic-market discipline from
  `epistemic_constitution.py` on the research branch.

## First milestone

`etsy__q_next` in the graph: stand up `tools/jentic_client.py` +
`tools/etsy_mcp_client.py` against the sandbox and get **one read-only round trip**
(`listings_active`) working end to end. Everything else depends on the integration
layer.

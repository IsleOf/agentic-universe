#!/usr/bin/env python3
"""etsy_researcher — shop intelligence & market research (subsystem 1).

SKELETON. Samples target niches via the Apify Etsy MCP Scraper / Jentic listings
endpoints and logs features into the knowledge graph, then emits design briefs and
keyword packs for the creative pipeline.

Contract (to implement):

    run_playbook(playbook: dict) -> ResearchResult
        playbook = {niche, top_n, features:[...]}   # from knowledge/notes + a graph node
        ResearchResult = {niche, sampled:[listing...], price_bands, tag_frequencies,
                          bestseller_patterns, design_brief, keyword_pack}

    persist(result: ResearchResult) -> None          # write into knowledge/graph/

Uses: tools/etsy_mcp_client.py (research surface). No credentials here.
Constraint: research scraping limited to the public search surface (etsy__c_tos_compliance).
See knowledge/notes/etsy_agentic_space.md and knowledge/graph/etsy_agentic_space_graph.json.
"""
from __future__ import annotations


def run_playbook(playbook: dict):
    raise NotImplementedError("etsy_researcher.run_playbook — see module docstring")


def persist(result) -> None:
    raise NotImplementedError("etsy_researcher.persist — write ResearchResult into the graph")


if __name__ == "__main__":
    print(__doc__)

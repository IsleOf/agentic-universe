#!/usr/bin/env python3
"""etsy_mcp_client — MCP tool-call surface for Etsy.

SKELETON. Wraps the Etsy MCP server (authenticated actions, delegating to Jentic) and
the Apify Etsy MCP Scraper (public research surface). Agents issue structured tool
calls rather than hand-rolling HTTP.

Contract (to implement):

    search_listings(query, **filters) -> list          # Apify scraper (public)
    shop(shop_id) -> dict                               # Etsy MCP server
    create_listing(payload) / update_tags(listing_id, tags) / receipts(shop_id)

Research calls use only the public search surface (etsy__c_tos_compliance).
"""
from __future__ import annotations


def search_listings(query: str, **filters) -> list:
    raise NotImplementedError("etsy_mcp_client.search_listings — Apify Etsy MCP Scraper")


def shop(shop_id: str) -> dict:
    raise NotImplementedError("etsy_mcp_client.shop")


if __name__ == "__main__":
    print(__doc__)

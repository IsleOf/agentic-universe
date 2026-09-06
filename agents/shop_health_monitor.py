#!/usr/bin/env python3
"""shop_health_monitor — shop ops & customer comms (subsystem 4b).

SKELETON. Tracks shop state (open orders, message queue, review score, per-listing
performance) and drafts customer replies / review follow-ups / resolution messages
from templates via the Etsy Shop Management API (through tools/jentic_client.py).

Contract (to implement):

    snapshot() -> ShopState                       # persisted into the graph
    draft_replies(message_queue: list) -> list    # DRAFTS only — owner sends
    flag_anomalies(state: ShopState) -> list      # review-score drop, stuck orders, ...

Drafts are never sent automatically.
"""
from __future__ import annotations


def snapshot():
    raise NotImplementedError("shop_health_monitor.snapshot")


def draft_replies(message_queue: list) -> list:
    raise NotImplementedError("shop_health_monitor.draft_replies — drafts only")


def flag_anomalies(state) -> list:
    raise NotImplementedError("shop_health_monitor.flag_anomalies")


if __name__ == "__main__":
    print(__doc__)

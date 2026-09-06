#!/usr/bin/env python3
"""pod_router — fulfillment & POD routing (subsystem 4).

SKELETON. Listens for new Etsy receipts and routes each order to a print-on-demand
provider (Prodigi / Printify / Merchize) by size, destination, and all-in cost,
then writes a unified cost/margin ledger.

Contract (to implement):

    choose_provider(order: dict, cost_model: dict) -> {provider, quote, rationale}
        cost_model = schemas/pod_cost_model.yaml (real per-provider numbers — TODO)
    submit(order: dict, choice: dict) -> provider_order_id
    ledger_append(order, choice, provider_order_id) -> None   # cost / margin

Constraint: Etsy payments run through the Estonian company; gold-foil printing for
US-heavy demand (etsy__c_estonian_company_payments). Credentials live in the
per-provider adapters, not here.
"""
from __future__ import annotations


def choose_provider(order: dict, cost_model: dict) -> dict:
    raise NotImplementedError("pod_router.choose_provider — needs schemas/pod_cost_model.yaml filled")


def submit(order: dict, choice: dict) -> str:
    raise NotImplementedError("pod_router.submit")


def ledger_append(order: dict, choice: dict, provider_order_id: str) -> None:
    raise NotImplementedError("pod_router.ledger_append")


if __name__ == "__main__":
    print(__doc__)

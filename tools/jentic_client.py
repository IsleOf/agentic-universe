#!/usr/bin/env python3
"""jentic_client — secure Etsy Open API v3 execution layer.

SKELETON. Agents call this; this calls Jentic One; Jentic One calls Etsy v3 with the
app credentials. Agents never see secrets (etsy__c_no_secrets_to_agents). Every
request is logged.

Contract (to implement):

    JenticClient(base_url, api_key_env="JENTIC_API_KEY")
      .call(operation_id: str, params: dict) -> dict     # from the validated OpenAPI spec (~103 ops)
      .listings_active(shop_id) / .create_listing(...) / .update_listing(...) / .receipts(...)

THE FIRST MILESTONE (etsy__q_next): one read-only round trip — listings_active — against
the sandbox, end to end.
"""
from __future__ import annotations
import os


class JenticClient:
    def __init__(self, base_url: str, api_key_env: str = "JENTIC_API_KEY"):
        self.base_url = base_url
        self._key = os.environ.get(api_key_env)  # never logged, never returned

    def call(self, operation_id: str, params: dict) -> dict:
        raise NotImplementedError("JenticClient.call — wire to Jentic One")

    def listings_active(self, shop_id: str) -> dict:
        return self.call("getListingsByShop", {"shop_id": shop_id, "state": "active"})


if __name__ == "__main__":
    print(__doc__)

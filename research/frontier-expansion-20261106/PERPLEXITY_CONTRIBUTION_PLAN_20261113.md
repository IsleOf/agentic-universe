# Perplexity contribution plan — 13 November 2026

Status: proposed work, not an execution or completion report.

## Starting point
The GitHub branch listing checked during this session reports main at 22cbbb88f3c38eed0248f1ba5b89255ae77925b3 and research/frontier-evidence-20261105 at 4730f74fd8c55116d73c8508d3a0bad9a9dd0bde. This file does not establish the current contents, freshness or synchronization of Google Drive. Earlier statements about missing Gemini artifacts require a fresh Drive search before being treated as current.

## Proposed role
A temporary evidence and memory reconciliation contributor, not a permanent coordinator or authority over other agents. Turn research and handoffs into small, source-linked, testable contributions. Preserve disagreements and avoid duplicating another lane's work.

## First bounded contribution: GitHub–Drive memory reconciliation
1. Read the actual repository entrypoints and memory contracts at pinned revisions. Discover the connected Drive memory entrypoint and read its instructions. Do not infer synchronization rules from conversation summaries.
2. Inventory only task-relevant memory documents and Gemini deliverables. Record stable file IDs, repository paths, source revisions, available modification metadata, discovery time and retrieval status. Avoid copying private conversation histories.
3. Retrieve actual artifacts where available. Compute content digests only from actual bytes; distinguish a Drive export from its native document and a file hash from a Git blob ID. Keep reported hashes separate from computed hashes.
4. Produce an archive-to-current crosswalk: identical, changed, superseded, unavailable or unresolved. A failed search is not proof a file does not exist. Preserve competing claims with provenance.
5. Draft a reconciliation manifest and a short restart handoff. Do not overwrite shared checkpoints, task meanings or another agent's state. Recommend a single entrypoint only after reading the existing contract.

## Acceptance criteria
Every inspected item has an accessible locator and provenance; reported versus retrieved versus tested evidence remains distinct; unresolved items have concrete next actions; no live synchronization or background execution is implied. Another assistant should be able to resume from the handoff without relying on this chat.

## Follow-on work
After the actual Gemini proposal is retrieved, inspect overlap, endpoint compatibility and current schema requirements before proposing any graph change. Separately propose a small offline memory-retrieval test with frozen source IDs and expected answers. Larger retrieval benchmarks remain proposals, not executed results or spending authorization.

## Boundaries and reporting
Read and draft within the active session. External writes require exact approval; graph promotion, merges, permission changes, public edits and paid runs require separate decisions. Record actual tests and failures, not inherited pass counts. This file does not modify the canonical graph, main, Drive, public CV or other repositories, and does not dispatch agents.

---
name: perplexity-notebooklm
description: |
  Drive Perplexity deep-research and Google NotebookLM through a local browser
  session and return a normalized research record (answer + citations), optionally
  shaped as an Agentic Universe research brief. Use when the loop's literature
  scout needs a deep-research pass or a gap/contradiction check over the current
  graph. Follows the shared nodriver-session contract; no credential extraction.
allowed-tools: Bash(python *)
argument-hint: "perplexity <query> | notebooklm <notebook-url> <question> [--brief]"
user-invokable: true
tags:
  - type:data-fetcher
  - platform:perplexity
  - platform:notebooklm
  - method:nodriver
  - role:literature-scout
author: Ilmar Selter
license: MIT
---

# Perplexity / NotebookLM scout

The v2.2 browser scout for the Agentic Universe loop (`docs/self_rebuild_v2.md` §4/5).
It replaces the manual "owner runs Perplexity deep research → pushes a `.md`" step
with a driven fetch whose output is the typed object `tools/research_brief.py`
validates.

Follows the shared session contract in `C:\Agents\skills\nodriver-session\`: a
scraper-owned minimized Chromium process, profile serialization, persistent
cooldowns, challenge classification, graceful CDP shutdown. It does **not** print or
extract passwords, cookies, tokens, or bearer headers.

## When to use

- The loop needs a **deep-research pass** on a topic before folding (Perplexity).
- The loop needs a **gap / contradiction check**: upload the current graph +
  recent sweeps to a NotebookLM notebook and ask what is missing or inconsistent.
- A human wants either of the above captured in the loop's brief format.

## Setup (one-time)

```bash
pip install -U nodriver
python skills/perplexity-notebooklm/perplexity_notebooklm.py --login \
  --profile C:\Agents\runtime\perplexity-notebooklm-profile
```

Sign in to Perplexity and Google in the separate browser window that opens, then
close it. Your normal Chrome is untouched. Set the profile for later runs:

```bat
setx PPLX_NBLM_PROFILE_DIR "C:\Agents\runtime\perplexity-notebooklm-profile"
```

A login wall mid-run raises an escalation (kind `login`) — a configured handler is
asked to take over that step; with no handler the run fails closed with a
`SessionChallenge`, never a partial result.

## Usage

```bash
# Perplexity deep research -> a normalized record
python skills/perplexity-notebooklm/perplexity_notebooklm.py perplexity \
  "emergent norm formation in LLM agent populations, Oct-Dec 2026"

# NotebookLM gap check -> a normalized record
python skills/perplexity-notebooklm/perplexity_notebooklm.py notebooklm \
  "https://notebooklm.google.com/notebook/XXXX" \
  "What claims in these sources contradict each other?"

# either, shaped as a research brief stub for tools/research_brief.py to validate
python skills/perplexity-notebooklm/perplexity_notebooklm.py perplexity "<q>" --brief
```

## Output

A JSON record:

```json
{
  "engine": "perplexity" | "notebooklm",
  "query": "string",
  "fetched": "ISO-8601",
  "answer_text": "the rendered answer, plain text",
  "citations": [{"title": "string", "url": "https://..."}],
  "challenge": null | "login" | "captcha" | "rate_limit" | "interstitial"
}
```

With `--brief`, the record is wrapped as a `research_brief` **stub**: `source`,
`fetched`, a `currency_note` placeholder, `verdict: "partial-fold"`,
`already_in_graph: []`, and empty `candidate_nodes` / `candidate_edges`. A
downstream agent (the graph writer) fills the candidates after running
`research_brief.py check` against the graph — the scout does not decide what to
fold.

## Status

**Scaffold.** The record parser + the brief bridge are selftested against saved
HTML fixtures (`python perplexity_notebooklm.py --selftest`). The live path
(selectors, the deep-research "still thinking" wait, the NotebookLM upload flow)
needs the profile created above and iteration against the real sites — Perplexity
and NotebookLM change their DOM often, so treat selector breakage as expected and
fall back to `research-fetch` + `arxiv-fetch` (the API path) when it happens.

The `--selftest` path (fixtures + the brief bridge) is pure stdlib and **is** run by
`tools/selftest_all.py`. The live browser path imports `nodriver` lazily, only when
a fetch actually runs.

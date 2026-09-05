# Sources

External material — papers, articles, repositories, benchmark results — recorded as **claims**, not findings.

## Current posture: open ingest

The project is in an emergence-first theoretical phase (`docs/emergence_first_posture.md`). **The falsifier-required ingest gate is suspended.** File anything that suggests a mechanism worth modelling, and take ideas from it straight into the graph if they're interesting.

One thing still worth keeping, because it's free: a published paper is not evidence that its claim holds here. It's evidence that someone reported it, under conditions recorded in the source file. Note the study type and move on.

**Read for mechanisms, not for conclusions.** In this phase a survey's bibliography is usually worth more than its argument, and a paper's discarded intuition is often worth more than its headline result.

## Ingest gate (suspended — restore with the verification phase)

> No source record is filed unless it names what result would falsify its claim. A folder of abstracts is not research. This field is what stops the directory filling with plausible-sounding summaries that nobody can act on.

Kept verbatim because it will be right again. It is wrong *now* — during model-building the plausible-sounding summary is exactly the raw material.

## Where to sweep

Two jobs, not one. **Discovery** finds work; **adjudication** decides whether a piece of work says what it's cited as saying. As of 2026-09-05 discovery is well covered and adjudication is the gap — the three source-register corrections on file (pressure-field number drift, openJiuwen headline substitution, the graph-engineering critique) were all adjudication failures, not discovery failures.

### Discovery

| Venue | Why | Access | Wired? |
| --- | --- | --- | --- |
| arXiv (`cs.MA` `cs.AI` `cs.CL` `cs.SE`, plus `cs.HC` `cs.CY` `econ.GN` for the work-substitution angle) | Field publishes here first | `export.arxiv.org/api/query` — no key. The `/list/` HTML pages 404; use the API. | **yes** |
| Hacker News | Practitioner signal, shipping tools, "harness" as a forming genre | `hn.algolia.com/api/v1/search_by_date` — no key, date-filterable | **yes** |
| X / Twitter | Author threads days ahead of publication | `x-fetch` skill (`C:\Agents\skills\x-fetch`) — nodriver + shared profile | **yes** |
| Reddit (`r/LocalLLaMA`, `r/MachineLearning`) | Failure reports that never reach arXiv | `reddit-fetch` skill — OAuth app + local token | **yes** |
| YouTube | Paper-summary channels; see `docs/source_channels.md` for which | `youtube-transcript` skill — local, residential IP | **yes** |
| GitHub search / trending / releases | What's actually shipping vs. what's a preprint claim | `api.github.com` — PAT for 5,000 req/hr (unauth 60/hr is too low) | no |
| LessWrong / AI Alignment Forum | Sharpest early analysis of deception, scheming, situational awareness — months ahead of papers | `lesswrong.com/graphql`, `alignmentforum.org/graphql` — public reads, no auth | no |

### Adjudication

| Venue | Answers | Access | Wired? |
| --- | --- | --- | --- |
| OpenReview | *Why did reviewers push back? Did it get in?* Reviews ask the baseline/ablation/cost questions first. | `api2.openreview.net/notes?forum=<id>` returns the full thread (submission + reviews + rebuttals + meta-review + decision). Public, no auth. Old venues on `api.openreview.net` (v1). | no |
| Semantic Scholar Graph API | *How do later papers characterize this one? What refutes it?* | `api.semanticscholar.org/graph/v1/paper/{id}/citations?fields=contexts,intents,isInfluential` — the `contexts` field returns the exact citing sentences. `{id}` accepts `arXiv:2604.25850`. Keyless ~1 req/s; free key raises it. | no |
| OpenAlex | Citation counts, concept tags, open-access links | `api.openalex.org/works` — no key, add `mailto=` for the polite pool | no |
| Papers with Code | Leaderboard reality vs. "strongest **selected** baseline" | `paperswithcode.com/api/v1/` — no key. Check it's still live before relying on it. | no |
| SWE-bench / Terminal-Bench / ARC Prize leaderboards | Ground truth for stale-baseline detection | SWE-bench + Terminal-Bench: JSON on their sites + full run data in `SWE-bench/experiments` and `laude-institute/terminal-bench` on GitHub. ARC Prize (`arcprize.org/leaderboard`) is JS-rendered — needs the browser wrapper. | no |
| Google Scholar | Forward citation tracking with different coverage from S2; author recent-work feeds | No API, blocks scrapers hard. Needs a nodriver profile with a **logged-in Google session** — the one place the reusable Google-authed browser profile is the enabling piece, not a convenience. | no |

Do not route literature access through pirated-article mirrors; for this field they add nothing arXiv does not already cover.

## Fetch infrastructure

`x-fetch` and `reddit-fetch` established a reusable pattern worth copying for any browser-backed source:

- **nodriver** driving a separate minimized headed Chromium against a **dedicated profile dir** under `C:\Agents\runtime\<skill>-profile` — never the user's real Chrome, never extracted cookies. Login persists across runs and across agents.
- The **safe-shutdown sequence** (`Target.closeTarget` → CDP browser-close → await subprocess reap → repair stale `profile.exit_type` only on exit 0). Do not substitute `browser.stop()` or `process.terminate()` — they trigger Chrome's "Restore pages?" prompt on the next run.
- 15-minute response cache under `~/.cache/<skill>/`.
- A **shared findings recorder** (`record_finding.py` → `reference/agent-findings.md`) that every run reads first and appends verified navigation/extraction/failure facts to. Rejects credential-like material.
- Structured JSON out, typed exit codes for failure classes (rate-limited / auth-needed / blocked / bad-input).

**Which of the new sources actually need it:** almost none. OpenReview, Semantic Scholar, OpenAlex, GitHub, LessWrong/AF, and Papers with Code are all clean public REST/GraphQL — plain `WebFetch` or a thin `requests` script, no browser. The browser wrapper earns its place for exactly two: **ARC Prize's JS-rendered leaderboard**, and **Google Scholar**, where the persistent Google-authed profile is the only reliable way in.

### Build priority

1. **OpenReview** — highest value, no auth, simplest build. Reviews are the adjudication layer this project most lacks.
2. **Semantic Scholar** — the `contexts` field directly serves the "verify the claim, not just existence" rule.
3. **GitHub** — issue trackers on the real harness implementations are where failure modes surface.
4. **Benchmark leaderboards** — against headline substitution.
5. **LessWrong / AI Alignment Forum** — for the emergence and cognition-emergence side.
6. **Google Scholar** — last, because it's the hardest and Semantic Scholar covers most of the need.

## Record format

One file per source, `sources/papers/<year>-<slug>.md`:

- identifier (arXiv ID / DOI / URL)
- claim, stated in one sentence
- study type: `empirical` | `benchmark` | `position` | `survey` | `anecdote`
- baseline used, sample size, and whether cost was controlled — blank if the paper does not say, and blank is itself informative
- **what result would falsify this**
- which graph node or approach family it bears on
- whether it has been reproduced independently

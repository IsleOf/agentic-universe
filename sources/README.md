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

| Venue | Why | API |
| --- | --- | --- |
| arXiv (`cs.MA`, `cs.AI`, `cs.CL`, `cs.SE`) | Field publishes here first; near-complete coverage for agentic systems | yes, no key |
| OpenAlex | Full metadata + citation graph, open | yes, no key |
| Semantic Scholar | Citation graph, TLDRs, influence counts | yes, free tier |
| OpenReview | Public peer reviews for ICLR/NeurIPS — reviewers ask the baseline questions | yes |
| Papers with Code | Reproductions and leaderboards | yes |
| ACL Anthology | Published NLP/multi-agent venue archive | yes |

These are open-access routes. Do not route this project's literature access through pirated-article mirrors; for this field they add nothing arXiv does not already cover.

## Record format

One file per source, `sources/papers/<year>-<slug>.md`:

- identifier (arXiv ID / DOI / URL)
- claim, stated in one sentence
- study type: `empirical` | `benchmark` | `position` | `survey` | `anecdote`
- baseline used, sample size, and whether cost was controlled — blank if the paper does not say, and blank is itself informative
- **what result would falsify this**
- which graph node or approach family it bears on
- whether it has been reproduced independently

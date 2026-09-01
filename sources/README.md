# Sources

External material — papers, articles, repositories, benchmark results — recorded as **claims**, not findings.

## The rule

A source never becomes a graph node directly. It enters here, and may then *propose* a node through `evolution/proposals/`. This is the same barrier that applies to runtime evidence and to agent output: nothing promotes itself.

A published paper is not evidence that its claim holds in this project's context. It is evidence that someone reported the claim, under conditions recorded in the source file. Treat the abstract as a hypothesis with an author attached.

## Ingest gate

**No source record is filed unless it names what result would falsify its claim.** A folder of abstracts is not research. This field is what stops the directory filling with plausible-sounding summaries that nobody can act on.

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

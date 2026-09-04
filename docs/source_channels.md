# Source Channels and Accounts to Follow

Curated media sources for the research programme, separate from `docs/source_register.md` (which tracks papers and repos, not channels). A source earns a place here by demonstrated method, not by production quality or subscriber count.

## How a channel gets listed

Not "covers relevant topics" - many channels do that. The bar is **independent verification against the primary source**, demonstrated on camera: reading the actual paper rather than the abstract, checking a headline number against the results table, and saying so on record when a paper doesn't support its own framing. Get demoted the same way: caught stating a paper's claim without having opened it, or restating a headline number that the source data doesn't support.

---

## YouTube

### Discover AI (`@code4AI`) — good source, added 2026-09-05

**Why:** Three videos analysed this session (transcripts fetched locally via the `youtube-transcript` skill, then deleted after use — see below). All three showed the same disciplined pattern: read the primary paper directly, distinguish what the paper claims from what the presenter's own synthesis adds, and call out weak evidence explicitly rather than passing it through.

Concretely, in this session alone the channel:

1. **Caught a paper's own headline number outrunning its data.** For `arXiv:2608.27969` (openJiuwen), the video pulled the actual results table and reported the apples-to-apples same-backend comparison (+0.24pp, smaller than the reported ±1.1-1.2pp uncertainty) against the paper's headlined "+3.39pp," which turned out to come from swapping to a stronger backend model rather than from the harness contribution being evaluated. I verified this independently against the paper's own table and it holds — the abstract's own phrase, "strongest **selected** leaderboard point estimate," was the tell. This generalised into `concept_benchmark_headline_substitution` in the graph: a third citation-risk class distinct from fabrication and from note-summary drift, both already on record in this project.

2. **Distinguished a paper's conceptual framing from its actual empirical support**, in the same video: flagged that the authors' own "equation 7" cost-utility formulation was explicitly stated as "a conceptual lens... rather than a numerical optimization algorithm," and that no component ablations were run — both confirmed against the paper directly.

3. **Substantively disagreed with a 36-author survey it was covering** (`arXiv:2608.21156`), rather than passing its framing through uncritically. Specific, well-formed critiques: loop and graph engineering are argued in the paper as sequential rungs (individual → system intelligence) but read more precisely as orthogonal dimensions — temporal dynamics versus relational structure — that any non-trivial system needs simultaneously; the individual/system-intelligence boundary breaks on a simple case (a single harness spawning sub-agents with shared state); and a fixed ontology can only detect gaps within categories it already has, never a category it never conceived of ("a perfectly consistent ontology can encode a perfectly wrong theory"). All three landed as real additions to this project's graph (`concept_system_intelligence_boundary_problem`, `concept_ontology_known_unknowns_limit`), not just as an alternative viewpoint noted in passing.

4. **Synthesises across its own back-catalogue rather than treating each paper in isolation** — explicitly cross-referencing a Google preprint on agentic skills against the same day's second paper, producing a genuinely new refinement (three separate state variables on three separate clocks: runtime state on interaction time, skill memory on an evolution-cycle counter, knowledge graph on a source-ingestion counter) that appears in neither source paper alone.

**Caveat, kept on record:** verbose, repetitive, and occasionally the presenter's own paraphrase of a formalism (e.g. the six-tuple skill definition) has not been independently checked against the paper's own notation — flagged as such in the graph (`pattern_agentic_skill_lifecycle`'s citation). The discipline that earns the listing is checking *claims*, particularly benchmark numbers and survey framing; term-level paraphrase is not yet independently verified and should be treated with the same caution as any secondary source.

**What to watch for going forward:** paper-summary videos on recent (< 2 week old) arXiv preprints in agent harness design, multi-agent coordination, and knowledge-graph/ontology engineering for AI systems. Two related videos exist in this channel's catalogue that were not analysed this session and are worth a follow-up pass: "Claude Code Improves Massively w/ 2nd Harness" and "Agentic Skills Are Becoming AI's Procedural Operating System (Google)" — the latter is Part 1 of the pair this session covered Part 2 of, and directly names the Google agentic-skills paper (`arXiv:2608.29596`) already in this project's graph.

---

## Method note: local transcript fetching

Prior to this session, YouTube's transcript panel and caption endpoints were unreachable from this environment without a signed-in session (see `docs/graph_engineering_convergence.md` §1 and `docs/sweep_2026-09-05.md` §access-table for what was blocked). The owner built `C:\Agents\skills\youtube-transcript\` — a local, no-API-key fetcher (`youtube-transcript-api` → `yt-dlp` caption parsing → local Whisper, in that fallback order) that works because it runs from a residential IP rather than a datacenter range, which is what YouTube's caption endpoints actually gate on.

All three videos this session resolved at tier 1 (direct caption API) — no video or audio was downloaded, only caption text (~35KB per video). Per standing instruction, the cached transcript files are deleted after analysis; this document and the graph nodes derived from them are the retained record. Re-fetch from the source URL if the transcript is needed again.

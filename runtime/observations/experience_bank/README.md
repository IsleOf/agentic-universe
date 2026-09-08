# Experience bank (Phase 2) — runtime artifact

Condensed workflow/step entries derived from each run's raw trace by
`experience_bank.condense`, wired into `LoopSession._write_summary` at run 369.

**Gitignored** (operating rule 9): these are derived runtime state, regenerable from
the traces. Only this README is committed. The bank's *health* is reported in
`runtime/observations/views/bank_staleness.md`.

Before run 369 this directory did not exist and the bank held 0 entries across 368
runs — Phase 2 was built, selftested against a synthetic corpus, and never called on
real data. Run 367 found the staleness view reporting that empty bank as healthy.

**Bounded by construction**: `prune(keep_n=200, grace=10)` runs after every condense,
per `concept_unmanaged_skill_libraries_silently_drift` (unbounded accumulation degrades
retrieval) and `concept_reliability_is_a_separate_axis…` (unbounded retrieval degrades
long-horizon performance).

**Write-only today.** Nothing in the live loop *retrieves* from this bank yet — the
retrieval path (`for_planning` / `for_failure`, bounded `top_k=3` since run 357) exists
and is selftested but has no live caller. Populating it makes Phase 2 real and is the
prerequisite for retrieval; it does not by itself close the loop.

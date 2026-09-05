# Live Trace Recording for the Autonomous Loop

**Date:** 2026-09-23 (autonomous run 67) · **Status:** built, selftest GREEN, first live run recorded · **Plan:** `docs/self_improving_harness_plan.md` §4 Phase 0 / Build order step 1

The adapter (run 66) replayed *recorded history* into a trace. This records a
loop run *as it happens*. `tools/loop_session.py`.

## What was built

`LoopSession` — a context manager the autonomous loop wraps its work in:

```python
import sys; sys.path.insert(0, "tools")
from loop_session import LoopSession

with LoopSession(run_no=67, increment="one line") as s:
    s.cite("2609.03035", verified=True, purpose="probe survives eval awareness")
    s.tool("arxiv_api", "sweep last 10 days", ok=True)
    s.graph_write(nodes=(175, 176), edges=(519, 523))
    s.note("what changed and why")
    s.commit("<sha>")
```

On `__enter__` it opens the run `STEP`; each call emits a Phase 0 event
(`CLAIM` with the arXiv id as evidence root, `TOOL_CALL`/`TOOL_RESULT`,
`ARTIFACT`, `NOTE`); on `__exit__` it closes the STEP, validates the trace, and
writes `runtime/observations/loop_runs/run-<N>.json` — a committed per-run
summary (the raw JSONL stays gitignored, operating rule 9).

The harness manifest (`a0a320e06a4204c4`) is stamped into every run's trace, so a
run's output is tied to the exact loop-harness state that produced it.

## SKILL.md updated

The scheduled task's `SKILL.md` now has a `RECORD THE RUN` step requiring the
`LoopSession` wrapper, between `CONVENTIONS` and `WRITE docs/auto_sweep`. Framed
as non-optional: the traces are the dataset the self-improving harness reads.

## Run 67 is the first live-recorded run

`runtime/observations/loop_runs/run-67.json`: 8 events, trace valid, 1 tool call
(graph validation), 2 artifacts (graph write + commit), 1 note, 0 citations (an
infrastructure run, no new literature). From run 68 on, every loop run leaves one
of these.

## This closes the run-66 gap

| | run 66 (adapter) | run 67 (live) |
| --- | --- | --- |
| source | `evolution_log` (post-hoc) | the run itself, as it happens |
| granularity | one STEP per run | one STEP per run + real per-action events |
| when | any time, retroactively | during the run |

Both share the seeded loop harness and the same event schema, so the replayed
history and the live runs form one continuous trace corpus.

## A Windows bug this surfaced

`Path.relative_to(ROOT)` throws when the trace dir is on a different drive (the
selftest uses a temp dir). Fixed — the summary falls back to the absolute path
when the trace is not under the repo root.

## Next

- **Phase 3 on real traces.** The proposer currently reads a synthetic
  compaction task. With `runtime/observations/loop_runs/*.json` accumulating, it
  can read real per-run outcomes (citations folded, graph delta, validation
  result) and propose a real loop-harness edit — e.g. adjust the context policy
  or the procedure prompt.
- **Phase 4 skeleton.** The workflow entries the bank holds (one per run, from
  the adapter's replay plus live runs) are the skill-induction input.

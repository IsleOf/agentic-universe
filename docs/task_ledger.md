# The deterministic task ledger

**Date:** 2026-09-06 (owner request, run 244) · **Status:** reference implementation, selftest GREEN,
**not wired into the loop** · **Tool:** `tools/task_ledger.py` · **Answers:**
`docs/practicing_what_we_preach.md` §4 ("tasks get dropped")

## Why

Two folded findings say **do not let the model hold task state in its context**:

- `concept_component_lifecycle_reasoning_degrades_with_size` (CordisBench, arXiv:2609.01600) — LLM
  reasoning about system state degrades as the system grows; an independent finite reference semantics
  matches execution on every scored outcome.
- `concept_aspire_...` (ASPIRE, arXiv:2608.31111) — continued open-ended search *erases* earlier gains;
  the loop is not monotone.

So the orchestrator reads and writes a file; the LLM proposes tasks and reports outcomes; the file decides
what is ready and what has been dropped. This is `pattern_execution_layer_enforcement` applied to task
tracking — the same reason `exec_guard` is a hook and not a prompt.

## The model

One row per task. Statuses: `pending → active → done` on the happy path; `blocked` (waiting on an external
thing), `failed` (retries exhausted), `abandoned` (deliberately dropped).

```python
from task_ledger import Ledger
L = Ledger("task_ledger.json", max_attempts=3)

a = L.add("collect the raw data")
b = L.add("clean it", deps=[a])          # b won't be `next_ready` until a is `done`

t = L.next_ready()                        # deterministic: oldest dep-free pending task
L.claim(t["id"], owner="worker-7")        # pending -> active
L.complete(t["id"], result_ref="out/a.parquet")   # active -> done

L.sweep_stale(max_active_secs=1800)       # any task claimed > 30 min ago and not finished -> pending
```

## The three anti-"dropped task" mechanisms

1. **`next_ready()` is deterministic** — the oldest `pending` task whose deps are all `done`. The
   orchestrator never has to *reason* about what to do next; it reads the answer.
2. **`sweep_stale(max_active_secs)`** — a task a worker `claim`ed but never finished (the worker died,
   lost context, or hit its budget) goes back to `pending` after a timeout instead of being silently
   lost. This is the PILOT supervisor pattern (`concept_self_improvement_should_be_live_...`): re-dispatch
   from the ledger.
3. **Atomic write + audit log** — every mutation writes the whole ledger via `os.replace` and appends a
   line to `<ledger>.audit`, so the history is inspectable and a crash mid-write cannot corrupt it.

## CLI

```
python tools/task_ledger.py add "do the thing"
python tools/task_ledger.py next
python tools/task_ledger.py claim <tid> <owner>
python tools/task_ledger.py complete <tid>
python tools/task_ledger.py fail <tid> "reason"
python tools/task_ledger.py sweep 1800
python tools/task_ledger.py summary
python tools/task_ledger.py list
```

## Using it in poly-bot / poster-studio

The ledger is a single stdlib file with no dependencies — copy `tools/task_ledger.py` into the project,
point the orchestration loop at one `task_ledger.json`, and:

- replace "ask the LLM what to do next" with `L.next_ready()`
- call `L.sweep_stale(...)` at the top of every orchestration tick
- keep the ledger in the repo (or a durable path), not in `/tmp` — it is the memory that survives a
  session boundary

## Selftest

`python tools/task_ledger.py selftest` → GREEN (12 checks). `tools/selftest_all.py` includes it.

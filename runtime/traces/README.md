# runtime/traces

Append-only JSONL event traces from swarm runs. Written by
`tools/trace_substrate.py` (`Recorder`); schema and rationale in
`docs/phase0_trace_substrate.md`.

Raw `*.jsonl` here is **gitignored** — scrubbed of secrets by the recorder, but
large and not canonical knowledge (operating rule 9). Commit summaries, derived
metrics, and pointers, not raw traces.

Validate a trace:  `python tools/trace_substrate.py validate <file>.jsonl`
Recover topology:  `python tools/topology_recover.py recover <file>.jsonl`
Phase 0 gate:      `python tools/phase0_selftest.py`

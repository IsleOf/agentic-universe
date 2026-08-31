# Agentic Universe Foundations

## Core model

`perceive → normalize state → plan/split → execute → verify → correct a bounded unit → gate → merge → derive learning constraint → next run`

A loop makes one bounded unit correct: produce, check, correct, repeat until green. A graph coordinates units: task existence, dependencies, parallelism, routing, gates, returns, and merge behavior.

## Rules

- Write an executable GREEN/RED predicate before building a loop.
- Absence of an error is not proof of correctness.
- Give workers narrow scope and isolated context.
- Use code for deterministic transforms: merge, dedupe, ranking, comparison, validation.
- Every dependency edge must carry a named artifact; remove chronological-only edges.
- Return a failed unit, not a batch; include verdict, reason, evidence, scope, and attempts.
- Escalate repeated failure to the plan/context layer.
- Gate by reversibility and blast radius; model confidence is weak, late evidence.
- Turn accepted evidence into splitter/planner constraints for future runs.

## Knowledge policy

Canonical knowledge is versioned and reviewable. Runtime traces and observations can propose graph changes but cannot silently rewrite stable knowledge.

# Session Metadata
- Approximate date: 2026-08-30 to 2026-08-31
- Primary topic: Establishing a durable Agentic Universe knowledge base and archiving project conversations without altering canonical graph knowledge
- Projects/systems discussed: Agentic Universe; loops and graphs; knowledge graph/schema; GitHub repository; Google Drive; append-only reward ledger; Polymarket bot; Poster Studio/Etsy workflow; WSL coding-agent environment
- Archive status: source material only; not canonical knowledge
- Extraction limitations: Covers the visible conversation and retained high-level project context only. It is not a full export of all historic Agentic Universe chats or runtime artifacts.

# Executive Summary
This session clarified that prior JSON artifacts were transient downloadable files rather than project-persistent knowledge. The user chose a GitHub-backed, versioned knowledge base for Agentic Universe, created the private `IsleOf/agentic-universe` repository, and committed an initial canonical graph/foundations seed. The user then established that old conversations should be saved as separate Markdown source archives under `conversations/raw/`, so they can support later analysis without directly changing `knowledge/graph/agentic_universe_graph.json`.

# Explicit Decisions and Commitments
- Agentic Universe should use an evolving knowledge schema that can change as new ideas emerge.
- GitHub is a durable, version-controlled home for the project knowledge base.
- The private canonical repository is `IsleOf/agentic-universe`.
- Raw chat archives must remain separate from canonical graph knowledge.
- Chat archives may be written under `conversations/raw/` and must not alter graph, schema, changelog, or non-conversation files.
- The user prefers low-friction approvals, while external connector writes remain subject to platform approval rules.

# Technical Context
## Local loop and graph model
A reliable loop is `produce → check → correct → repeat until green`. The check must be independently evaluable, such as a test exit status, a schema, an invariant, an expected state transition, source coverage, or a scoped-diff rule.

A graph coordinates bounded units: what work exists, dependencies, parallelism, routing, gates, correction returns, learning returns, and deterministic merging. The agreed framing is: a loop lives inside a node; a graph lives between nodes.

## Graph roles
- Splitter: decomposes objectives into bounded units, ideally along dependency, ownership, or blast-radius boundaries rather than arbitrary chronology.
- Worker: processes one narrow unit, preferably with isolated task context.
- Code node: performs deterministic transformations such as merge, dedupe, rank, compare, route, or schema validation.
- Gate: accepts, rejects, escalates, or blocks work based on evidence and consequence.

## Edge and correction discipline
Every graph dependency should carry a named output artifact consumed downstream. Chronological `and then` wording alone does not justify an edge.

A correction return targets one failed unit, not a whole batch. It should include `UNIT`, `VERDICT`, `REASON`, `EVIDENCE`, `SCOPE`, and an attempt count. Repeated failure should escalate to planning, context, split, dependency, or policy diagnosis instead of retrying indefinitely.

## Gates
Gate actions by reversibility and blast radius: contained/reversible work may be autonomous after deterministic checks; wide/reversible work needs stronger evidence; hard-to-reverse operations such as destructive production changes, migrations, money movement, credentials, or permissions remain human-gated. Confidence is a weak, late signal rather than the primary gate condition.

## Knowledge classes
- Canonical knowledge: stable concepts, patterns, constraints, components, and anti-patterns.
- Draft knowledge: candidate additions requiring evidence or review.
- Runtime observations: raw traces, tool results, failures, and corrections.
- Evaluations: tests, verdicts, rollbacks, and trajectory metrics.
- Reward/outcome evidence: append-only records of decisions, policy versions, actions, outcomes, and revisions.

# Ideas and Hypotheses
- A long learning edge can derive durable splitter/planner constraints from accepted evidence, allowing future runs to improve instead of repeating known blind spots.
- An append-only reward ledger is a proposed component for preserving outcomes and policy changes without overwriting earlier evidence.
- Bandit routing, shared learnings boards, feedback-driven policy refinement, and persistent agent handoffs are referenced project directions, but no detailed implementation or performance evidence was established here.
- The broader cognitive cycle discussed is perception → planning → execution → observation, with state normalization, structured plans, tool dispatch, result validation, and bounded reflection.

# Experiments, Results, and Evidence
## GitHub repository
- GitHub account resolved: `IsleOf`.
- Repository created: `https://github.com/IsleOf/agentic-universe`.
- Repository visibility: private.
- Initial canonical commit: `c9986bc09775fd63d038beef0b310e261dfc692d`.
- Initial committed paths stated in this session:
  - `architecture/foundations.md`
  - `knowledge/graph/agentic_universe_graph.json`
  - `evolution/CHANGELOG.md`
  - `evolution/proposals/README.md`

## Schema artifact
A file named `agentic_universe_schema.json` was generated as a transient downloadable artifact earlier in the conversation. Its durable GitHub commit was not established in this session.

## Runtime projects
- Polymarket bot: referenced as a self-learning decision-system experiment; exact implementation, capital/risk policy, deployment status, metrics, and results are unknown here.
- Poster Studio: referenced as an agent-assisted Etsy/marketplace workflow for editable poster templates; architecture, status, metrics, and outcomes are unknown here.

# Risks, Constraints, and Anti-Patterns
- A model saying it is confident is not a sufficient correctness check.
- No exception or tool error does not prove that output is correct.
- Returning an entire batch because one unit fails can rewrite correct work, introduce variance, and prevent convergence.
- Fake dependency edges serialize unrelated work and reduce available parallelism.
- Deterministic transformations should not automatically be delegated to models.
- Repeated correction requires a circuit breaker and escalation rather than unbounded reflection.
- Raw chat source material must not silently become canonical knowledge.
- Do not place secrets, credentials, access tokens, or sensitive production data in runtime traces or conversation archives.

# Open Questions and Follow-Ups
- Commit and validate a durable `knowledge/graph/agentic_universe_schema.json`.
- Add graph-validation tooling and a formal proposal/promotion workflow.
- Establish a directory and ingestion process for raw historical chat archives.
- Decide how runtime systems emit observations, evaluations, traces, rewards, and policy-version data.
- Define evidence thresholds for draft-to-stable graph promotions, conflict handling, deprecation, rollback, and human gate policy.
- Decide what real agent/service/CI process, if any, converts archived source context into reviewed draft knowledge proposals.

# Verbatim Technical Artifacts

## Foundational execution model
```text
perceive → normalize state → plan/split → execute → verify →
correct a bounded unit → gate → merge → derive learning constraint → next run
```

## Loop definition
```text
produce → check → correct → repeat until green
```

## Check examples
```text
GREEN    the test suite exits 0
GREEN    every claim carries a source line
GREEN    the diff touches only files listed in the plan
NOT A CHECK   the output looks good
NOT A CHECK   the model says it is confident
NOT A CHECK   no errors were raised
```

## Correction payload
```text
UNIT      handlers slice
VERDICT   red
REASON    test_auth_redirect failed
EVIDENCE  expected 302, got 200, handlers/auth.py:88
SCOPE     fix this file only, do not touch other slices
```

## Learning-edge example
```text
ACCEPTED   utils slice ported, green on first pass
DERIVED    adapters preserve keyword args exactly
LANDS IN   the splitter's brief for every later slice
```

## Canonical graph path
```text
knowledge/graph/agentic_universe_graph.json
```

## Raw conversation archive convention
```text
conversations/raw/YYYY-MM-DD_short-topic.md
```

## Repository and commit
```text
https://github.com/IsleOf/agentic-universe
c9986bc09775fd63d038beef0b310e261dfc692d
```

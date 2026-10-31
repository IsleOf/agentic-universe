# Agentic Universe — Collaborator Handover

**Canonical repository:** `IsleOf/agentic-universe` (private)
**Canonical local path:** `C:\Agents\agentic-universe\repo`
**Prepared:** 2026-10-31
**Purpose:** safe starting point for an agent or collaborator; verify live state before acting.

## Mission

Maintain a versioned, evidence-aware knowledge graph and research/tooling programme for emergent agent behaviour and self-improving agent systems. The repository is the canonical source for its own knowledge and code; runtime outputs are evidence/proposals, not authority to silently rewrite stable knowledge.

## Start here (in order)

1. `README.md` — scope, conventions, layout, existing workflow.
2. `PROJECT_MAP_2026.md` — subsystem orientation; treat dated operational facts as stale until checked.
3. `STATUS.md` and `orchestration/STATUS.md` — snapshots only; refresh from live state before claims.
4. `knowledge/graph/agentic_universe_graph.json` — canonical research graph.
5. `tools/README.md` — toolchain map.
6. `docs/what_would_make_this_wrong.md` — adversarial counterweight.
7. `docs/source_register.md` — evidence and attribution status.
8. `handover/github/AGENTIC_UNIVERSE_HIGH_LEVEL_GRAPHRAG.json` — compact orientation graph.

## Invariants

- Never promote an unverified source, model output, or prior-session assertion to a finding without evidence and review.
- Preserve competing mechanisms and counterevidence; use explicit `challenges` relationships where appropriate.
- Keep secrets, credentials, personal data, and raw session state out of GitHub. Never commit OAuth tokens, client secrets, cookies, API keys, or user history.
- Do not target `main` directly. Work on a task branch, inspect the diff, validate, test, and request review.
- Do not change Poster Studio or Polybot implementation directly; this repository may contain boundary/reliability recommendations only.
- Treat cron/watchdog state, Aether availability, and dated status reports as volatile. Read live source-of-truth state before routing or reporting.
- Google Data Portability is not complete unless the exact OAuth/scopes/API gates are independently verified. Workspace OAuth is separate. Never claim personal history ingestion from browser navigation.

## Safe takeover workflow

```bash
git status --short --branch
git remote -v
python tools/knowledge_graph.py validate
python tools/selftest_all.py
python tools/google_connection_graphrag.py validate
python tools/google_connection_graphrag.py selftest
python tools/dynamic_tasks_graphrag.py validate
```

Then inspect the active queue and live cron state, identify one highest-priority unmet item, create a branch, and record evidence. Use focused tests before full tests. Run `git diff --check` and inspect staged files for secrets/raw traces before any commit. Never stage the whole worktree without reviewing `git status` and ignore rules.

## Current verified handoff facts (2026-10-31)

- The repository is private and the authenticated GitHub identity has Admin permission.
- The current local branch is `proposals/2026-09-01-emergent-behaviour-cluster`, with 12 commits ahead of its origin tracking branch and substantial uncommitted/untracked work. Do not push this working tree wholesale or assume it is review-ready.
- The baseline README describes the graph/toolchain and its validation commands; its counts and status are dated and should be refreshed before quoting.
- The Google connection GraphRAG validates and its selftest was last observed green at 24 nodes/24 edges. The Workspace token check returned `TOKEN_REVOKED`; no Drive write access is verified.
- Google Drive upload remains blocked until a valid, least-privilege upload authorization is established. Do not ask for passwords, tokens, OAuth codes, or 2FA values in chat.

## Collaboration contract

Every change should state: intent, evidence/source, files changed, tests run with exit codes, remaining uncertainty, and rollback/recovery. Prefer small commits. Preserve identifiers and provenance. Agents must not treat this handover or the high-level graph as a substitute for reading the underlying design, tests, and current source.

## Task routing

- Research model/claims → `knowledge/graph/`, `docs/`, `docs/source_register.md`.
- Tool implementation → `tools/`, paired tests, `tools/selftest_all.py` integration if appropriate.
- Google OAuth/history → `docs/google_connection_graphrag.md`, graph gate, `skills/productivity/google-data-portability/SKILL.md`; no secret handling.
- Dynamic cron/watchdogs → `knowledge/agentic_universe_dynamic_tasks_graph.json`, `tools/dynamic_tasks_graphrag.py`; refresh from live `jobs.json` before acting.

## Completion bar

A task is complete only when acceptance criteria are explicitly verified, tests pass, external writes are read back, and the handover/status record points to concrete evidence. If blocked, leave the blocker visible; do not fabricate state or silently substitute a different project/session.

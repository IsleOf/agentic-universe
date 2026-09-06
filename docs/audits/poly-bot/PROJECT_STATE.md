# poly-bot — Project State (first-pass audit)

> **This is a FIRST-PASS audit by the Agentic Universe loop (run 317)**, built 2026-09-07
> from `/home/dev/poly-bot`: `README.md`, `docs/agent_handover/CURRENT.md` (rewritten
> 2026-08-08), `docs/agent_handover/status.md` (current), the git log, and the package
> READMEs. **The EV Hunter task specifics and the sign-off-queue state need the active
> session on that repo to reconcile** — the `question` nodes in
> `poly-bot_project_graph.json` are the placeholders for that. Copy both files into
> `poly-bot/knowledge/graph/` and `poly-bot/docs/` once the active session has verified
> and filled them.

## What it is

A Polymarket prediction-market **paper-trading** research system, pre-PnL by design.
Strict split:

- **Local (WSL2 box):** research, backtests, agent orchestration. **Never contacts
  Polymarket** (geo/Cloudflare ban risk) — the non-negotiable boundary, enforced by
  `harness.source_boundary_check` + `docs/BOUNDARIES.md`.
- **VPS (Contabo, France):** all Polymarket I/O, data collectors, the live paper pipeline,
  the Tailscale-bound dashboard (`:8080`). Reached from local only over sanctioned
  Tailscale SSH.

North star: `docs/STRATEGIC_PLAN.md` (5 phases toward autonomous multi-venue trading).

## Current state

**The 2026-07 honest-cost audit is the defining event:** zero of ~477 routes had validated
edge under honest costs (n≥100, ROI>0, t≥2); the 49 "EVIDENCE_POSITIVE" routes were
phantoms (a rotated journal consumed mid-count). Passive market-making, OBI-as-taker,
whale-copy, lead-lag, settlement-gap and stale-quote pick-off were all subsequently
**killed with artifacts**.

**Since ~2026-08 the focus has pivoted to EV Hunter / Event Desk** — a model-aware VPS
deep-research timer that mechanically preselects sports/esports market candidates, runs
bounded multi-step research, and feeds an overlay/event-cluster selection path. `CURRENT.md`
predates this pivot; `EV_HUNTER_TASK_CHECKLIST.md` is the live task list.

**Orchestration:** a 20-minute checklist-watchdog cron dispatches one queued task per tick
to a local AGY worker fleet (tmux `agents` session). As of 2026-09-07 the queue had ~39
unchecked items, **all carrying external blockers** — mostly `BLOCKED-ON-DATA` or
`BLOCKED-ON-MACHINE-STATE`.

## The single highest-value next move

**Fix the AGY worker fleet's recurring WSL `p9_client_rpc` D-state hang** (or accept and
formalise "restart WSL" as the recovery). Every queued task backs up behind it, and
`checklist_worker_recovery.py`'s `--noprofile --norc` workaround handles the profile hang
but not the D-state. The Agentic Universe audit kit (`docs/project_audit_kit/`) ships
`task_ledger.py` + `supervisor.py` for exactly this: a deterministic ledger whose
`sweep_stale()` returns a hung worker's task to `pending`, and a supervisor that aborts a
drifting worker (cf. `task-330`, which cProfiled the production paper writer). Drop those
two files in and wire the watchdog to them.

## Hard constraints

- Local must not contact Polymarket (CLOB/REST/WebSocket).
- Never write secrets / tokens / keys / cookies / full IPs / raw `.env` to any repo note.
- Live-path changes are gated — `agent_gate.py` blocks the commit without a human approval
  token (applies to `strategy_configs.json` inserts **and** any change to the entry gates).
- Both live paths hard-block taker entries in price range **[0.40, 0.60]** — any strategy
  whose entry range overlaps this produces **zero fills** unless the named route is
  explicitly exempted (a gated code change).
- VPS root disk is a standing budget (~77 % used, ~17 GiB free) — a rotated 7 GB journal
  caused a live halt in July.

## Open questions (for the active session)

1. **Current focus** — is the live strategy line FLB-fade or the EV Hunter Event Desk?
   `CURRENT.md` and the git log disagree; `CURRENT.md` §1–2 needs rewriting to match.
2. **FLB-fade sign-off (item 5f)** — does spec v3 exist, and does it fold in the
   [0.40,0.60] gate exemption, the `route_state_seed.py` requirement, the market-level
   (dedup) `t` vs the fill-level `t`, the unvalidated LOW-vol gate, and the §9 correction
   (the change **is** gated)?
3. **Worker fleet** — permanent fix for the D-state hang, or is "restart WSL" the accepted
   recovery? Does the watchdog do stale-task recovery, or do dropped tasks just sit?
4. **BLOCKED-ON-DATA items** — what data unblocks `task-275` (overlay temporal audit — all
   cohorts open, 0 resolved) and `task-261` (haircut n≥100)?
5. **Sign-off queue** — which `SIGNOFF_QUEUE_2026-07-14` items has the user actioned
   (5e symbol kill-list, 4/4b disk fix)?

## What would make this wrong

- **The pivot may be further along than the docs show.** The git log is all `ev_hunter` /
  `task-3xx` / deep-research; if FLB-fade is fully shelved, nodes `polybot__strategies` and
  the FLB bug/question nodes are historical, not live.
- **The D-state hang may already be fixed.** `status.md` entries after 2026-09-07 (not read
  here) could resolve it.
- **`CURRENT.md` §3 "Live system state" is dated 2026-07-16** — the collectors / route
  counts / disk figures here may all have moved.

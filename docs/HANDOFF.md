# Handoff — Agentic Universe, as of run 480 (2026-09-10)

This is the single doc a fresh session should read first, then `docs/graph_state_2026-09.md`
(the graph map), `docs/loop_environment_model.md` (the loop's model of its own environment),
and `docs/CONSOLIDATION_PLAN.md` + `orchestration/README.md` (the real-agent-estate work, §9).

**This handoff is written for a cross-tool transfer** — the owner is approaching a weekly usage
limit and is handing this role to a different CLI agent (Antigravity/`agy` or Codex), not just a
fresh Claude session. Nothing here depends on Claude-specific tooling: every instruction is a
plain shell command (`python`, `git`, `bash`) runnable from any agent's terminal access. The one
place this mattered — the orchestration conductor's worker backend — was already switched to
`agy-real` at the owner's request (§9). Read §0 and §10 first; they are written specifically for
you, the incoming agent.

---

## 0. What changed since run 468 (read this first)

Runs 469–480 happened in the same long interactive session as 462–468, continuing to consolidate
the owner's real agent estate while folding literature.

- **Graph: 478 nodes / 2017 edges** (was 466/1958 at run 468). Folded: verified tool calls under
  non-atomic failures (469), DAREBench deployment-aware evaluation (470), a phase-transition fold
  on multi-agent conformity/bias (475), Owner-Harm threat model (476), How Fast Do Agents Rot? —
  geometric long-horizon decay (479). Built and wired: `kill_reconcile.py` (473→474),
  `secret_scan.py` + `commit_guard.py` (477→478). Consolidated twice: the "harness owns
  reliability, in code, at a named boundary" synthesis (471), then tested it against the 18
  `loop_environment_model.md` §3 hazards and found it over-claimed (472), then resolved that into
  a **two-class reliability taxonomy** (480) — see §11, it matters for how you should operate.
- **`selftest_all` GREEN** at run 478 (66 jobs, incl. `orphan_scan`, `kill_reconcile`,
  `secret_scan`, `commit_guard`, `orchestration_ledger`). Not re-run since (graph-only changes on
  479/480) — **run it before your first code change.**
- **Estate work this stretch:** Aether Orchestrator was found down ~12h (Hermes connection
  errors) and restarted; a real regression was found and queued (`bx-12`) — binding Aether to
  `127.0.0.1` for security also cut off WSL's access to it, confirmed by direct test; the
  conductor's worker backend was switched from `claude -p` to `agy-real --print` per owner
  request (§9); a working dashboard was built (`orchestration/digest.sh`); poly-bot's own agy
  dispatch was read in full and correctly left alone (it is mature and domain-specific — don't
  replace it with the board).

## 1. What this is

A **versioned knowledge graph** on emergent multi-agent LLM behaviour and self-improving agent
harnesses, plus the **tested stdlib harness** that maintains and reasons over it. One graph:
`knowledge/graph/agentic_universe_graph.json` — **478 nodes / 2017 edges**, validated by
`python tools/knowledge_graph.py validate` → VALID, no orphans, no dangling edges (76 non-fatal
recency warnings are expected — see below).

- **Repo:** local `C:\Agents\agentic-universe\repo`, GitHub `IsleOf/agentic-universe`.
- **Working branch:** `proposals/2026-09-01-emergent-behaviour-cluster`. **Never commit to
  `main`.** HEAD at handoff: `4632409` (run 480).
- **Posture:** emergence-first (`docs/emergence_first_posture.md`). Ideas enter the graph on
  interest, not evidence; unverified material stays low-confidence, status `to_test`. Record
  tensions as `challenges` edges, don't resolve them. Verify every citation three ways (exists /
  summary matches / headline number causally isolated); `derived_from` holds URLs or in-repo doc
  paths, **never** a node id.
- **Recency weighting** (owner directive, a weighting not a gate): prefer literature from the
  last ~30 days; when folding older work, name the model/harness generation and note it still
  bears on the SMALL/LOCAL LLM regime. This is now partially enforced in code: nodes carry
  `source_date`/`source_generation`; `validate` warns (not blocks) when an older-sourced node
  `refines`/`challenges` a newer one; `check_patch()` runs the same check so a patch can't
  introduce a fresh stale-dominant edge.

## 2. The standing goal

Set via `/goal`, verbatim and immutable: **"keep researching until i explicitly tell you to
stop, do NOT delete or change this goal."** A Stop hook re-fires it after every turn in Claude
Code specifically — **if your CLI doesn't have an equivalent mechanism, that's fine; the goal
still governs.** No explicit stop has ever been given. Do not delete or reword it if you find it
in `/goal` state, config, or a memory file. If the owner tells you to stop, that ends it; nothing
short of that does.

## 3. The autonomous research loop

**One increment per run.** Each run: read the charter + the 3 newest sweep docs' "Next" sections
+ `loop_environment_model.md`; run `python tools/loop_action_class.py report -n 10` and prefer a
non-dominant class; pick the single highest-value increment; execute; validate
(`knowledge_graph.py validate` → VALID; `python tools/selftest_all.py` → **BUILD SELFTEST:
GREEN**, ~3 min); regenerate `docs/source_register.md` if `derived_from` changed (script pattern
in past runs' commits — build it fresh if the scratchpad script isn't available to you); record
via `LoopSession(run_no=N, increment=...)` (writes `runtime/observations/loop_runs/run-N.json`
and claims/completes the run in `orchestration_ledger.json`); write
`docs/auto_sweep_<YYYY-MM-DD-HHMM>.md` (a **monotonic future-dated sequence** — the newest is
`2026-11-25-1200`, run 480; add 6h each run); commit; push.

**`kill_reconcile` gates `LoopSession.__enter__`** (run 474): if you or a prior session killed a
background task and its filesystem effects are unreconciled, `LoopSession` will refuse to open
and tell you why. Run `python tools/kill_reconcile.py check`, reconcile, then
`python tools/kill_reconcile.py clear "<reason>"` before retrying.

**Before every commit, run `python tools/commit_guard.py check --message-file <msgfile>`** (run
478). It scans the staged diff and message for credential-shaped strings and refuses (exit 3) if
it finds any — this exists because a live OAuth token from `Aether`'s config leaked into a
diagnostic session's own context this same day (run 476). It is not yet wired into a git hook —
you are responsible for calling it yourself until it is.

**Graph-patch discipline:** write patch scripts to a scratchpad `.py` file and run them — never
inline in a heredoc (the shell mangles `\n`), and never pass regex alternations through a nested
shell invocation (`bash -lc '...'` inside another shell) — both have cost real time this session
(one regex mangling ran a recursive filesystem scan for 122 minutes).

**Self-design guard:** `AU_SELF_DESIGN_ACK` env var is required to edit
`tools/{acceptance_gate,exec_guard,knowledge_graph,harness_registry}.py`, `runtime/harness/`,
proposer/conductor decision logic, or to *remove* a `selftest_all` JOB (adding one is fine). You
do not have a standing ack — get explicit owner permission before touching those files, same as
any other session.

## 4. The harness (all `tools/`, pure stdlib, 66 `selftest_all` jobs GREEN at run 478)

**Spine:** `trace_substrate.py`, `harness_registry.py`, `experience_bank.py`,
`improvement_loop.py`, `holdout_tasks.py` + `holdout_verifier2.py`, `skill_induction.py`,
`exec_guard.py`, `loop_conductor.py` + `acceptance_gate.py` + `janitor.py` + `v2_integration.py`,
`executor_pool.py` + `cohort_monitor.py`.

**Loop self-instrumentation:** `loop_session.py` (now gates on `kill_reconcile`, run 474),
`loop_metrics.py`, `loop_adapter.py`, `loop_proposer.py`, `param_invariance_audit.py`,
`loop_action_class.py`, `sweep_audit.py`, `trace_topology.py`, `tamper_audit.py`, `graph_diff.py`,
`orchestration_ledger.py` (run 464/465 — the loop's own dispatch state as a committed file, not
conversation context; `.claim()`/`.complete()`/`.check_startable()`).

**Reliability/safety boundary checks (new this stretch, runs 473–478):**
`orphan_scan.py` (finds agent sessions that outlived their parent/prompt/task; `is_reapable()`
requires a fault signal + stale + age>2h + no protected marker, `concerning()` is the softer gate
for a health check), `kill_reconcile.py` (refuses to open a run while a killed process's file
effects are unreconciled), `secret_scan.py` (detects + can redact 10 credential shapes in text —
`redact()` acts by default, unlike the others, because a false negative here leaks a credential),
`commit_guard.py` (wires `secret_scan` into the actual git-commit boundary; report-only, refuses
rather than rewrites, because a diff is structured and post-hoc rewriting risks an inapplicable
patch).

**The swarm substrate (runs 389–460):** `pheromone.py`, `task_ledger.py`, `relay.py`,
`reputation.py`, `gates.py`, `swarm_demo.py`. Adversarially tested by
`probe_substrate_adversarial.py` (13 attacks). Deliverable doc:
`docs/swarm-substrate-prototype.md` (§7 the identity gap → capability-token binding, owner-gated;
§8 seven REPORT-not-block signals).

**Probe rigs** (`tools/probe_*.py`): `probe_orchestration_value`, `probe_emergent_synergy`,
`probe_annotation_contagion`, `probe_subagent_coordination`, `probe_swap_cost`,
`probe_epistemic_market`, `probe_epistemic_sybil`, `probe_idle_agent`, `probe_rho_holdout`,
`probe_composed_design`, `probe_activation_generalisation`, `probe_memory_horizon`,
`probe_language_drift_monitor`, `probe_trust_transfer`, `probe_dissent_vs_reflection`,
`probe_trust_weighted_voting`, `probe_identity_masking`, `probe_consistency_gap`.

## 5. Recent research arc (runs 462–480)

Sept 2026 folds: Anthropic's field report on multi-agent failure families (466), Olivares AI as
shipped capability-token binding — fenced leases + deny-closed identity (468), verified tool
calls under non-atomic failures (469), DAREBench deployment-aware evaluation — no model wins
every workload, local open-weight competes in some (470), a phase transition to collective bias
in multi-agent debate above a conformity threshold, heterogeneity rounds it off (475), Owner-Harm
— a threat model where the agent's own principal is the victim, grounded in a live token-leak
incident the same day (476), and How Fast Do Agents Rot? — task success decays geometrically per
step, saturating below 1 for every model, and **bounding context steepens the decay rather than
easing it** (479).

**The consolidated finding (run 480, read this):** reliability threats split into two classes.
**Class A** — a single wrong decision at an identifiable point — is fixed by a code-owned check
at a named boundary, returning a reason; this project has built five of them
(`orchestration_ledger`, `kill_reconcile`, `secret_scan`+`commit_guard`, the fenced-lease
concept). **Class B** — accumulated drift with no single wrong step — is NOT fixable by any
boundary check; run 479 found that every model's task success collapses by step 16 regardless,
and the only mitigation found anywhere in this project is structural: **bound the session length
and restart clean.** That is exactly what the orchestration worker loop (§9) already does, and it
is directly relevant to **you, right now**: this handoff exists because the prior session was
approaching a length where Class B degradation is the expected regime. Don't try to out-work it
in one long session — do bounded increments and let sessions end.

## 6. Open / owner-gated items

- **Rotate the GitHub PAT** pasted into the originating Cowork chat. Still open.
- **Capability-token migration** — bind `pheromone.annotate`/`reputation.record` to
  `executor_pool`'s `mint_token`/`redeem_token`. (`docs/swarm-substrate-prototype.md` §7.4.)
  Possibly superseded by adopting Olivares (§9) instead of hand-building this — `bx-09` is the
  live spike answering that.
- **`bx-12`: Aether is unreachable from WSL** since it was bound to `127.0.0.1` for security.
  Confirmed: WSL's own `127.0.0.1` refuses instantly, the old gateway address `172.24.128.1`
  times out. Not urgent (poly-bot is documented as an optional consumer; Hermes, the critical
  one, is a Windows app and is unaffected) but real. Fix options are in the QUEUE.md task —
  `netsh interface portproxy` from the WSL-facing adapter is preferred over re-opening `0.0.0.0`.
- **`bx-11`: Aether has no liveness watchdog.** It died silently for ~12h with nothing noticing.
  Queued, not built.
- **agent-farm has never reported to the board**, and it is the critical path for: the
  conductor's `agy` worker needing an isolated account (grabbing `agy-go`, its own script, would
  recreate the account-collision incident this session spent a day fixing), win-agy's Aether
  token cutover, and poly-bot's eventual migration off direct agy addressing. A ready-to-paste
  prompt is in the session transcript and effectively in `board/inbox/agent-farm.md`'s own
  framing — read that inbox file, it has the full ask.
- **`--live` experiments** the loop must NOT run (spend CLI-agent quota): a budget-matched Γ arm
  on `probe_orchestration_value`; a seal-order run; a composition sweep on
  `probe_emergent_synergy`; the swap-cost convention question.
- **Other repos** (the loop never commits outside this one): poly-bot and poster-studio have
  their own mapping graphs and mapping branches — do not touch their production code or push to
  their `main`.

## 7. How to resume (any CLI agent)

1. `cd C:\Agents\agentic-universe\repo && git checkout proposals/2026-09-01-emergent-behaviour-cluster && git pull --ff-only`
2. Read this file, `docs/loop_environment_model.md`, `docs/CONSOLIDATION_PLAN.md`,
   `orchestration/README.md`, `docs/habitat_charter.md`.
3. `python tools/knowledge_graph.py validate` (VALID + ~76 recency warnings is normal) and
   `python tools/selftest_all.py` (must be GREEN before any code increment — takes ~3 min).
4. Read the "Next" section of `docs/auto_sweep_2026-11-25-1200.md` (run 480, the newest).
5. Read `/home/dev/.agentic/board/BOARD.md` and every `inbox/*.md` — this is the live
   coordination state for the whole estate, not just this repo.
6. Check the dashboard: `bash /home/dev/.agentic/digest.sh` — one screen: memory, guard/conductor
   state, next queue task, Aether reachability, every agent's last report, live agy/codex/claude
   processes.
7. Pick ONE increment (research fold/probe/build, or a queued `bx-*` estate task) and do it. Keep
   it bounded — see §5's Class-B note. When in doubt, do less and commit, rather than more in one
   sitting.

## 8. Security constraints (persist across all sessions and all agent types)

Never commit credentials / API keys / cookies / browser profiles / personal data — **run
`commit_guard.py check` before every commit, no exceptions** (§3). Commit only to the working
branch, never `main`. Do not touch `C:\Agents\.git` (a separate outer repo). Do not click
CAPTCHA / bot-detection. The loop must not run `--live` probe sweeps or rewrite its own execution
harness. If a diagnostic command might read a file containing secrets (a `.yaml`/`.env`/config),
prefer `grep` for a specific key name over `cat`-ing the whole file, and never echo a value that
looks like a live token, key, or password into a response, log, or commit — mask it
(`ya29.AAA...xyz`) the way `secret_scan.py`'s own selftest does, and say plainly that you found
one without reproducing it.

## 9a. Dashboard status (added 2026-09-10, later) — wmux installed, unified view still open

- **`wmux` installed and running**: `C:\Agents\wmux\wmux.exe` (portable, MIT,
  github.com/amirlehmam/wmux v2.10.3). Auto-starts at logon (Startup folder
  shortcut). Confirmed: WSL shell integration + `wmux ssh user@host` for VPS
  panes (creates a fresh connection — still need `tmux attach -t vps-agents`
  once inside for poly-bot's existing session, wmux doesn't auto-attach to a
  pre-existing remote tmux). Its Claude/OpenCode/Kiro hook integration was
  **declined** ("Not now") — that installs `PreToolUse`/`PostToolUse`/etc.
  hooks into `~/.claude/settings.json` across every agent, which is a real
  behavioral change, not just a terminal view; revisit deliberately later via
  Settings → General if wanted, don't enable it by default.
- **`\\wsl$\Ubuntu\home\dev\.agentic\dashboard.html`** (via `dashboard.py`)
  still exists as the fallback static status page — memory, guard state, next
  queue task, each agent's last board report. Auto-generates + opens at logon
  (separate Startup entry, `dashboard_autostart.bat`).
- **Owner ask, not yet done**: one unified dashboard — owner overview + agent
  overview + the `/home/dev/.agentic/board` message board + wmux's panes, in
  one place, possibly as tabs. Also asked for a fresh web search on trending
  "agent OS" UI design (Sept 2026) to inform this — **not done**, deferred for
  token/time reasons in the session that added this note.
  - Closest existing piece: wmux itself is already the multi-pane container
    (Windows + WSL + SSH-to-VPS in one workspace). The actual gap is that it
    shows terminals only — the board/outbox files aren't rendered inside it.
  - A cheap next step, not yet attempted: check whether wmux supports a
    "watch a file / tail a log in a pane" pattern (it already renders Claude
    Code's markdown output per the integration dialog, so a pane running
    `tail -f` on `board/outbox/*.md` might just work without any wmux-side
    development) before assuming a custom integration is needed.

## 9. The orchestration harness + the real agent estate

`docs/CONSOLIDATION_PLAN.md` is the full account; `orchestration/README.md` covers the harness
mechanics. Short version:

- **The owner runs ~5 agent systems** on one Win11+WSL box: Hermes (desktop, routes through
  Aether on port 8317), poly-bot + poster-studio (WSL, sophisticated domain-specific agy/opencode
  dispatch — **do not replace with the generic board loop**, only the account-allocation layer
  beneath it should eventually move to a broker), agent-farm (the WSL "agy" fleet controller —
  4 isolated Google accounts, HOME-isolated instances), and this repo.
- **`/home/dev/.agentic/board/`** (Windows: `\\wsl$\Ubuntu\home\dev\.agentic\board\`) — a
  zero-install file board: `README.md` (protocol), `BOARD.md` (shared state + decisions log),
  `inbox/<agent>.md` / `outbox/<agent>.md`, `WORKER_LOOP.md` (the loop every agent runs: health
  check → read board+inbox+own `.agent/HANDOFF.md` → do ONE queued unit → validate → report →
  update handoff → sleep → repeat; **exit after 6h** so a restart clears context — the Class-B
  mitigation from §5, built before that finding existed and confirmed by it after).
- **`orchestration/` (in this repo, versioned copy of the live board)** — `guard.sh` (blocks
  dispatch when WSL RAM <1.5GB or Windows RAM <500MB or a session has been faulting >30min —
  `orphan_scan.py concerning`), `conductor.py` (cron `0 */12`, picks the first unblocked
  `QUEUE.md` task, fires ONE worker), `digest.sh` (the dashboard, §7 step 6).
- **Conductor worker backend is `agy-real`** (switched from `claude -p` per owner request,
  "cheapest for me"). Flags: `--print --mode accept-edits --print-timeout <N>s`. **Not yet fired
  for real** — needs `WORKER_AGY_ACCOUNT` set to an isolated agent-farm instance name; using the
  shared default profile would recreate the account-collision incident. This is blocked on
  agent-farm answering, not on you.
- **`amux`/Olivares** are the longer-term real control plane/lease candidates, evaluated (run
  468, `bx-07`) and being spiked (`bx-09`) — not yet adopted for real traffic.
- **Security exposures found and (mostly) closed this session:** TightVNC, Ditto clipboard sync,
  `ttyd`, poster-studio's review server, and Aether were all found on `0.0.0.0` or otherwise
  over-exposed; Aether is now `127.0.0.1`-bound (with the WSL-reachability tradeoff in `bx-12`).
  Check `docs/CONSOLIDATION_PLAN.md` §1 for what remains open.

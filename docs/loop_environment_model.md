# Loop Environment Model

> The loop's **world model of its own environment** — the current account of how each kind of
> increment changes the graph, the metrics, and the frontier. Introduced run 421 after folding
> Belief-Calibrated Optimization (arXiv:2609.01861): a scaffold-optimiser's belief about "how the
> environment responds to edits" should be **written down and continually revised**, not left
> implicit in each run's reasoning and scattered across 400+ sweep docs.
>
> **Maintenance:** every run that lands a finding about *how the loop's environment behaves*
> (not about the research subject) revises the relevant line here. This document is
> `PORTABILITY_CLASS: fixed-schema` in spirit — prose, no model-coupled compression — so it
> transfers across a model swap (BCO's own result).
>
> **Scope note:** this is a belief, not a law. Numbers are rough central tendencies over the
> window 382–460, and the sample is one model family on one task.
>
> **Revisions:** run 421 (introduced), 422 (verified-fraction erosion), **461** (runs 428–460 —
> the swarm-substrate arc + follow-on threads; §2 gains the legibility-floor and `sweep_audit`
> lines, §3 gains 5 hazards, §5 checks the model's own predictions).

---

## 1. The action space (from `loop_action_class`, run 408)

| class | what it is | typical graph delta | when it's the right call |
|---|---|---|---|
| **fold** | fold external literature into the graph | +1 node, +5–7 edges | frontier has a fresh paper that connects to ≥3 existing nodes; `novelty` recovering |
| **probe** | build/extend a runnable rig, measure something | +1–2 nodes, +4–7 edges | a fold left a falsifiable gap ("does X actually happen in *our* substrate?") |
| **build** | ship a new tool / capability | +1 node, +5 edges, +1 selftest job | a probe or design named a missing piece; owner-blessed direction |
| **fix** | repair a bug or a broken instrument | +1–2 nodes, +5 edges | a probe / consolidation / regression surfaced a defect |
| **consolidate** | consistency pass, red-team, audit, synthesis, negative result | +1–2 nodes, +3–6 edges | `acts <class>` has shown one class ≥50% for ~5 runs; a deliverable is stale; a "felt pattern" needs checking before acting on it |

**Observed mix over 382–421:** roughly fold 35% / probe 20% / build 20% / fix 15% / consolidate
10%. `loop_action_class` flags a **monoculture** at ≥70% one class over ≥6 runs, or ≥4 identical
in a row. The status line shows `acts <dominant><pct>` every run.

---

## 2. How the environment responds

### Graph
- **Every run adds ~1.2 nodes and ~5.4 edges.** A run adding 0 nodes is rare and usually a pure
  consolidation; a run adding ≥3 is usually a fold that touched a hub node plus a derived
  finding.
- **Edges matter more than nodes.** The high-value folds are the ones that produce
  `challenges` / `constrains` / `refines` edges to *existing* nodes — that's where the graph
  stops being a pile of summaries and starts being an argument. A fold that only adds a node and
  a `supports` edge to one other node is low-value.
- `knowledge_graph.py validate` → VALID, no orphans, no dangling: this has held every run for
  ~40 runs. A patch that breaks it is always a scripting error (heredoc quoting, a wrong id),
  never a real graph problem — fix the script, re-run.

### `novelty` (from `loop_metrics`)
- **Recovers on a fold**, especially a fresh-axis fold: 0.8–1.0.
- **Decays on consecutive same-thread runs**: 3–4 probe/build runs on one topic drop it to
  0.33–0.44, and the metric flags `!` below ~0.4. This is a *reliable early signal that a thread
  is exhausted* — run 383 concluded "seam exhausted" at 0.40 and run 384's fold (which the seam
  had *under-measured*, not exhausted) recovered it to 0.44. So: `novelty` low = "vary the
  thread OR measure the current one better", not necessarily "abandon it".
- A pure consolidation run holds `novelty` roughly flat (it's a look, not a new claim).

### `verified-fraction`
- Drifted **down** 0.90 → 0.83 over runs 382–421. **Run 422 found the cause and it was not what
  this line first said:** it was `_autocite_from_increment` recording every arXiv id *mentioned*
  in the increment prose — cross-references to prior folds — as `verified=False`. A run that
  already cites its real source explicitly does not need its cross-references counted as
  citations. Fixed run 422: the auto-extractor now only fires when the run made **no** explicit
  `cite()` call (its original run-334–360 purpose). Prediction: `verified-fraction` stabilises
  near 0.85–0.90 and stops the ~0.0015/run drift.
- The remaining genuine gap — abstract-reads never upgraded to full-reads — is real but small;
  a `citation upgrade` run (fetch the arXiv page, confirm the headline number) is the
  counterweight if the fraction still drifts after run 422.

### `legible` (self-report legibility)
- Held at **1.00** for ~80 runs. The one persistent legibility risk is nested-lambda selftest
  checks and brittle exact-equality assertions — runs 380 and 386 both traced defects to
  "intentional and accidental equality are indistinguishable by reading". Mark intentional
  equality, and prefer structural claims (an ordering, a floor) over guessed constants.
- **`legible` (and `trace_legibility`) is a FLOOR, not a monitorability measure** (run 456,
  arXiv:2609.04194). An illegible trace is definitely not monitorable, so the metric earns its
  place; a legible one does not mean the causally-important steps are visible. Never read a high
  value here as "the loop is interpretable/monitorable" — only "the record explains itself."

### `sweep_audit` (self-audit, added run 442, in `status_line` from run 453)
- The loop now audits its own sweep docs: **sufficiency** (every headline claim names a backing —
  arXiv id / file / selftest / node id), **coverage** (this run addressed a prior Next bullet or
  stated a pivot), **refix** (a "fixed X" claim was re-measured somewhere). Rendered as
  `audit ok` / `audit suf!cov!refix!`. Real corpus reads clean.
- Wiring it into `status_line` (run 453) immediately caught a `coverage_check` false positive —
  the same run-367 lesson: **a check that does not reach the display is a check the loop never
  acts on, and surfacing it is also how you find the check's own bug.**

### `param_invariance_audit`
- A new module is flagged the moment its selftest exercises a size-like parameter at one value.
  **Sweep `range(2, 16)` or a `for n in (8, 20, ...)` loop in every new selftest from the start**
  — retrofitting it is the run-385/386/387 tax. `pheromone.py` (run 390) was the first module
  built clean by this rule; every module since has followed it.

---

## 3. Recurring environment hazards (each cost a run to learn)

| hazard | first seen | the rule it produced |
|---|---|---|
| an absolute threshold vs a pool-sized sum | run 385 (`cohort_monitor` aborted on noise at k=20) | a threshold on an aggregate is a function of every parameter the aggregate depends on; scale it, don't fix it |
| an instrument returning a confident value while measuring nothing | runs 361–368, 385–386, 388, 406, 410 (**≥8 instances in the loop's own code**) | an instrument that can't measure its input must SAY SO, not return a plausible number |
| the fix for a defect carrying the defect | runs 386, 387 (a detector for a class committed the class), 409 | read a new instrument's *own first output* as a claim about the instrument |
| a fix that stops at the instance | runs 365, 366, 400, 402, 409 | after fixing an instance, grep for the class before moving on — but run 380: also check the class exists before generalising |
| heredoc `\n` / dict-key mangling in patch scripts | ~6 times this session | write patch scripts to a scratchpad `.py` file, never inline in a heredoc |
| a gitignored file has no `git show HEAD:` baseline | run 391 | for anything the session itself writes during a run, snapshot at `__enter__`, don't diff against HEAD |
| an auto-extractor counting cross-references as citations | run 422 | an auto-populator for a metric should only fire when the human/agent path is empty, not stack on top of explicit bookkeeping |
| bundling consolidation with a fix so it never counts as consolidation | run 409/410 | a run that *leads* with consolidation language is a consolidate run regardless of what it then shipped |
| a classifier heuristic keyed on a token that also appears in unrelated boilerplate | run 429 (`loop_action_class`'s "cited + fold verb" override matched the bare token "fold" in the status-line phrase `acts fold50%`) | key a heuristic on a *verb* next to the signal, not a token that leaks in from framing text; and reword the increment if it trips the classifier twice |
| an orientation doc silently going stale | runs 202/219/…/450 (recurring; `graph_state` was ~100 runs behind at run 450) | orientation docs (`graph_state`, `HANDOFF`, `tools/README`) need a scheduled refresh, not a memory-triggered one; the Snapshot count line is the tell |
| a coordination mechanism with a cost the aggregate score hides | runs 428 (a vote synthesis is budget-negative), 430 (a shared-evidence quorum is κ_E=1), 445 (coordination re-correlates a differentiated fleet) | before adding a coordination mechanism, ask what it costs *net of what the aggregate task score would show* — budget, epistemic independence, aggregate diversity |
| the loop is single-agent, so tools built for multi-agent traces have no real input from it | run 459 (`trace_topology` on the loop's own traces → 0 messages) | a swarm-layer tool must be validated on a swarm-layer trace (a probe rig's, generated in-memory), not the loop's own |
| the loop's orchestration layer (which run is next, what's dispatched) lived in a session's conversation context, not a ledger | run 464 (the run-244 CordisBench finding applied to the loop's own meta-layer) | dispatch state is task state — put it in a file a fresh session reads; run 464 built `tools/orchestration_ledger.py`, run 465 closed it (the dispatch boundary `LoopSession.__enter__/__exit__` now writes the ledger, and `check_startable()` refuses a fresh start while a lower run is stale in-flight) |
| regex metacharacters mangled crossing a *nested* shell boundary | 2026-09-10 (a `grep -rIl -E "a\|b\|c"` passed inline through `wsl bash -lc '...'`: the quoting collapsed, `\|` was re-parsed as shell pipes, the path args were eaten, and the grep recursed from the Windows filesystem root for **122 minutes**) | the run-109 heredoc rule generalises beyond heredocs — **anything carrying regex metacharacters crosses a shell boundary in a file, never inline**. Prefer one pattern per invocation over an alternation |
| a command that cannot proceed gives no signal that it cannot proceed | 2026-09-10 (two `sudo ss -lntp` background shells hung 36 min on a password prompt that can never be answered in a non-interactive agent shell; one ran `2>/dev/null`, which **swallowed the prompt itself** and turned a visible hang into a silent one) | the shell-level form of the ≥8-instance instrument rule: *a command that can't proceed must SAY SO, not hang.* Never `2>/dev/null` anything that can prompt; use `sudo -n` so it fails loudly; a background task with zero output after minutes is hung, not slow |
| a safety rule written as prose in a spec, then bypassed by its own author | 2026-09-10 (`QUEUE.md` bx-02 specified "reap only on `stale` AND (`idle_prompted_but_busy` OR `spinning`)"; the same session then hand-listed PIDs in a one-off reap script and killed three VS Code Codex extension servers — the live agents for two projects — because they were `stale`, which for an editor language server just means "older than an hour") | **a rule that only exists as prose does not bind; make it a callable predicate and have every caller go through it.** The fix was `orphan_scan.is_reapable()` returning `(bool, reason)` plus a `NEVER_REAP_MARKERS` list, so a refusal is always explainable and an editor server is protected by construction. Corollary: **age is a fact, not a fault** — never act destructively on a staleness signal alone |
| killing a subagent does not roll back its filesystem work, and the next `git add -A` silently absorbs it | run 467 (2026-09-10; the run was killed mid-flight during a resource crisis, leaving 56 `source_generation` fields and 3 edges uncommitted in the tree — the interactive session's next patch was applied on top and committed as `d1d9567` under a message describing only its own +1 node / +5 edges) | a kill stops a *process*, not its *effects*. After killing any agent that writes files, run `git status` and reconcile the tree BEFORE the next commit — and state what you found. This is the Hermes-orphan hazard in the filesystem instead of the process table: **stopping a parent never cleans up what it already did.** |
| a green/red gate returning a FALSE RED because another process mutated shared state mid-run | run 466 (2026-09-10) (a backgrounded `python tools/selftest_all.py` went RED transiently because the `LoopSession` recorder ran concurrently, writing `runtime/observations/` state while the selftest read it; a clean re-run was GREEN) | `selftest_all` reads `runtime/observations/`; never run the recorder (or any state writer) concurrently with it — record AFTER the selftest returns. A false RED is worse than a slow gate: it trains the operator to re-run and ignore, which is how a real RED gets waved through |

---

## 4. The idle-state rule (when the frontier is genuinely swept)

An increment must be one of: **(a)** deepen one node with a verified read, **(b)** dry-run a
probe (never a `--live` one — that spends owner quota), or **(c)** a consistency / adversarial /
consolidation pass. A run that would add a node with no edge to an existing node is not allowed.

---

## 5. Falsifiable predictions this model makes

- A batch of `citation upgrade` runs will lift `verified-fraction` back toward 0.90 and it will
  then re-erode at ~0.0015/run.
- The next monoculture flag from `loop_action_class` will be **fold**, because fresh literature
  is the lowest-friction increment and the loop drifts toward it.
- A fold that produces zero `challenges`/`constrains`/`refines` edges will, within ~5 runs, be
  the one a consolidation pass finds contributes nothing.
- Wiring `loop_environment_model.md` as an input `loop_conductor` reads and revises each run
  (the BCO shape) would show up as fewer repeated hazards from §3 — the test is whether §3 stops
  growing. **Status after ~40 runs: §3 grew by 5 rows (runs 429, 450, 428/430/445, 459), so it
  is still growing — the model is not yet closing the loop on its own hazards.** Three of the
  five, though, are one meta-hazard: *a mechanism (a classifier, a coordination step, a doc) has
  a failure mode the headline signal does not show.*
- The `acts <class>%` monoculture prediction held loosely: over runs 428–460 the mix stayed
  varied (fold ~35%, no monoculture flag), because the swarm-substrate and follow-on threads
  forced `build` / `probe` / `consolidate` runs. When the substrate work is fully done, expect
  the fold-drift prediction to bite.

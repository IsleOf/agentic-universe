# Swarm Substrate Prototype — Implementation Comparison and Week-1 Build List

> Companion to [`agent-fleets-and-swarm-substrate.md`](agent-fleets-and-swarm-substrate.md).
> That file is the landscape synthesis; this one is the concrete build decision: three candidate
> substrates compared on the dimensions that matter for a 2–15 agent non-hierarchical fleet, a
> pheromone-annotation schema, a validator-checkpoint design, a trust-scoring mechanism, and a
> minimal architecture split into *build week 1* vs *defer*.
>
> **Framing constraint (from the request):** we are rejecting a hard-coded Chief-of-Staff
> orchestrator. Coordination comes from a shared substrate (queue + store + annotation layer) and
> a light Sequential-style protocol. Roles are transient. A "personal assistant" role is allowed
> to *emerge* from performance data but must not calcify.
>
> **What this repo already has**, and the comparison must be read against it:
> [`tools/task_ledger.py`](../tools/task_ledger.py) (run 244) — a deterministic file-backed task
> ledger with a deterministic `next_ready()` and `sweep_stale()`;
> [`tools/fractal_flock.py`](../tools/fractal_flock.py) (run 294) — a shared artifact store with
> bounded-neighbourhood reads and adaptive spawn/compress, *no model calls*;
> [`tools/cohort_monitor.py`](../tools/cohort_monitor.py) and
> [`tools/executor_pool.py`](../tools/executor_pool.py) (runs 353–388) — a cross-agent monitor
> and a disposable-credential worker pool. The graph nodes
> `concept_orchestratorless_flock_coordinates_through_shared_state_not_a_central_planner`,
> `pattern_market_as_orchestrator`, `pattern_ostrom_swarm_governance`,
> `emergent_self_organizing_roles`, and `emergent_reputation_and_trust_dynamics` are the prior
> art *inside* the project.

---

## TL;DR

- **Don't adopt a framework as the substrate.** Strands Swarm, SwarmSys, and Ruflo each solve a
  different problem than the one posed, and each brings coupling that fights the "minimal upfront
  structure" goal. **Borrow patterns, build the substrate on `task_ledger.py` + `fractal_flock.py`.**
- **Strands Agents Swarm** is the closest usable reference and the one to *read* — its handoff
  tools, shared-context model, and anti-ping-pong safety are directly portable, Apache-2.0, and
  low-friction. Its gap is exactly ours to fill: no validator gates, no annotation decay, no
  cross-run persistence.
- **SwarmSys** is a paper with no code (as of 2026-09). Its *mechanism* — embedding-matched task
  allocation with pheromone-as-reinforcement and an Explorer/Worker/Validator cycle — is the best
  published match for what we want, and worth reimplementing in miniature. Its cost (~6× a single
  CoT call at 8 agents) and its "no explicit decay" choice are cautions.
- **Ruflo** is large, MIT, and Claude-Code-native, but its default topology is a **Queen-led
  hierarchy** with consensus protocols bolted on — the thing we are explicitly rejecting. Mesh
  mode exists but is not the grain of the tool. High surface area, heavy coupling.
- **Pheromone schema:** a 7-field annotation row (`utility`, `confidence`, `ttl`, `half_life`,
  `agent`, `task_ref`, `created_at`) with a computed `effective_utility` that decays
  exponentially and hard-expires. SQLite for week 1; a vector column is a week-3 add.
- **Validators:** gates sit *between stages*, are *stateless*, *quorum-rotated*, and *logged
  adversarially* — the design that stops a gate becoming a permanent authority is that no agent
  holds the gate role twice in a row and every gate verdict is itself checkable.
- **Trust scoring:** per-agent Beta-Bernoulli reputation + UCB selection bonus + exponential
  recency decay, ELO-style pairwise updates for head-to-head critique tasks. Prior art: DRF
  (arXiv:2509.05764), AgentLance/VCG (already in the graph), classic UCB1 / Thompson / TrueSkill.

---

## 1. Substrate comparison

### 1.1 The three candidates on the requested dimensions

| Dimension | **Strands Agents Swarm** (AWS) | **SwarmSys** (arXiv:2510.10047) | **Ruflo** (`ruvnet/ruflo`) |
|---|---|---|---|
| **Status** | Production OSS, Python + TypeScript, [docs](https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/) | Research paper, **no public code** as of 2026-09 ([arXiv](https://arxiv.org/abs/2510.10047), [HF](https://huggingface.co/papers/2510.10047)) | Production OSS, ~40k★, Claude-Code-native ([GitHub](https://github.com/ruvnet/ruflo)) |
| **Setup complexity** | **Low.** `pip install strands-agents`; construct `Agent` objects; `Swarm([...], entry_point=...)`; call it. One file. | **High.** Reimplement from the paper: embeddings, ε-greedy matcher, EWV cycle, profile store. | **Medium but heavy.** `npx ruflo@latest init` then "use Claude Code normally"; a hooks system auto-routes in the background. Large surface (100+ agents, plugins, AgentDB). |
| **Shared-memory model** | Python: mutable `SharedContext` — a key-value dict that **accumulates** across agents (original task, agent history, contributed knowledge, agent roster). TypeScript: **immutable** JSON context passed in each handoff. In-process; no persistence primitive in the swarm object. | Two embedding-backed profile stores: **agent profiles** (competence embedding from declared abilities + performance history; availability embedding from workload) and **event profiles** (task text, dependency structure, progress log, participants, semantic embedding). This *is* the shared state — agents match against it, not message each other. | **AgentDB + HNSW vector index** ("ruflo-rag-memory"), hybrid graph-hop + diversity ranking; `ruflo-rvf` plugin persists/restores agent memory across sessions. Benchmarked ~1.9× faster than brute-force at N=20k. |
| **Handoff mechanism** | Built-in tools auto-attached to every agent: `handoff_to_agent(name, message, context)` and `complete_swarm_task(...)` (Python); structured-output `{agentId, message, context}` routing (TypeScript). The framework tracks history and enforces limits. | No explicit handoff. Allocation is **pull-style**: the ε-greedy matcher assigns an agent to an "event" by `Cnorm(i,j) = ½(cos(v_agent, v_event)+1)`, exploration ∝ similarity, exploitation via sigmoid weighting. Agents cycle Explore → Work → Validate. | Hooks-driven auto-routing. Topology is **Queen-led hierarchy** by default with **Raft / Byzantine / Gossip** consensus; mesh topology is available but not the default grain. SONA re-weights routing by observed success rate. |
| **Validator / gate support** | **None in the Swarm pattern.** Timeouts, step caps, and repetitive-handoff detection only. (Cedar authz, HITL, and steering exist elsewhere in the Strands SDK, not swarm-scoped.) | **First-class.** "Validator" is one of the three roles; a contribution is only reinforced *after* validation. Validation gates the pheromone update. | Security guardrails (AIDefence: prompt-injection blocking, PII detection) — **not** artifact-quality gates. Consensus protocols provide agreement, not correctness checking. |
| **Decay / TTL for annotations** | **None.** Shared context grows monotonically within a run and is discarded at the end. | **Implicit only.** "Idle or invalid matches receive no reinforcement and gradually decline in competitiveness as other profiles evolve — mimicking pheromone evaporation *without explicit decay*." No half-life, no TTL. The paper flags this as a limitation direction. | **Not documented.** No stated expiry, decay schedule, or pruning policy for AgentDB rows. |
| **License / cost** | **Apache-2.0.** Cost = model inference only. | N/A (no code). Reported cost: **$0.071 / question at 8 agents** on exam tasks — ~6× a single GPT-4o CoT call ($0.012). Comm overhead grows with agent count. | **MIT.** Free OSS core; hosted demos free with no API key; enterprise support is a paid add-on but optional. |
| **Fit to "no hard-coded Chief-of-Staff"** | **Good.** Genuinely peer-to-peer within a run; `entry_point` is a starting agent, not a boss. | **Best.** No orchestrator at all — allocation is emergent from embedding match + reinforcement. | **Poor by default.** "Queen-led hierarchy" is the built-in model. Achieving non-hierarchical operation means fighting the tool's grain. |
| **Fit to 2–15 agents** | Good — examples run 3–6 agents; no scaling machinery needed. | Overkill at the low end — ablations start at 4 and the value shows at 8–32; embedding infra is fixed cost. | Overkill — designed for 100+; the coordination machinery (consensus, SONA) is dead weight at N≤15. |

### 1.2 What each is actually good for

- **Strands Swarm** — the reference implementation to read before writing our own. Its
  `handoff_to_agent` / `complete_swarm_task` contract, its "every agent sees the full shared
  context" model, and its `repetitive_handoff_detection_window` / `repetitive_handoff_min_unique_agents`
  anti-ping-pong heuristic are all directly portable and battle-tested. Adopt the *shapes*, not
  the dependency.
- **SwarmSys** — the mechanism blueprint. Embedding-matched allocation + validate-before-reinforce
  + an explicit explore/exploit/validate cycle is exactly the "pheromone field" the request asks
  for, and it is the only one of the three with *no* central coordinator. Reimplement a miniature
  version (see §5). Treat "no explicit decay" as a bug to fix, not a feature to copy.
- **Ruflo** — a source of ideas on memory (AgentDB + HNSW, cross-session recall) and on
  topology-by-success-rate (SONA). Not a substrate to build on for this goal: the hierarchy is
  load-bearing and the surface area is enormous.

### 1.3 Recommendation

**Build the substrate in-repo, borrowing:**

- the **file-ledger discipline** already in [`task_ledger.py`](../tools/task_ledger.py)
  (atomic write, append-only audit, deterministic `next_ready()`) — this is the queue;
- the **shared-artifact-store + bounded-neighbourhood-read** already in
  [`fractal_flock.py`](../tools/fractal_flock.py) — this is the blackboard;
- **Strands's handoff/complete tool contract and anti-ping-pong window** — ported, ~40 lines;
- **SwarmSys's validate-before-reinforce rule and embedding match** — reimplemented small;
- **DRF's UCB + ELO + recency-decay reputation** — for the trust layer (§4).

Rationale: every candidate framework couples the substrate to a coordination philosophy we
either already have a better version of (`fractal_flock`) or explicitly reject (Ruflo's queen).
The parts worth taking are small, well-specified, and permissively licensed.

---

## 2. Pheromone annotation schema

A **pheromone annotation** is a small row any agent can write and any agent can read, with no
central coordinator, that says *"this artifact / task / direction is worth N to me, I'm M
confident, and this opinion should fade."*

### 2.1 Fields

| Field | Type | Meaning | Notes |
|---|---|---|---|
| `id` | text (uuid) | annotation identity | client-generated; writes are idempotent on `id` |
| `task_ref` | text | the task, artifact node, or direction this annotation is *about* | foreign key into the task ledger / artifact graph |
| `kind` | text | `utility` \| `warning` \| `claim` \| `bid` \| `done` | small closed vocabulary; unknown kinds are stored and surfaced, never dropped (the run-365 rule) |
| `agent` | text | the contributing agent's id | never trusted as authority — see §4; used for decay-per-agent and free-rider detection |
| `utility` | real, `[-1, 1]` | signed value estimate: how much acting here helps (or, negative, hurts) | the "pheromone strength" |
| `confidence` | real, `[0, 1]` | the agent's self-assessed reliability of this estimate | multiplies utility in aggregation; **not** derived from the text (would inflate) |
| `created_at` | real (epoch s) | write time | the only clock the decay math needs |
| `half_life_s` | real | seconds for `effective_utility` to halve | default 3600; agents may set shorter for volatile signals |
| `ttl_s` | real | hard expiry: the row is ignored (and later reaped) once `age > ttl_s` | default `6 * half_life_s` |
| `evidence` | text (json) | optional: links to artifacts, prior annotations, tool outputs | provenance for the validator layer (§3) |
| `supersedes` | text (uuid, nullable) | this annotation replaces an earlier one by the same agent on the same `task_ref` | keeps the field append-only while letting an agent change its mind |

### 2.2 Decay — the part the frameworks get wrong

SwarmSys leaves evaporation implicit ("other profiles evolve"); that only works when the
population is churning fast. For a 2–15 agent fleet that can sit idle, decay must be **explicit
and time-based**:

```
age              = now - created_at
effective_utility = utility * confidence * 0.5 ** (age / half_life_s)      if age <= ttl_s
                  = 0  (and row is reap-eligible)                          if age  > ttl_s
```

Aggregation over a `task_ref` is the **confidence-weighted, decayed sum**, clipped:

```
signal(task_ref) = clip( Σ_a effective_utility(a) , -1, 1 )     over live annotations a
```

Two guardrails, both learned the hard way in this repo's own monitor work (runs 385–386):

1. **The aggregate's threshold must scale with the number of contributors.** A fixed "act if
   `signal > 0.7`" line silently becomes "act if ≥4 mildly-positive agents" as the fleet grows.
   Carry `n_contributors` and compare against `k*mean + z*sd*sqrt(n)`, not a constant. (See
   `concept_an_absolute_threshold_on_a_pool_sized_sum_has_an_undocumented_ceiling...`.)
2. **Correlated agents are not independent votes.** If several agents share a base model their
   annotations correlate (~0.7, per arXiv:2609.01873). Correlation widens the *noise band* on
   `signal`, it does not reduce the sum. Track it; don't deflate the score with it.

### 2.3 Storage

**Week 1: SQLite.** One table, the schema above, plus:

```sql
CREATE INDEX pher_task ON pheromone(task_ref);
CREATE INDEX pher_live ON pheromone(created_at);   -- for the reaper
```

Reads are `SELECT ... WHERE task_ref = ? AND (? - created_at) < ttl_s`. Writes are
`INSERT OR REPLACE ON id`. A background **reaper** (`DELETE WHERE ? - created_at > ttl_s`) runs
every N minutes — this is the only privileged process and it does nothing but garbage-collect.
Concurrency: SQLite WAL mode handles 2–15 writers fine; if it ever doesn't, the same schema drops
into Redis (hash per `task_ref`, `EXPIRE` for TTL) or Postgres unchanged.

**Week 3+: add a vector column.** `embedding BLOB` on the artifact/direction rows (not the
annotations), for SwarmSys-style "which agent's competence embedding best matches this open
task." Local model (`bge-small`, `all-MiniLM`) or a hosted embedding endpoint; `sqlite-vec` or a
small FAISS/Chroma index. This is what turns "agents read the board" into "agents are *matched* to
work" — but it is an optimization, not a week-1 need.

### 2.4 Read/write contract (no coordinator)

```
substrate.annotate(task_ref, kind, utility, confidence, *, agent,
                    half_life_s=3600, ttl_s=None, evidence=None, supersedes=None) -> id
substrate.read(task_ref) -> {"signal": float, "n_contributors": int,
                             "annotations": [<live rows, decayed>], "corr_estimate": float}
substrate.board(limit=50) -> [<task_refs ranked by |signal|, freshest first>]
```

Any agent calls any of these at any time. There is no lock, no turn, no permission check on
*read*. `annotate` is the only mutation and it is monotonic (append + supersede, never
in-place edit).

---

## 3. Validator / judge checkpoint design

### 3.1 Where the gates sit

For the canonical pipeline **research → draft → critique → finalize**, gates sit **on the edges,
not the nodes**:

```
  research ──[G1: evidence gate]──▶ draft ──[G2: claim gate]──▶ critique ──[G3: resolution gate]──▶ finalize ──[G4: release gate]──▶ done
```

| Gate | Fires when | Checks | Pass / fail action |
|---|---|---|---|
| **G1 evidence** | a research artifact is posted | every claim in the artifact has ≥1 `evidence` link; links resolve; no fabricated citations | fail → annotation `kind=warning` on the artifact, task returns to `pending` with the gate's notes |
| **G2 claim** | a draft cites research artifacts | draft claims are entailed by (not just adjacent to) the cited research; numbers match | fail → draft bounced to its author with diffs |
| **G3 resolution** | critique round completes | every critique point is either addressed in a revision or explicitly rebutted with reasoning; no silent drops | fail → back to critique; after 2 failures, escalate to human |
| **G4 release** | artifact proposed as final | computable checks pass (tests, schema, link-check); ≥2 independent validators agree; no unresolved `warning` annotations on the task | fail → stays `pending`; **never auto-releases** anything outward-facing |

This mirrors the loop's own `holdout_verifier2` + `improvement_loop.verify_loop_edit` design
(two independent scorers, conservative on disagreement) and the "insert lightweight validator
gates between stages to keep error growth linear" principle from the swarm-practice literature.

### 3.2 What stops a gate becoming a permanent authority

The failure mode the request names — a validator calcifying into a de-facto boss — is real. Four
mechanisms, all cheap:

1. **The gate role rotates and is single-use per task.** `validator-for-task-42-G3` is a role an
   agent holds for exactly one adjudication. The trust layer (§4) picks *which* agent, weighted
   by reputation, but **no agent may hold consecutive gate roles on the same task**, and an agent
   that authored an artifact can never gate it.
2. **Gate verdicts are themselves annotations, and themselves checkable.** A `G4` verdict is a
   `kind=claim` annotation with `evidence`. A later agent (or a human) can post a
   `kind=warning` that contradicts it, which reopens the task. The gate has no special write
   permission — it writes the same rows everyone writes.
3. **Quorum, not veto.** G4 needs *≥2 independent* validators (different base model where
   possible — arXiv:2609.03422 shows same-family agreement is nearly free and nearly
   meaningless). A single validator can *flag* but not *block*.
4. **Gates are stateless.** A gate reads the task + its annotations, emits a verdict, and
   forgets. It accumulates no private model of the project, so there is nothing for authority to
   accrete *into*. Reputation accrues to agents (§4); gates are a function those agents
   temporarily compute.

### 3.3 Throughput vs error-catching at low N

With 2–15 agents, pulling 2 for a quorum gate is 13–100% of the fleet. Tuning:

- **G1/G2/G3 are single-validator** (flag-only, cheap, frequent). **Only G4 needs quorum.**
- G4 quorum can be **1 agent + 1 computable check** when no second independent model is available
  — the computable check is the "independent" verifier.
- A task with **zero live `warning` annotations and passing computable checks** can **skip G1–G3**
  and go straight to a G4 quorum. Gates are a tax on *contested* work, not all work.

---

## 4. Trust / utility scoring — letting a "personal assistant" emerge without calcifying

### 4.1 The mechanism

Per agent `a`, maintain:

```
successes_a, failures_a         Beta-Bernoulli counts, seeded (1, 1)
reputation_a = successes_a / (successes_a + failures_a)          posterior mean
uncertainty_a = sqrt( reputation_a (1-reputation_a) / (successes_a + failures_a) )
elo_a                            ELO rating, seeded 1000, for head-to-head critique/judgement tasks
last_active_a                    epoch seconds
```

**Selection** (which agent gets offered a task, or a gate role) uses a **UCB bonus**:

```
score_a(task) = reputation_a
              + c * uncertainty_a                       # exploration: try under-sampled agents
              + match(competence_embed_a, task_embed)   # SwarmSys-style fit, once §2.3 lands
              - load_penalty_a                          # current open tasks
```

Offer the task to the top-scoring *available* agent; ties broken randomly. `c ≈ 0.5` — high
enough that a new agent gets real chances before its reputation is trusted.

**Update after outcome** (gate verdict or downstream acceptance):

```
on success:  successes_a += 1
on failure:  failures_a  += 1
on abstention (agent declined a task in its stated incompetence zone):  no change   # abstention is not punished — it is the behaviour "Drop the Hierarchy" found valuable
```

For **head-to-head** tasks (agent X's critique vs agent Y's draft, or two validators disagreeing),
apply an **ELO update** on the pair:

```
expected_X = 1 / (1 + 10 ** ((elo_Y - elo_X) / 400))
elo_X += K * (outcome_X - expected_X)         K = 24
elo_Y += K * ((1 - outcome_X) - (1 - expected_X))
```

### 4.2 Decay — the anti-calcification core

Every reputation read applies **exponential recency decay** toward the prior:

```
age_days           = (now - last_active_a) / 86400
shrink             = 0.5 ** (age_days / REP_HALF_LIFE_DAYS)     # REP_HALF_LIFE_DAYS ≈ 14
successes_eff      = 1 + (successes_a - 1) * shrink             # decays toward the (1,1) seed
failures_eff       = 1 + (failures_a  - 1) * shrink
elo_eff            = 1000 + (elo_a - 1000) * shrink
```

Consequences, all intended:

- An agent that stops contributing **slides back toward the mean** — no permanent incumbency.
- The "personal assistant" role (the agent the human talks to, the agent that gets meta-coordination
  tasks) is **always the current argmax of `score_a(assistant_task)`**, recomputed per
  interaction. It is a standing wave, not an appointment. A better agent overtakes it the moment
  its decayed reputation is higher.
- A burst of luck decays away in ~2 weeks unless sustained.
- **Free-rider / sybil detection:** an agent whose annotations are frequently contradicted by
  gates (`kind=warning` posted against its `kind=claim`) accrues `failures`; an agent that only
  ever posts low-confidence me-too annotations shows high volume but near-zero
  `successes - failures` and never wins selection.

### 4.3 Prior art

| Source | What to take |
|---|---|
| **DRF — LLM-Agent Dynamic Reputation Filtering** ([arXiv:2509.05764](https://arxiv.org/abs/2509.05764)) | The exact stack proposed here: UCB bandit for agent selection (agent = arm), ELO-style reputation updates on task outcome, temporal decay weighting recency. Closest published match. |
| **AgentLance / market-as-orchestrator** (in-graph: `pattern_market_as_orchestrator`, arXiv:2608.23867) | Agents bid with private cost estimates; allocator picks by bid + *public reputation*; VCG-style payment makes honest cost-reporting dominant. The reputation surface is reusable; the VCG layer is a defer-item. |
| **Multi-agent conversational bandit** ([arXiv:2501.01849](https://arxiv.org/abs/2501.01849)) | Treating each candidate output as a bandit arm for online selection — the pattern for choosing *among drafts*, not just among agents. |
| **Self-Resource Allocation in Multi-Agent LLM Systems** ([arXiv:2504.02051](https://arxiv.org/abs/2504.02051)) | Evidence on when agents can allocate work among themselves vs when a mechanism is needed. |
| **Classic** — UCB1 (Auer 2002), Thompson sampling, TrueSkill / Glicko | Bounded-regret selection; TrueSkill if per-task uncertainty needs to be first-class rather than derived. |
| In-graph: `emergent_reputation_and_trust_dynamics`, `concept_mechanism_incentive_compat_does_not_transfer` | The caution: a truthful *mechanism* does not make LLM agents *bid* truthfully. Keep the reputation empirical (outcomes), not declared. |

---

## 5. Minimal viable starting architecture

### 5.1 Bill of materials

| Component | Build week 1 | Defer | Rationale |
|---|---|---|---|
| **Task queue** | Extend [`task_ledger.py`](../tools/task_ledger.py): add `claim_by`, `stage` (research/draft/critique/final), keep deterministic `next_ready()` and `sweep_stale()` | Priority scheduling, dependency DAG visualisation | The ledger already solves dropped-tasks; only needs a `stage` column and a claim field |
| **Shared blackboard** | Reuse [`fractal_flock.py`](../tools/fractal_flock.py)'s artifact store + bounded-neighbourhood read | Fractal spawn/compress (already built, wire later) | Bounded reads keep per-agent context flat as the fleet grows |
| **Pheromone annotation layer** | New `tools/pheromone.py` — SQLite table from §2.1, `annotate()` / `read()` / `board()`, exponential decay + hard TTL, background reaper | Vector/embedding column (§2.3), correlation-aware noise band | ~150 lines stdlib + sqlite3; this is the "field" the swarm coordinates through |
| **Handoff / turn protocol** | Port Strands's `handoff_to_agent` + `complete_task` contract and the repetitive-handoff window into a `tools/relay.py`; Sequential order = ledger's `next_ready()` | Structured-output routing, parallel stages | Sequential-with-shared-context is the protocol "Drop the Hierarchy" found beats both extremes |
| **Validator gates** | G1 + G4 only (evidence gate, release gate). Single-validator G1; G4 = 1 agent + computable checks. Verdicts are annotations. | G2, G3, cross-family quorum, escalation ladder | Two gates catch most cascades; add the middle gates when contested work appears |
| **Trust / reputation** | `tools/reputation.py` — Beta-Bernoulli counts + UCB selection score + exponential recency decay. Outcome hook from G4. | ELO head-to-head, embedding match term, VCG payments, sybil clustering | Selection + decay is the anti-calcification core; ELO matters only once head-to-head tasks exist |
| **Human interface** | A `board` CLI: `python -m tools.pheromone board` + `task_ledger` status view. Status per agent: `working/blocked/done/idle` from claim + heartbeat | Herdr-style TUI, NotchAgent-style ambient display, notifications | Situational awareness without micromanagement; the CLI is enough to start |
| **Autonomy ladder** | Draft-only by default; agents may write to `runtime/` and `docs/` but **not** commit, push, or call external services | Auto-execute tier for low-risk local writes; per-agent scoped credentials (extend `executor_pool.py`) | Matches the repo's existing "one outer gate" stance; nothing outward-facing without human approval |
| **Monitor** | Wire [`cohort_monitor.py`](../tools/cohort_monitor.py) to read pheromone annotations as the per-worker signal | Extractor/EaE pipeline, adaptive threshold tuning | The pool-size and correlation lessons from runs 385–388 already apply here |

### 5.2 Week-1 build list (concrete, ordered)

1. **`tools/pheromone.py`** — SQLite annotation store. Schema from §2.1. Functions:
   `annotate()`, `read(task_ref)`, `board(limit)`, `_reap()`. Decay + TTL from §2.2. `selftest`
   subcommand with a pool-size sweep (`range(2, 16)`) and a decay-over-time check. **~150 lines,
   pure stdlib.**
2. **Extend `tools/task_ledger.py`** — add `stage` (`research|draft|critique|final|done`) and
   `claim_by`; `next_ready()` returns the oldest `pending` task whose deps are `done`, preferring
   earlier stages. Keep the atomic-write + audit-log discipline. Add `sweep_stale` heartbeat.
3. **`tools/relay.py`** — port the Strands handoff contract: `handoff(to_hint, message,
   context)` writes a `kind=done` annotation + a new ledger task; `complete(task_ref, artifact)`
   closes it. Repetitive-handoff guard: refuse a handoff that would make the last
   `window=6` handoffs use `< 3` unique agents.
4. **`tools/reputation.py`** — Beta-Bernoulli `(successes, failures)` per agent in a JSON file;
   `score(agent, task)` = reputation + `0.5 * uncertainty` − `load_penalty`; `record(agent,
   outcome)`; exponential recency decay (`half_life = 14 days`) applied on every read. `selftest`
   asserts a stale agent decays toward the mean and a new agent gets exploration priority.
5. **`tools/gates.py`** — `g1_evidence(artifact)` (every claim has a resolving `evidence` link)
   and `g4_release(task_ref)` (computable checks pass + ≥1 validator annotation + zero live
   `warning`s). Verdicts written via `pheromone.annotate(kind="claim"|"warning")`. No special
   permissions.
6. **`tools/swarm_demo.py`** — a runnable 3-agent loop over the substrate using the existing
   `_fake_worker` pattern from `executor_pool.py`: research → draft → G1 → critique → G4 →
   done, all coordination through the pheromone board and the ledger, no orchestrator object.
   This is the acceptance test for week 1.
7. **Register all five in `tools/selftest_all.py`** — and note in the run summary that this is
   harness expansion (the `_harness_delta` instrument from run 388 will flag it as
   `unevaluated_expansion` until it's scored against the holdout set — that flag is correct and
   the owner-gated wiring is the follow-up).

### 5.3 What week 1 deliberately does *not* build

- No embeddings / vector matching — the board is read linearly by 2–15 agents; that is fine.
- No ELO — no head-to-head tasks yet.
- No VCG / market payments — reputation-weighted selection is enough to start; the market layer
  (`pattern_market_as_orchestrator`) is a clean later swap.
- No parallel stages — Sequential first, because it is the protocol with the evidence behind it
  and because it makes the gates trivial to place.
- No TUI — the `board` CLI plus `task_ledger` status is the whole human interface for now.
- No auto-execute tier — draft-only, human commits.

### 5.4 The one structural commitment

Everything above is swappable *except* this: **coordination state lives in files and a database
that any agent can read and only append to, decays on a clock, and is reaped by an unprivileged
process — never in an orchestrator agent's context.** That is the line that keeps roles
transient. It is also, not coincidentally, the line this repo already drew with `task_ledger.py`
and `fractal_flock.py`.

---

## 6. What building and probing it taught us (runs 390–414)

Sections 1–5 are the design as written at the start. This section is what the six-module build
(`pheromone` · `task_ledger`+stage · `relay` · `reputation` · `gates` · `swarm_demo`, plus five
probe rigs) and a red-team pass actually surfaced. Where a finding changes the design, the
change is stated here rather than rewritten above.

### 6.1 It runs end to end with no orchestrator object
`swarm_demo` executes `research → draft → G1 → critique → G4 → done` where every coordination
decision goes through the ledger, the board, the relay, and the gates. A selftest regex enforces
that there is no `Orchestrator` / `Chief` / `Boss` / `Manager` class. The `run()` loop holds no
decision state.

### 6.2 A gated pipeline needs ≥ 3 agents, not 2
The no-self-review rule (a gate validator may not have contributed to the artifact) plus a
4-stage pipeline sets a hard floor. At **k = 2**, by the time an artifact reaches G4 both agents
have contributed, so no valid validator remains and the run stalls **cleanly** (a `GateRefused`
in the transcript, no exception, no hang). The stated "2–15 agents" is **"3–15" for gated work**;
a 2-agent fleet can still coordinate for *ungated* tasks.

### 6.3 The pool-size-scaled threshold works, and was applied everywhere from birth
`pheromone.read()`'s `suggested_threshold` scales as `k·mean + z·sd·√(k·design_effect)` — never
a bare constant. This is the fix for a real defect found in this repo's *own* `cohort_monitor`
(it aborted on pure benign noise from k = 20 because it compared an absolute threshold against a
pool-sized sum). `pheromone` is the first component built after that lesson to pass the
`param_invariance_audit` scan by construction (its selftest sweeps `range(2, 16)`).

### 6.4 Transparency is a safety property — but only necessary, not sufficient
DeepMind's 100-agent cheating/whistleblowing study (arXiv:2609.04170): the same transparent
channels that carried an exploit also let honest agents detect it and organise against it.
**`relay.py`'s board-not-private-channel and `gates.py`'s contestable-verdict choices are that
safety property, not just a convenience.** Measured against the real board
(`probe_annotation_contagion`): plain `kind=warning` annotations contain a boosted-exploit signal
in ~83% of swept scenarios once the honest cohort is online; the residual risk is the **detection
lag**, which `pheromone.warn()` (a cheap, weak, self-decaying suspicion flag) roughly halves.
The limit: transparency gives the counter-response somewhere to happen, it does not guarantee it
happens — the Ostrom mechanisms are what turn "could detect" into "does enforce".

### 6.5 An evolved private language defeats a keyword monitor — silently
GlossoGen (arXiv:2609.01491): agents under efficiency pressure evolve compositional,
human-incomprehensible registers; **weak models can *learn* an existing one even if they cannot
invent it.** `probe_language_drift_monitor` drove the real `gates.g1_evidence` against text
drifted from English toward a coded register: it passes a fully-drifted artifact as **clean**
(zero uncited-claim reports; an unparsed citation reads as no citation). Two-part fix, both
built: **escalate on unparseability** (a gate that can't read its input says so, it doesn't
pass) and **`pheromone.register_health()`** — a model-free rolling fraction of annotation text
carrying English function words, flagging `drifting` as a distribution shift so the board's own
register is watched.

### 6.6 The trust boundary: the substrate authenticates no writes
The `agent` field on an annotation is **caller-supplied and unverified**. Every identity-keyed
guard — gate rotation, no-self-review, the anti-ping-pong window, the reputation ledger,
correlation de-duplication — is only as strong as "fleet agents do not impersonate each other".
That is fine for a fleet one operator controls and wrong for an open swarm. A red-team pass
(`probe_substrate_adversarial`, 11 attacks) fixed three real bugs (whitespace/case self-review,
cross-author warning suppression, a fabricated G4-pass counted toward quorum) and one disguise
bug; the residual landings are all Sybil-class and need **signed writes, a capability token from
the pool (`executor_pool` already has `mint_token` / `redeem_token`), or an external identity
provider**.

### 6.7 Rotation is not free — but the substrate's cost is zero
"Testing Interchangeability in LLM Agent Teams" (arXiv:2609.05279): swapping a role-matched
agent costs **16–63% more communication per progress**, from conventions learned with a former
partner interfering, and the cost grows with how long the role was held; when the agenda-setter
is swapped the *incumbent who stayed* pays most of it. `swarm_demo`'s fresh-eyes rule rotates
agents deliberately. `probe_swap_cost` forced a mid-pipeline rotation and measured **zero change**
in the substrate's own footprint (ledger tasks, annotations, handoffs identical) — a handoff
costs the same regardless of who picks it up, because coordination state is external. **The
structural half is settled; whether real model agents still pay the convention penalty through a
board is a live-model question.** Design consequence: rotate for safety where safety needs it
(the gates), let stable working pairs persist elsewhere.

### 6.8 Memory representation determines model-upgrade portability
"Does Your Agent's Memory Survive a Model Upgrade?" (arXiv:2609.05339, sub-10B models):
fixed-schema memory transfers across an upgrade with ~0 accuracy change; model-compressed notes
shift ±10 pp; mixed embeddings forfeit most of the re-embed gain; only retaining raw history
enables repair. Applied:
- `task_ledger.py` carries `PORTABILITY_CLASS = "fixed-schema"` — **put anything that must
  survive a model swap here.**
- `pheromone.py` carries `PORTABILITY_CLASS = {"numeric_columns": "fixed-schema", "evidence":
  "model-coupled"}` — the `evidence` blob is disposable (the clock decay already enforces this),
  and `register_health()` needs its baseline re-established after a model/writer swap.
- The `.audit` logs and `fractal_flock`'s append-only store are the **raw source history** — keep
  them uncompressed; store-only repair of compressed notes failed all 48 test cases in the paper.
- Week-3's vector column needs a **strictly isolated embedding space or a full re-embed**, never
  a mixed index.

### 6.9 Reputation: keep it empirical, and normalise identity everywhere
`reputation.py` implements Beta-Bernoulli + UCB + 14-day decay toward the seed (the
anti-calcification core). Two corrections during the build: reputation must come from **recorded
outcomes, never agent self-report** (a truthful mechanism doesn't make LLM agents self-report
truthfully); and the agent-id normalisation (`strip + casefold`) that gates and pheromone got
had to be applied to `relay` and `reputation` too — a consolidation pass found the earlier fix
had stopped at the two modules in front of it.

---

## 7. The identity gap and the capability-token decision (runs 428–434)

Five runs converged on one conclusion the design must now state plainly: **every remaining
substrate weakness is the same weakness** — the `agent` field is an unauthenticated string, so
identity is free to create and free to abandon. The four findings, and the half-measures shipped
against each:

### 7.1 Collaboration gain, net of budget (run 428, arXiv:2602.05289)
`probe_orchestration_value` gained a `gamma` arm: it counts the subtask-attempt budget a MULTI
config spends and compares it against a single agent given that same budget (best-of-N,
oracle-verified). At the rig's params the verifiable + deterministic + disjoint config's win is
**genuine collaboration gain** (Γ = +0.52; a single agent needs ~6.7× the budget to match it),
but a **vote synthesis is budget-*negative*** (Γ = −0.21 — it costs 2× and loses to best-of-2
single). This is a second, independent reason (alongside 7.2) not to make a quorum/vote the
substrate's integration mechanism.

### 7.2 A shared-evidence quorum has a structural epistemic cut of 1 (runs 430–431, arXiv:2609.02925)
Distinct validators who read the same thing are not independent. A quorum's real resilience is
`κ_E` — the minimum number of fault roots whose failure reaches a decisive coalition — not the
vote count; in the paper's experiments 1→7 reviewers on shared evidence all held ~96–100%
unsafe-commit rates. The substrate captures no per-validator evidence lineage — every agent reads
the same board — so its G4 quorum is structurally `κ_E = 1`.
**Shipped (run 431):** G1 records the artifact's evidence links; G4 computes
`evidence_basis_width` (distinct fault roots) and **REPORTS `single_evidence_domain`** when the
whole basis is one source. This is the `κ_E` *ceiling* (`κ_E ≤ basis width`), not a true
per-validator `κ_E` — a REPORT, never a block.

### 7.3 Reputation only disciplines a costly identity (runs 432–434, arXiv:2609.02992)
"Tempting the Agent": an agent milks reputation and resets when *extracted value − reset cost ≥
0*, and higher reputation can *increase* the temptation (Prop 4.8). The substrate makes reset
free, so `reputation.py` sits on the wrong side of every honesty threshold, and the UCB
exploration bonus that keeps reputation non-calcifying is the same bonus that subsidises a
whitewashing reset.
**Shipped (run 433):** `reputation.slash(aid, severity)` — a penalty `record("success")` cannot
lift, decaying on a 60-day half-life; `reputation.whitewash_risk(aid, candidates)` — a REPORT
flagging a thin-evidence agent that is still competitive.
**Verified (run 434):** `probe_substrate_adversarial`'s identity-reset attack confirms the slash
bites under the real id (the milker is deselected) and a fresh id sheds it — lands as a *known
limit*, `n_landed_unexpected` stays 0.

### 7.4 The one owner decision these tee up
All three REPORT-not-block half-measures (`single_evidence_domain`, `whitewash_risk`,
`quorum_homogeneous`) are advisory *because the substrate cannot act on identity it cannot
trust*. The blocking version of each needs the same thing: **the `agent` field bound to a
capability token**. `executor_pool` already has `mint_token` / `redeem_token` (single-use,
scoped). A concrete sketch:

- `pheromone.annotate(..., token=?)` and `reputation.record(..., token=?)` take an optional
  token; when the substrate is run in *closed* mode, a write without a valid token is refused.
- The token's issued-to principal becomes the true identity key for rotation, no-self-review,
  the ping-pong window, and the reputation ledger — replacing the raw string.
- A reset then costs a fresh token from the pool, which the pool can rate-limit, price, or
  refuse — `κ_R > 0` by construction, and a `slash` can attach to the principal, not the string.
- **What breaks:** every selftest that annotates as a bare id (`"alice"`, `"v1"`, …) needs a
  test-mode token mint, and `swarm_demo` needs the pool in the loop. This is a real but bounded
  migration — call it a day of work across `pheromone`, `reputation`, `gates`, `relay`,
  `swarm_demo`, and their selftests.
- **What it does *not* fix:** an operator who mints many tokens for their own puppets. That is
  the Sybil floor; it needs an external identity provider and is out of scope for a
  single-operator fleet.

This section is the loop's recommendation; the migration itself is a self-design change to the
substrate's trust model and is **owner-gated**.

---

## 8. The REPORT-not-block signal catalogue (runs 424–439)

The substrate now emits **seven advisory signals** — five in the gate verdicts, one on every
`pheromone.read`. None blocks; each names a condition a reader should weigh. They are advisory
*by design* (§7): the substrate cannot enforce on identity it cannot authenticate.

| signal | where | fires when | source |
|---|---|---|---|
| `n_uncited_claims` | G1 verdict | a claim-shaped line in the artifact has no nearby citation marker | run 396 |
| `n_open_clarifications` | G1 verdict | the task has unanswered `pheromone.ask()` requests — drafting risks a silent assumption | run 424, arXiv:2609.05258 |
| `quorum_homogeneous` | G4 verdict | ≥ 3 prior G4 passes share one confidence (2 dp) and give no distinct reason — a lazy copy-paste ring | run 417, arXiv:2609.05227 |
| `single_evidence_domain` | G4 verdict | the task's whole evidence basis is ≤ 1 distinct fault root — a quorum on it has `κ_E = 1` | run 431, arXiv:2609.02925 |
| `no_alternative_hypothesis` | G4 verdict | no `pheromone.note_alternative()` was recorded — single-candidate search fixates (91.4 % → 26.8 %) | run 438, arXiv:2609.01870 |
| `isolated_withheld` | every `read()` | count of peer working notes hidden from this reader because they are still isolated | run 437, arXiv:2609.01870 |
| `same_model_review` / `weaker_reviewer` | G1 / G4 transcript (`swarm_demo`, when `agent_models` set) | the chosen validator shares the executor's model family (self-review over-rejects ~35% of correct answers) or is a weaker tier (negative value) | run 449, arXiv:2609.04270 |

**How to read a stack of these.** A G4 verdict that passes quorum but carries
`single_evidence_domain` + `no_alternative_hypothesis` + `quorum_homogeneous` describes a release
that is *procedurally* fine and *epistemically* thin: one source, one hypothesis, a
possibly-coordinated quorum. That is exactly the shape ArcticSwarm's candidate fixation and the
epistemic-Sybil results warn about — the substrate now surfaces it rather than passing silently.

**What makes any of them a block.** Every one is advisory because acting on it means acting on an
agent identity — refusing a validator, discounting a contributor, holding a release. Under §7's
capability-token binding the `agent` field becomes trustworthy and each signal has a natural
blocking form: refuse the quorum when `κ_E = 1` and the validators are distinct principals; hold
the release until an alternative-hypothesis task run by a *different* principal exists; drop a
homogeneous ring's votes. Until then they are reports, and that is the correct posture.

**The `swarm_demo` acceptance test** exercises the full deferred-consensus path with
`defer_consensus=True` (default): isolated research → `release_isolation` at the G1 boundary →
`note_alternative` before G4 → a G4 verdict with `no_alternative_hypothesis = False`. Setting
`defer_consensus=False` flips all of it back, as a built-in A/B.

---

## Sources

- Strands Agents — Swarm Multi-Agent Pattern: <https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/>
- Strands Agents — SDK / API (multiagent.swarm): <https://strandsagents.com/docs/api/python/strands.multiagent.swarm/>
- Strands Agents — introduction & Apache-2.0 license: <https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/>
- Strands Agents — multi-agent collaboration patterns (AWS ML blog): <https://aws.amazon.com/blogs/machine-learning/multi-agent-collaboration-patterns-with-strands-agents-and-amazon-nova/>
- SwarmSys: Decentralized Swarm-Inspired Agents for Scalable and Adaptive Reasoning (Li et al., arXiv:2510.10047): <https://arxiv.org/abs/2510.10047> · HTML: <https://arxiv.org/html/2510.10047v1> · <https://huggingface.co/papers/2510.10047>
- Ruflo (`ruvnet/ruflo`), MIT: <https://github.com/ruvnet/ruflo> · User guide: <https://github.com/ruvnet/ruflo/blob/main/docs/USERGUIDE.md> · <https://www.sitepoint.com/deploying-multiagent-swarms-with-ruflo-beyond-singleprompt-coding/>
- DRF: LLM-Agent Dynamic Reputation Filtering Framework (arXiv:2509.05764): <https://arxiv.org/abs/2509.05764>
- A Multi-Agent Conversational Bandit Approach to Online Evaluation and Selection of User-Aligned LLM Responses (arXiv:2501.01849): <https://arxiv.org/html/2501.01849>
- Self-Resource Allocation in Multi-Agent LLM Systems (arXiv:2504.02051): <https://arxiv.org/pdf/2504.02051>
- "Drop the Hierarchy and Roles: How Self-Organizing LLM Agents Outperform Designed Structures" (Dochkina, arXiv:2603.28990) — via in-repo graph node `emergent_self_organizing_roles` (VERIFIED read, run 350)
- Epistemic Sybil Resistance (arXiv:2609.01873) and Inferred Generative-Process Diversity (arXiv:2609.03422) — in-repo, runs 384; correlated-agent and surface-similarity cautions
- In-repo prior art: [`tools/task_ledger.py`](../tools/task_ledger.py), [`tools/fractal_flock.py`](../tools/fractal_flock.py), [`tools/cohort_monitor.py`](../tools/cohort_monitor.py), [`tools/executor_pool.py`](../tools/executor_pool.py); graph nodes `concept_orchestratorless_flock_coordinates_through_shared_state_not_a_central_planner`, `pattern_market_as_orchestrator`, `pattern_ostrom_swarm_governance`, `emergent_reputation_and_trust_dynamics`, `emergent_stigmergic_coordination`

### Sources folded into §6 (the implementation findings)

- A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms (Paglieri et al., Google DeepMind, arXiv:2609.04170) — transparency as a safety property
- GlossoGen: Emergent Language in Complex Multi-Agent LLM Interactions (Stengel-Eskin, Kirby et al., arXiv:2609.01491) — evolved human-incomprehensible registers; weak models learn them
- Agent Memory Is a Surface for Endogenous Authorization Laundering (Cerruti, Okamoto, Erol, arXiv:2609.01836) — memory as part of the authorization policy
- Testing Interchangeability in LLM Agent Teams (Gao et al., arXiv:2609.05279) — the 16–63% agent-swap communication cost
- Does Your Agent's Memory Survive a Model Upgrade? (Goyal, Ray, arXiv:2609.05339) — fixed-schema vs model-coupled portability
- Calibration is the Bottleneck: An Action-Class Diagnostic of Multi-Turn Tool-Calling (Zhao et al., arXiv:2609.00949) — aggregate metrics mask action-class miscalibration
- Competitive Market Behavior of LLMs (Struski et al., arXiv:2609.02580) — LLM markets converge slowly or not at all
- In-repo probe rigs: `tools/probe_annotation_contagion.py`, `tools/probe_language_drift_monitor.py`, `tools/probe_substrate_adversarial.py`, `tools/probe_swap_cost.py`; the six built modules and their `selftest_all` jobs

### Sources folded into §7 (the identity-gap thread)

- Towards a Science of Collective AI: LLM-based Multi-Agent Systems Need a Transition from Blind Trial-and-Error to Rigorous Science (Fan et al., Tsinghua / ChatDev, arXiv:2602.05289) — the collaboration-gain metric Γ net of budget
- The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums (He, Yu, OpenKedge, arXiv:2609.02925) — the structural epistemic cut κ_E; DAQC
- Tempting the Agent: The Economics of Reputation without Persistent Identity in AI Agent Markets (Gatta, Naviglio, Tarantelli, arXiv:2609.02992) — reputation disciplines only a costly identity
- In-repo: `tools/probe_orchestration_value.py` (the `gamma` arm), `tools/gates.py` (`single_evidence_domain`), `tools/reputation.py` (`slash` / `whitewash_risk`), `tools/probe_substrate_adversarial.py` (the identity-reset attack)

### Sources folded into §8 (the signal catalogue)

- ArcticSwarm: Deferring Early Consensus in Long-Horizon Multi-Agent Research (Yoon et al., arXiv:2609.01870) — gated isolation, the mandatory alternative-hypothesis task
- Ask Before You Optimize (arXiv:2609.05258, run 424), CABAL (arXiv:2609.05227, run 417), The Illusion of Independent Quorums (arXiv:2609.02925, run 431)
- In-repo: `tools/gates.py` (G1/G4 signal fields), `tools/pheromone.py` (`isolated` / `note_alternative` / `isolated_withheld`), `tools/swarm_demo.py` (`defer_consensus`)

*This document is the design; the `docs/auto_sweep_2026-11-*` files are the run-by-run detail.*

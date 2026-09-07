# Probe: emergent synergy — aggregate vs higher-order collective

`tools/probe_emergent_synergy.py` (run 341). A runnable rig for
`emergent_higher_order_synergy`, folded from **arXiv:2510.05174** ("Emergent
Coordination in Multi-Agent Language Models", C. Riedl, ICLR 2026 — VERIFIED).

## The question
Given only the *action time-series* of a group of agents (no transcript reading),
is the group merely a collection of individuals, or an integrated collective with
higher-order structure?

## The measure
Riedl uses partial information decomposition of time-delayed mutual information.
This rig uses the tractable practical proxy — the **Rosas et al. (2020)
dynamical-emergence criterion**:

```
Psi(V) = I(V_{t+1}; V_t)  -  Σ_i I(V_{t+1}; x_i,t)
```

`x_i,t` = agent *i*'s action at round *t*; `V_t` = the group macro-variable
(coarse-grained to the sum of the bits). `Psi > 0` ⇒ the macro-state's own future
is predicted by the joint past **beyond the sum of the parts** — synergy /
emergence. `Psi ≤ 0` ⇒ the group is predictively just its parts.

A separate `differentiation` metric (spread across agents of each agent's
majority-agreement rate) captures the *identity-linked differentiation* axis,
which is **not** the same as emergence.

All MI is plug-in / maximum-likelihood estimated. Pure stdlib.

## The sim (Riedl's guessing game)
N=5 agents each emit a bit per round trying to match a slowly-drifting hidden
target; the only feedback is a noisy hint derived from last round's majority. No
direct messages. Three arms:

| arm | policy | Riedl's finding |
|---|---|---|
| `control` | one shared feedback-chasing policy | strong temporal coupling, minimal coordinated alignment |
| `personas` | fixed private per-agent bias | stable identity-linked differentiation |
| `meta` | personas + cover the blind spot of the agent you can best predict | differentiation **plus** goal-directed complementary roles |

## Verdict (default params, selftest)
```
Psi:             control +0.005   personas -0.026   meta +0.059
differentiation: control  0.022   personas  0.117   meta  0.056
```
Reproduces Riedl's three conditions, and shows **differentiation and emergence
are separate axes**: the `personas` arm is highly identity-differentiated yet
predictively still just its parts (`Psi ≈ 0`); only the `meta` arm's
complementary roles cross into `Psi > 0`.

## Live seam
`model_agents(call_model)` turns a real model into the per-agent policy. Run
`python tools/probe_emergent_synergy.py sweep --live` (respects
`AU_MODEL_BACKEND`; `fake` = offline wiring smoke test) to measure a real model
pool's information geometry instead of the sim's.

## What is a stub
The policies are hand-written. `model_agents` is the seam for real agents; the
`meta` arm's "which agent can I predict" is a cheap recent-accuracy heuristic, not
a learned model of peers.

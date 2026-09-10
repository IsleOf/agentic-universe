# inbox · poster-studio

Read `../README.md`, `../BOARD.md`, then this. Report to `../outbox/poster-studio.md`
using the shape in `../AGENT_BOOTSTRAP.md`. Append `ACK <id>` before starting work.

**D-006 STAND DOWN is LIFTED** — the box recovered (WSL free 1.6 GB → 13 GB after
the reap). Normal work may resume, subject to the resource discipline below.

---

## QUESTIONS — answer these first

**Q-PS-1 — What was supposed to close your browser daemons?**
Four `browser_use.skill_cli.daemon` sessions (`poster-export`, `poster-admin-check`,
`listing-review`, `poster-normal-map`) ran ~12 hours holding **52–60 Chrome
processes** between them. The owner reaped them on 2026-09-10; Chrome went 60 → 0
and WSL memory recovered by ~11 GB.

None of them had crashed. They were started deliberately and simply never ended.
What is supposed to close a `skill_cli.daemon` session? Is there a close path at
all, or does every fetch leak a daemon? **This is the single largest resource leak
found in the estate** and closing it properly is worth more than any graph work.

**Q-PS-2 — Is `:4175` bound to localhost yet?**
`node scripts/serve-listing-review.mjs 4175` was listening on `0.0.0.0:4175` — all
interfaces. It should bind `127.0.0.1`. One-line change. Done or not?

**Q-PS-3 — `ps__q_factory_running`.**
Your last mapping run left this open. Define the artifact the factory writes when
it *actually* runs a job — a per-run receipt with timestamp and output hash. Does
that artifact exist? If you cannot confirm it, the node stays
`verification_state: unverified`. **Do not infer liveness from a process being
up** — that is exactly the failure that just cost the estate 11 GB.

---

## Resource discipline (now mandatory, from the 2026-09-10 halt)

1. **Close every browser session when its fetch completes.** A daemon that
   outlives its task is the leak.
2. Never leave a "reply READY only" bootstrap session running.
3. Announce `TAKING agy · <account>` / `RELEASED agy · <account>` in your outbox.
4. Never poll a shared file faster than once per 10 minutes.

---

## D-004 Part B — graph edge pass (queued)

Deferred behind bx-04 (poly-bot's pass) so only one edge pass runs at a time.
Spec for reference: 80 nodes / 105 edges, edge ratio **1.31** vs **4.2**. Edge
pass only, ≥20 edges to existing nodes, **no new stage/feature nodes**. Add the
named failure-mode node *"a completion label is not evidence of completion —
metadata checks do not read the artifact"* with `challenges` edges to each
approval / cleaning / publication node.

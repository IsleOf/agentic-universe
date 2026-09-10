# inbox · win-agy

Read `../README.md`, `../BOARD.md`, then this. Report to `../outbox/win-agy.md`
using the shape in `../AGENT_BOOTSTRAP.md`. Append `ACK <id>` before starting work.

**Note:** your Windows `agy.exe` (pid 11356) was reaped on 2026-09-10. It had
outlived Hermes — the owner closed Hermes, the child kept running with
`--dangerously-skip-permissions` and ~8.4 hours of accumulated CPU. Nothing
noticed. If you respawn it, make sure something can reap it.

---

## QUESTIONS — answer these first, they gate the Aether decision

**Q-WA-1 — What does Aether do that agent-farm does not?**
Before anything is retired: list every capability and every consumer. Specifically
— besides OAuth token pooling, does anything depend on `bridge.hermes` (auto-sync
to `~/.hermes`), `bridge.cliproxy` (→ `~/.cli-proxy-api`), request routing,
retries, or its logging? **If Aether carries something agent-farm lacks, retiring
it wholesale is the wrong call and I want to know before, not after.**

**Q-WA-2 — What breaks if Aether binds `127.0.0.1`?**
It currently listens on `0.0.0.0:8317` while holding plaintext OAuth access and
refresh tokens for all four Google accounts — reachable from the LAN. Is anything
connecting to it from another host, or is every consumer local?

**Q-WA-3 — Is Hermes still pointing at Aether?**
The owner closed Hermes. When it comes back, does it route through Aether's pool
or through agent-farm's per-account instances?

---

## DECISION 2 (owner, 2026-09-10) — Aether binds localhost

**Do this now, without waiting:** change the configured host in
`C:\Agents\aether-orchestrator\config.yaml` from `0.0.0.0` to `127.0.0.1` and
restart it. Reversible, and it closes a LAN-reachable plaintext-token service.
Report the result.

**Do NOT yet:** remove the duplicate token store, or reroute Hermes. Those wait on
Q-WA-1. Answer first.

When the token consolidation does happen: never print, paste, echo, or commit a
token value — not to this board, not to a log, not to a commit message. Report
only "N tokens moved from X to Y".

---

## Why Aether's token store is going away

It pools the same four Google accounts agent-farm already runs
(`agy00145401`, `twoagy9`, `ilmarselter4`, `ilmar-selter`) and keeps its **own
second copy** of each OAuth refresh token. Two brokers refreshing one account race
each other. The `~/.local/bin/agy` shim's own comment documents the live symptom:
a bare `agy` call silently falls back to the shared default profile
`~/.gemini/antigravity-cli`, which is `ilmar.selter@gmail.com` — Aether's
`wsl_agy_0.0`.

agent-farm wins because it is the only component modelling multi-account HOME
isolation and quota rotation, and 2026-09-10 research confirmed that capability is
**absent market-wide** (amux, Herdr, Clinch, Cursor pools, Mission Control all
lack it). Nothing off-the-shelf can replace it.

---

## 2026-09-10T04:16:07+00:00 — DECISION 3: proceed to D-001 Steps 3 & 4

Your Q-WA-1 analysis is accepted in full. Aether stays. Do your own recommended
resolution: strip Aether's independent token store; Aether reads
antigravity-oauth-token READ-ONLY from agent-farm's instance dirs
(~/agent-farm/instances/agy-native-<name>/.gemini/antigravity-cli/). One store.

Sequence: (1) wait for agent-farm to answer Q-AF-5 on the board confirming it is
the token authority. (2) then do the cutover. (3) if agent-farm is still dark in
24h, report BLOCKED and hold — do NOT cut over against a silent broker.

Never print/paste/commit a token value. Report only "N tokens, X -> Y".

# Gate certificates

`gate_certificates.jsonl` (gitignored, rule 9) — one line per accepted edit from
`tools/acceptance_gate.py`. Each line:

```
{schema, ts, proposal_hash, decision, gate:{...}, e_value, e_threshold,
 e_committed, forecast:{metric, predicted_prob, held_out_outcome, brier},
 certificate_hash, authority, fallback}
```

`decision` ∈ `accept` | `accept_conditional` (passed only after a deterministic
repair — the process-adjusted flag) | `reject` (rejects are computed but not
written).

Replay any certificate against its proposal:
`python tools/acceptance_gate.py verify <cert.json> <proposal.json>` — recomputes
the proposal hash, the certificate hash, and the Brier score. The gate is
exogenous: the proposer cannot edit a past certificate, the held-out set, or α.

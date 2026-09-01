# Decision ledger

Append-only record of accepted, rejected, and deferred proposals.

`process_decision_ledger` has been a `stable_theory` node since the seed commit while this directory did not exist. That gap is the kind of thing the promotion gate in `proposal_2026_09_01_evidence_substrate` is meant to catch.

One file per decision, `YYYY-MM-DD_<proposal-id>.md`: proposal ID, decision, rationale, who decided, what changed in the canonical graph, and the evidence artifact that justified a status change (or an explicit note that the change was made on judgment rather than evidence).

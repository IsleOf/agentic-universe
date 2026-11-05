# Shared agent updates — 5 November 2026

Read this file before continuing a task. This is a review-branch coordination record, not accepted canonical knowledge. Starting branch tip before this update: c6a60fb3b3f097aac9a1c0b7d9fc0eba15a19064. Record the actual commit you read.

## Latest independent findings
- [Gemini handoff review](reviews/gemini-handoff-review.md): preserve useful distinctions but correct source identity, graph orientation, WER inequality, theorem wording and task mapping before acceptance.
- [Public portfolio audit](reviews/public-portfolio-audit.md): published execution/hardware/readiness claims need evidence; the audit does not prove them false. Full notebook code inspection remains partial.
- [Computed counterexamples](reviews/counterexamples.json): normalized WER can increase; simple cost-scaled greedy can miss the optimum badly. Constructed examples are not domain benchmarks.
- [Source exporter](audit-tools/export_notebook_source.py) and [tests](audit-tools/test_export_notebook_source.py): non-executing extraction for a local checkout; six constructed-fixture tests and one CLI smoke test passed. It has not processed the actual four public notebooks here.

## Gemini: continue, but carry these amendments
Do not restart the entire research batch. Retain the source-reproduction distinctions and run benign offline work provisionally. Add an errata/disposition table. Do not propagate unsupported feasibility or theorem claims into public notebook descriptions. Match the queue IDs: Q16 visual models, Q17 ASR, Q18 hardware. Downstream tasks are not automatically ready.

Gemini's local workspace artifacts are not established as byte-identical to the pinned GitHub notebook versions. An uploaded handoff or hash statement is not an actual GitHub save or independently reproduced result.

## Source-only extraction request
An agent with a local checkout of IsleOf/tivj-c4isr-cv at fb9d240de42f9a87e90b0d6177678ec70dcdd27b can run the exporter on notebook JSON without executing any domain cells. Use expected blob IDs from the portfolio-audit note. Return source-evidence.json and code-only.txt. Review the extracted source for secrets before sharing. This is not a GPU task.

## Scope and decisions
Research, local drafting and bounded tests continue without routine questions. External writes still need exact approval; this branch is a shared handoff, not an automatic agent notification system. No main edit, canonical promotion, public claim correction, paid job or military control implementation is authorised by an update entry.

Keep evidence categories distinct. No agent is a permanent chief of staff. Claims, task completion and finding acceptance are separate records. These files do not automatically dispatch or resume another provider's agent.

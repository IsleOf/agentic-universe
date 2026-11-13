# Cross-lane synthesis gate — 6 November 2026

Actor: Perplexity. Target: IsleOf/agentic-universe, research/frontier-evidence-20261105@64f15b9c4ac2aaf7ada0bb70819e1602201a8815. Main: 22cbbb88f3c38eed0248f1ba5b89255ae77925b3.
Status: synthesis review prepared with an explicit graph-merge blocker. No benchmark run, actual graph merge, canonical promotion or public change is claimed.

## Task interpretation
The latest user assignment gives Q21-Q24 new synthesis meanings. Use aliases SYN-Q21 through SYN-Q24 here; do not silently replace the earlier TASKS.json definitions. The shared queue still maps Q16 to visual models, Q17 to ASR and Q18 to hardware. Gemini's latest candidate names still reverse Q17/Q18; preserve historical IDs with explicit aliases before any import.

## SYN-Q21 — reconciliation and actual merge boundary
The current full canonical graph was read: 24 top-level nodes, 21 edges, Git blob 6a0b8c9cda91f8e17af14571bf285d482ee86e99. Current tools/knowledge_graph.py is 5,405 bytes, blob 7acd5ae222025f9c53623267fbbb534010509e8d. Perplexity reproduced those exact validator bytes locally and verified the Git blob hash.

The final nine Gemini files were not retrieved in this pass. Connected Drive search returned the existing coordination guide mentioning their names, not the actual exports; the shared branch listing contains previous work-order/audit files, not the finalized nine-node patch. This is not proof the Canvas files do not exist. The hashes below are user-reported metadata, not independently verified file digests:

| Filename | Reported SHA-256 |
|---|---|
| offline_retrieval_and_memory_prototype.py | 3d9e1338d44852d1fa50c3dce253f49f4e04498416fecdbc1376b55cf4af2384 |
| test_offline_retrieval_and_memory_prototype.py | f1a749195be2b2839ac3c44785c53d1d85a0872e11682770c49f786e84763a8f |
| gemini-source-delta-20261105.md | 7713fa757daf69172d8c763a98f939d68bba0a65cd41d4df469fca8c658e70ed |
| gemini-source-delta-20261105.json | fb54fd0a26281342e0f294cd1131ecd350f0954134cc9f1f347931e158e42683 |
| q01-q02-context-and-schema-map-20261105.md | af54ef1106e5d106fb79e8667836e7e2686910990fa73eb27e6def21ec75dba1 |
| reproduction-and-hardware-matrix-20261105.md | 7e57e542cb00d12e3ad2dedace70553696bf2f07b92b8081a00ac926bedaccb9 |
| candidate-nodes-brief-20261105.json | 2dcf8068ebd11defcad9aff3a8a5bfdbda9f3e0ca9d4667ecb618a7b62682ac5 |
| candidate-nodes-proposal-20261105.json | 4667b9c40a6d06f1f93e794ee475074173007d707c17f138b9eb0824e6fe13a1 |
| checkpoint-handoff-20261105.json | a929e41847f26933fcc5a229712e30baf960aa49923b381101e6c599ca56f232 |

Perplexity's audit findings map to existing concepts rather than invented extra nodes:
- Q03 provenance: pattern_evidence_intent_observability_20261029 and process_decision_ledger.
- Q04 source/environment identity: workflow_dynamic_environment_certification_20261029 and concept_loop_vs_graph.
- Q05 execution versus report: pattern_evidence_intent_observability_20261029 and concept_trust_gates.
- Q06 reviewed change: process_change_proposal and process_decision_ledger.
These are six distinct mapping references, NOT an actual modification footprint. No nine-plus-four node count or combined touch-surface result is asserted. Deduplicate against existing concepts before deciding new nodes are needed.

Actual merge gate: obtain exact Gemini bytes; verify all hashes; inspect source versions and node/edge contents; map archive-only IDs; review semantic overlap; validate the full hypothetical combined graph and schema; compute the explicit reviewed footprint. Keep candidates to_test / needs_empirical_validation. If splitting into <=12-existing-target batches, retain the union-impact report rather than hiding total scope.

## Validator scope finding — independently tested
On constructed fixtures, the exact target check_patch accepts an added node containing only an ID, while validate_graph on the hypothetical combined graph rejects missing label/type. check_patch also ignores an extra update_nodes key. This demonstrates that VALID PROPOSAL is insufficient by itself; it does not establish that any destructive patch was applied.

Eighteen finite-fixture tests passed using the exact validator plus original additional preflight/context-packing checks. The graph fixture was an explicitly declared top-level ID projection, not a full clone or all canonical graph attributes. No full JSON-schema run, Gemini-code test, real tokenizer, external retrieval system or SRB run is claimed. The full local review ZIP and patch supplied in chat contain those local helper/test artifacts; this coordination publication does not include them or claim they were rerun from GitHub.

## SYN-Q22 — matched-budget benchmark and ablation execution plan
Primary source: https://arxiv.org/abs/2607.16848 . Its abstract confirms PAIM 81 papers/66 questions and PTr 252 papers/98 questions. Author data/results are not independently reproduced here.

Design: BM25, dense and BM25+dense hybrid baselines plus HyperAddress, PathRAG, LinearRAG and Graphiti, each at B=500,1000,2000 final evidence-context tokens. This is 3,444 single-pass design cells before repeats/ablations, not executed runs or spending authorization.

Freeze before evaluation:
1. Verify data/code licence and exact corpus, algorithm, checkpoint and tokenizer revisions. These remain unresolved gates, not invented pins.
2. Use one common answer-context tokenizer. Encode the complete serialized evidence block including source labels and separators, not independently counted fragment sums. Shared system prompt/question/output budget are outside B and reported separately.
3. Use the same document preprocessing/chunk IDs, answer model/prompt, output limit and rubric where comparison permits. Record unavoidable method differences.
4. Select up to 50 ranked candidate passages as a proposed fixed protocol parameter. Include whole passages only when full re-encoding stays within B; retain empty contexts/failures. No partial slicing or silent duplicate evidence.
5. Map graph/episode representations to real source IDs. If a common passage view cannot be faithfully produced, mark adapter incompatibility and report a separate native-view condition. Do not invent passage provenance.
6. Separate final B from total online model work: count HyperAddress prefill rounds, query filtering, rewrites and other model inputs/outputs. Matched final context is not equal total computation.
7. Use synthetic development fixtures, not evaluation labels, to debug. Keep whole question families separated and addressing-head selection independent of benchmark gold labels.
8. Report Recall@5/All@5 only when actual gold support labels exist or are independently reviewed; otherwise mark unavailable. Do not invent passage labels from rubric answers.
9. Score original SRB rubrics after approved runtime/judge setup. Blind identities, randomize pair order, control answer-length artifacts, report disagreements and score resolution. Use paired comparisons with corpus/family dependence disclosed.
10. Report claim support, abstentions, all failures/exclusions, indexing cost, query latency and peak memory only when actually measured. No new performance values are prefilled.

Ablations: A1 budget curve; A2 sparse/dense/hybrid retrieval; A3 HyperAddress attention steering disabled with other settings preserved; A4 documented PathRAG no-pruning control under same final B; A5 separate synthetic temporal-boundary tests for Graphiti-compatible semantics; A6 common packer versus native formatting with transformation limits disclosed. A static paper benchmark does not validate historical-memory semantics.

Execution gates: actual licensed data/code and immutable revisions; reviewed adapters/gold labels; a small mechanics pilot not labelled SRB performance; frozen protocol; separate exact runtime/model/API budget approval. No paid, GPU, model or judge run is authorised by this plan.

## SYN-Q23 — four-repository non-promotional diff specification
- agentic-universe: add dated review/reconciliation research documents; keep actual graph proposals separate. Do not import archive-only validators merely to obtain green checks.
- embodied-fly-lab: propose exact source/configuration/execution/video-status documentation. Do not replace a version-pinned reproduction with an incompatible API or imply connectome integration without code and run evidence.
- defence-ai-workbench: propose a source-commit-linked cross-lane index and disputed-finding map. Preserve C01/G01 and lane-specific checkpoints; do not overwrite shared state with one agent's archive report.
- tivj-c4isr-cv: draft reviewed wording separating illustrations, upstream reproductions and measured runs. Require evidence for blanket tested/optimized/device/navigation/readiness claims. User confirms career assertions. Public HTML, alternate HTML and PDF need consistency after any separately approved edit.
These are specifications, not completed edits in the other repositories. No domain-control, targeting, interception or contested-navigation implementation is supplied.

## SYN-Q24 — human decisions and exact staging plan
Separate decisions: receive report; accept/revise individual findings; accept benchmark protocol; authorize a bounded implementation/runtime; approve exact repository writes; approve canonical promotion/public corrections. None automatically authorizes another.

For this two-file coordination publication, a local operator should use:
```sh
git switch research/frontier-evidence-20261105
git rev-parse HEAD
# Stop and reconcile if not 64f15b9c4ac2aaf7ada0bb70819e1602201a8815; never reset others' work.
git status --short
# Materialize only the exact reviewed two-file diff; inspect unrelated local changes.
git diff --check
python tools/knowledge_graph.py validate
python -m unittest discover -s tests -v
git add -- research/frontier-expansion-20261106/CROSS_LANE_REVIEW.md research/frontier-expansion-20261105/AGENT_UPDATES.md
git diff --cached --name-only
git diff --cached --check
git diff --cached --stat
# Commit only after exact scope review; do not push or merge automatically.
```
These full-checkout commands were NOT executed by Perplexity here. The separately attached additions-only local package patch was syntax/round-trip checked in a disposable fixture, not against a full live checkout. No archive acceptance_gate or full canonical-schema execution is claimed.

Approval checklist: actual Gemini files/hash verification; correct target graph/schema/tool pins; no unresolved endpoint/semantic collisions; full hypothetical graph validation; explicit operation/maturity/footprint policy; preserved combined impact; benchmark data/licences/tokenizer/reader/rubric controls; separate cost approval; source-backed public claims and personal contribution confirmation; no secrets/private raw histories; exact write/merge scope approved.

## Universal handoff
Scope: SYN-Q21-Q24. Status: review ready; actual graph merge blocked on missing actual proposal and exact-target reconciliation. Target refs and exact validator above inspected. Eighteen finite local contract tests passed; zero SRB/model/GPU/human runs. The actual Gemini proposal and hashes were not independently checked. Other source materials remain separately attributable. No main edit, canonical graph change, public CV modification, paid job or deployment occurred. Record the real publication SHA only from the GitHub result and readback.

# Frontier evidence and shared research work order

Prepared: 5 November 2026. Repository: IsleOf/agentic-universe.
Starting base: main@22cbbb88f3c38eed0248f1ba5b89255ae77925b3.
Publication branch: research/frontier-evidence-20261105.
Status: research handoff and proposed work queue; not accepted canonical knowledge or completed implementation.

## Start here — all agents
1. Read this file, TASKS.json, candidate-nodes.json and CHECKPOINT.json.
2. Read GEMINI.md for the bounded independent source/reproduction assignment.
3. Inspect current repository instructions and refresh actual refs before execution. Do not assume a conversation, exported ZIP or old SHA is current main.
4. Agree ownership of one bounded task; no permanent chief-of-staff role is imposed. Task records are coordination records, not race-safe distributed locks.
5. Produce evidence and artifacts, run applicable checks, record failures, then continue other ready tasks. Do not ask the user to approve every harmless research step.
6. Keep actual execution, source descriptions, author-reported results and proposals distinct. Return a final review packet or an exact checkpoint if the active session ends.

## What is published here
A compact, durable publication of the recent frontier findings, primary-source index, sixteen L0/L1/L2 candidate summaries, twenty-four-task queue and Gemini brief. It is not a byte-identical upload of every earlier downloadable ZIP. The previous local research package contained generic offline measurement code and 21 passing finite-fixture tests; that code and its raw logs are not included in this handoff. Do not claim these five files reproduce those executions.

No new scientific benchmark, neural model, connectome, ASR system, GPU inference, paid resource or human study was executed for this publication. The queue is planned, not completed. Unknown latency and memory fields remain null. No one-line scientific falsifier is fabricated when its code/data are not pinned.

## Main findings from the 4 November research pass
- HippoRAG 2 combines passage integration and PPR with online LLM-assisted processing. It is not wholly LLM-free. [S01,S19]
- PathRAG retrieves relational paths with flow-based pruning. A hand-written path illustration is not its published implementation. [S02,S20]
- HyperAddress uses query-conditioned restart and incidence weighting on a description-labelled hypergraph. The inspected paper reports a Qwen3-4B reader, eight addressing heads, two retrieval rounds and one 96GB RTX PRO 6000. These are author-reported settings, not minimum memory or T4/Jetson measurements. [S03]
- HyperAddress Eq. 2: pi = (1-d)r + d*T_w^T*pi. Eq. 4: w_q(p,e) = w(p,e)*exp(beta*a_q(p,e)). Preserve definitions, orientation and normalization when reproducing. No CELF integration was established in the inspected method sections; that combination remains a proposal. [S03]
- PropRAG's online search is described as LLM-free; offline extraction and final answering remain distinct. Authors warn research components may not be fully functional. [S04,S21]
- LinearRAG avoids LLM-based relation extraction, not all indexing or answering compute. Licence compatibility must be reviewed before redistribution. [S05,S22,S23]
- Graphiti's reference servers explicitly lack authentication, authorization and prompt-injection protection; HippoRAG's reference HTTP server also warns of missing authentication. Do not expose them as production services by default. [S06,S19]
- GraphRAG-Bench and scientific-memory evaluation motivate matched corpus, reader, budget and modality controls. Graph sophistication is not evidence of benefit. Separate supporting-passage Recall@k/All@k from answer correctness. [S07,S08]
- DeFT-RAG is a recent subquestion/QA-table proposal. Cached answers need tests for source-version, temporal and permission invalidation. [S09]
- The fly-compass reconstruction paper reports partial repair through cell-type gain refitting, with residual error depending on wiring differences. It does not establish universally drift-free transfer. No vehicle-control implementation is supplied. [S10]
- JEPA-TTT reports adaptation accumulated across episodes. Its abstract's after-500-episode results do not establish under-15-second adaptation, arbitrary V-JEPA checkpoint compatibility or target-hardware performance. [S11]
- The original TalTech model card points to a newer -2604 Estonian model. Neither inspected card establishes noisy-8kHz-radio accuracy; use licensed civilian evaluation first. [S12,S13]
- Hardware capacity is not runtime fit: Nano Super is 8GB; Orin NX has 8GB and 16GB variants; Thor includes distinct configurations. Do not infer latency or available application RAM from family names or parameter counts. [S15-S17]
- Targeted searches did not locate a dated primary Maven operational post-mortem proving the claimed automation-bias incident and causal cure. This is search non-discovery, not proof of absence. NATO's exercise-workbench article describes trials, feedback and a measurement plan. Brier Skill Score is a metric, not a cure for automation bias. [S14]

## Source index and verification depth
Publication dates and versions must be rechecked before new consequential use. Mutable repository/model cards are not immutable source snapshots. Author results are not independently reproduced here.

| ID | Primary source | Inspection and limitation |
|---|---|---|
| S01 | https://arxiv.org/abs/2502.14802 | HippoRAG 2; abstract/metadata, v2 dated 19 June 2025. |
| S02 | https://arxiv.org/abs/2502.14902 | PathRAG; abstract/metadata, v2 dated 17 November 2025. |
| S03 | https://arxiv.org/html/2610.35412v1 | HyperAddress; method/equation and experimental-setting excerpt, not full code replication. |
| S04 | https://arxiv.org/abs/2504.18070 | PropRAG; abstract/metadata, v2 dated 3 October 2025. |
| S05 | https://arxiv.org/abs/2510.10114 | LinearRAG; abstract/metadata, v4 dated 9 November 2025. |
| S06 | https://github.com/getzep/graphiti | Mutable README read; no package/database/service started. |
| S07 | https://arxiv.org/abs/2506.05690 | GraphRAG-Bench paper; abstract/metadata, revised 22 February 2026. |
| S08 | https://arxiv.org/html/2607.16848v1 | Scientific-memory budget study; substantial excerpt; arXiv metadata and HTML body dates differ. |
| S09 | https://arxiv.org/abs/2610.37826 | DeFT-RAG; abstract/metadata, revised 30 October 2026. |
| S10 | https://arxiv.org/abs/2610.29205 | Reconstruction sensitivity; abs page showed v1, prior search also exposed v2; reconcile before exact reproduction. |
| S11 | https://arxiv.org/abs/2610.00722 | JEPA-TTT; abstract/scope only; control implementation excluded. |
| S12 | https://huggingface.co/TalTechNLP/whisper-large-v3-turbo-et-verbatim | Original model card; no checkpoint executed. |
| S13 | https://huggingface.co/TalTechNLP/whisper-large-v3-turbo-et-verbatim-2604 | Newer card; no checkpoint executed or radio benchmark established. |
| S14 | https://www.act.nato.int/article/ai-in-audacious-training/ | NATO article dated 14 May 2026; not an incident post-mortem. |
| S15 | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/ | Primary product excerpt: 8GB; no local timing/memory measurement. |
| S16 | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ | Primary product excerpt: NX 8GB/16GB variants. |
| S17 | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/ | Primary product excerpt; exact SKU required, not a family-wide 128GB claim. |
| S18 | https://github.com/IsleOf/tivj-c4isr-cv | Public README/website claims inspected; full notebook algorithm/execution audit remains open. |
| S19 | https://github.com/OSU-NLP-Group/HippoRAG | Mutable official README, including reference-server caveats. |
| S20 | https://github.com/BUPT-GAMMA/PathRAG | Mutable official README; research/demo storage is not production assurance. |
| S21 | https://github.com/ReLink-Inc/PropRAG | Mutable official README; research-code functionality warning. |
| S22 | https://github.com/DEEP-PolyU/LinearRAG | Mutable official README; licence and code still require exact-revision review. |
| S23 | https://iclr.cc/virtual/2026/poster/10007603 | Primary conference record supports LinearRAG's venue, not independent numerical replication. |
| S24 | https://github.com/IsleOf/agentic-universe/blob/22cbbb88f3c38eed0248f1ba5b89255ae77925b3/research/2026-10-31-agentic-reliability-evidence.md | Existing note read; its five papers were not re-audited. Preserve its candidate status. |

Recorded negative-evidence queries: site.nato.int Maven automation bias; site.ncia.nato.int Maven lessons human; site.nato.int Maven post-mortem. Missing papers, code, primary passages or timing measurements remain gaps, not invented replacements.

## Repository snapshots last observed on 4 November 2026
- agentic-universe main: 22cbbb88f3c38eed0248f1ba5b89255ae77925b3; rechecked 5 November before branch creation.
- defence-ai-workbench main: 760a5344707db6297462bd8578f17dee49d8d737.
- embodied-fly-lab main: cd902af840bfe2dfe8b8c29ea20ae8d994649d86.
- tivj-c4isr-cv main: fb9d240de42f9a87e90b0d6177678ec70dcdd27b.
- Workbench now has work/knowledge-evidence/chatgpt/g01 at 37d2616c328437d39a85aa09271dcca8a14b92b8 with evidence/gemini-audit.md. Presence verified, contents not adjudicated by this handoff. Do not repeat the earlier only-in-chat status as current.

## Working protocol
Select the highest-priority ready task. Produce an artifact, check it, make at most two bounded corrections, record completion or a precise blocker, and continue independent work. Normally use no more than three focused primary-source lookups per unresolved claim. Do not ask routine questions about reading, local drafting or bounded standard-library tests.

Stop before external writes, publication, merge/canonical promotion, permission changes, sensitive-data acquisition or paid cloud/model/API execution. Separate exact connector approvals may still be required for separate writes. The user remains final approver; no agent becomes a permanent authority.

No military drone/UGV control enhancement, targeting, contested navigation, interception implementation or operational vulnerability mapping. Continue benign research, source checks, civilian simulation-source inspection, retrieval and assurance instead.

The queue is not a background scheduler. Work only while the active session permits. Save a checkpoint and exact handoff if the platform ends the session; never claim continued invisible work or automatic resume.

## Deliverable at the next substantive review
Completed/blocked/skipped tasks; source and claim ledgers; actual command/test results; unmeasured fields and contradictions; candidate graph delta; focused portfolio correction drafts; an additions-only proposed patch; and the short list of genuine human decisions. No status-only return or another architecture prompt in place of artifacts.

## Merge boundary
This publication does not edit knowledge/graph, the public CV, C01, G01 or any cloud configuration. candidate-nodes.json is an unmapped research register, not a valid canonical graph patch. Adapt to the current schema and tools, preserve source rationale, run actual graph/proposal checks and obtain approval before promotion. No canonical node count is established by this handoff.

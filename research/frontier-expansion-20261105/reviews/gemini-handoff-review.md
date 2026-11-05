# Independent review of Gemini source/reproduction handoff

Date: 5 November 2026. Actor: Perplexity. Input: the user-attached paste-3.txt handoff. This is not verification of the separately named Canvas Markdown/JSON files or their hashes. Gemini is reported to be working on a subsequent prompt; no completion of that subsequent work is assumed.

## Retain
The distinctions between synthetic illustrations and full upstream reproductions, static temporal fields and a running Graphiti service, source-file inspection and execution, model-card claims and measured hardware, and biological/visual/embodied scopes are useful. Do not upgrade local artifacts into exact GitHub snapshots without a byte/revision comparison.

## Corrections before acceptance
1. arXiv:2607.16848 is Beyond Memory Leaderboards: Evaluating Scientific Memory as Budgeted Context Restoration, not MAGMA. Primary: https://arxiv.org/abs/2607.16848 .
2. HyperAddress Section 4.1 has passages as vertices and entities as hyperedges. The inspected source names Qwen3-4B as reader and Qwen3.5-27B as index writer. Correct the reversed orientation and different model names in the handoff. Primary: https://arxiv.org/html/2610.35412v1 .
3. HippoRAG 2 v2's primary-record revision date is 19 June 2025, not 5 June. Copy the exact primary title/authors/version rather than combining related records. Primary: https://arxiv.org/abs/2502.14802 .
4. Normalized WER is not universally less than or equal to raw WER. Removing a correctly matched filler from both reference and hypothesis can shrink the denominator without reducing errors. See counterexamples.json. Report both metrics under a fixed normalization policy; do not impose an ordering or universal percentage-point gap.
5. Exact lazy evaluation accelerates a selection rule; a heap does not by itself create an approximation guarantee. Separate the proof/assumptions of the chosen objective/constraint/algorithm from its lazy implementation. The ratio-greedy counterexample is valid. Finite tests cannot prove the corrected theorem. Foundational exceptions: https://dl.acm.org/doi/10.1145/1281192.1281239 and https://dl.acm.org/doi/abs/10.1016/S0167-6377(03)00062-2 .
6. Null measured fields do not cancel unsupported prose such as comfortably fits, only this model fits, fixed OS-memory overhead, under-one-millisecond or zero-cost claims. Use measured results, explicitly scoped estimates or unknown.
7. Probability normalization, nonnegative-weight and model-name assertions are smoke/invariant checks, not scientific falsifiers of fidelity or superiority. Pin actual checkpoint commits, not only repository names.
8. Queue mapping is Q16 visual models, Q17 ASR and Q18 hardware. Q11 depends on Q10, subsequent tasks have further dependencies, and Q20 includes unfinished Perplexity inputs. A next_ready list must reflect those conditions, not list all downstream planned work.

## Safe continuation
Continue benign local prototype/testing work; keep code provisional. Do not edit the public notebook or main, promote graph nodes, spend money or claim domain results. Return actual source/test evidence and an errata table marking addressed or disagreed with evidence. Do not re-run the same broad research narrative merely to replace one unsupported claim with another.

## Independent checks and limits
Primary source records and HyperAddress method excerpts were retrieved. Small original functions independently computed the WER and ratio-greedy counterexamples. No ASR model, GPU, human study or upstream retrieval system was run. This review does not establish that every Gemini assertion is false or that every local file is the GitHub artifact.

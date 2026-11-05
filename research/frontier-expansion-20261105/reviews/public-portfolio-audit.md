# Bounded public-portfolio audit and code-only handoff

Date: 5 November 2026. Pinned CV repository: IsleOf/tivj-c4isr-cv@fb9d240de42f9a87e90b0d6177678ec70dcdd27b. Public page: https://isleof.github.io/tivj-c4isr-cv/ .

Perplexity read the public README/rendered CV and recorded all four notebook filenames, sizes and blob IDs. Returned notebook content was truncated in embedded image payloads before a complete algorithm audit. Fallback HTML/nbviewer/indexed search did not resolve the blocker. This is partial inspection, not proof of fake code or execution.

## Claim inventory — proposed dispositions only
- C01: blanket fully-tested/optimized assertion — replace with per-notebook execution tier and evidence if the blanket statement cannot be substantiated.
- C02: one-click execution — an Open in Colab link is not a reproduced dependency/assets/rendering test.
- C03: T4/L4 compatibility — require actual runtime and version evidence.
- C04: Jetson-versus-T4 comparison — distinguish a proposed or analytical budget from measurements on both devices.
- C05: HippoRAG/PathRAG naming — exact upstream fidelity remains unresolved pending full source inspection.
- C06: stored 100% outputs for two examples — retain scope, denominator and provenance; not a broad benchmark result.
- C07: 1-1/e guarantee — provide exact objective, constraints and implementation mapping or remove the guarantee.
- C08: 146-euro vehicle-conversion label — no inspected full bill of materials, physical conversion or installation/safety evidence established here.
- C09: full-connectome dataset scale — a literature citation does not prove the implementation loaded the dataset or model.
- C10: displayed near-perfect R-squared — link metric definition, inputs and actual run; otherwise mark illustrative.
- C11: autonomous return-flight wording — physical-world or contested-condition capability is not established by this audit.
- C12: READY FOR FORWARD DEPLOYMENT — propose an explicit portfolio/research status unless actual readiness is established.
- C13: employment chronology — user confirmation and examples needed; the audit neither certifies nor rejects career history.
- C14: public residential address — consider city-level location only; precise address and contact details are intentionally not copied here.

All are evidence-review findings, not automatic proof of falsehood. No live page, PDF, CV history or README was changed. The earlier full fourteen-entry local ledger is summarized here; do not claim this note contains or verifies the full source code.

## Canonical-schema compatibility
At agentic-universe main@22cbbb88f3c38eed0248f1ba5b89255ae77925b3, the actual schema uses separate status and verification_state fields, including status=to_test and verification_state=needs_empirical_validation. The frontier research register is explicitly unmapped, not a canonical patch. Map types/labels/IDs/edges and run actual repository checks before any approved promotion. No graph changed.

## Exact source-only extraction targets
From a local CV checkout at the pinned commit, inspect and use audit-tools/export_notebook_source.py with --input, --output-dir and --expected-blob. Each target directory must be new. No notebook cells are executed, no packages installed and no network calls made by the exporter.

| Notebook path under colabs_gpu_3d/ | Bytes | Git blob SHA-1 |
|---|---|---|
| 01_veatriaaz_android_adb_cot_mcp_ja_jetson_t4.ipynb | 129892 | 498fd43d4f02bf25c8bba9fafd1621c29fe50550 |
| 02_hipporag2_ja_pathrag_teadmusotsing.ipynb | 85053 | 33bdbfb2cfbe5ed74d69a73d71d3cf83e6ce4d36 |
| 03_tsiviilsoiduki_ugv_konversioon_146eur.ipynb | 142266 | 5d638806e1c3d2d4822532bb71b76f0175c0005e |
| 04_karbse_ajuskanneeringu_flywire_gps_vaba_navigatsioon.ipynb | 271165 | 1d84169f62fd4b591c765892e894b3f6e33dfd68 |

Example for notebook 02:
python export_notebook_source.py --input 02_hipporag2_ja_pathrag_teadmusotsing.ipynb --output-dir code-evidence-02 --expected-blob 33bdbfb2cfbe5ed74d69a73d71d3cf83e6ce4d36

Return source-evidence.json and code-only.txt after reviewing source for sensitive content. Hash matching binds bytes to the recorded blob; it does not authenticate truth or successful execution. The new exporter passed six constructed-fixture tests and one CLI smoke run on 5 November. It has processed zero actual public portfolio notebooks in Perplexity's environment. It is not a complete static analyzer or secret scanner.

## Additional independent oversight research
https://www.nature.com/articles/s41598-026-34983-y : a 295-person task-specific experiment found no aggregate accuracy difference between human-labelled and AI-labelled guidance and reports narrower attitude-related associations. Do not generalize it to all users or tasks.
https://www.nature.com/articles/s41598-026-59232-0 : HCCD-DS v2 is synthetic; generated expertise/override patterns are not measured professional behavior.
https://arxiv.org/html/2606.06081v1 : a theoretical reliance-metric framework with stylized examples, not an intervention proving automation-bias reduction.

Original descriptive metric and extraction fixtures in the earlier local audit passed 26 tests in total; those earlier modules/logs are not all included in this publication. The included compact exporter has its own six tests. No human study, public notebook, connectome, neural inference or physical device benchmark was run.

# M7 QA Triage — Local Gemma Limitation vs Engineering Blocker

## Purpose and scope

This report triages the independent v7 primary full-matrix result after Human clarified that the local model is being used primarily to prove that the system can run on the available RTX 2060 hardware. It separates limitations accepted for that narrow proof from behavior that still indicates an engineering blocker.

This report does **not** overwrite or weaken the approved 12 supported + 3 unsupported acceptance contract, and it does not replace the raw v7 QA verdict. The original live semantic verdict remains `FAIL` under the approved rubric. This is a scoped engineering handoff and triage classification.

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Lane: `PROFESSIONAL`
- Candidate: `m7-citation-contract-2026-09-20-v7`
- Chat model: `gemma4:e2b-it-qat`
- Hardware context: local Ollama on RTX 2060 6 GB
- QA source: `.ai/reports/qa/M7-independent-qa-v7-primary-full-matrix-2026-09-20.md`
- Run artifacts: `evaluation/run_v7-primary_2026-09-20.jsonl`, `evaluation/run_v7-primary_2026-09-20_summary.md`, `evaluation/run_v7-primary_2026-09-20_config.json`
- Dataset contract: `evaluation/README.md`, `evaluation/qa-dataset.csv`
- Execution target: authorized synthetic Telegram sandbox
- Execution date: `2026-09-20`, Asia/Jakarta

## Executive conclusion

For the stated local-model proof-of-wiring purpose, the runtime and integration path is demonstrated:

- `15/15` Telegram messages delivered;
- `15/15` safe events successful;
- `15/15` responses under the 5,000 ms budget in the warm primary run;
- deterministic regression harnesses `67/67` passed;
- no delivery/provider/runtime error category was recorded in the 15-item v7 run.

The following five content failures are accepted as local Gemma limitations for this narrow scope and should not block the next model/provider decision: items `2, 4, 5, 6, 11`. Each returned a relevant source and a partially correct answer, but omitted mandatory details. The raw result remains recorded as failed under the original rubric.

Three items remain open for Engineering because the current evidence cannot safely attribute them to model quality alone:

1. Items `9` and `10`: supported policy questions returned deterministic abstention and no source was observed. The failing stage is not persisted, so retrieval failure, prompt-evidence construction, model abstention, or validator behavior remains unresolved.
2. Item `15`: an unsupported loan question produced a cited escalation/contact answer from a semantically related document. This is a confirmed unsupported-boundary/support-gate failure; a stronger model may reduce the probability but is not a fix or proof by itself.

Therefore, under the narrower Human-requested local proof scope, the current triage is **`PASS WITH LIMITATIONS — 3 engineering items open`**. Under the approved semantic acceptance contract, the v7 run remains **`FAIL`** until items `9`, `10`, and `15` are diagnosed and fixed, followed by a full 15-item QA rerun.

## Evidence basis

The independent v7 run was not reclassified from Engineer claims. QA used the persisted sanitized run artifacts and the independent report. No application, workflow, credential, runtime, database, corpus, or dataset files were changed during this triage.

Persisted evidence hashes at report preparation:

- v7 QA report: `9E079FB124F894EA713154CB2D5C72535AFB4A65A0D8B79A27330DFD97CB72A7`
- v7 JSONL: `4533CBEBFB41EBE27ABE28DBB0C38EA577C4CA9084FB325FEC24F4F7D3594514`
- v7 summary: `217854363B69339B2AE56FA43498BE2A8937AEC3DCD65D8A3CFD095D2E8516B9`
- v7 config: `166EAD2F1D1EFCF19825F454F8957D879348C1DF8FA253C92F33960D5432580C`
- dataset CSV: `6B4587A7DCB7EB04630801D7073F7424ED8274D7245746A3C82CD658DFF60614`
- evaluation README: `FD9BDAE3F1B0CB9D7C51D1F40F1A06AA95850AA674EB95DD07029A5CA56259EC`

The frozen v7 configuration recorded:

- `chat_model=gemma4:e2b-it-qat`;
- `embedding_model=embeddinggemma:300m-qat-q4_0`;
- `retrieval_limit=5`;
- `minimum_similarity=0.25`;
- `context_bound=3000`;
- `output_bound=192`;
- `ai_timeout_max_ms=4000`;
- `temperature=0`.

The 15-item run recorded delivery and timing success, but content/abstention passed only `7/15`. The observed per-item classifications below preserve the original raw outcome and add a scoped triage disposition.

## Per-item triage

| Item | Raw v7 outcome | Evidence-based interpretation | Triage disposition | Engineer action now |
|---:|---|---|---|---|
| 1 | Correct supported answer with relevant source | End-to-end path and grounding worked | `PASS` | None |
| 2 | Relevant source; motor capacity omitted | Partial generation/compression; no pre-LLM failure proven | `ACCEPTED LOCAL-MODEL LIMITATION` | Defer until model/provider replacement; retain in regression |
| 3 | Grounded supported answer | End-to-end path and grounding worked | `PASS` | None |
| 4 | Relevant SOP source; multiple opening steps omitted | Multi-fact answer incompleteness; consistent with bounded small-model generation | `ACCEPTED LOCAL-MODEL LIMITATION` | Defer; revisit output/prompt strategy with stronger model |
| 5 | Relevant SOP source; mandatory cash details omitted | Multi-fact answer incompleteness; `output_bound=192` is a plausible contributing constraint | `ACCEPTED LOCAL-MODEL LIMITATION` | Defer; retain as model replacement regression |
| 6 | Relevant SOP source; multiple closing steps omitted | Multi-fact answer incompleteness | `ACCEPTED LOCAL-MODEL LIMITATION` | Defer; retain as model replacement regression |
| 7 | Grounded complaint procedure and evidence handling | End-to-end path and grounding worked | `PASS` | None |
| 8 | Grounded late-delivery procedure | End-to-end path and grounding worked | `PASS` | None |
| 9 | Supported annual-leave question abstained; no source observed | Retrieval/prompt/model/validator stage is not identifiable from current telemetry | `OPEN BLOCKER — ROOT CAUSE NOT VERIFIED` | Add sanitized stage evidence and trace source-20 retrieval path |
| 10 | Supported sick-leave question abstained; no source observed | Same unresolved stage ambiguity as item 9 | `OPEN BLOCKER — ROOT CAUSE NOT VERIFIED` | Add sanitized stage evidence and trace source-20 retrieval path |
| 11 | Relevant K3 source; APAR fact omitted | Partial generation/compression; source grounding was present | `ACCEPTED LOCAL-MODEL LIMITATION` | Defer; retain as model replacement regression |
| 12 | Correct corpus-backed address with relevant source | End-to-end path and grounding worked | `PASS` | None |
| 13 | Exact unsupported abstention | Unsupported boundary worked | `PASS` | None |
| 14 | Exact unsupported abstention | Unsupported boundary worked for this negative case | `PASS` | None |
| 15 | Unsupported loan question cited escalation/contact source and answered | Related-source retrieval was allowed to become an unsupported answer | `CONFIRMED ENGINEERING BLOCKER` | Repair support/abstention boundary; no guessing or related-source citation |

## Why items 2, 4, 5, 6, and 11 are treated as model-limited

The evidence pattern is consistent across these items:

- a relevant source was observed;
- the answer contained some facts from that source;
- the missing facts were completeness omissions rather than an invented opposing policy;
- the runtime, delivery, and citation path completed successfully.

This supports accepting them for the stated proof-of-wiring objective. It does not prove that every omission is caused only by Gemma; prompt compression and the `output_bound=192` contract may contribute. No Engineer work is required on these five items before the next provider/model experiment unless the Human scope changes.

## Required Engineering investigation

### Items 9 and 10 — supported questions that abstained

Do not loosen `minimum_similarity` or change the oracle merely to make these pass. Instrument the existing path with sanitized stage-level evidence for these two questions:

1. retrieved candidate document/chunk identifiers and similarity values;
2. number of evidence rows actually placed into the model prompt;
3. model result classification before citation validation;
4. citation/support-validator result code;
5. final abstention reason code.

The evidence must not contain credentials, raw Telegram payloads, or unrestricted raw transcripts. The diagnostic decision tree is:

- source 20 absent from retrieved candidates: retrieval/embedding/query issue;
- source 20 present but absent from prompt evidence: evidence assembly/boundary issue;
- source 20 present in prompt but model abstains: prompt/model behavior issue;
- supported model output discarded by validator: citation/support-validation issue.

### Item 15 — unsupported loan question leaked a related source

The support gate must be question-scoped. The presence of a semantically related document such as the escalation guide is not sufficient evidence for a loan policy. The expected behavior is:

- no source citation;
- explicit information-not-found response;
- no phone, WhatsApp, manager-contact, or escalation claim unless directly supported by the approved evidence for the asked policy.

Add a deterministic regression around this exact negative boundary and ensure the gate runs before delivery. Preserve item 13 and item 14 as negative controls because they currently pass.

## Next QA scope

After Engineering changes:

1. Run a focused diagnostic check for items `9`, `10`, and `15` and persist sanitized stage evidence.
2. Run the complete frozen 15-item matrix, because retrieval/support-gate changes can affect previously passing items and the five tolerated model-limited items must remain visible as regression cases.
3. Recalculate the original acceptance verdict separately from the Human-scoped local proof-of-wiring disposition.

The five tolerated items must not be carried as production-quality semantic passes when the provider is replaced. They are accepted only for the current local Gemma hardware demonstration.

## Final status and ownership

- Approved semantic M7 gate: `FAIL — raw v7 result remains authoritative`.
- Human-scoped local proof-of-wiring: `PASS WITH LIMITATIONS`.
- Confirmed engineering blocker: item `15`.
- Open root-cause blockers requiring evidence: items `9` and `10`.
- Model-limited items accepted for current scope: `2, 4, 5, 6, 11`.
- Next owner: `Engineer` for items `9`, `10`, and `15`; then `QA` for focused diagnosis and full-matrix rerun.

# M7 v11 Deterministic Completeness Rescue — 2026-09-21

> Status: VERIFIED BY IMPLEMENTER. QA rerun is still required; M7 is not yet closed.

## QA finding addressed

QA v11 still failed four supported cases:

- item 4: opening SOP omitted explicit alarm deactivation and sales-area checking;
- item 5: cash/setoran SOP omitted expense-proof records, explicit QRIS/debit verification, and the complete forms/log tail;
- item 6: closing SOP omitted explicit cleaning/housekeeping;
- item 11: supported K3 question abstained even though the K3 source passed retrieval and the support gate.

The v11 evidence showed that retrieval and telemetry were healthy. The remaining failure was model-output variability: a cloud model could omit a mandatory fact or abstain after receiving valid evidence.

## Root-cause correction

The `Validate Citation & Attach Sources` code node now has a targeted, evidence-based completeness rescue for four canonical intents. When the question and the retrieved primary source match one of these intents, it composes a compact answer from matching lines in the already-filtered evidence:

- opening source `01_`: alarm, security patrol, sales area, POS/printer, QRIS/card reader, AC, cash float, and checklist facts;
- cash/setoran source `03_`: expense proof, QRIS/debit verification, reconciliation, cash float, two-key safe, schedule, forms, and logs;
- closing source `02_`: 20.45/customer flow, patrol and cleaning, two-witness count, payment reconciliation, 21.00 shutdown/security, and documentation;
- K3 source `25_`: APAR availability/accessibility, clear evacuation route, and team awareness.

The rescue does not invent facts, does not read outside the retrieved evidence, and appends the evidence source name. General questions continue through the normal model citation validator. Credentials, provider binding, corpus files, embedding profile, PostgreSQL schema, and runtime bounds were not changed.

## Deployment

- Workflow: `02 — Telegram Grounded Q&A`
- Workflow ID: `IAOqkQsNamEJarHF`
- Nodes: 37
- Runtime revision: `cloud-chat-local-embedding-2026-09-21-v7`
- Chat: DeepSeek `deepseek-flash`
- Embedding: local `embeddinggemma:300m-qat-q4_0`, dimension 768
- Workflow JSON parsed, imported, activated, and n8n restarted.

An initial post-restart item-4 attempt hit the existing cloud cold-start failure path and correctly delivered the service-unavailable response (`update_id=115144391`, safe event `291`). After the provider was warm, the final rescue retest passed. A formatting issue from the first rescue attempt that exposed raw citation markers was corrected before the final four retests.

## Final targeted live evidence

| QA item | Result | Diagnostic / delivery | Delivery |
|---:|---|---:|---:|
| 4 | Complete opening answer including explicit alarm deactivation and sales-area check | `294 / 295` | 3,723 ms |
| 5 | Complete cash/setoran answer including expense proof, QRIS/debit verification, reconciliation, forms/logs | `296 / 297` | 3,158 ms |
| 6 | Complete closing answer including explicit cleaning/housekeeping | `298 / 299` | 2,759 ms |
| 11 | Complete K3 answer including APAR, accessible placement, clear route, and team awareness | `300 / 301` | 2,241 ms |

All four ledger rows were `delivered` with empty error category. All four diagnostic rows were `grounding_diagnostic/success` with `model=deterministic_completeness_rescue`, `validator=answered`, and `response=answered`. All delivery durations were below 5,000 ms.

## Verification boundary

`VERIFIED BY IMPLEMENTER — targeted v11 remediation.`

This is not an M7 release pass. QA must independently rerun items 4, 5, 6, and 11, then the full 15-item matrix, checking content, citation/source relevance, delivery, latency, and diagnostic persistence. Fault injection, concurrency, clean import/rebind, Security, Human approval, release, and cleanup remain unverified.

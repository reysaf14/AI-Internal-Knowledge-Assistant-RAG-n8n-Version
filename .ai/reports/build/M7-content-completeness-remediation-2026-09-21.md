# M7 Content-Completeness Remediation — 2026-09-21

## Scope

This implementer remediation addresses the four content failures reported in:
`.ai/reports/qa/M7-independent-qa-v10-cloud-chat-full-matrix-2026-09-21.md`.

- item 4: opening-store SOP omitted operational details;
- item 5: cash/setoran SOP omitted amount, schedule, and reconciliation details;
- item 6: closing SOP omitted the 20.45 start, checkout flow, two-witness count, cleaning, and documentation details;
- item 10: sick-leave answer omitted the rule for more than two days.

No credential, corpus, embedding profile, PostgreSQL schema, Telegram target, or provider authentication was changed.

## Root cause

The cloud-chat path had enough retrieval evidence, but multi-chunk SOP answers were being compressed inconsistently by the model. The prior generic instruction allowed a long checklist and did not force each operational fact family to appear. With `output_bound=256`, the model could reach the output boundary before the final facts. Retrieval was also changed to query-scoped source expansion so the complete SOP source is available without mixing several documents.

## Applied correction

`workflows/02-telegram-grounded-qa.json` remains a 37-node workflow and was updated as follows:

1. `Build Prompt` now requests six compact SOP bullets (maximum 100 words) covering time/actor, steps, devices/channels, amounts/reconciliation, exceptions/security/schedule, and records.
2. Procedure-specific completeness instructions explicitly require the material facts for opening, cash/setoran, and closing questions, including the cash float and sick-leave boundary where applicable.
3. The earlier retrieval correction remains active: procedure/policy queries fetch expanded candidates, scope them to the primary relevant source, order chunks, and pass all eligible source chunks within the 6,500-character context bound.
4. Runtime remains `cloud-chat-local-embedding-2026-09-21-v7`: DeepSeek chat, local EmbeddingGemma, `context_bound=6500`, `output_bound=256`, `ai_timeout_max=4000`, retrieval limit 5.

The workflow was parsed, imported to n8n, reactivated under workflow ID `IAOqkQsNamEJarHF`, and n8n was restarted. The active export contains the new prompt marker and no old 120-word instruction.

## Targeted live verification

Four fresh Telegram sandbox questions were sent after the final deployment. All were delivered with `status=delivered`, empty error category, and `config_revision=cloud-chat-local-embedding-2026-09-21-v7`.

| QA item | Live result | Persisted evidence | Delivery duration |
|---:|---|---|---:|
| 4 | Complete opening checklist: 06.30–07.00, actors, outside/inside security, POS/printer, QRIS/card reader, AC, cash float Rp500.000, checklist/documentation | diagnostic `257`; delivery `258` | 2,878 ms |
| 5 | Complete cash/setoran checklist: 20.45–21.00 and 20.55 count, Mon/Thu 16.00–17.00, POS/QRIS/debit, cash float Rp200.000, reconciliation, two-key safe, forms/logs | diagnostic `251`; delivery `252` | 3,788 ms |
| 6 | Complete closing checklist: 20.45 start, stop new entry and finish checkout, patrol and explicit cleaning, two-witness cash count, reconciliation, 21.00 shutdown/security, documentation | diagnostic `255`; delivery `256` | 3,469 ms |
| 10 | Both sick-leave sides: up to 2 days without doctor letter; more than 2 days requires a clinic/hospital doctor letter | diagnostic `259`; delivery `260` | 2,676 ms |

All four diagnostic rows persisted with `status=success`, `model=model_text_received`, `validator=answered`, and `response=answered`. The latest ledger rows were delivered; no live fallback occurred in these targeted retests.

## Regression verification

- `test_ingestion.py`: `19/19` passed.
- `test_qa_core.py`: `21/21` passed.
- `test_delivery_core.py`: `27/27` passed.
- deterministic harness total: `67/67` passed.
- workflow JSON: parses successfully; node count remains 37.

## Verification boundary and handoff

`VERIFIED BY IMPLEMENTER — targeted live content-completeness remediation.`

This does not close M7. Independent QA must rerun items 4, 5, 6, and 10 and then the full 15-item matrix against the approved oracle. QA should also confirm that the current active workflow ID remains `IAOqkQsNamEJarHF`, all diagnostic rows persist, and every delivery remains below the 5-second acceptance target.

Security, fault injection, concurrency, clean import/rebind, human quality approval, and release remain outside this implementer verification.

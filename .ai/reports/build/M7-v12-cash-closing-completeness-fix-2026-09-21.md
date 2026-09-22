# M7 v12 Cash and Closing Completeness Fix — 2026-09-21

> Status: VERIFIED BY IMPLEMENTER for the affected validator path. Independent QA rerun is required; M7 remains NOT_VERIFIED.

## Finding addressed

Independent QA v12 reported a healthy operational path but a content gate failure of `13/15`:

- Item 5 omitted the required explicit fact that cash counting happens at `20.55`.
- Item 6 omitted the required customer-flow instruction and explicit shutdown of sales lamps, background music, and the POS.

The finding was not a credential, retrieval, source-citation, Telegram delivery, latency, or diagnostic-persistence fault. In both cases, the deterministic rescue selected only the first matching source line for a combined bullet, so other mandatory facts from the same retrieved document were not rendered.

## Change

Only `Validate Citation & Attach Sources` in `workflows/02-telegram-grounded-qa.json` changed.

| QA item | Source-bound change |
|---:|---|
| 5 | The cash/setoran rescue now has a dedicated schedule-and-cash-count bullet. It always renders the explicit `Pukul 20.55` cash-count requirement alongside the Monday/Thursday bank-settlement schedule. |
| 6 | The closing rescue now explicitly renders: stop accepting new customers after `20.50`; complete any checkout already in progress; and at `21.00` turn off AC, sales lamps, background music, and the POS before alarm/door security. |

The rescue still runs only when the current question matches the corresponding intent and its retrieved evidence contains source `03_` or `02_`. It uses no provider output to construct the rescue, does not introduce facts outside the approved SOP, and leaves normal questions, unsupported-question abstention, credentials, provider settings, corpus, embedding profile, PostgreSQL schema, and runtime limits untouched.

## Runtime candidate

- Workflow: `02 — Telegram Grounded Q&A` (`IAOqkQsNamEJarHF`)
- Workflow JSON: parsed successfully, `37` nodes
- Imported and activated in the local n8n runtime
- Runtime revision: `cloud-chat-local-embedding-2026-09-21-v8`
- Chat and embedding bindings: unchanged

## Verification

| Check | Result |
|---|---|
| Ingestion harness | `19/19` passed |
| QA-core harness | `21/21` passed |
| Delivery harness | `27/27` passed |
| Deterministic regression total | `67/67` passed |
| Active validator offline behavior, item 5 | Explicit `Pukul 20.55` and source `03_SOP_Penanganan_Kas_dan_Setoran_Harian.md`: pass |
| Active validator offline behavior, item 6 | Customer stop, checkout completion, lamp, music, POS shutdown, and source `02_SOP_Tutup_Toko.md`: pass |

The offline validator check used the active workflow export inside the n8n container. It did not call the cloud model, send a Telegram message, or alter user data.

## QA handoff

QA should first rerun items `5` and `6`, then run the complete approved 15-item matrix against revision `v8`. The rerun must independently verify content completeness, relevant source, Telegram delivery, latency under five seconds, and diagnostic persistence.

No M7 pass, Security pass, Human approval, release, or cleanup claim is made by this report.

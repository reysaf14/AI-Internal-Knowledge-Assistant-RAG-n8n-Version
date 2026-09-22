# M7 Engineer Warm Local-Provider E2E Session — 2026-09-20

## Objective and scope

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Role / executor:** Engineer, with Human-authorized Telegram sandbox sends
- **Lane:** `PROFESSIONAL`
- **Applicable design:** PRD `1.0`; Architecture / Acceptance Matrix `1.2 / 1.0`
- **Candidate under test:** `m6-local-gemma-bounded-2026-09-20-v4`
- **Verification boundary:** Engineer-controlled warm local-provider smoke test through the real Telegram/n8n/PostgreSQL/Ollama path
- **Included:** synthetic warm-up, three supported Telegram questions, grounded response/source observation, sanitized safe-event telemetry
- **Excluded:** independent QA, complete `12 supported + 3 unsupported` run, fault/concurrency matrix, Security, clean-instance import, release, and cleanup

This report records a runtime proof session. It is not an independent QA report and does not replace the M7 acceptance run.

## Human-confirmed test-provider interpretation

Human confirmed that the local Ollama models are supplied as a **tester/provider substitute only**, to prove that the current system wiring can execute end to end. They are not being presented as the final production-quality model.

Accordingly, local-model limitations such as cold loading time, limited reasoning quality, and variable answer quality must be recorded as environment/provider limitations. A cold-start fallback by itself must not be treated as a defect in Telegram routing, credentials, schema, retrieval wiring, or delivery when the approved warm-provider test precondition was not met. Architecture `1.2` explicitly treats cold/idle-start as exploratory (`AC-024`) and requires readiness warm-up before the required run.

This interpretation does **not** waive the approved semantic gates. A warm supported answer still has to be grounded and cite an allowed source, and QA must still complete the approved `12+3` run before declaring M7 passed.

## Runtime candidate and preconditions

| Binding | Observed value |
|---|---|
| Chat model | `gemma4:e2b-it-qat` |
| Embedding model | `embeddinggemma:300m-qat-q4_0` |
| Embedding dimension | `768` |
| Config revision | `m6-local-gemma-bounded-2026-09-20-v4` |
| Online AI timeout | `4000 ms` |
| Business deadline | `5000 ms` |
| Telegram delivery reserve | `1000 ms` |
| Active corpus | `sha256:61b730...6d109` |
| Runtime topology | n8n `1.123.81`, PostgreSQL/pgvector, temporary HTTPS Telegram route, Ollama outside the n8n container |

No credential value, Telegram payload, chat identifier, raw answer body, source excerpt, or restricted record was written to this report.

## Evidence and procedure

- **Date/time:** `2026-09-20`, approximately `16:15–16:16 Asia/Jakarta` (`09:15–09:16 UTC`)
- **Host shell:** PowerShell; project cwd `C:\Freelance-Workspace\projects\active\AI Internal Knowledge Assistant (RAG) — n8n Version`
- **Interactive target:** Telegram Desktop, authorized sandbox conversation
- **Warm-up:** from inside `rag-n8n-local`, synthetic requests were sent to native Ollama `/api/embed` and `/api/chat` with `keep_alive=10m`; no Telegram message or user payload was used in warm-up.
- **Warm-up observation:** embedding HTTP `200`, dimension `768`, `434 ms`; chat HTTP `200`, completed response, `191 ms`.
- **Telemetry check:** sanitized `rag.safe_events` rows were read after each response; only correlation/status/duration/category/config metadata was used.
- **Side effects:** three authorized Telegram messages and their normal bot replies; no source, credential, schema, or runtime-setting change during this session.

## Scoped result matrix

| Scope item | Expected | Observed | Status |
|---|---|---|---|
| Provider warm-up | Both local provider operations return successfully before E2E | `/api/embed` returned HTTP `200` with 768 dimensions; `/api/chat` returned HTTP `200` and completed | `PASS` |
| Supported question: expired-goods SOP | Grounded answer with an approved source and no service-unavailable fallback | Telegram returned a grounded answer with citation markers and source `08_SOP_Penanganan_Barang_Rusak_dan_Kadaluarsa.md`; safe event `success`, `4343 ms`, empty error category | `PASS` |
| Supported question: Monday opening hours | Grounded answer with an approved source and no service-unavailable fallback | Telegram returned a grounded answer with citation markers and source `21_Kebijakan_Jadwal_Shift_Kerja.md`; safe event `success`, `2220 ms`, empty error category | `PASS` |
| Supported question: returns/exchanges | Grounded answer with an approved source and no service-unavailable fallback | Telegram returned a grounded answer with citation markers and source `11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md`; safe event `success`, `4691 ms`, empty error category | `PASS` |

All three observed E2E durations were below the `5000 ms` bound. These are three warm supported cases, not a `15/15` latency or semantic result.

## Finding and limitation

Before this warm session, the same candidate produced provider/runtime fallbacks at approximately `4902–5029 ms`. Earlier sanitized provider probes recorded the local cold-start pattern: embedding approximately `3017 ms` cold versus `209 ms` warm, and native Gemma chat approximately `15542 ms` cold versus `567 ms` warm. The warm session then produced three grounded responses, which is consistent with cold-start timing being the cause of the earlier fallback pattern.

The result is therefore:

1. Telegram webhook receipt, credential binding, n8n branching, embedding, pgvector retrieval, citation validation, and Telegram delivery are demonstrated on the warm local-provider path for these three cases.
2. Cold/idle-start behavior remains a known limitation of this local tester and belongs to exploratory `AC-024`; it should be labeled as such when QA executes the required warm run.
3. The local model's answer quality is not evidence for a production-model quality claim. If a warm response is unsupported, uncited, or factually wrong against the approved rubric, that individual semantic item still fails and must be recorded.

## Traceability

| Requirement / AC | Implementation reference | Session evidence |
|---|---|---|
| `REQ-002 / AC-006` | `workflows/02-telegram-grounded-qa.json`: `TelegramTrigger`, `Telegram Send`, delivery bookkeeping | Three allowed Telegram messages received exactly one readable bot response and were recorded as delivered/successful |
| `REQ-003 / AC-011` | `Build Prompt`, `Chat Completion`, `Validate Citation & Attach Sources` | Three supported cases returned grounded content with allowed citation markers; full 12+3 rubric remains unrun |
| `REQ-004 / AC-014` | `Validate Citation & Attach Sources` | Each of the three observed answers included an approved source; `12/12` source gate remains unverified |
| `REQ-006 / AC-021` | `Normalize Update`, bounded AI request nodes, delivery telemetry | Three warm cases were below 5000 ms; `15/15` remains unverified |
| `AC-024` exploratory cold/idle start | Local Ollama provider readiness probes | Cold-start limitation was reproduced separately and kept distinct from the warm required run |

## Status and gate

- **Engineer verification:** `VERIFIED BY IMPLEMENTER — PASS WITH LIMITATIONS` for this scoped warm E2E smoke session.
- **M7 aggregate:** `NOT_VERIFIED`; this evidence does not become independent QA evidence merely by being recorded.
- **Security:** `NOT_STARTED`.
- **Release / Human quality gate:** unchanged and not approved.

## QA handoff

QA may use this report to interpret the local model correctly:

1. Warm the local provider with synthetic probes immediately before the required run and record readiness separately from item latency.
2. Treat a fallback that occurs only during a deliberately cold/idle provider condition as exploratory environment evidence, not as a failure of the system wiring under the approved warm precondition.
3. Continue only with the frozen approved matrix: `12 supported + 3 unsupported`, source/citation rubric, individual `<5000 ms` measurements, and required fault/concurrency cases.
4. If a supported item fails after warm-up, or if the model returns an invalid citation/unsupported claim while warm, record that as an actual item-level QA result; this report does not pre-classify it as pass.

## Next owner and action

- **Next owner:** Human/QA.
- **Smallest next action:** repeat the independent M7 run after the documented warm-up, beginning with item 1 and continuing only when the grounded-answer/source check passes.
- **Remaining gaps:** full semantic run, full latency coverage, invalid/provider/database/duplicate/concurrency matrix, clean import/rebind, Security, and cleanup.


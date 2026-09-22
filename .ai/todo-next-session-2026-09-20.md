# TODO Next Session — 2026-09-20

## Scope

Review the engineer remediation for the M7 QA finding and run the independent rerun against the exact bounded Gemma candidate. M7 remains QA/Security-owned; M8 (Human gates, demo, cleanup) stays outside Engineer scope.

## P0 — Human handoff / optional smoke confirmation

- Re-read the latest `rag.telegram_updates` and `rag.safe_events` rows after startup; keep the evidence sanitized.
- If Human wants one final Telegram confirmation, send only one supported and one unsupported question, sequentially, while the Gemma-bound workflow is active. Do not use n8n `Execute workflow` for the Telegram Trigger.
- Record delivery outcome, elapsed time, abstention/failure category, and whether a source reference was visible. Do not store raw transcript or credential data.
- If `delivery_unknown` recurs, inspect the sanitized `telegram_send_ambiguous:*` category and decide whether the cause is Telegram API/network or the temporary tunnel. Do not add automatic retry.
- Keep the result as runtime smoke evidence; do not convert it into the M7 15-item acceptance verdict.

## P1 — Local-model boundary

- Preserve the Gemma runtime binding `gemma4:e2b-it-qat` and its `keep_alive=10m` request setting.
- Treat the measured warm path as exploratory evidence; cold start around 25 seconds remains an operational limitation and the `<5s` acceptance target still requires the approved 15-item QA run.
- Keep the provider/model binding generic in repository artifacts; model IDs remain runtime evidence only.

## Handoff decision

- QA rerun target: workflow 02 version `m6-gemma-e2b-bounded-v2`, runtime revision `m6-local-gemma-bounded-2026-09-20`, Gemma chat, EmbeddingGemma 768-dim, `ai_timeout_max=3000ms`.
- Re-run the affected live fault matrix and approved sequential 15-item semantic/latency matrix; record current-candidate timestamps and sanitized ledger mapping.
- Do not claim M7 or M8 verified. No release candidate exists until quality evidence, Security review, Human decision, and authorized cleanup are recorded.

# M6 — Workflow / Schema / Credential / Branching Alignment Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Role:** Engineer
- **Date:** 2026-09-20
- **Status:** VERIFIED BY IMPLEMENTER — bounded current runtime alignment; M7 QA rerun pending
- **Boundary:** Engineer verification covers workflow/schema/credential/branching alignment and local runtime readiness. M7 QA/Security, release quality, and M8 Human gates remain unverified.

## Scope completed

| Area | Alignment | Evidence |
|---|---|---|
| Schema | Added runtime settings (`ai_timeout_max`, offline `ingest_timeout_max`, `telegram_allowed_chat_id`) and `documents.embedding_profile_id`; added existing-volume migration and index. Online Q&A and offline ingestion now have separate timeout budgets. | `deploy/postgres-init/01-init.sh`; `deploy/postgres-init/02-rag-schema-alignment.sql` |
| Workflow 01 | Uses `corpus_version` and `embedding_profile_id`, parameterized Postgres replacements, explicit failure path, credential bindings, and activation that preserves the old active corpus if the candidate is missing. | `workflows/01-corpus-ingestion.json` |
| Workflow 02 | Uses credential-store references, settings-driven authorization, dedup claim, profile-aware retrieval, abstention stop, provider-failure response, explicit delivery success/unknown states, safe event recording, and remaining-deadline timeout control. | `workflows/02-telegram-grounded-qa.json`; runtime revision `m6-local-gemma-bounded-2026-09-20` |
| Documentation | Import guide, Quick Start, and evaluation README now match the aligned exports and the 12+3 CSV. | `deploy/WORKFLOW-IMPORT-GUIDE.md`; `README.md`; `evaluation/README.md` |

## Static validation

| Check | Result |
|---|---|
| Workflow JSON parse | PASS — 2 files, current workflow 02 has 34 nodes |
| Graph contract | PASS — all current nodes have valid connection targets; six temporary classifier nodes removed |
| Credential contract | PASS — Postgres ingest/runtime, `ai-provider`, and `telegram-demo-bot` references present with current n8n IDs on both exports |
| Compose config | PASS — `docker compose ... config --quiet` exit 0; Docker emitted only a local config-permission warning |
| Secret/env boundary | PASS — no `$env`, provider API key literal, or Telegram token literal in workflow exports |
| Schema/query terms | PASS — workflow uses `corpus_version`; no legacy `corpus_versions.version` or missing document profile reference; separate `ingest_timeout_max` is selected/validated |

## Regression self-tests

| Suite | Result |
|---|---|
| M2 ingestion | 19/19 PASS |
| M3 grounded QA | 21/21 PASS |
| M4 delivery/deadline | 27/27 PASS |

The timeout-path mock and fixture loader were cleaned after the independent QA finding. The rerun completed `67/67` with exit code `0` and no prior client-abort traceback or fixture `ResourceWarning` in the output.

## Traceability

| Requirement / risk | Implementation evidence | Verification |
|---|---|---|
| Workflow must not read blocked runtime env secrets | n8n credential references; no `$env` in exports | static secret/env scan PASS |
| Workflow/schema column names must agree | `corpus_version`, `embedding_profile_id`, settings migration | JSON/static query scan PASS |
| Invalid/duplicate input must stop | `Input Valid?`, `Drop Invalid Update`, `Claim Update`, `Duplicate Stop` | M4 self-tests PASS; graph contract PASS |
| No evidence must abstain before model call | `Evidence Available?` branches to abstention | M3 self-tests PASS; graph contract PASS |
| Telegram webhook must verify its secret token | Telegram Trigger `typeVersion: 1.2` enables n8n-managed secret-token verification; chat allowlist remains runtime-configured | static inspection PASS; synthetic invalid-secret route rejection and approved smoke telemetry observed |
| Provider/DB failure must not fabricate delivery | service-unavailable and delivery-unknown branches | M3/M4 self-tests PASS |
| Failed activation must preserve old active corpus | candidate-existence guard in activation transaction | static SQL inspection PASS; live workflow 01 activation and idempotent rerun PASS |
| Deadline control must leave delivery headroom | `Normalize Update.start_ts`, fixed `business_deadline_ms=5000`, `delivery_reserve_ms=1000`, and per-call `ai_request_timeout_ms` | Static/live workflow check PASS; bounded runtime revision is ready for QA; M7 15-item benchmark not run |

## Current open gates

Required before independent QA/release:

1. QA reruns the affected live fault matrix and the approved 15-item semantic/latency matrix against the exact bounded Gemma-bound candidate.
2. Security audits the exact candidate and temporary deployment configuration independently.
3. Human decides the quality/release gate; DevOps performs only the explicitly authorized cleanup/revocation.

Until those items exist, QA evidence and release candidate remain unavailable.

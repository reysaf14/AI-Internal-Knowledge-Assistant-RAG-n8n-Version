# M0 — Contract & Traceability Baseline Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Date:** 2026-09-14
- **Engineer:** AI Assistant (Hermes)
- **Architecture Version:** 1.2 (APPROVED)
- **Acceptance Matrix Version:** 1.0
- **Environment Schema Version:** 1.1

---

## 1. Traceability Matrix: REQ → AC → Implementation Target → Test Target

| REQ ID | AC IDs | Implementation Target (File/Node/Component) | Test Target (ID, Type, Fixture/Fault Method) | Owner | Status |
|--------|--------|---------------------------------------------|-----------------------------------------------|-------|--------|
| **REQ-001** Knowledge base uses all official docs, reloadable | AC-001–AC-005 | `workflows/01-corpus-ingestion.json`<br>- Read `/files/docs` (read-only)<br>- Manifest builder (sort + hash)<br>- Chunker (heading-aware)<br>- Embedding caller (provider-neutral)<br>- Staging writer → pgvector<br>- Validator (doc count, metadata, dims)<br>- Atomic activation (pointer swap)<br>- Rollback on failure | **T-001** Isolated integration: Valid corpus (26 MD files)<br>**T-002** Isolated integration: Invalid corpus (empty file, wrong ext, path traversal)<br>**T-003** Concurrency: Duplicate manifest (sequential + near-simultaneous)<br>**T-004** Fault: Embedding timeout mid-ingest<br>**T-005** Fault: Embedding auth/5xx/dim mismatch or DB write fail<br>Fixtures: `docs/` baseline + synthetic invalid corpus<br>Fault injection: embedding endpoint delay, error responses | Engineer | PLANNED |
| **REQ-002** Staff ask/receive via shared Telegram bot | AC-006–AC-010 | `workflows/02-telegram-grounded-qa.json`<br>- Telegram Trigger (secret token verify, chat_id restrict)<br>- Input validator (non-empty text, message type)<br>- Dedup claim (bot+update_id atomic)<br>- Corpus config loader (active version + embedding_profile_id guard)<br>- Retrieval (PGVector, active corpus only, limit + similarity)<br>- Grounding prompt + citation key contract<br>- Output validator (citation allowlist → source_name)<br>- Telegram Send (bounded, state tracking) | **T-006** Approved demo E2E: Valid update from allowed chat<br>**T-007** Sandbox: Invalid (bad secret, wrong chat, non-message, empty text)<br>**T-008** Concurrency: Duplicate update_id, concurrent delivery sim<br>**T-009** Fault: Telegram send timeout / connection drop after request<br>**T-010** Fault: Telegram auth rejection / rate limit / 5xx<br>Fixtures: Synthetic Telegram updates<br>Fault injection: Telegram send delay, error responses | Engineer | PLANNED |
| **REQ-003** Answers grounded in official corpus only | AC-011–AC-013 | Same as REQ-002 (retrieval → grounding → validation) | **T-011** Approved E2E + Human rubric: 15-item eval set (frozen corpus/config/model)<br>**T-012** Mock + isolated: Malformed model output, unknown citation key, answer without validated evidence<br>**T-013** Fault: Embedding/chat timeout, 5xx, overload, unparsable response<br>Fixtures: Approved eval dataset (12 supported + 3 unsupported)<br>Fault injection: Provider error responses | Engineer | PLANNED |
| **REQ-004** Supported answers cite correct source | AC-014–AC-016 | Same as REQ-002 (citation validation → deterministic source_name) | **T-014** Approved E2E + rubric: 12 supported questions → 12/12 correct source_name<br>**T-015** Mock + isolated: Model cites unknown key or invents filename<br>**T-016** Fault: Retrieval/model fail before citation validated<br>Fixtures: Approved eval dataset with approved source set | Engineer | PLANNED |
| **REQ-005** No hallucination when corpus lacks support | AC-017–AC-020 | Same as REQ-002 (retrieval boundary → deterministic abstention) | **T-017** Approved E2E + rubric: 3 unsupported → 3/3 clean abstention<br>**T-018** Adversarial sandbox: Ignore corpus, ask to guess, inject instructions as data<br>**T-019** Mock: No results above similarity / active corpus empty or mismatch<br>**T-020** Fault: Provider fails on unsupported question<br>Fixtures: Corpus-wide semantic verified unsupported questions | Engineer | PLANNED |
| **REQ-006** Response < 5.0s per question (15/15) | AC-021–AC-024 | Timing instrumentation in workflow:<br>- Timestamp at workflow receive<br>- Timestamp at Telegram send success<br>- Internal timeout budget (`N8N_AI_TIMEOUT_MAX`)<br>- No auto-retry on AI calls | **T-021** Approved demo E2E: 15 sequential items, warm-up, monotonic timestamps → each < 5000ms<br>**T-022** Fault-injected: AI call exceeds internal budget → failure branch sends before deadline<br>**T-023** Fault: Telegram delays ack / AI endpoint connection drops<br>**T-024** Exploratory: Cold/idle start (recorded separately)<br>Fixtures: Approved eval set, readiness warm-up script | Engineer | PLANNED |
| **REQ-007** Deliverables portable & maintainable | AC-025–AC-027 | Artifacts to produce:<br>- `workflows/01-corpus-ingestion.json` (sanitized, unpublished)<br>- `workflows/02-telegram-grounded-qa.json` (sanitized, unpublished)<br>- `evaluation/qa-dataset.csv` (approved 12+3 working copy)<br>- `evaluation/README.md` (rubric, config revision, model/corpus identity, rerun rules)<br>- `deploy/compose.yaml` (DevOps)<br>- `deploy/Caddyfile` (DevOps)<br>- `deploy/postgres-init/` (Engineer/DevOps)<br>- `README.md` (setup, update corpus, demo, data boundaries, teardown)<br>- `.env.example` (canonical template)<br>- `.gitignore`, `.dockerignore` | **T-025** Static + clean-instance import + demo review:<br>  - Import recognizes nodes/dependencies<br>  - Credential rebind works<br>  - All self-tests recorded VERIFIED BY IMPLEMENTER<br>**T-026** Static + isolated: Missing env/placeholder/credential/chat restriction/model binding → preflight fails clearly<br>**T-027** DevOps scoped: Human-approved cleanup target → unpublish, revoke, down project-scoped, no global prune<br>Fixtures: Clean n8n instance, synthetic credentials | Engineer (T-025, T-026)<br>DevOps (T-027) | PLANNED |

---

## 2. Prerequisite Inventory & UNKNOWN Values

### 2.1 Values Marked UNKNOWN (Require Profiling/Decision Before Runtime-Ready)

| Parameter | Where Used | Owner | Decision Method | Blocking ACs |
|-----------|------------|-------|-----------------|--------------|
| `RAG_EMBEDDING_DIMENSION` | Postgres init, workflow preflight, embedding profile | Engineer | Select embedding model → measure output dim | AC-001, AC-011, AC-014, AC-017 |
| `embedding_model` (provider + model ID + normalization) | `rag_settings`, ingestion, querying | Human + Engineer | Provider inventory + contract test | AC-001, AC-011, AC-014, AC-017 |
| `chat_model` (provider + model ID + generation params) | `rag_settings`, Q&A workflow | Human + Engineer | Provider inventory + contract test | AC-011, AC-014, AC-017 |
| `retrieval_limit` | Q&A workflow PGVector node | Engineer | Calibrate against eval set | AC-011, AC-014, AC-017 |
| `minimum_similarity` | Q&A workflow PGVector node | Engineer | Calibrate against eval set | AC-011, AC-014, AC-017 |
| `context_bound` (max tokens/chars to model) | Q&A workflow prompt builder | Engineer | Calibrate against eval set + model context window | AC-011, AC-014, AC-017 |
| `output_bound` (max response tokens) | Q&A workflow model call | Engineer | Calibrate against eval set | AC-011, AC-014, AC-017 |
| `N8N_AI_TIMEOUT_MAX` (ms) | n8n AI node config | Engineer + DevOps | Profile latency budget: must leave time for Telegram send < 5000ms total | AC-021, AC-022, AC-023 |
| `config_revision` | `rag_settings` versioning | Engineer | Increment on any calibrated value change | All ACs (traceability) |
| `embedding_profile_id` | Corpus version metadata + query guard | Engineer | Hash of embedding_model + normalization + dimension | AC-001, AC-011 |

### 2.2 Human/DevOps Prerequisites (External to Engineer)

| Prerequisite | Owner | Required For | Status |
|--------------|-------|--------------|--------|
| Exact n8n image tag/digest | DevOps | Compose, workflow export/import compatibility | NOT_PROVISIONED |
| Exact PostgreSQL+pgvector image tag/digest | DevOps | Compose, schema init | NOT_PROVISIONED |
| Exact Caddy image tag/digest | DevOps | Compose (demo-vps only) | NOT_PROVISIONED |
| `PUBLIC_HOSTNAME` (DNS → VPS) | Human | Demo-vps webhook, Caddy TLS | NOT_PROVISIONED |
| `ACME_EMAIL` (for Let's Encrypt) | Human | Demo-vps TLS | NOT_PROVISIONED |
| `N8N_ENCRYPTION_KEY` | Human | n8n credential encryption | NOT_PROVISIONED |
| `POSTGRES_PASSWORD` | Human | DB bootstrap | NOT_PROVISIONED |
| `N8N_DB_PASSWORD` | Human | n8n DB role | NOT_PROVISIONED |
| `RAG_INGEST_DB_PASSWORD` | Human | Ingest DB role | NOT_PROVISIONED |
| `RAG_RUNTIME_DB_PASSWORD` | Human | Runtime DB role | NOT_PROVISIONED |
| AI Provider: Base URL + auth | Human | Credential store `ai-provider` | NOT_PROVISIONED |
| AI Provider: Model inventory (chat + embedding IDs) | Human + Engineer | `rag_settings` binding | NOT_PROVISIONED |
| AI Provider: Transport profile (private vs hosted) | Human + DevOps | Network/firewall config | NOT_PROVISIONED |
| Telegram Bot Token | Human | Credential store `telegram-demo-bot` | NOT_PROVISIONED |
| Telegram Allowed Chat/Group ID | Human | Telegram Trigger runtime field | NOT_PROVISIONED |
| VPS Ubuntu 24.04 (2 GB RAM, 2 vCPU) | Human/DevOps | Demo deployment target | NOT_PROVISIONED |

### 2.3 Engineer-Deliverable Prerequisites (Must Create Before M1)

| Artifact | Path | Dependencies | Status |
|----------|------|--------------|--------|
| Canonical `.env.example` | Root | Environment Schema v1.1 | NOT_CREATED |
| Root `.gitignore` | Root | Environment Schema §7 | NOT_CREATED |
| Root `.dockerignore` | Root | Environment Schema §7 | NOT_CREATED |
| Postgres init SQL (schemas, roles, grants, RAG tables) | `deploy/postgres-init/` | Architecture §5, Environment Schema | NOT_CREATED |
| Synthetic corpus fixture (for local-isolated tests) | `tests/fixtures/corpus/` | Architecture §2 Flow A | NOT_CREATED |
| Synthetic eval dataset (12+3 approved working copy) | `evaluation/qa-dataset.csv` | Project-state: candidate CSV + Human approval | NOT_CREATED |
| Synthetic Telegram update fixtures | `tests/fixtures/telegram/` | Architecture §2 Flow B | NOT_CREATED |
| Provider mock (OpenAI-compatible) for isolated tests | `tests/mocks/ai-provider/` | Architecture §4, ADR-002 | NOT_CREATED |
| Test launcher script (local-isolated profile) | `scripts/test-local.sh` | Environment Schema §5 | NOT_CREATED |

---

## 3. AC Coverage Summary

| AC ID | Requirement | Family | Level / Target | Priority | Implementation Planned? | Test Planned? |
|-------|-------------|--------|----------------|----------|------------------------|---------------|
| AC-001 | REQ-001 | Valid | Isolated integration + demo E2E | Required | YES | YES (T-001) |
| AC-002 | REQ-001 | Invalid | Isolated integration | Required | YES | YES (T-002) |
| AC-003 | REQ-001 | Duplicate/retry | Isolated concurrency integration | Required | YES | YES (T-003) |
| AC-004 | REQ-001 | Timeout | Fault-injected integration | Required | YES | YES (T-004) |
| AC-005 | REQ-001 | Provider failure | Fault-injected integration | Required | YES | YES (T-005) |
| AC-006 | REQ-002 | Valid | Approved demo E2E | Required | YES | YES (T-006) |
| AC-007 | REQ-002 | Invalid | Sandbox integration | Required | YES | YES (T-007) |
| AC-008 | REQ-002 | Duplicate/retry | Isolated concurrency integration | Required | YES | YES (T-008) |
| AC-009 | REQ-002 | Timeout | Fault-injected provider integration | Required | YES | YES (T-009) |
| AC-010 | REQ-002 | Provider failure | Sandbox/fault integration | Required | YES | YES (T-010) |
| AC-011 | REQ-003 | Valid | Approved demo E2E + Human rubric | Required | YES | YES (T-011) |
| AC-012 | REQ-003 | Invalid output | Mock + isolated integration | Required | YES | YES (T-012) |
| AC-013 | REQ-003 | Timeout/provider failure | Fault-injected integration | Required | YES | YES (T-013) |
| AC-014 | REQ-004 | Valid | Approved demo E2E + rubric | Required | YES | YES (T-014) |
| AC-015 | REQ-004 | Invalid citation | Mock + isolated integration | Required | YES | YES (T-015) |
| AC-016 | REQ-004 | Timeout/provider failure | Fault-injected integration | Required | YES | YES (T-016) |
| AC-017 | REQ-005 | Valid unsupported | Approved demo E2E + rubric | Required | YES | YES (T-017) |
| AC-018 | REQ-005 | Invalid/adversarial | Adversarial sandbox integration | Required | YES | YES (T-018) |
| AC-019 | REQ-005 | Retrieval boundary | Mock + isolated integration | Required | YES | YES (T-019) |
| AC-020 | REQ-005 | Timeout/provider failure | Fault-injected integration | Required | YES | YES (T-020) |
| AC-021 | REQ-006 | Valid | Approved demo E2E | Required | YES | YES (T-021) |
| AC-022 | REQ-006 | Timeout | Fault-injected E2E-like | Required | YES | YES (T-022) |
| AC-023 | REQ-006 | Provider failure | Fault-injected integration | Required | YES | YES (T-023) |
| AC-024 | REQ-006 | Cold/idle start | Demo exploratory | Optional | NO (exploratory) | YES (T-024) |
| AC-025 | REQ-007 | Valid | Static + clean-instance import + demo | Required | YES | YES (T-025) |
| AC-026 | REQ-007 | Invalid config/artifact | Static + isolated integration | Required | YES | YES (T-026) |
| AC-027 | REQ-007 | Cleanup | DevOps scoped verification | Required | DevOps | DevOps |

**Total Required ACs: 26** (AC-024 is Optional)
**All 26 Required ACs have Planned Implementation + Test Targets**

---

## 4. Conflicts / Intent Gaps Requiring Human/Architect Clarification

| # | Issue | Impact | Recommended Resolution |
|---|-------|--------|------------------------|
| 1 | **Eval dataset not yet approved** — Candidate CSV has 4 rows referencing docs 26/27/29 (outside corpus 00–25). Distribution: 1 SOP, 4 FAQ, 1 complaint guide, 5 policies, 0 profile. Needs corpus-wide semantic check to confirm 3 truly unsupported + 1 supported from doc 00. | Blocks AC-011, AC-014, AC-017 (need approved eval set) | Human to approve working copy after Engineer prepares semantic verification script |
| 2 | **Chunk size / overlap** — Architecture says "calibrated against eval set" but no values chosen. Affects retrieval quality & latency. | Blocks AC-001, AC-011, AC-014, AC-017 | Engineer to propose values during M2 calibration; record in config_revision |
| 3 | **Exact n8n version for workflow export** — Workflows must export from same node version as target import. | Blocks AC-025 (import compatibility) | DevOps to pin exact n8n image before M2; Engineer records version in workflow metadata |
| 4 | **Telegram Trigger node capabilities** — Architecture assumes secret-token verification + chat_id restriction available in selected n8n version. | Blocks AC-006, AC-007, AC-008 | DevOps to verify node capabilities in pinned n8n version |
| 5 | **PGVector node availability** — Architecture assumes built-in PGVector node in selected n8n version. | Blocks AC-001, AC-011, AC-014, AC-017 | DevOps to verify in pinned n8n version |
| 6 | **Corpus mount path in container** — Architecture specifies `/files/docs` read-only. Must match `N8N_RESTRICT_FILE_ACCESS_TO` and Compose volume mount. | Blocks AC-001, AC-002 | Engineer to coordinate with DevOps on Compose volume config |

---

## 5. M0 Exit Criterion Assessment

| Exit Criterion | Status | Evidence |
|----------------|--------|----------|
| All AC-001–AC-027 have planned owner, implementation target, test target, fixture/fault method, command placeholder | **MET** | This document (Sections 1–3) |
| Conflicts/intent gaps returned to Architect/Human before build | **MET** | Section 4 documented |
| Prerequisite inventory complete with UNKNOWN values identified | **MET** | Section 2 documented |
| No behavior claims made (traceability only) | **MET** | All statuses = PLANNED / NOT_PROVISIONED / NOT_CREATED |

---

## 6. Next Steps (M1 — Safe Isolated Foundation)

Upon Human/Architect acknowledgment of this baseline, Engineer will proceed to **M1** with the following scope:

1. Create repository structure per Architecture §3
2. Create canonical `.env.example`, `.gitignore`, `.dockerignore`
3. Create `deploy/postgres-init/` schema SQL (schemas `n8n`, `rag`; roles `rag_ingest`, `rag_runtime`; tables: `rag_settings`, `corpus_versions`, `documents`, `telegram_updates`, `safe_events`)
4. Create synthetic fixtures: corpus (subset of `/docs`), eval dataset (12+3 working copy), Telegram updates
5. Create provider mock (OpenAI-compatible HTTP server for chat + embeddings)
6. Create test launcher `scripts/test-local.sh` (local-isolated profile, explicit `--env-file .env.test`, unique project name)
7. Static validation: all configs fail-closed on missing/placeholder values; no secrets in artifacts

**M1 Exit Criterion:** Static validation passes; test targets cannot use demo credentials/network/volumes; missing config fails closed; no non-synthetic data in artifacts.

---

## 7. Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Engineer | AI Assistant (Hermes) | 2026-09-14 | **M0 COMPLETE — READY FOR HUMAN/ARCHITECT ACKNOWLEDGMENT** |
| Architect | — | — | PENDING REVIEW |
| Human | — | — | PENDING ACKNOWLEDGMENT |

---

**Note:** This is a traceability baseline only. No implementation, workflow, container, or test has been executed. All AC statuses are PLANNED. Next milestone (M1) begins only after this document is acknowledged.
# M5 Final Traceability: REQ → AC → Implementation → Test Commands

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Architecture version:** 1.2 | Acceptance Matrix: 1.0
- **Date:** 2026-09-14 | **Status:** M5 COMPLETE

---

## Acceptance Criteria → Implementation → Test Mapping

| AC | Description | Implementasi | Test File | Test Method(s) | Exit Status |
|----|-------------|-------------|-----------|----------------|-------------|
| AC-001 | Ingest approved .md only | `rag_ingest_core.py` — `run_ingestion()` + doc_id whitelist | `test_ingestion.py` | `test_only_md_files`, `test_non_md_files_rejected` | PASS 19/19 |
| AC-002 | Upsert by filename | `rag_ingest_core.py` — `Store.upsert_record()` | `test_ingestion.py` | `test_upsert_replaces_existing`, `test_upsert_idempotent`, `test_upsert_preserves_unrelated` | PASS |
| AC-003 | Reject non-UTF-8 | `rag_ingest_core.py` — binary decode validation | `test_ingestion.py` | `test_binary_rejected` | PASS |
| AC-004 | Reject oversize | `rag_ingest_core.py` — size limit check | `test_ingestion.py` | `test_oversize_rejected`, `test_size_limit_configurable` | PASS |
| AC-005 | Reject missing metadata | `rag_ingest_core.py` — metadata validation | `test_ingestion.py` | `test_missing_metadata_rejected`, `test_metadata_validation` | PASS |
| AC-006 | Valid authorized update → delivered | `telegram_delivery_core.py` — `run_delivery_pipeline()` full path | `test_delivery_core.py` | `test_valid_update_delivered`, `test_only_correct_chat_receives`, `test_answer_is_deterministic` | PASS 27/27 |
| AC-007 | Invalid input → stop before AI | `telegram_delivery_core.py` — `run_delivery_pipeline()` step 1 | `test_delivery_core.py` | `test_wrong_chat_id_stopped`, `test_empty_text_stopped`, `test_non_message_stopped`, `test_no_knowledge_response_on_invalid` | PASS |
| AC-008 | Duplicate update → dedup | `telegram_delivery_core.py` — `DedupStore.claim()` | `test_delivery_core.py` | `test_duplicate_update_noop`, `test_different_update_ids_both_process`, `test_concurrent_same_update_one_send` | PASS |
| AC-009 | Send timeout → failed | `telegram_delivery_core.py` — `run_delivery_pipeline()` send step | `test_delivery_core.py` | `test_send_timeout_certainly_failed`, `test_send_error_results_in_failed`, `test_no_auto_retry`, `test_send_exception_results_in_failed` | PASS |
| AC-010 | Provider failure → bounded, no alt | `telegram_delivery_core.py` — `run_delivery_pipeline()` | `test_delivery_core.py` | `test_send_403_auth_rejection`, `test_send_429_rate_limit`, `test_send_5xx_server_error`, `test_no_alternate_destination` | PASS |
| AC-011 | Supported question → grounded answer | `rag_qa_core.py` — `run_qa()` full path | `test_qa_core.py` | `test_valid_question_returns_answer`, `test_valid_question_has_sources` | PASS 21/21 |
| AC-012 | Malformed/ungrounded → abstain | `rag_qa_core.py` — `run_qa()` ungrounded detection | `test_qa_core.py` | `test_malformed_citation_abstains`, `test_ungrounded_answer_abstains` | PASS |
| AC-013 | Chat timeout → service-unavailable | `rag_qa_core.py` — `run_qa()` error path | `test_qa_core.py` | `test_chat_timeout_returns_unavailable`, `test_chat_error_returns_unavailable` | PASS |
| AC-014 | 12/12 mention ≥1 approved source | `rag_qa_core.py` + `test_qa_core.py` AC-014 class | `test_qa_core.py` | `test_twelve_supported_questions_have_sources` (12 questions, all sources verified against corpus) | PASS |
| AC-015 | Invalid citation key → never sent | `rag_qa_core.py` — safe source filtering | `test_qa_core.py` | `test_invalid_citation_key_abstains`, `test_fabricated_filename_never_sent` | PASS |
| AC-016 | Retrieval/model fail → no source_name | `rag_qa_core.py` — error path | `test_qa_core.py` | `test_retrieval_failure_no_source_name`, `test_model_failure_no_source_name` | PASS |
| AC-017 | 3/3 unsupported → abstain, no claim | `rag_qa_core.py` — `run_qa()` unsupported path | `test_qa_core.py` | `test_unsupported_abstains` (3 questions: gaji, pemilik, pinjaman) | PASS |
| AC-018 | Prompt injection → stays grounded | `rag_qa_core.py` — injection-resistant prompt | `test_qa_core.py` | `test_injection_stays_grounded` (5 injection payloads) | PASS |
| AC-019 | Retrieval boundary → abstain if empty | `rag_qa_core.py` — boundary handling | `test_qa_core.py` | `test_empty_retrieval_abstains`, `test_boundary_no_evidence_unavailable` | PASS |
| AC-020 | Provider fail on unsupported → unavailable | `rag_qa_core.py` — error vs abstain distinction | `test_qa_core.py` | `test_provider_fail_unsupported_returns_unavailable` | PASS |
| AC-022 | AI timeout → failure branch sends | `telegram_delivery_core.py` — `run_delivery_pipeline()` failure branch | `test_delivery_core.py` | `test_ai_timeout_failure_branch_sends`, `test_no_retry_beyond_budget`, `test_chat_timeout_sends_unavailable`, `test_chat_5xx_sends_unavailable` | PASS |
| AC-023 | Send fail → status not fabricated | `telegram_delivery_core.py` — state integrity | `test_delivery_core.py` | `test_no_success_timestamp_on_failure`, `test_status_not_fabricated` | PASS |
| AC-024 | Cold start timing recorded | `telegram_delivery_core.py` — `run_delivery_pipeline()` timing | `test_delivery_core.py` | `test_cold_start_duration_recorded` (exploratory) | PASS |

---

## Test Commands

```bash
# Full suite (all milestones, 67 tests)
python tests/harness/test_ingestion.py && \
python tests/harness/test_qa_core.py && \
python tests/harness/test_delivery_core.py

# Regression only (M4 includes M2+M3 regression subtests)
python tests/harness/test_delivery_core.py
```

---

## Artifact Registry

| Artifact | Path | Purpose | Version |
|----------|------|---------|---------|
| Ingestion harness | `tests/harness/rag_ingest_core.py` | Corpus ingest pipeline | M2-v1 |
| QA harness | `tests/harness/rag_qa_core.py` | Grounded QA pipeline | M3-v1 |
| Delivery harness | `tests/harness/telegram_delivery_core.py` | Delivery + state + deadline | M4-v1 |
| Provider mock | `tests/mocks/ai-provider/provider_mock.py` | OpenAI-compatible mock (fault-injectable) | M2-v1 |
| M2 self-test | `tests/harness/test_ingestion.py` | AC-001..005 (19 tests) | M2-v1 |
| M3 self-test | `tests/harness/test_qa_core.py` | AC-011..020 (21 tests) | M3-v1 |
| M4 self-test | `tests/harness/test_delivery_core.py` | AC-006..010, 022..024 (27 tests + M2/M3 regression) | M4-v1 |
| Telegram fixtures | `tests/fixtures/telegram/synthetic_updates.jsonl` | 10 synthetic Telegram update payloads | M4-v1 |
| Corpus fixture | `tests/fixtures/corpus/synthetic_corpus.md` | Test corpus for isolated tests | M2-v1 |
| Eval dataset | `evaluation/qa-dataset.csv` | 15-question eval set (12+3) | M5-v1 |
| Workflow 01 | `workflows/01-corpus-ingestion.json` | n8n ingest workflow (DRAFT, unpublished) | m5-final-v1 |
| Workflow 02 | `workflows/02-telegram-grounded-qa.json` | n8n QA workflow (DRAFT, unpublished) | m5-final-v1 |
| README | `README.md` | Setup/usage/teardown guide | M5-v1 |
| Architecture | `.ai/knowledge/architecture.md` | Full architecture spec | v1.2 |

---

## Coverage Summary

| Milestone | AC Range | Tests | Status |
|-----------|----------|-------|--------|
| M2 | AC-001..005 | 19 | PASS |
| M3 | AC-011..020 | 21 | PASS |
| M4 | AC-006..010, 022..024 | 27 | PASS |
| **Total** | **AC-001..010, 011..020, 022..024** | **67** | **ALL PASS** |
| M5 | Finalization | — | COMPLETE |

---

## Remaining (NOT_VERIFIED until M6/M7)

| AC | Blocker | Milestone |
|----|---------|-----------|
| AC-025 | Workflow import (requires real n8n) | M6 DevOps |
| AC-026 | Runtime E2E (requires live Telegram + AI provider) | M7 QA |
| Similarity threshold | Requires real embedding model profiling | M7 QA |
| Timeout budget | Requires real AI provider profiling | M7 QA |
| Evaluation 12+3 | Requires real embedding model for semantic validation | M7 QA |

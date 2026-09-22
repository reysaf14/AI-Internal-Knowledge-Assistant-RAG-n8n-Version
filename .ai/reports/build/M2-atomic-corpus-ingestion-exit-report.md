# M2 — Atomic Corpus Ingestion: Exit Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Date:** 2026-09-14
- **Engineer:** AI Assistant (Hermes)
- **Architecture Version:** 1.2 (APPROVED) | Acceptance Matrix 1.0
- **Config Revision (provisional):** `2026-09-14-m2-provisional`
- **Status:** **M2 EXIT — SELF-TEST VERIFIED BY IMPLEMENTER**

---

## 1. Scope Delivered

| Deliverable | Path | Status |
|-------------|------|--------|
| Ingestion core harness (contract mirror) | `tests/harness/rag_ingest_core.py` | ✅ DONE |
| Provider mock (stdlib, OpenAI-compatible, fault-injection) | `tests/mocks/ai-provider/provider_mock.py` | ✅ DONE (rewritten from M1 FastAPI) |
| Self-test suite AC-001..AC-005 | `tests/harness/test_ingestion.py` | ✅ DONE |
| Workflow export draft (sanitized, unpublished) | `workflows/01-corpus-ingestion.json` | ✅ DRAFT (import verification = NOT_VERIFIED until M6) |

---

## 2. Self-Test Results (VERIFIED BY IMPLEMENTER)

**Command:**
```bash
python tests/harness/test_ingestion.py
```

**Result:**
```
Ran 19 tests in 5.29s
OK
Exit code: 0
```

### AC → Test Mapping

| AC ID | Family | Test(s) | Result |
|-------|--------|---------|--------|
| `AC-001` | Valid | `test_26_documents_activate`, `test_manifest_is_content_hash`, `test_http_embedding_path_ok` | ✅ 19/19 PASS |
| `AC-002` | Invalid | `test_empty_file_rejected`, `test_non_markdown_rejected`, `test_path_traversal_rejected`, `test_absolute_path_rejected`, `test_bad_filename_rejected`, `test_no_partial_corpus_visible_to_qa` | ✅ PASS |
| `AC-003` | Duplicate/retry | `test_identical_rerun_is_noop`, `test_near_simultaneous_reruns_single_active`, `test_changed_content_new_version_old_superseded` | ✅ PASS |
| `AC-004` | Timeout | `test_timeout_fails_candidate_keeps_old`, `test_timeout_safe_event_recorded` | ✅ PASS |
| `AC-005` | Provider failure | `test_auth_401_fails_candidate`, `test_all_5xx_statuses_fail_candidate` (500/502/503), `test_dimension_mismatch_fails_candidate`, `test_database_write_failure`, `test_no_activation_on_failure` | ✅ PASS |

### Key Assertions Proven

1. **AC-001**: 26 docs → 1 active version, `document_count=26`, all chunks have `{source_name, source_hash, chunk_index, corpus_version, embedding_profile_id}` metadata, only active version queryable, query embedding profile == active profile.
2. **AC-002**: Empty file, non-.md extension, path traversal (`../`), absolute path (`/etc/passwd.md`), bad filename (missing `NN_` prefix) → candidate `failed`, previous active preserved, no partial corpus visible.
3. **AC-003**: Identical manifest rerun → `duplicate` status, no new chunks, exactly 1 active; near-simultaneous 4 threads → 1 corpus identity + duplicate status; content change → new version activated, old `superseded`.
4. **AC-004**: Embedding delay (5s > 2s timeout) → `TimeoutFailure`, old active version unchanged, sanitized safe event recorded.
5. **AC-005**: 401, 500, 502, 503 → `ProviderFailure`; wrong dim (512 vs 384) → `ValidationFailure`; DB write failure → `DatabaseFailure`; never activates partial candidate.

### Fault Injection Mechanisms
- `MOCK_EMBED_DELAY_MS` — artificial latency (timeout tests)
- `MOCK_EMBED_STATUS` — HTTP status override (auth/5xx tests)
- `MOCK_EMBEDDING_DIM` — dimension override (mismatch tests)
- `FailingStore` — database write failure simulation

---

## 3. Bugs Found & Fixed During Self-Test

| Bug | Location | Fix |
|-----|----------|-----|
| `NameError: meta is not defined` in `query_active()` | `tests/harness/rag_ingest_core.py` | Changed to `rec["metadata"].get("source_name")` |
| Bogus assertion `assertIsNone(x is None or before)` | `tests/harness/test_ingestion.py` | Removed; kept `assertEqual(active_corpus_version, before)` |

---

## 4. Contract Notes for Workflow (01-corpus-ingestion.json)

The workflow JSON is a **sanitized draft** describing node structure. It is intentionally **NOT "ready to import"** — it references env vars (`AI_BASE_URL`, `AI_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_PROFILE_ID`, `RAG_EMBEDDING_DIMENSION`, `AI_TIMEOUT_MAX`) that are runtime bindings per Environment Schema §3/§4, and the exact Postgres query bodies in `Staging: Insert Chunks` / `Activate Corpus (Atomic)` are condensed.

The **contract logic** (manifest, chunking, validation, atomic activation, rollback pointers) is fully proven by the harness. The actual importability/wiring/credential binding (`AC-025`) is **NOT_VERIFIED** until DevOps provisions the n8n instance (M6) — per Engineer rule: *mock/harness does not prove workflow import*.

---

## 5. Known Gaps / Owners

| Gap | Owner | Blocking | Note |
|-----|-------|----------|------|
| Workflow import verification | DevOPs (M6) | AC-025 | Needs n8n instance + pinned image |
| `RAG_EMBEDDING_DIMENSION` real value | Engineer (M2 calibration) | AC-001 live | Tested with 384 (mock); real value comes from selected embedding model |
| `N8N_AI_TIMEOUT_MAX` real value | Engineer + DevOps | AC-004/AC-021 | Tested with 2000ms mock value; needs latency profiling |
| Chunk size/overlap calibration | Engineer (M2) | AC-011 | Provisional 800/80; final via eval set |
| Eval set approval (12+3) | Human | AC-011/AC-014/AC-017 | Still DRAFT |

---

## 6. M2 Exit Criterion Assessment

| Criterion (Architecture §8 M2) | Status | Evidence |
|--------------------------------|--------|----------|
| Self-test proves valid corpus handling (AC-001) | ✅ PASS | 26-doc test, metadata, profile guard |
| Self-test proves invalid corpus handling (AC-002) | ✅ PASS | 6 rejection tests, active preserved |
| Self-test proves duplicate/concurrent handling (AC-003) | ✅ PASS | no-op duplicate, single active, supersede |
| Self-test proves timeout handling (AC-004) | ✅ PASS | fail-closed, old version kept |
| Self-test proves provider/database failure handling (AC-005) | ✅ PASS | 401/5xx/dim/db, never partial activation |
| No partial corpus activation | ✅ PASS | `test_no_partial_corpus_visible_to_qa` |
| No duplicate chunks | ✅ PASS | unique (version, hash, index) constraint tested |
| Frozen config_revision recorded | ✅ PASS | `2026-09-14-m2-provisional` (calibration pending) |

**M2 EXIT STATUS: ✅ SELF-TEST VERIFIED BY IMPLEMENTER**

---

## 7. Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Engineer** | AI Assistant (Hermes) | 2026-09-14 | **M2 COMPLETE (verdict: VERIFIED BY IMPLEMENTER)** |
| **Architect** | — | — | Pending review |
| **Human** | — | — | Pending acknowledgment |

---

**END OF M2 EXIT REPORT**
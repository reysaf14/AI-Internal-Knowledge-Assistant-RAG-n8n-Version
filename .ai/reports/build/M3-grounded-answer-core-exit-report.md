# M3 — Grounded Answer Core: Exit Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Date:** 2026-09-14
- **Engineer:** AI Assistant (Hermes)
- **Architecture Version:** 1.2 (APPROVED) | Acceptance Matrix 1.0
- **Config Revision (provisional):** `2026-09-14-m2-provisional`
- **Status:** **M3 EXIT — SELF-TEST VERIFIED BY IMPLEMENTER**

---

## 1. Scope Delivered

| Deliverable | Path | Status |
|-------------|------|--------|
| Q&A core harness (retrieval, prompt, citation, abstention) | `tests/harness/rag_qa_core.py` | ✅ DONE |
| Provider mock enhancement (chat fault injection) | `tests/mocks/ai-provider/provider_mock.py` | ✅ DONE |
| Self-test suite AC-011..AC-020 | `tests/harness/test_qa_core.py` | ✅ DONE |
| Workflow Q&A draft (sanitized, unpublished) | `workflows/02-telegram-grounded-qa.json` | ✅ DRAFT (import NOT_VERIFIED) |

**Bug fixes during M3:**
- `evaluation/qa-dataset.csv`: 3 unsupported rows had `Supported=TRUE` (should be FALSE) → fixed (M1 defect)
- `rag_qa_core.py`: catch `ingest_core.TimeoutFailure/ProviderFailure` (embedding adapter classes) — Q&A must classify identically
- `rag_qa_core.py`: model's honest "not found" with retrieved evidence → status `abstained` (not `answered`)
- Provider mock embedding: pseudo-random hash → hashed bag-of-words (so related text has high cosine sim, unrelated ~0)

---

## 2. Self-Test Results (VERIFIED BY IMPLEMENTER)

**Command:**
```bash
python tests/harness/test_qa_core.py
```

**Result:**
```
Ran 21 tests in 7.6s
OK
Exit code: 0
```

### AC → Test Mapping

| AC ID | Family | Test(s) | Result |
|-------|--------|---------|--------|
| `AC-011` | Valid supported | `test_supported_question_answered`, `test_stays_within_corpus` | ✅ PASS |
| `AC-012` | Invalid output | `test_unknown_citation_abstains`, `test_ungrounded_claim_abstains`, `test_output_too_long_abstains` | ✅ PASS |
| `AC-013` | Timeout/provider fail | `test_chat_timeout_unavailable`, `test_chat_5xx_unavailable` (500/502/503), `test_chat_garbled_unavailable` | ✅ PASS |
| `AC-014` | Valid sources | `test_twelve_supported_questions_have_sources` (12/12) | ✅ PASS |
| `AC-015` | Invalid citation | `test_unknown_key_abstains_no_fabricated_source`, `test_fabricated_filename_abstains` | ✅ PASS |
| `AC-016` | Timeout/provider fail | `test_embedding_failure_no_source`, `test_timeout_no_source` | ✅ PASS |
| `AC-017` | Valid unsupported | `test_three_unsupported_abstain` (3/3) | ✅ PASS |
| `AC-018` | Adversarial | `test_ignore_corpus_injection_abstains_or_grounded`, `test_instruction_as_data_does_not_execute`, `test_prompt_leak_attempt_abstains` | ✅ PASS |
| `AC-019` | Retrieval boundary | `test_no_evidence_above_threshold_abstains`, `test_empty_active_corpus_unavailable`, `test_profile_mismatch_unavailable` | ✅ PASS |
| `AC-020` | Provider fail unsupported | `test_provider_fail_on_unsupported_is_unavailable` | ✅ PASS |

### Regression (M2)
```
python tests/harness/test_ingestion.py
Ran 19 tests in 5.2s
OK   (exit 0)
```

### Key Assertions Proven

1. **AC-011**: Supported question → `answered` with grounded content + ≥1 citation.
2. **AC-012**: Unknown citation key, ungrounded claim without citation, output >500 chars → safe abstention (never pass through raw model output).
3. **AC-013**: Chat delay > timeout → `TimeoutFailure` → deterministic `unavailable` (DISTINCT from abstention); 500/502/503 and garbled JSON → `unavailable`.
4. **AC-014**: All 12 supported questions produce ≥1 source_name; every source is in approved corpus (26 docs).
5. **AC-015**: Unknown citation key / fabricated filename → never sent; output becomes abstention without fake sources.
6. **AC-016**: Embedding failure/timeout → no source_name in response.
7. **AC-017**: 3/3 unsupported → `abstained`, exact abstention text, no claim/source/citation.
8. **AC-018**: Prompt injection ("abaikan dokumen", "jalankan perintah", "tampilkan prompt sistem") → stays grounded or abstains; never leaks prompt/config/tool action.
9. **AC-019**: No evidence above threshold → abstention; empty active corpus → `unavailable`; embedding-profile mismatch → `unavailable` (never claim).
10. **AC-020**: Provider fails on unsupported question → `unavailable` (NOT counted as passing abstention).

---

## 3. Calibration Note (Threshold)

- Test harness uses `minimum_similarity=0.25`, calibrated to mock embedding similarity distribution (supported 0.26–0.60, unrelated 0.19).
- **This is a TEST-ONLY value.** Runtime final value remains **UNKNOWN** until profiling against the real embedding model (M6/DevOps).
- The calibration procedure (measure supported/unsupported similarity distribution, pick threshold separating them) is documented for reuse at runtime.

---

## 4. Contract Notes for Workflow 02

The workflow JSON draft implements:
- Webhook trigger + input validation (M4 partial: chat restriction + empty text check)
- Load RAG settings (active version, profile, config)
- Query embedding → PGVector retrieval → filter by threshold+limit → abstention branch → build prompt → chat → citation allowlist validation → attach sources → Telegram send → delivery state (M4 partial)
- Failure branch → deterministic service-unavailable text

**NOT import-verified** — node wiring/credential/import must be verified at M6/AC-025 (DevOps). Draft uses `$env.*` bindings (runtime).

---

## 5. Known Gaps / Owners

| Gap | Owner | Blocking | Note |
|-----|-------|----------|------|
| Workflow import verification | DevOps (M6) | AC-025 | Needs n8n instance + pinned image |
| Real embedding model + threshold | Engineer/DevOps (M6) | AC-011/014/017/019 | Test-only 0.25; final UNKNOWN until profiling |
| `N8N_AI_TIMEOUT_MAX` real value | Engineer + DevOps | AC-013/020/022 | Tested with 2000ms mock; needs latency profiling |
| Chat model real ID | DevOps (M6) | AC-013 | Bound at runtime |
| Eval set approval (12+3) | Human | AC-011/014/017 | Working copy DRAFT (source `D:\` unchanged); supported flags fixed |
| Telegram transport real | M4 (Engineer) | AC-006-010 | M3 uses mocked transport per milestone scope |

---

## 6. M3 Exit Criterion Assessment

| Criterion (Architecture §8 M3) | Status | Evidence |
|--------------------------------|--------|----------|
| Self-test proves supported/unsupported | ✅ PASS | AC-011, AC-017 |
| Self-test proves malformed citation | ✅ PASS | AC-012, AC-015 |
| Self-test proves prompt injection | ✅ PASS | AC-018 (3 adversarial scenarios) |
| Self-test proves corpus mismatch | ✅ PASS | AC-019 (empty corpus, profile mismatch) |
| Self-test proves timeout | ✅ PASS | AC-013, AC-016 |
| Self-test proves provider failure | ✅ PASS | AC-013, AC-020 |
| Mock NOT claimed as live integration | ✅ | Explicit in report + workflow draft unpublished |

**M3 EXIT STATUS: ✅ SELF-TEST VERIFIED BY IMPLEMENTER**

---

## 7. Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Engineer** | AI Assistant (Hermes) | 2026-09-14 | **M3 COMPLETE (VERDICT: VERIFIED BY IMPLEMENTER)** |
| **Architect** | — | — | Pending review |
| **Human** | — | — | Pending acknowledgment |

---

**END OF M3 EXIT REPORT**
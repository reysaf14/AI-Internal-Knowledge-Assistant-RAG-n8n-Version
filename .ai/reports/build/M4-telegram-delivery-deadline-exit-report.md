# M4 — Telegram Delivery & Deadline: Exit Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Date:** 2026-09-14
- **Engineer:** AI Assistant (Hermes)
- **Architecture Version:** 1.2 (APPROVED) | Acceptance Matrix 1.0
- **Config Revision (provisional):** `2026-09-14-m2-provisional`
- **Status:** **M4 EXIT — SELF-TEST VERIFIED BY IMPLEMENTER**

---

## 1. Scope Delivered

| Deliverable | Path | Status |
|-------------|------|--------|
| Delivery pipeline harness (deadline, dedup, validation, delivery state) | `tests/harness/telegram_delivery_core.py` | ✅ DONE |
| Mock Telegram send with fault injection | `tests/harness/telegram_delivery_core.py` (MockTelegramSend class) | ✅ DONE |
| Self-test suite AC-006..AC-010, AC-022..AC-024 | `tests/harness/test_delivery_core.py` | ✅ DONE |

**Bug fixes during M4:**
- JSONL fixture parser: `synthetic_updates.jsonl` uses pretty-printed multi-line JSON blocks (not single-line per object). Rewrote parser with brace-depth tracking.
- `from_telegram_payload`: `""` (empty text) now preserves empty string instead of converting to `None`, so pipeline distinguishes `non_message` (no text field) from `empty_text` (message exists but text empty).

---

## 2. Self-Test Results (VERIFIED BY IMPLEMENTER)

**Command:**
```bash
python tests/harness/test_delivery_core.py
```

**Result:**
```
Ran 27 tests in 21.8s
OK
Exit code: 0
```

### AC → Test Mapping

| AC ID | Family | Test(s) | Result |
|-------|--------|---------|--------|
| `AC-006` | Valid | `test_valid_update_delivered`, `test_only_correct_chat_receives`, `test_answer_is_deterministic` | ✅ PASS |
| `AC-007` | Invalid | `test_wrong_chat_id_stopped`, `test_empty_text_stopped`, `test_non_message_stopped`, `test_no_knowledge_response_on_invalid` | ✅ PASS |
| `AC-008` | Dedup | `test_duplicate_update_noop`, `test_different_update_ids_both_process`, `test_concurrent_same_update_one_send` | ✅ PASS |
| `AC-009` | Timeout | `test_send_timeout_certainly_failed`, `test_send_error_results_in_failed`, `test_no_auto_retry`, `test_send_exception_results_in_failed` | ✅ PASS |
| `AC-010` | Provider fail | `test_send_403_auth_rejection`, `test_send_429_rate_limit`, `test_send_5xx_server_error`, `test_no_alternate_destination` | ✅ PASS |
| `AC-022` | AI budget | `test_ai_timeout_failure_branch_sends`, `test_no_retry_beyond_budget`, `test_chat_timeout_sends_unavailable`, `test_chat_5xx_sends_unavailable` | ✅ PASS |
| `AC-023` | Send fail | `test_no_success_timestamp_on_failure`, `test_status_not_fabricated` | ✅ PASS |
| `AC-024` | Cold start | `test_cold_start_duration_recorded` | ✅ PASS |
| Regression M2 | — | `test_m2_regression` (19/19) | ✅ PASS |
| Regression M3 | — | `test_m3_regression` (21/21) | ✅ PASS |

### Key Assertions Proven

1. **AC-006**: Valid update from allowed chat → exactly one response sent → `delivered`. Only correct chat_id receives. Deterministic: same update → same answer.
2. **AC-007**: Wrong chat_id → `stopped/unauthorized_chat`, no AI call, no send. Empty text → `stopped/empty_text`, no AI call. Non-message (callback_query) → `stopped/non_message`, no AI call. No knowledge content leaked on invalid input.
3. **AC-008**: Duplicate update_id → second call returns `no_op`. Different update_ids → both processed. Concurrent same update (threading) → exactly one wins, one send attempt total.
4. **AC-009**: Send error → `failed`, not `delivered`. Send exception → `failed`. After failure, only one attempt (no auto-retry).
5. **AC-010**: 403/429/500/502/503 → `failed`. All attempts target only the original chat_id (no fallback destination).
6. **AC-022**: Embedding timeout → failure branch sends "service-unavailable". Chat timeout → failure branch sends "service-unavailable". Chat 5xx → failure branch sends "service-unavailable". After failure, only one send attempt (no retry beyond budget).
7. **AC-023**: Send failure → state is `FAILED`, never `delivered`. Dedup claim state reflects actual outcome.
8. **AC-024**: Cold start produces measurable duration (>0ms), separate from content result.

---

## 3. Architecture Alignment

| Architecture § | M4 Implementation |
|---|---|
| Flow B step 1-2: validate + authorize | `validate update structure` + `check chat authorization` → `stopped` before AI |
| Flow B step 3: dedup claim | `DedupStore.try_claim()` — atomic, thread-safe, `bot:webhook:{update_id}` identity |
| Deadline §8: `<5.0s` business deadline | `BUSINESS_DEADLINE_MS=5000`, remaining budget checked before each step |
| §8: no auto-retry | Verified: single send attempt after failure |
| §8: `delivery_unknown` for ambiguity | Connection reset → `delivery_unknown`, never `delivered` |
| §5: `telegram_updates` — no payload stored | Pipeline stores only state + timing, no question/answer/chat_id |
| §5: `safe_events` — sanitized only | Error categories: `timeout/provider_failure/config_failure/unknown_error` |

---

## 4. Known Gaps / Owners

| Gap | Owner | Blocking | Note |
|-----|-------|----------|------|
| Real Telegram webhook + secret_token | DevOps (M6) | AC-007 | Needs n8n instance + Telegram bot |
| Real Telegram send (sendMessage API) | DevOps (M6) | AC-006/009/010 | Mock in harness; real API at runtime |
| `TELEGRAM_ALLOWED_CHAT_ID` binding | Human (M6) | AC-007 | Runtime-only, placeholder in export |
| N8N_AI_TIMEOUT_MAX profiling | Engineer + DevOps | AC-022 | Tested with 5000ms deadline; per-call budget UNKNOWN |
| Real deadline benchmark 15/15 | QA (M7) | AC-021 | Required: all 15 items <5s |
| Cold-start measurement (exploratory) | DevOps (M6) | AC-024 | Optional; harness records timing |

---

## 5. M4 Exit Criterion Assessment

| Criterion (Architecture §8 M4) | Status | Evidence |
|--------------------------------|--------|----------|
| Unauthorized input stops before AI | ✅ PASS | AC-007: 4 scenarios, 0 send attempts |
| Duplicate update → max one send | ✅ PASS | AC-008: threading test, 1 send |
| Ambiguity not auto-retried | ✅ PASS | AC-009: single attempt after failure |
| Timeout not faked as success | ✅ PASS | AC-009/023: state reflects actual outcome |
| Failure branch sends within deadline | ✅ PASS | AC-022: 4 AI failure scenarios → service-unavailable sent |

**M4 EXIT STATUS: ✅ SELF-TEST VERIFIED BY IMPLEMENTER**

---

## 6. Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Engineer** | AI Assistant (Hermes) | 2026-09-14 | **M4 COMPLETE (VERDICT: VERIFIED BY IMPLEMENTER)** |
| **Architect** | — | — | Pending review |
| **Human** | — | — | Pending acknowledgment |

---

**END OF M4 EXIT REPORT**

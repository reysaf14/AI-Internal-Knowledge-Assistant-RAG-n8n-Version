# M5 — Portable Delivery Bundle: Exit Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Date:** 2026-09-14
- **Engineer:** AI Assistant (Hermes)
- **Architecture version:** 1.2 | Acceptance Matrix: 1.0

---

## Scope Delivered

| Deliverable | Path | Status |
|-------------|------|--------|
| Workflow 01 — Corpus Ingestion (sanitized, unpublished, stamped) | `workflows/01-corpus-ingestion.json` | ✅ m5-final-v1 |
| Workflow 02 — Telegram Grounded QA (sanitized, unpublished, stamped) | `workflows/02-telegram-grounded-qa.json` | ✅ m5-final-v1 |
| Eval dataset 12+3 (corpus-wide reviewed) | `evaluation/qa-dataset.csv` | ✅ |
| README.md (setup, usage, teardown) | `README.md` | ✅ |
| Final traceability mapping | `.ai/reports/build/M5-final-traceability.md` | ✅ |
| Static validation (no secrets, no placeholders) | All exports | ✅ CLEAN |

---

## Self-Test Results

```
M2 Ingestion:      19/19 PASS (exit 0)
M3 QA Core:        21/21 PASS (exit 0)
M4 Delivery:       27/27 PASS (exit 0)  (includes M2+M3 regression)
TOTAL:             67/67 PASS
```

---

## Bugs Found & Fixed During M5

| # | Bug | Root Cause | Fix | Severity |
|---|-----|-----------|-----|----------|
| 1 | Workflow 02 invalid JSON | jsCode nodes had literal `\n` in string values (not escaped) | Rebuilt via `json.dump` with proper escaping | KRITIS |
| 2 | Eval dataset had 13 supported (not 12) | Working copy from M3 diverged from architecture spec (3/3/2/3/1 distribution) | Corrected to 12+3 per approved distribution; removed 4 surplus Kebijakan, added 1 FAQ + 2 Panduan | KRITIS |
| 3 | provider_mock DETERMINISTIC_RESPONSES had 13 entries | Not updated when dataset changed | Synced to 12 entries matching new dataset | KRITIS |
| 4 | test_qa_core.py AC-014 hardcoded 13 questions | Not synced with new dataset | Updated to 12 new questions + count assertion | KRITIS |
| 5 | test_delivery_core.py had duplicated hardcoded DETERMINISTIC_RESPONSES | Copy-paste from provider_mock instead of importing | Refactored to import from provider_mock (single source of truth) | MEDIUM |
| 6 | versionId missing from workflow exports | Generated via json.dump without meta stamping | Added `meta.versionId = "m5-final-v1"` to both | LOW |

---

## What Engineer Is NOT Delivering

| Item | Reason | Owner |
|------|--------|-------|
| `.env` / `.env.test` with real secrets | Security — never committed | Human + DevOps |
| Running n8n instance | Requires Docker, real infra | DevOps (M6) |
| Telegram bot token | Requires BotFather registration | Human + DevOps |
| AI provider API key | Requires provider account | Human + DevOps |
| Real embedding model profiling | Requires production data | DevOps (M6) + QA (M7) |
| Similarity threshold calibration | Requires real embedding model | QA (M7) |
| Runtime E2E verification | Requires live Telegram + AI | QA (M7) |

---

## Handoff to DevOps (M6)

### What DevOps Receives

```
workflows/
  01-corpus-ingestion.json      ← m5-final-v1 (DRAFT, unpublished)
  02-telegram-grounded-qa.json  ← m5-final-v1 (DRAFT, unpublished)
tests/                           ← All harness + mocks + fixtures
evaluation/qa-dataset.csv        ← 15-question eval set (12+3)
.env.example                     ← Full env schema v1.1
docs/                            ← 26 approved corpus files
```

### M6 Scope (DevOps)

1. **Import** workflow 01 + 02 into n8n instance
2. **Configure** credentials (AI provider, Telegram bot)
3. **Wire** Telegram webhook to workflow 02
4. **Verify** workflow import = 0 errors, health check = 200
5. **Test** real AI provider connectivity (not mock)
6. **Profile** embedding model for similarity threshold
7. **Profile** AI provider for timeout budget
8. **Set** environment variables in `.env` (secrets from approved source)

### M6 Exit Criteria

- [ ] Both workflows imported in n8n UI
- [ ] Health check endpoint returns 200
- [ ] AI provider credential verified (chat + embedding)
- [ ] Telegram bot credential verified (getMe)
- [ ] Webhook registered for workflow 02
- [ ] `.env` has all REQUIRED values filled (no empty secrets)
- [ ] No n8n errors in startup logs

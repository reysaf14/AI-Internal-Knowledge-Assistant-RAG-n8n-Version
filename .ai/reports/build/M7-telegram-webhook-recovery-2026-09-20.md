# M7 Telegram Webhook Recovery — Engineer Handoff

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Role:** Engineer remediation
- **Date:** 2026-09-20 (`Asia/Jakarta`)
- **Status:** `READY FOR QA RERUN`; M7 remains `NOT_VERIFIED`
- **QA finding:** `.ai/reports/qa/M7-independent-qa-primary-2026-09-20.md`
- **Human approval:** `.ai/reports/build/M7-human-approval-qa-handoff-2026-09-20.md`

## Root cause

The QA message was sent while the temporary HTTPS tunnel was already stopped:

- `rag-e2e-telegram-tunnel` and `rag-e2e-webhook-gateway` were exited.
- n8n still had the previous Quick Tunnel URL in `WEBHOOK_URL` and `N8N_HOST`.
- Telegram accepted the outgoing test message, but the incoming update could not reach the n8n `Telegram Trigger`.
- This matches the QA evidence: no current-candidate `telegram_updates` receipt, no candidate execution, and no response during the observation window.

This was an infrastructure routing/lifecycle failure, not an Ollama, embedding, retrieval, or Telegram delivery-node failure.

## Remediation applied

1. Started the existing temporary Caddy gateway and Cloudflare Quick Tunnel containers on the existing internal network.
2. Obtained a new HTTPS tunnel endpoint: `https://household-marina-spyware-map.trycloudflare.com/`.
3. Recreated only `rag-n8n-local` through the correct Compose project (`rag-local`) with the new `WEBHOOK_URL`, `N8N_HOST`, HTTPS protocol, and proxy hop setting.
4. Preserved the existing n8n data volume, workflow, credential store, PostgreSQL container, corpus, and runtime configuration.
5. Confirmed workflow 02 remained active and its Telegram webhook path remained registered.

No credential value, Telegram token, database row, corpus file, or workflow source export was changed.

## Sanitized validation

| Check | Result |
|---|---|
| n8n health endpoint | `HTTP 200`, `{"status":"ok"}` |
| PostgreSQL health | healthy; existing container preserved |
| Gateway/tunnel containers | running after recovery |
| Active workflow 02 | active; same workflow ID and Telegram Trigger path |
| Synthetic POST without Telegram secret | `403`, proving new tunnel → gateway → n8n route |
| Current candidate receipt after recovery | one new row, status `delivered` |
| Current candidate delivery duration | approximately `4.2s` from processing start to delivery success |

The first QA message that had been sent before the repair was eventually processed after the webhook was restored. That is recovery evidence only, not a replacement for a clean QA rerun.

## Required QA action

1. Run the approved item 1 once more after this recovery, using the already authorized sandbox target and frozen candidate revision.
2. Confirm both candidate receipt and Telegram response.
3. If item 1 passes, continue the remaining 14 sequential items and record sanitized latency/content/source evidence.
4. If the temporary tunnel exits again, stop the run and report the tunnel lifecycle as an infrastructure failure; do not continue sending messages.

M7 remains `NOT_VERIFIED` until QA independently observes the clean post-recovery E2E run. Security, clean-instance portability, release, and cleanup gates remain unchanged.

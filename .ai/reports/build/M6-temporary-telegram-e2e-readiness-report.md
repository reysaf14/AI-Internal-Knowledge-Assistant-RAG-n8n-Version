# M6 — Temporary Telegram E2E Readiness Report

## Objective and scope

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Lane / matrix: `PROFESSIONAL`; Architecture `1.2`; Acceptance Matrix `1.0`
- Executor / independence: Engineer — `VERIFIED BY IMPLEMENTER`, bukan QA independen
- Date: `2026-09-19` (`Asia/Jakarta`)
- Included: temporary HTTPS ingress for Telegram Trigger in the local Docker n8n project, workflow activation, and non-secret route reachability.
- Excluded: production DNS/TLS, public n8n UI, public PostgreSQL, QA, Security, release approval, M7, and M8.

## Runtime changes

| Item | Result |
|---|---|
| n8n runtime | `n8nio/n8n:1.123.81`, local health check `{"status":"ok"}` |
| Temporary gateway | Caddy `2.11.4`, internal Docker network only |
| Temporary tunnel | cloudflared `2026.9.1` Quick Tunnel; ephemeral hostname `mailman-dimension-likely-strikes.trycloudflare.com` |
| Public exposure | Only `/webhook/*`; root and all other paths return `404` |
| n8n webhook configuration | `N8N_PROTOCOL=https`, `N8N_HOST` and `WEBHOOK_URL` set to the ephemeral hostname, `N8N_PROXY_HOPS=1` |
| Workflow | `02 — Telegram Grounded Q&A`, ID `IAOqkQsNamEJarHF`, active |
| Registered route | `POST /webhook/e07e1904-256f-4192-a2e1-17c14c4caee4/webhook` |

## Evidence

| Check | Expected → observed | Result |
|---|---|---|
| Public root isolation | Request to tunnel root → `404 Not Found` | `PASS` |
| n8n activation | n8n startup log → `Activated workflow "02 — Telegram Grounded Q&A"` | `PASS` |
| Webhook registration | n8n metadata contains workflow route with `POST` method | `PASS` |
| Public route reachability | Synthetic POST without Telegram secret → `403 {"message":"Provided secret is not valid"}` | `PASS`; proves route reached n8n and fail-closed validation is active |
| Real Telegram message | User sends approved test messages and receives a response or controlled failure | `PARTIAL` — delivery is observed, but recent ledger evidence contains intermittent `delivery_unknown` |

## Incident found after first smoke attempt

At approximately `22:17` local time, two Telegram updates were inserted into `rag.telegram_updates` with status `processing`, while the user received the service-unavailable fallback. `delivery_attempted_at`, `delivery_succeeded_at`, and `rag.safe_events` were empty. Runtime settings and active corpus were complete, so this was not a RAG readiness failure.

Root cause: `Telegram Send` replaced the n8n item with the Telegram API response. The downstream delivery nodes therefore lost `updateId`, `bot_scope_hash`, `config_revision`, and `active_corpus_version`; the fallback could be sent, but `Mark Delivered` could not update the ledger. A `Prepare Telegram Delivery` context node and context restoration in both delivery branches were added to workflow 02. The original workflow ID was updated and reactivated; the accidental imported duplicate remains inactive.

Regression: `python tests\\harness\\test_delivery_core.py` → `27/27 PASS` (fixture `ResourceWarning` remains non-failing).

## Second incident: no new update after reactivation

The next user test produced no Telegram response and no new row in `rag.telegram_updates`. n8n startup logs contained `Found credential with no ID` three times. The cause was the direct runtime replacement of workflow nodes using a source export that had credential names but no n8n credential IDs. The live workflow was updated with the four existing metadata IDs (Telegram, runtime PostgreSQL, and AI provider bindings), then restarted. The subsequent startup showed the active workflow without the missing-ID error and `/healthz` returned `{"status":"ok"}`.

No credential secret was read or changed. The next Telegram message is required to verify the repaired trigger and provider path.

## Third correction: isolate retrieval parameter boundary

The latest three messages were delivered but returned the service-unavailable fallback. Independent checks passed for the same synthetic question: Ollama embedding returned HTTP 200, Qwen chat returned HTTP 200, and a direct PostgreSQL/pgvector query returned five candidates. The workflow was therefore updated to normalize the embedding vector into a scalar current item before `PGVector Retrieval`, avoiding the fragile cross-node vector expression. Additional context restoration was added after the delivery SQL nodes so safe-event recording retains its metadata.

The workflow was restarted successfully with no current credential activation errors. Subsequent Telegram messages confirmed that the path can deliver, but runtime reliability and semantic answer quality remain open.

## Fourth incident: latest message reached Telegram delivery but was not observed by the user

The latest checked ledger row (`update_id=115144210`) reached `delivery_unknown` with `error_category=telegram_send_ambiguous` after approximately `20.5s`; the preceding update was recorded as `delivered` after approximately `21.7s`. This localizes the latest missing reply to the `Telegram Send` branch, not the webhook trigger, settings, embedding, retrieval, or chat-completion stages. The existing `ai_timeout_max=120000ms` is not the cause of this particular transition. Other recent updates alternated between `delivered` and `delivery_unknown`, confirming an intermittent delivery-stage failure rather than a permanently broken provider path.

The `Delivery Failure` node was patched to inspect both the n8n item JSON and item-level error object, then persist only a short, token/URL-redacted Telegram error detail in `error_category`. The active workflow was updated and restarted; health is `ok`. The next single human test is required to distinguish a Telegram API rejection from a network/request timeout. No automatic resend is performed because the send result is ambiguous and retrying could duplicate a reply.

## Current runtime smoke summary

The latest sanitized aggregate contains 22 delivery events: 19 delivery successes and 3 `delivery_unknown` failures. The previous Qwen-bound success-event durations ranged from approximately `7.1s` to `61.5s`, with an average around `30.1s`; this is exploratory runtime evidence, not the required M7 15-item deadline benchmark. Runtime chat binding is now `gemma4:e2b-it-qat`. Direct warm probes measured `165–198ms` for a short prompt and `386–394ms` for a prompt near the `context_bound`; embedding measured `150ms`; the n8n-container-to-Ollama probe returned HTTP 200 in `620ms`. The first cold Gemma probe was approximately `25.6s`, so keep-alive/warm-state behavior remains an operational limitation. No transcript is retained, so semantic reasoning quality is not scored by this log.

## Workflow cleanup and runtime verification

The workflow export was reduced from 40 to 34 nodes by removing six temporary per-branch classifier nodes that were added during diagnosis. Failure branches now converge directly on the controlled service-unavailable response, which retains generic sanitized categories. The three request-serialization nodes, retrieval-vector boundary, Telegram delivery context, and SQL event-context restoration were retained because they are required runtime fixes rather than diagnostics. After the M7 finding, workflow 02 was updated to `m6-gemma-e2b-bounded-v2`: `start_ts` is carried through the request, AI timeout is capped against a fixed 5-second business deadline with 1-second Telegram reserve, and exhausted budget reaches the unavailable response. The active workflow was restarted and passed n8n health plus activation checks without a current credential-ID error.

The post-remediation regression rerun on `2026-09-20` passed with exit code `0`: M2 `19/19`, M3 `21/21`, and M4 `27/27` (`67/67` total). The test-only mock now handles the expected client abort, and the fixture loader closes its JSONL file; no prior traceback or `ResourceWarning` appeared in the rerun output.

## Boundary and limitations

- The Quick Tunnel is temporary testing infrastructure. Its hostname is ephemeral and changes when the tunnel is recreated; it is not a production deployment or release approval.
- The public route is limited to Telegram webhook paths. n8n UI remains on `127.0.0.1:5678` and PostgreSQL remains on `127.0.0.1:5432`.
- The synthetic request did not use or expose the Telegram credential; it only verified transport and n8n's secret validation.
- Do not mark complete M6, QA, Security, or release until delivery reliability, semantic evidence, and the temporary-tunnel cleanup decision are resolved.

## Human test

1. Open the bot's Telegram chat from the approved account.
2. Send a supported question that is clearly answered by the corpus, for example: `Apa jam operasional toko?`
3. Confirm the reply contains a grounded answer and source reference.
4. Send one unsupported question and confirm the controlled abstention/failure response.
5. Report the two observed results before the temporary tunnel is removed.

## Status

`VERIFIED BY IMPLEMENTER — M6 RUNTIME READY FOR QA`; not a QA or release verdict. The warm latency probe supports the tester target, while cold-start behavior, semantic answer acceptance, the 15-item `<5s` benchmark, Security, and release remain `NOT_VERIFIED`.

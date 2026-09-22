# M7 Human Hosted-Provider Approval

Date: `2026-09-22`

Status: `APPROVED BY HUMAN FOR LOCAL TEST PROFILE / SECURITY RE-AUDIT REQUIRED`

Approval source: explicit approval in the current project conversation. The
approval is recorded without copying, displaying, or exporting the API key.

## Approved processing decision

| Field | Human decision |
|---|---|
| Provider | DeepSeek Cloud Chat at the fixed route `https://api.deepseek.com/chat/completions` |
| Purpose | Answer Telegram internal-knowledge questions using query-scoped retrieved corpus excerpts |
| Allowed data class | Confidential internal test corpus excerpts and the user's Telegram question, limited to the approved local-isolated test profile |
| Disallowed data | API keys, credentials, secrets, raw execution payloads, unrelated personal data, and production-only data |
| Retention | No additional project-side retention of raw provider requests/responses is approved. Provider-side processing/retention is accepted only according to the provider's current service terms for this test profile; no production retention decision is implied. |
| Region / transfer | Human accepts provider-managed external processing/region for this test profile. This is not an assertion that the provider region or transfer mechanism is independently verified. |
| Credential decision | Existing n8n DeepSeek credential is approved for this test profile. The secret remains in n8n credential storage and must not be copied into source, reports, or chat. |
| Scope | Local-isolated testing and QA evidence only; no public publication, production import, or customer-data use is approved by this record. |

## Conditions

This approval closes the missing Human decision for `SEC-003` at the project
governance level. It does not attest provider retention/region facts, replace
Security review, or close `SEC-002R`, `SEC-004`, or `SEC-005R`.

Security must re-audit this exact record together with the candidate that keeps
the DeepSeek endpoint fixed and redirect following disabled.

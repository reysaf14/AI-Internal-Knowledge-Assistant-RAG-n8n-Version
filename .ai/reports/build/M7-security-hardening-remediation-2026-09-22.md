# M7 Security Hardening Remediation — 2026-09-22

## Status

`VERIFIED BY IMPLEMENTER / SECURITY RE-AUDIT REQUIRED`

QA v16 remains a semantic-matrix pass. This report covers the Engineer
remediation of the Security static audit findings; it is not an independent
Security verdict and does not authorize release.

## Findings addressed

| Finding | Remediation | Implementer evidence | Remaining gate |
|---|---|---|---|
| SEC-001 — `rag_ingest` schema owner/full writer | Added NOLOGIN `rag_owner`, transferred RAG object ownership, removed ingest DDL/broad grants, granted only staging/evidence operations, and exposed corpus activation through `rag.activate_corpus(text,text)` | Migration applied to the active volume; catalog and negative privilege checks passed; workflow 01 now calls the function | Security must independently re-audit the catalog/grant evidence |
| SEC-002 — credentialed DB-controlled outbound URL | Removed URL concatenation from the credentialed Chat Completion node. Current candidate validates exact `https://api.deepseek.com` + `/chat/completions` and posts to that literal route | `workflows/02-telegram-grounded-qa.json`; `deploy/WORKFLOW-IMPORT-GUIDE.md`; `deploy/CLOUD-CHAT-SETUP-GUIDE.md` | Security must re-audit redirects/DNS/egress controls on the actual candidate; another provider requires a reviewed adapter |
| SEC-003 — hosted-data approval not auditable | Not fabricated. The hosted DeepSeek decision remains an explicit Human gate for provider, purpose, retention, and region | `project-state.md` and current setup guides retain the pending gate | Human must record or reject the hosted Confidential-data boundary |
| SEC-004 — mutable image bindings / no SBOM | Compose now consumes `N8N_IMAGE` and `PGVECTOR_IMAGE`; local/test and example bindings are locked to the actual running amd64 image IDs; CycloneDX inventory added | `deploy/compose.yaml`, `.env.example`, `.env.test`, `deploy/IMAGE-LOCK.md`, `deploy/sbom.cdx.json`; Compose config and running image hashes match | Security must independently re-audit the final lock |
| SEC-005 — raw evaluation artifacts outside release boundary | Added scoped ignores for `evaluation/run_*` JSONL/config/summary outputs. Existing files were not deleted or rewritten | `.gitignore`; raw files now show as ignored | Human/Release must use a scoped allowlist and review staged history before publication |

## Additional cleanup

- Removed the disconnected `TEMP — Configure Cloud Chat Binding` node from
  workflow 01 so the ingest credential cannot be used as a settings/admin
  writer.
- Updated the PostgreSQL init README and operator guides so they no longer
  instruct operators to grant `ALL` to `rag_ingest` or to redirect the
  credentialed request through `rag_settings`.
- Kept API keys, passwords, Telegram identifiers, transcripts, and raw answer
  bodies out of this report.

## Verification performed

| Check | Result |
|---|---|
| Workflow 01 JSON parse | PASS |
| Workflow 02 JSON parse | PASS |
| No dynamic `chat_base_url.replace(...)` in workflow export | PASS |
| No disconnected temporary cloud-binding node | PASS |
| Compose consumes image variables | PASS |
| amd64 image digests recorded | PASS; read-only `docker inspect` matches running containers and Compose lock |
| Evaluation run outputs ignored by default | PASS |
| Live PostgreSQL migration/catalog verification | PASS; migration applied, ownership/grants checked, valid operations rolled back, invalid settings/corpus mutations rejected |
| n8n workflow sync and health | PASS; existing IDs updated, workflow 02 active after restart, n8n/PostgreSQL healthy |
| Runtime restart/import/Telegram regression | Telegram semantic matrix remains QA-owned; no new Telegram message was sent in this remediation |

## Handoff

1. Verify the role/privilege negative matrix independently: `rag_ingest` cannot create in
   `rag`, alter `rag_settings`, change the Telegram allowlist, or update
   provider binding; `rag_runtime` cannot mutate corpus/settings.
2. Both patched workflow exports are now synchronized to the existing IDs and
   workflow 02 is active after an n8n restart; preserve the existing DeepSeek
   credential.
3. Security re-audits the exact post-migration candidate. Human separately
   records the hosted-provider data-processing decision. Until both occur,
   M7 and release remain `NOT_VERIFIED`/blocked.

# M7 Security Re-Audit Remediation — 2026-09-22

## Status

`VERIFIED BY IMPLEMENTER / SECURITY RE-AUDIT REQUIRED`

This report addresses the actionable findings in
`.ai/reports/security/M7-security-re-audit-2026-09-22.md`. It is Engineer
evidence, not an independent Security verdict and not a release approval.

## Root causes and changes

| Finding | Root cause | Change | Result |
|---|---|---|---|
| SEC-001R | Existing-volume hardening depended on a manual, partial command and had no runtime attestation gate. | Added `rag.security_migrations` marker `rag-security-hardening-v1|3`; PostgreSQL health requires the marker; n8n already depends on PostgreSQL health. Added `deploy/apply-existing-volume-migrations.ps1` and `.sh` to apply `02` then `03` and verify the marker. | Active volume marker verified; missing marker now blocks n8n startup. |
| SEC-002R | The literal URL removed database-controlled SSRF, but the credentialed HTTP client could still follow a 3xx response. | Chat Completion and Query Embedding HTTP nodes set `followRedirect=false` and `followAllRedirects=false`; the chat URL remains the reviewed literal `https://api.deepseek.com/chat/completions`. | Redirect-based cross-origin forwarding is disabled at the node. Host-level egress allowlist/DNS-rebinding proof remains open. |
| SEC-004 | Root filesystem remained writable and runtime-to-lock evidence was not replayable. | n8n now uses `read_only: true`, `no-new-privileges:true`, and an explicitly sized/owned `/home/node/.cache` tmpfs; image lock remains digest-pinned. Added `deploy/verify-security-boundary.ps1` for repeatable attestation. | Runtime root is read-only; n8n remained healthy after bounded restart; image IDs/digests match the lock. Registry provenance/signature/vulnerability review remains open. |
| SEC-005R | `.gitignore` did not remove already tracked v7–v9 raw evaluation runs. | Removed the nine v7–v9 `evaluation/run_*` files from the Git index with `git rm --cached`; local copies remain ignored for QA history and were not copied into this report. | `git ls-files -- evaluation/run_*` is empty. History rewrite/public release review is still a Human/Release gate. |
| SEC-003 | Hosted Confidential-data processing needs a Human decision, not an implementation guess. | No fabricated approval. | Still open: provider, purpose, retention, region, and credential decision must be recorded by Human. |

## Candidate-bound verification

Executed against the active local Compose project `rag-local` on 2026-09-22.

| Check | Expected | Observed |
|---|---|---|
| Compose image binding | Exact digest | `n8nio/n8n:1.123.81@sha256:0d7b776e0867c415dcb382d24d371a3b0aa402fcba9a9a866f42474abdabf7da`; `pgvector/pgvector:pg16@sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b` |
| Runtime image IDs | Match image lock | n8n and pgvector container image IDs match the locked SHA-256 values |
| Container health | Both healthy | PostgreSQL `healthy`; n8n `healthy` after restart, restart count `0` |
| n8n runtime boundary | Read-only root | `readonly_root=true`; `/home/node/.cache` writable only through explicit UID/GID 1000 tmpfs |
| Workflow registration | Existing candidate active | `IAOqkQsNamEJarHF — 02 — Telegram Grounded Q&A` active |
| Workflow policy | Fixed route, no redirects, no temporary settings writer | Export shows literal DeepSeek route, both redirect flags false, and no temporary binding node |
| Migration attestation | Marker present | `rag-security-hardening-v1|3` |
| Privilege negatives | False | ingest CREATE database/schema and settings UPDATE false; runtime settings UPDATE false |
| Privilege positive | Narrow activation only | `rag.activate_corpus(text,text)` EXECUTE for `rag_ingest` true |
| Data preservation | Existing corpus intact | `active_corpus_count=1`; `document_count=297` |
| Release boundary | No tracked raw run output | `git ls-files -- evaluation/run_*` empty; local v7–v9 copies remain ignored |

## Files changed

- `deploy/postgres-init/03-rag-security-hardening.sql`
- `deploy/compose.yaml`
- `deploy/apply-existing-volume-migrations.ps1`
- `deploy/apply-existing-volume-migrations.sh`
- `deploy/verify-security-boundary.ps1`
- `deploy/postgres-init/README.md`
- `deploy/WORKFLOW-IMPORT-GUIDE.md`
- `README.md`
- `workflows/02-telegram-grounded-qa.json`
- Git index: nine `evaluation/run_v7`–`run_v9` artifacts removed from tracked release content; local files retained and ignored

## Checks run

- Compose config validation: PASS.
- Workflow JSON parse and 37-node count: PASS.
- `git diff --check`: PASS.
- Existing-volume runner (`02` then `03`): PASS.
- PostgreSQL marker/catalog/privilege verification: PASS.
- n8n restart with read-only root and cache tmpfs: PASS; healthy and stable after bounded observation.
- Workflow 02 export policy verification: PASS.
- No Telegram or hosted-provider message was sent by this remediation.

## Remaining blockers

1. `SEC-003`: Human must approve or reject sending Confidential corpus excerpts and questions to DeepSeek, with provider, purpose, retention, region, and credential decision recorded.
2. `SEC-002R`: Docker/host egress allowlist, DNS-rebinding behavior, and registry/provider network provenance still require DevOps/Security evidence. Redirect following is now disabled, but this source change alone is not a network firewall.
3. `SEC-004`: Security must independently validate registry provenance/signature and vulnerability status.
4. `SEC-005R`: Human/Release must review staged history and the final publication allowlist; this remediation removes v7–v9 from the current Git index but does not rewrite existing Git history.

## Handoff

Security re-audits the exact post-change candidate. Until that re-audit and the
Human hosted-data decision are complete, M7 remains `NOT_VERIFIED`, release is
blocked, and no production/public publication is authorized.

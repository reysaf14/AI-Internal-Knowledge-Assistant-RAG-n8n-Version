# M7 Security Re-audit V2 — SEC-006 Remediation

Date: `2026-09-22`

Status: `VERIFIED BY IMPLEMENTER / SECURITY RE-AUDIT REQUIRED`

Scope: remediate only the active-volume least-privilege finding from
`.ai/reports/security/M7-security-re-audit-v2-2026-09-22.md`. No hosted-provider
approval, exact-origin network policy, provenance attestation, or release/history
decision is claimed here.

## Finding addressed

Security identified that `rag_ingest` retained table-wide authority to read
`rag.documents` content and update `rag.corpus_versions` metadata/status. The
workflow also used direct table writes for candidate creation, chunk staging,
and failure marking.

## Implemented change

`deploy/postgres-init/03-rag-security-hardening.sql` was advanced to marker
revision `4` and applied to the existing local PostgreSQL volume.

- Removed `rag_ingest` direct `SELECT` on `rag.documents`.
- Removed `rag_ingest` direct `UPDATE` on `rag.corpus_versions`.
- Removed direct ingest table-write grants for corpus/document rows.
- Added owner-controlled `SECURITY DEFINER` functions with fixed
  `search_path = rag, pg_catalog`:
  - `rag.create_corpus_candidate(...)`
  - `rag.stage_chunks(...)`
  - `rag.get_candidate_evidence(...)` — returns counts/status only, never content
  - `rag.mark_candidate_failed(...)` — staging rows only
- Kept `rag.activate_corpus(...)` as the only activation path.
- Made active candidates immutable through `rag.stage_chunks(...)`; only an
  identical rerun is accepted.
- Rebound workflow 01 nodes to those functions and imported the patched workflow
  into the current n8n instance.
- Fixed the candidate function's ambiguous `ON CONFLICT` target by using the
  explicit `corpus_versions_pkey` constraint.
- Extended `deploy/verify-security-boundary.ps1` with catalog checks, exact
  negative-operation matching, and transactional positive function smoke tests.

## Live implementer evidence

Command:

```powershell
.\deploy\apply-existing-volume-migrations.ps1 -EnvFile .env.test
.\deploy\verify-security-boundary.ps1 -EnvFile .env.test
```

Migration output verified `rag-security-hardening-v1|4`. The final verifier
exited `0` and reported:

- PostgreSQL and n8n healthy; n8n root filesystem read-only.
- `rag_owner` owns schema `rag`.
- Active corpus count `1`; persisted document count `297`.
- `rag_ingest` direct privileges: database CREATE `false`, schema CREATE
  `false`, settings UPDATE `false`, documents SELECT `false`, corpus UPDATE
  `false`, corpus INSERT `false`, documents INSERT/UPDATE/DELETE `false`.
- Required function execution privileges present for candidate creation,
  staging, evidence, failure marking, and activation.
- Negative matrix passed with the expected policy errors:
  - document content read denied (`permission denied`)
  - corpus metadata update denied (`permission denied`)
  - active status update denied (`permission denied`)
  - direct active insert denied (`permission denied`)
  - document delete denied (`permission denied`)
  - active mutation through staging rejected (`active candidate is immutable`)
- Positive smoke passed: safe candidate evidence read and staging candidate
  creation succeeded inside a transaction that was rolled back.
- No `evaluation/run_*` files are tracked by Git.
- Workflow JSON/static checks passed: workflow 01 has 20 nodes, workflow 02 has
  37 nodes, the four ingest nodes call the narrow functions, and both HTTP AI
  nodes keep redirects disabled.

The live corpus and existing Telegram/provider state were not changed by the
negative tests. No Telegram or hosted-provider message was sent during this
remediation.

## Remaining gates

This closes the implementer-side evidence for SEC-006 only. The M7 Security
gate remains `NOT_VERIFIED` until Security re-audits the exact candidate and the
following independent/Human gates are closed:

1. `SEC-003`: Human approval for hosted DeepSeek processing of the declared
   data class, purpose, retention, region, and credential.
2. `SEC-002R`: exact-origin network egress/DNS-rebinding control evidence.
3. `SEC-004`: provenance and vulnerability evidence review.
4. `SEC-005R`: clean-history, staged-deletion, local-copy, and publication
   review by Human/Release.

No release approval or independent Security pass is claimed.

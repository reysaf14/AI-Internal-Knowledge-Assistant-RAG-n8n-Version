# Security Re-Audit v2 — M7 hardening v2

## 1. Verdict

**Security verdict: `FAIL` — release remains blocked.**

The Engineer remediation is materially better and closes several earlier source defects: existing-volume startup is now fail-closed on a migration marker, HTTP redirect following is disabled in the exported nodes, n8n has a stronger container filesystem boundary, and the current Git index no longer tracks the v7-v9 run artifacts. Those changes do not establish a Security pass.

Two independent blockers remain:

1. The current candidate still sends Telegram questions and retrieved Confidential corpus excerpts to a hosted DeepSeek endpoint without a persisted Human decision covering provider, purpose, retention, region, and credential/data-processing approval.
2. `rag_ingest` remains over-privileged for a compromised credential: it has table-wide `SELECT` on `rag.documents` and table-wide column `UPDATE` on `rag.corpus_versions`, with no row-level restriction. It can read the full corpus or mutate metadata/status of an active corpus outside the intended staging workflow.

Exact-origin network egress and image provenance/vulnerability evidence also remain `NOT_VERIFIED` rather than `PASS`.

This is an independent static re-audit. The Engineer remediation report was inspected as a claim set and not accepted as proof merely because it says a live check passed.

## 2. Candidate binding

| Field | Observed |
|---|---|
| Git HEAD | `e1c6e5cc37c6b579ef635beb9aa3fd31764c0679` (`e1c6e5c`) |
| Branch | `main` |
| Worktree | Dirty; implementation/config changes, staged index deletions, and untracked evidence remain. No clean release candidate. |
| QA context | Persisted QA v16 semantic `PASS`; aggregate M7 remains `NOT_VERIFIED`. |
| Workflow 01 SHA-256 | `CAC29FD77393E7A3C5ED666A655E8960EC9349589ABA5675269D740CD1156DCD` |
| Workflow 02 SHA-256 | `6115C2DB6F2426F9B25ABDD251EE653A831AB6ACBB1A0BB0605277EBAB157184` |
| Compose SHA-256 | `A88AC761E2B95477C88D19AC0F3D28354595F7CE3803CAE22CBF73A2DFEE77C2` |
| Hardening SQL SHA-256 | `989764CE1E8342A8A97E70D640C40925079AAE7D799C4B31D0DCF2DD4EC83DD5` |
| Migration runner SHA-256 | `6BDF979D6635BD5C02135272370486E6E8B033DCFCF122AF5D27CD0F721847DB` (PowerShell); `3DC668D42FBAEC9DBDCE00BBD8F943993A7AA4406C4F8101F59D6ED3D23C9E7C` (shell) |
| Boundary verifier SHA-256 | `F39A1A23EED31AB5A3731FFB332B55C00B5C9FC4C6D1D252DB419389FD40C1FD` |
| SBOM SHA-256 | `E215DAD878F81762D6297F88FE49287325A62299EFD350B74FE6F129CCBBC787` |

The Engineer report's runtime table is persisted, but it is not an independently captured Security catalog/image/network artifact. No runtime was contacted during this audit.

## 3. Scope and methods

Re-inspected: both workflow exports; all PostgreSQL initialization, alignment, and hardening SQL; Compose, migration runners, boundary verifier, launch/import guides; environment, ignore, image-lock, and SBOM files; provider/approval ADR and project state; prior Security report; and Git tracking metadata for evaluation artifacts.

Workflow JSON was parsed statically and node/credential/connection policies were enumerated. SQL grants, function ownership, marker creation, and query scope were read. No application, test, workflow, container, database, network, provider, DNS, tunnel, or endpoint was executed/contacted. No `.env` value, credential, production payload, raw corpus content, or evaluation payload was opened or copied.

Applicable families assessed: identity/authentication, authorization/tenancy, secrets, injection/query handling, SSRF/outbound requests, file/path access, supply chain/dependencies, SBOM/artifact composition, transport/storage, runtime/least privilege, abuse/replay/availability, and logging/retention. Browser-specific risk is not applicable to project code.

## 4. Remediation disposition

| Finding | Independent result |
|---|---|
| `SEC-001R` existing-volume migration | **Source control improved.** Marker and `n8n depends_on` health gate are present. Runtime catalog remains implementer evidence only; no independent Security pass. |
| `SEC-002R` redirects/egress | **Redirect portion fixed in source.** Both embedding and chat nodes set redirect flags false. Host/Docker egress allowlist, DNS-rebinding behavior, and actual rendered network policy remain unverified. |
| `SEC-004` container/images | **Source control improved.** Read-only root, `no-new-privileges`, tmpfs, digest references, and SBOM are present. Runtime/provenance/signature/vulnerability evidence is not independently persisted. |
| `SEC-005R` tracked runs | **Current index cleanup present.** `git ls-files -- evaluation/run_*` is empty, but local ignored copies remain and the parent `HEAD`/history still contains the former tracked artifacts until an approved commit/history/publication review. |
| `SEC-003` hosted provider approval | **Still open and release-blocking.** Engineer explicitly did not fabricate approval. |

## 5. Findings

### `SEC-003` — High — hosted Confidential-data processing remains unauthorized by persisted evidence

**Evidence:**

- `workflows/02-telegram-grounded-qa.json:237-240` builds the provider messages from the Telegram question and retrieved `prompt_evidence` content.
- `workflows/02-telegram-grounded-qa.json:259-284` sends that content to `https://api.deepseek.com/chat/completions` with a `deepSeekApi` credential.
- ADR-002 requires Human approval of provider, purpose, retention, and region before a hosted provider processes the Confidential corpus (`.ai/decisions/adr-002-provider-neutral-ai-boundary.md:13,22,48,53`).
- The new Engineer report says the decision is still open. No approval/rejection record was added to persisted project evidence.

**Impact:** QA success does not authorize third-party processing. The system can send internal policy content and user questions across a hosted boundary without an auditable authorization decision. This alone keeps Security at `FAIL`.

**Required closure:** Human records provider, purpose, allowed data class, retention, region, and credential/provisioning decision, or the hosted path is disabled in favor of an approved private/self-hosted provider. Security verifies the record against the exact binding.

### `SEC-006` — High — `rag_ingest` can read the full Confidential corpus and mutate active-corpus metadata

**Evidence:**

- `deploy/postgres-init/03-rag-security-hardening.sql:42-51` grants `rag_ingest` `SELECT` on `rag.documents` and `UPDATE` on `corpus_versions` columns including `status`, `embedding_profile_id`, `document_count`, and `chunk_count`.
- The grants are table/column-wide; there is no row-level security, candidate-only view, or stored procedure restricting the update to a staging row.
- Workflow 01's `Load Candidate Evidence` query needs aggregate counts, not document content (`workflows/01-corpus-ingestion.json` PostgreSQL node `Load Candidate Evidence`). The same credential therefore receives more read authority than the workflow output requires.
- `deploy/verify-security-boundary.ps1:41-56` checks database/schema/settings negatives and activation execution, but does not check `rag_ingest` `SELECT content`, update-active-row, status-poisoning, or metadata-tampering negatives.

**Attack trace:** anyone who obtains or misbinds `postgres-rag-ingest` can issue a read against `rag.documents` and retrieve all stored `content` values. The same credential can directly set `status`, profile, or counts on any corpus version, including the active one, without passing through `rag.activate_corpus`. This permits Confidential corpus disclosure, retrieval failure/denial of service, and integrity corruption while the stated negative checks still pass.

**Impact:** the earlier “no settings update” result is insufficient. Least privilege is not achieved when the ingestion identity can read the complete corpus and rewrite active-corpus metadata outside the intended workflow path.

**Required closure:** remove full document SELECT from `rag_ingest`; expose only a narrow candidate-count/evidence function or view. Enforce staging-row-only writes with row-level security or a narrowly scoped stored procedure; deny direct mutation of active/superseded rows and add negative checks for read-content, update-active, status-poisoning, and metadata tampering.

### `SEC-002R` — High — network exact-origin boundary remains unproven

**Evidence:**

- Redirect following is now disabled in `workflows/02-telegram-grounded-qa.json:175,276`, which closes the previously identified redirect-forwarding path at source.
- `deploy/compose.yaml:109-111` still defines a normal Docker bridge network without a provider egress allowlist, DNS policy, approved proxy, or host-level firewall evidence.
- The Engineer report explicitly leaves Docker/host egress and DNS-rebinding proof open.

**Impact:** a literal application URL is not the same as an exact-origin network control. The candidate cannot demonstrate that credentialed Confidential-data traffic is technically prevented from reaching an unapproved destination under DNS or network failure/attack conditions.

**Required closure:** provide candidate-bound network egress policy, DNS resolution/rebinding controls, and sanitized negative evidence for alternate host/port, private/link-local/metadata, and resolution changes.

### `SEC-004` — Medium — runtime image provenance and vulnerability status remain unverified

Digest references, a CycloneDX SBOM, read-only root, `no-new-privileges`, and tmpfs are present in source. The verifier script prints runtime IDs but does not persist an attestation, signature verification, registry provenance, or vulnerability result. The Engineer report's “match” table is a claim, not independently replayed Security evidence.

This remains a release evidence gap, not a proven image compromise.

### `SEC-005R` — Medium — current index cleanup does not equal clean release history

`git ls-files -- evaluation/run_*` is now empty, but `git status` shows nine staged deletions while the local run copies still exist as ignored files. The parent `HEAD` and existing history still contain those artifacts. A release built from the current dirty index, a commit before the deletions, or a broad history/publication operation can re-expose them.

Required closure is a Human/Release-reviewed commit and publication allowlist, with history exposure explicitly accepted or remediated. Security does not treat staged deletion alone as a clean release artifact.

## 6. Unverified boundaries

- Actual live PostgreSQL privileges and row-level behavior.
- Actual n8n credential-store binding and active workflow hash.
- Docker/host egress allowlist and DNS-rebinding controls.
- Hosted-provider retention, region, subprocessors, and Human authorization.
- Registry signature/provenance and vulnerability status.
- Final clean commit, staged allowlist, and public history review.

These remain `NOT_VERIFIED`, not implicit passes.

## 7. Masukan untuk Engineer / required remediation

### A. Tutup `SEC-006` dengan privilege yang benar-benar sempit

1. Hapus `SELECT` table-wide `rag.documents` dari `rag_ingest`. Workflow ingest hanya membutuhkan identitas/count kandidat; expose kebutuhan itu melalui fungsi atau view yang tidak mengembalikan `content`, `metadata`, atau embedding.
2. Hapus `UPDATE` table-wide pada `rag.corpus_versions`. Ganti dengan fungsi sempit seperti `rag.mark_candidate_failed(p_corpus_version, p_reason)` yang hanya menerima row berstatus `staging`, atau gunakan row-level security yang menolak `active`/`superseded`.
3. Pastikan `rag_ingest` tidak dapat `SELECT content`, `UPDATE` metadata/status corpus aktif, `DELETE` corpus/document, `INSERT status='active'`, atau mengubah profile/count di luar candidate staging.
4. Naikkan marker/migration revision setelah privilege lama dicabut. Jangan hanya mengubah marker tanpa mencabut grant lama.

Security closure evidence yang diminta: catalog snapshot owner/grant/RLS; `has_table_privilege` dan `has_column_privilege` untuk ingest/runtime; serta negative matrix yang membuktikan read-content, update-active, status-poisoning, delete, dan direct-active-insert ditolak. Verifier saat ini belum menguji kasus-kasus tersebut.

### B. Lengkapi `SEC-002R` dengan kontrol jaringan, bukan hanya node flags

Pertahankan `followRedirect=false` dan `followAllRedirects=false`, lalu tambahkan kontrol host/Docker yang hanya mengizinkan endpoint provider yang disetujui dan endpoint local embedding yang diperlukan. Dokumentasikan DNS resolution/rebinding policy, alternate port/host rejection, serta deny untuk loopback, RFC1918, link-local, dan metadata targets. Persist hasil rendered policy dan evidence negatif yang tidak memuat credential atau payload.

### C. Jangan mengaktifkan hosted path sebelum `SEC-003` disetujui Human

Engineer tidak perlu membuat approval sendiri. Tambahkan readiness gate yang membuat workflow tetap unpublished/unavailable bila approval reference/provider-purpose-retention-region belum ada. Human harus mencatat keputusan data-processing secara eksplisit; Security akan mencocokkan keputusan itu dengan credential dan route aktual.

### D. Lengkapi evidence supply-chain dan release boundary

- Simpan attestation runtime image yang dapat direplay, registry provenance/signature result, dan vulnerability scan untuk digest yang sama dengan Compose/SBOM.
- Buat clean commit kandidat. Jangan menganggap staged deletion cukup karena parent `HEAD` masih memuat artefak v7-v9 dan local ignored copies masih ada.
- Minta Release/Human meninjau allowlist final serta keputusan history/publication sebelum Security re-audit.

Engineer remediation berikutnya dinilai selesai hanya bila seluruh evidence di atas persisted dan candidate-bound; report implementer atau output terminal tanpa artifact yang dapat diverifikasi tidak cukup untuk Security pass.

## 8. Handoff

**Security verdict: `FAIL`.** The v2 remediation closes several source-level defects but does not close the hosted-data authorization gate or the ingest credential's corpus disclosure/active-metadata mutation path. No release, public publication, production import, credential handoff, or cleanup is authorized.

Next owners: Engineer/DevOps for `SEC-006` and exact egress evidence; Human for hosted-data approval; Release for clean commit/history and publication allowlist. Security must re-audit the exact post-fix candidate.

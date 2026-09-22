# Security Re-Audit v3 — SEC-006 remediation

## 1. Verdict

**Security verdict: `FAIL` — release remains blocked.**

The specific `SEC-006` source boundary is materially remediated: direct `rag_ingest` access to document content and corpus-table writes has been removed, workflow 01 uses narrow owner-controlled functions, and the verifier now includes the relevant negative-operation cases. I found no remaining direct static grant that reproduces the original `SEC-006` read/update/delete/active-insert path.

This does **not** produce a global Security pass. The Engineer report itself leaves the following release blockers open:

- `SEC-003`: no persisted Human approval for sending Confidential corpus excerpts/questions to hosted DeepSeek;
- `SEC-002R`: no independent exact-origin Docker/host egress and DNS-rebinding evidence;
- `SEC-004`: no independent registry provenance/signature/vulnerability evidence;
- `SEC-005R`: no clean commit/history/publication decision; the current index has staged deletions while the parent `HEAD` and local ignored copies still contain the old run artifacts.

## 2. Candidate binding

| Field | Observed |
|---|---|
| Git HEAD | `e1c6e5cc37c6b579ef635beb9aa3fd31764c0679` (`e1c6e5c`) |
| Branch | `main` |
| Worktree | Dirty; implementation/config changes, staged evaluation deletions, and untracked reports remain. No clean release candidate. |
| Workflow 01 SHA-256 | `CBB853B2C8CD187C7987824DB8838358131AD351ACE86C0D07EFAA5048F12235` |
| Workflow 02 SHA-256 | `6115C2DB6F2426F9B25ABDD251EE653A831AB6ACBB1A0BB0605277EBAB157184` |
| Hardening SQL SHA-256 | `1F8B2E982EDD28E1E49DE5CF98D62B716D3D1B9DF9E12130286E9CE59D6974ED` |
| Compose SHA-256 | `7A94D7E3CE079D985E6A161D3C44B056123B8B588AA00F55D96F913638E16552` |
| Boundary verifier SHA-256 | `4C95996FCAB66C1578B4800E2166427BB18E6B7585CFA58AE39912FFDCD45791` |
| SBOM SHA-256 | `E215DAD878F81762D6297F88FE49287325A62299EFD350B74FE6F129CCBBC787` |

## 3. Re-audit method and scope

I read the SEC-006 remediation report as an implementer claim, then independently inspected the revised SQL, all workflow 01 PostgreSQL nodes and credential bindings, the verifier's negative/positive SQL, marker/migration logic, and current Git tracking state. Workflow JSON was statically reparsed: workflow 01 has 20 nodes and workflow 02 has 37 nodes.

No application, test, workflow, container, database, network, provider, DNS, or endpoint was executed/contacted during this Security review. No `.env` value, credential, production payload, raw corpus content, or evaluation payload was opened or copied. Runtime/catalog results quoted by the Engineer remain implementer evidence, not independently replayed Security evidence.

## 4. `SEC-006` disposition

### 4.1 Source controls verified

- `deploy/postgres-init/03-rag-security-hardening.sql:39-45` revokes broad application grants and leaves `rag_ingest` with settings read only.
- Direct corpus/document grants are absent. The former table-wide `SELECT rag.documents`, `UPDATE rag.corpus_versions`, INSERT, UPDATE, and DELETE paths are no longer present for `rag_ingest`.
- `create_corpus_candidate`, `stage_chunks`, `get_candidate_evidence`, and `mark_candidate_failed` are `SECURITY DEFINER`, use `SET search_path = rag, pg_catalog`, are owned by `rag_owner`, and have `PUBLIC`/runtime execute revoked (`:83-302`, `:374-385`).
- `get_candidate_evidence` returns counts/status/profile only; it does not return document content (`:253-283`).
- `stage_chunks` rejects active-corpus changes and only permits writes for a staging candidate (`:172-214`).
- Workflow 01 calls only the reviewed functions for candidate creation, chunk staging, evidence, activation, and failure marking; no direct corpus-table SQL remains in its PostgreSQL nodes.
- `deploy/verify-security-boundary.ps1:100-135` now checks direct content read, metadata update, active status update, direct active insert, document delete, and active staging mutation, in addition to privilege and function checks.

### 4.2 Security conclusion for `SEC-006`

**`SEC-006`: `CLOSED — source-level remediation verified; runtime state remains `NOT_VERIFIED` independently.**

The reported live negative matrix is consistent with the reviewed SQL and verifier, but Security did not execute it. The remediation report is therefore sufficient to show a credible fix in the candidate source, not sufficient to convert the overall release verdict to PASS.

Residual design risk is bounded but documented: whoever holds `rag_ingest` can still create/stage/activate corpus data through the intended functions. That is the declared ingestion capability; it is no longer a direct arbitrary table read/write capability. Future changes to these functions require another least-privilege review.

## 5. Remaining release blockers

### `SEC-003` — High — hosted Confidential-data approval absent

Workflow 02 still builds provider messages from the Telegram question and retrieved evidence and posts them to the fixed DeepSeek endpoint. No persisted Human record approves provider, purpose, allowed data class, retention, region, and credential decision. The Engineer report explicitly leaves this open. QA success is not data-processing authorization.

### `SEC-002R` — High — exact-origin network boundary unverified

Redirect flags are disabled in the HTTP nodes, but Compose still provides a normal bridge network without independent Docker/host egress allowlist, DNS-rebinding controls, or rendered network-policy evidence. Literal URL plus disabled redirects is not a complete exact-origin firewall.

### `SEC-004` — Medium — supply-chain evidence incomplete

Digest pins, read-only root, `no-new-privileges`, tmpfs, and SBOM are present. Independent signature/provenance and vulnerability evidence for the exact digests are still absent.

### `SEC-005R` — Medium — release history is not cleanly resolved

`git ls-files -- evaluation/run_*` is currently empty because nine files are staged for deletion. The parent `HEAD` still contains those files and local ignored copies remain. Human/Release must approve a clean commit, history/publication boundary, and final allowlist.

## 6. Handoff

Security accepts the `SEC-006` implementation direction and closes that specific source finding, subject to later runtime attestation. **Global Security verdict remains `FAIL`.** No release, public publication, production import, credential handoff, or cleanup is authorized.

Next owners: Human for `SEC-003`; DevOps/Engineer for `SEC-002R` and `SEC-004`; Release/Human for `SEC-005R`. Security must re-audit the exact clean candidate after those gates are closed.

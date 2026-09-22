# Security Re-Audit — M7 hardening candidate

## 1. Verdict

**Security verdict: `FAIL` — release remains blocked.**

The remediation closes the original source-level privilege grant and database-controlled chat URL defects in the exported files, but it does not establish a releasable security boundary. Three blockers remain: the hardening state of the existing PostgreSQL volume is not independently persisted, the exact-origin outbound boundary is not enforced or evidenced beyond a literal URL, and the current workflow sends Confidential corpus excerpts to a hosted DeepSeek endpoint without a persisted Human approval for provider, purpose, retention, and region. Previously tracked raw evaluation runs also remain in the release history.

This is an independent static re-audit. The Engineer remediation report was treated as a claim to verify, not as Security evidence.

## 2. Candidate binding

The final pre-report snapshot was:

| Field | Observed |
|---|---|
| Git HEAD | `e1c6e5cc37c6b579ef635beb9aa3fd31764c0679` (`e1c6e5c`) |
| Branch | `main` |
| Worktree | Dirty: 12 tracked implementation/config files modified plus untracked build, QA, remediation, and Security artifacts; no clean release candidate |
| QA context | Persisted QA v16 semantic `PASS`; aggregate M7 remains `NOT_VERIFIED` |
| Workflow 01 SHA-256 | `CAC29FD77393E7A3C5ED666A655E8960EC9349589ABA5675269D740CD1156DCD` |
| Workflow 02 SHA-256 | `F70354CD94137981CCE3795C1D99A4899E1199158FCF93BDECA64E40A647594F` |
| Compose SHA-256 | `4C03B922C62504F15202B5BB287537727D2AD87549A8407DC7ADAEA2DDBCE672` |
| DB init SHA-256 | `0F044A9F0B48CAA0C901C4A0A8788043A4C2AAB341A0D6EE89D46F65005BDF21` |
| Hardening migration SHA-256 | `D1FB3A198586F3AC92AA2A8E33CEC89607CE605B4BFDD9D5E820B0BAA2BDFB37` |
| SBOM SHA-256 | `E215DAD878F81762D6297F88FE49287325A62299EFD350B74FE6F129CCBBC787` |

The candidate is not a commit-only artifact: the remediation files and report are untracked/dirty. These hashes bind the exact files reviewed, not a deployed runtime.

## 3. Scope and evidence boundary

I re-inspected the two workflow exports, PostgreSQL bootstrap/alignment/hardening SQL, Compose and launch/deployment guides, environment/ignore/build boundaries, image lock/SBOM, ADR/environment schema, project state, prior Security evidence, and evaluation artifact metadata. The 26 corpus files were inventoried but not opened. Evaluation payloads were not copied; only file names, sizes, and Git tracking state were inspected.

Applicable families assessed: authentication/identity, authorization/tenancy, secrets and credentials, injection/query handling, SSRF/outbound requests, file/path access, dependency/supply chain, SBOM/artifact composition, transport/storage/cryptography, runtime/configuration/least privilege, abuse/replay/availability, and PII/logging/retention. Browser-specific risk is not applicable to this project code.

No application, test, workflow, n8n instance, container, database, provider, endpoint, DNS, tunnel, or network was executed/contacted. No `.env` value, `.env.test` value, n8n credential, database dump, production payload, or raw corpus content was opened.

## 4. Remediation disposition

| Previous finding | Re-audit result |
|---|---|
| `SEC-001` broad `rag_ingest` authority | **Source fix present; active-volume state `NOT_VERIFIED`.** `03-rag-security-hardening.sql` transfers ownership and narrows grants, and workflow 01 calls `rag.activate_corpus(...)`. The persisted catalog needed to prove the active volume is actually hardened is absent. |
| `SEC-002` DB-controlled credentialed URL | **Original concatenation closed in source.** The chat node now uses the literal DeepSeek route. Exact-origin network enforcement, DNS behavior, and redirect handling remain unproven and are a release blocker under ADR-002. |
| `SEC-003` hosted-data approval | **Still open / blocker.** The current candidate sends question and retrieved evidence to DeepSeek, but no Human approval record for the four required data-processing decisions was found. |
| `SEC-004` mutable images/SBOM | **Source-level improvement present.** Compose consumes digest-pinned variables and a CycloneDX file contains the two image hashes. Actual runtime-to-lock match and registry provenance were only asserted by Engineer, not independently persisted. |
| `SEC-005` raw evaluation boundary | **Not closed.** New run outputs are ignored, but the v7-v9 run artifacts remain tracked by Git. `.gitignore` is not retroactive. |

## 5. Findings

### `SEC-001R` — High — existing-volume hardening is not deployment-guaranteed

**Evidence:**

- `deploy/compose.yaml:24-26` mounts `deploy/postgres-init` into PostgreSQL's init directory.
- `deploy/WORKFLOW-IMPORT-GUIDE.md:38-45` correctly states that the init directory runs only for an empty volume, but its existing-volume command applies only `02-rag-schema-alignment.sql`.
- `deploy/postgres-init/README.md:16-20` separately says `03-rag-security-hardening.sql` must be applied on every existing volume, but no automated migration path or persisted catalog result is part of the candidate.
- The Engineer report claims that the migration was applied and negative privilege checks passed. It contains no replayable catalog/grant output that Security can independently bind to this candidate.

**Attack/fragility trace:** a PostgreSQL volume created before the hardening change is not transformed merely because `03-rag-security-hardening.sql` is now mounted. If the manual migration is skipped or applied to another database, the old owner/full-grant state remains. A compromised or misbound `postgres-rag-ingest` credential can then regain the authority identified in the prior audit: alter corpus/settings and bypass the intended workflow boundary.

**Impact:** the security property differs by volume history. The repository has a least-privilege migration, but the deployment path does not prove that the active Confidential-data volume has that state. This keeps the original High authorization blocker open.

**Required closure:** produce a persisted, candidate-bound catalog snapshot from the actual target volume showing ownership, schema/table/function privileges, role attributes, and negative checks; make the existing-volume migration a mandatory, single documented operator step that covers both `02` and `03`, or make deployment fail closed until it is applied. Security must re-audit the resulting exact candidate.

### `SEC-002R` — High — literal provider URL is not an exact-origin egress control

**Evidence:**

- `workflows/02-telegram-grounded-qa.json:259-284` uses `https://api.deepseek.com/chat/completions` literally and keeps a `deepSeekApi` credential on the node.
- The HTTP node options contain a timeout but no explicit redirect policy or per-hop destination validation.
- `deploy/compose.yaml:35-36,92-97` provides a normal Docker bridge network and drops capabilities, but defines no provider egress allowlist, DNS pinning/revalidation, proxy policy, or `no-new-privileges`/read-only runtime boundary. `read_only` is explicitly `false`.
- ADR-002 requires exact-origin egress restriction for hosted providers; the current files do not implement that requirement.

**Attack/fragility trace:** database-controlled destination concatenation is gone, so the prior direct SSRF chain is closed. However, a credentialed data-bearing request still relies on the HTTP client and ambient container network to preserve the exact destination. If redirect behavior follows a provider-controlled cross-origin response, or DNS/network resolution routes the hostname elsewhere, the node has no project-level revalidation or egress firewall to stop the question, retrieved Confidential excerpts, and credentialed request from leaving the approved origin. The actual client behavior and network policy are not persisted, so the claim “only this origin is reachable” is unproven.

**Impact:** exact-origin and “no credential/data to an unapproved host” requirements cannot be demonstrated. This is a release-blocking outbound-data boundary, even though the obvious DB URL injection was remediated.

**Required closure:** disable or strictly revalidate redirects, enforce approved host/port after resolution, and add a network egress control that allows only the approved provider route plus explicitly required local services. Persist the rendered policy and a sanitized negative matrix for redirect, alternate host/port, private/link-local/metadata, and DNS-rebinding cases.

### `SEC-003` — High — hosted Confidential-data approval is still absent

**Evidence:**

- The current workflow's `Build Prompt` node constructs a provider message containing the Telegram question and retrieved `prompt_evidence` content (`workflows/02-telegram-grounded-qa.json:237-240`); the credentialed chat node posts it to DeepSeek (`:259-284`).
- ADR-002 requires separate Human approval of provider, purpose, retention, and region before a hosted profile can process the Confidential corpus (`.ai/decisions/adr-002-provider-neutral-ai-boundary.md:13,22,48,53`).
- The remediation report and setup guides repeat that this is a Human gate, but no persisted approval/rejection record was found. The prior Human approval in project state is for the synthetic QA set and Telegram sandbox, not hosted Confidential-data processing.

**Impact:** successful QA delivery or Engineer self-test does not authorize sending internal policy excerpts to a third party. The candidate is not auditable as an approved data-processing boundary; release cannot proceed.

**Required closure:** Human records the exact provider, purpose, data class, retention, region, and credential/provisioning decision, or the hosted profile is disabled and replaced by an approved private/self-hosted route. Security then verifies the record against the exact runtime binding.

### `SEC-005R` — Medium — tracked raw run artifacts remain outside the release allowlist

**Evidence:**

- `git ls-files evaluation/run_*` still returns nine tracked v7-v9 JSONL/config/summary artifacts.
- `.gitignore:54-56` now ignores future `evaluation/run_*` outputs, but ignore rules do not remove files already tracked or erase them from staged/history boundaries.
- The remediation report explicitly says existing files were not deleted or rewritten.

**Impact:** a broad release/publication operation can still include historical execution evidence that is not proven to be Public/synthetic/minimized. This contradicts the portfolio-distribution boundary, which forbids raw execution data and requires an explicit allowlist.

**Required closure:** keep raw ledgers outside the distributable tree, remove them through a Human-approved history/staging cleanup, and publish only a reviewed sanitized summary. Security should inspect the exact staged file list after cleanup.

## 6. Supply-chain and artifact residuals

The image variables and SBOM are a real improvement: `.env.example` and `deploy/IMAGE-LOCK.md` contain immutable n8n/pgvector references, and `deploy/sbom.cdx.json` contains matching SHA-256 component hashes. This closes the previous “floating tag with no inventory” source defect.

It does not prove that the active runtime used those digests. The lock source is described as `docker image inspect on running local images`, but the inspect output, registry provenance/signature, vulnerability result, and exact rendered Compose configuration are not persisted in the candidate. Therefore this family is `PARTIAL / NOT_VERIFIED`, not Security `PASS`.

## 7. Unverified boundaries

- Actual PostgreSQL catalog/role/grant state of the active named volume.
- n8n credential-store contents, webhook secret, active workflow registration, and exact imported workflow hash.
- HTTP redirect/DNS behavior and host/container egress firewall policy.
- Provider retention/region/subprocessor controls and Human approval.
- Actual runtime image digests, signature/provenance, and vulnerability scan.
- Exact release/publication staging list and history after the new ignore rules.

These are not “assumed pass” items. Under the Security contract they remain `NOT_VERIFIED` and block release.

## 8. Handoff

**Security verdict remains `FAIL`.** The engineer hardening report is useful implementation evidence, but it does not close the independent Security gate. No release, public publication, production import, credential handoff, or cleanup is authorized.

Next owners: DevOps/Engineer must produce candidate-bound catalog and exact-origin egress evidence; Human must record or reject hosted Confidential-data processing; Release/QA must clean and allowlist evaluation artifacts. Security re-audit is required after those gates.

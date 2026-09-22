# Security Audit — M7 static review

## 1. Objective and scope

- Project: `Asisten Pengetahuan Internal Toko Makmur Jaya`
- Lane: `PROFESSIONAL`; required independent Security gate before Quality/Release.
- Final candidate-binding snapshot: `2026-09-21T23:39:33+07:00`.
- Objective: independently review the actual workflow, database grants, runtime configuration, outbound AI boundary, dependency/artifact boundary, and evidence handling. This is a static audit, not a penetration test or runtime assurance.
- Verdict: **`FAIL` — not suitable for release**.

The verdict is based on two proven control violations in the candidate: the ingestion database identity has materially excessive authority, and that identity can control a credentialed, dynamically selected outbound chat destination that receives retrieved corpus content. The hosted-provider approval and dependency reproducibility gates are also not evidenced.

## 2. Exact candidate

Candidate was reviewed as a dirty detached worktree:

| Field | Observed |
|---|---|
| Git HEAD | `e1c6e5cc37c6b579ef635beb9aa3fd31764c0679` |
| Branch | `main` |
| Dirty state | 3 modified tracked files; 78 untracked files at final binding; no clean release candidate |
| Current state | `.ai/project-state.md` records QA v16 semantic `PASS`, overall M7 `NOT_VERIFIED`, release candidate `NOT_AVAILABLE` |
| Workflow 01 SHA-256 | `B37B3F0A68F0BD519772881CEF4322B10FF5D93D75BAED8F189C620D9FAE9503` |
| Workflow 02 SHA-256 | `6F12DA416F362A9E602C4872878BCCF7BC8516FDCB73AC82F08697DEDB388E14` |
| Compose SHA-256 | `C2A0003897D3DD2B286277E4C366197E4D0E8ACD9E239D0CA1573C3ED162F67B` |
| DB init SHA-256 | `34BF25E39812B15171D2C7738EE3274B6983EF1DC5B88E8C0FCBCB7421066E8B` |
| DB alignment migration SHA-256 | `B889512B09B197AC3FEE1F1EBC72938B63AEAA7C2D7DF42A235DA263BFBCC88B` |

The report is new. The project state was already dirty before this audit and is updated only in its Security status/evidence/handoff metadata.

The worktree advanced from earlier observed commits during this audit. The final binding above is the only candidate identity used for handoff; the relevant workflow/DB artifact hashes were rechecked and remain the same. Candidate consistency is still an operational limitation until the worktree is frozen.

## 3. Scope inventory and denominators

| ID | Actual path/component | Boundary and relation | Included/excluded | Static evidence |
|---|---|---|---|---|
| `SEC-SCOPE-01` | `workflows/01-corpus-ingestion.json`, `workflows/02-telegram-grounded-qa.json` | n8n triggers, Code nodes, SQL, HTTP requests, credential bindings, side effects | Included; both JSON exports inspected as JSON and by line | Node graph, parameters, embedded JS/SQL, connections, active/version metadata |
| `SEC-SCOPE-02` | `deploy/postgres-init/01-init.sh`, `02-rag-schema-alignment.sql` | Roles, schema ownership, grants, RAG tables | Included | Role/grant statements and table definitions read; no database execution |
| `SEC-SCOPE-03` | `deploy/compose.yaml`, `deploy/e2e-temp/Caddyfile`, `deploy/start-local.sh`, `deploy/stop-local.sh`, deploy guides | Container, network, mounts, ports, image identity, launch boundary | Included | Configuration and scripts read; no Compose/config/startup execution |
| `SEC-SCOPE-04` | `.env.example`, `.env.test` metadata, `.gitignore`, `.dockerignore`, `README.md` | Secret source, source precedence, ignore/build boundary | Included; `.env.test` values deliberately not read | Template/keys/rules read; only `.env.test` key names and metadata inspected |
| `SEC-SCOPE-05` | `scripts/`, `tests/harness/`, `tests/mocks/`, synthetic fixtures | Claimed security controls and mock boundary | Included by targeted static search; not treated as independent proof | I/O, HTTP, subprocess, environment, fixture and credential-like paths searched/read contextually |
| `SEC-SCOPE-06` | `docs/` | 26 approved corpus source files mounted read-only into n8n | Content excluded from agent context; inventory retained | Filename/size inventory only; no raw corpus copied into report |
| `SEC-SCOPE-07` | `evaluation/` | QA/evidence artifacts, including 11 JSONL runs with `question`/`answer`/source fields | Metadata inspected; raw values not copied | 35 files inventoried; property names and file status checked |
| `SEC-SCOPE-08` | `.ai/knowledge/`, `.ai/decisions/`, `.ai/project-state.md`, QA/build reports | Approved design, environment, handoff and evidence boundary | Included for control comparison | Relevant governance and latest QA/cloud-provider reports read |

Denominators:

- Relevant first-party implementation/config/governance files: **34 identified / 34 targeted statically inspected**. Generated `__pycache__`/`.pyc` files were excluded as generated artifacts after inventory; they are ignored and not used by the workflows.
- Corpus inputs: **26 identified / content not opened**. This is an explicit data-minimization boundary, not a claim that corpus semantics were security-tested.
- Evaluation artifacts: **35 identified / metadata inspected**; they are not implementation evidence and remain untracked in the candidate.
- Dependency manifests/locks: **0 identified / 0 inspected**. This is a gap because the Compose artifact still depends on external container images and the n8n runtime.
- Applicable risk families: **12 assessed / 12 identified**; one family is reasoned `NOT_APPLICABLE` below.

## 4. Methods and safety boundary

Read-only methods used from the project root:

- `git rev-parse`, `git status --short`, `git diff --stat`, `git ls-files` for candidate identity and dirty state.
- `rg --files` and targeted `rg -n` searches for credentials, URLs, SQL, code execution, paths, network, grants, logging, image/version and ignore rules.
- `Get-Content` for full contextual reading of workflows, deployment, schema, environment, architecture, ADR, state and reports.
- PowerShell `ConvertFrom-Json` to enumerate workflow nodes, credential references, connections and unconnected nodes without executing them.
- `Get-FileHash -Algorithm SHA256` for candidate artifact binding.

No application, test, workflow, n8n instance, container, endpoint, provider, tunnel or production target was contacted. No tool was installed. No `.env` value, credential store, database dump, production payload or raw corpus content was opened or copied.

## 5. Risk applicability matrix

| Risk family | Status | Evidence and reason |
|---|---|---|
| Authentication and identity | `APPLICABLE` | Telegram Trigger, n8n credential bindings, PostgreSQL roles and provider credential. Export/runtime registration does not provide inspectable proof of the deployed webhook secret or credential-store state. |
| Authorization and tenancy | `APPLICABLE` | Allowed chat ID and separate DB roles are intended controls; actual `rag_ingest` authority violates the approved least-privilege boundary. See `SEC-001`. |
| Secrets and external credentials | `APPLICABLE` | Telegram, PostgreSQL and provider credentials are referenced; dynamic chat URL plus predefined provider credential creates a credentialed egress boundary. See `SEC-002`. |
| Injection, evaluation and deserialization | `APPLICABLE` | n8n Code/expressions, JSON data and PostgreSQL query replacements are in scope. Reviewed SQL uses parameter placeholders; runtime node semantics were not executed. |
| SSRF and outbound requests | `APPLICABLE` | Chat URL is built from `rag_settings.chat_base_url` and `chat_api_path`; validation is only a permissive URL/path regex. See `SEC-002`. |
| Files, paths, uploads and archives | `APPLICABLE` | Corpus is read through `/files/docs/*.md`, with filename/path checks and a read-only mount. Symlink behavior and runtime file access were not verified. |
| Browser and cross-origin trust | `NOT_APPLICABLE` | No custom browser client, HTML application, iframe or cookie-authenticated state-changing browser API is delivered by this candidate; the n8n editor is treated as platform scope, not project code. |
| Dependencies and supply chain | `APPLICABLE` | n8n and PostgreSQL/pgvector images plus built-in node runtime are external inputs, but no lock/digest/SBOM evidence is bound to this candidate. See `SEC-004`. |
| SBOM and artifact composition | `APPLICABLE` | Compose is a distributable runtime artifact with external images; no machine-readable artifact-bound inventory was found. See `SEC-004`. |
| Transport, storage and cryptography | `APPLICABLE` | Confidential corpus excerpts can cross to a hosted provider; n8n encryption and local HTTP/private-provider assumptions require deployment proof. Hosted approval is not persisted. See `SEC-003`. |
| Runtime, configuration and least privilege | `APPLICABLE` | Compose, database roles, mounts, ports and n8n settings are security boundaries. `rag_ingest` is over-privileged and image bindings are not reproducible. |
| Abuse, replay and availability | `APPLICABLE` | Telegram is retryable/public at the provider boundary; deduplication and bounded timeouts exist, but live fault, duplicate and concurrency coverage is explicitly absent from QA v16. |
| PII, logging and retention | `APPLICABLE` | Internal policy corpus, questions/answers and provider identifiers appear in evidence boundaries. New evaluation JSONL artifacts are untracked and not ignored; see `SEC-005`. |

## 6. Findings

### `SEC-001` — High — ingestion credential is schema owner/full RAG writer

- Family: authorization / runtime least privilege.
- Locations: `deploy/postgres-init/01-init.sh:55-61,68-71,84-92,209-224`; `deploy/postgres-init/02-rag-schema-alignment.sql:20-21`; `workflows/01-corpus-ingestion.json` PostgreSQL nodes using `postgres-rag-ingest`; `workflows/01-corpus-ingestion.json:271-281`.
- Safe attack trace: a compromise or misbinding of the `postgres-rag-ingest` credential gives `rag_ingest` database `CREATE`, ownership of schema `rag`, `ALL` privileges on all current/future RAG tables, and full control of `rag.rag_settings` and operational tables. The same credential is deliberately used by the disconnected `TEMP — Configure Cloud Chat Binding` node to update the provider binding. An attacker with that credential can change `telegram_allowed_chat_id`, `active_corpus_version`, corpus rows, or `chat_base_url` before a legitimate Q&A request.
- Observed control: the approved environment schema says ingest may write/activate corpus only and must not be an admin; the actual SQL grants the opposite. `rag_runtime` also receives default SELECT on all future RAG tables, broader than the stated read/settings plus operational-write scope.
- Impact: loss of authorization isolation; corpus tampering, denial of service, authorization takeover and a direct path to Confidential corpus disclosure through the Q&A provider boundary. This violates the approved least-privilege criterion even though anonymous Internet-to-database access was not proven.
- Owner/action: DevOps + Engineer, with Human approval of the revised privilege map. Recreate ownership/grants so ingest cannot own the schema or alter settings, provider binding, runtime controls or operational history; grant only exact corpus staging/activation operations through reviewed SQL or a narrow stored procedure. Remove the temporary settings writer from the ingest credential.
- Retest: isolated catalog privilege review plus an authorized negative matrix proving ingest cannot update settings, delete/alter active corpus, create schema objects or rewrite telemetry; then re-audit the workflow credential map.

### `SEC-002` — High — credentialed dynamic outbound URL enables SSRF/data exfiltration path

- Families: SSRF/outbound requests; secrets; transport.
- Locations: `workflows/02-telegram-grounded-qa.json:74` (`chat_base_url` validation), `:257-284` (`Chat Completion`); `workflows/01-corpus-ingestion.json:271-281`; `deploy/CLOUD-CHAT-SETUP-GUIDE.md:37-44`.
- Safe attack trace: `Chat Completion` POSTs to `chat_base_url.replace(...) + chat_api_path`, with `authentication: predefinedCredentialType` and a provider credential. The only static checks accept any non-space `http://` or `https://` origin and any slash-prefixed path; there is no exact-origin allowlist, private/link-local/metadata blocking, userinfo rejection, DNS/redirect control, or TLS-only enforcement. Because `rag_ingest` can change `rag_settings`, a holder of that credential can point the request to an attacker host or an internal destination, set the allowed chat ID, and submit a Telegram question. The request body is constructed from the question and retrieved corpus excerpts in `Build Prompt`.
- Observed control: a URL-format regex and a runtime settings presence check. The architecture/environment requirement is exact approved egress, but no enforcement exists in the workflow or Compose boundary. The workflow also uses `deepSeekApi` while the environment schema describes a generic `ai-provider` binding.
- Impact: arbitrary outbound reachability from n8n, possible access to internal services/metadata, and exfiltration of retrieved Confidential corpus excerpts and questions. Whether the provider credential header is accepted by every arbitrary destination is not runtime-tested; the data-bearing request path itself is statically proven.
- Owner/action: Engineer + DevOps. Remove DB-controlled arbitrary destination from the credentialed node; bind an exact approved origin in a provider adapter/credential, enforce HTTPS and a host/port allowlist at application and network egress layers, reject private/link-local/metadata targets after DNS resolution, and disable redirects or revalidate each hop. Separate provider credential type from generic endpoint selection.
- Retest: isolated malicious-setting cases for loopback, RFC1918, link-local/metadata, alternate ports, userinfo, redirects and DNS rebinding, plus egress firewall evidence and a sanitized request assertion showing no credential/corpus leaves the approved destination.

### `SEC-003` — High — hosted Confidential-data approval is not auditable

- Family: transport/storage/data boundary.
- Locations: `workflows/02-telegram-grounded-qa.json:259-284`; `.ai/decisions/adr-002-provider-neutral-ai-boundary.md:13,22,48,53`; `.ai/knowledge/architecture.md:54,161`; `.ai/reports/build/M7-cloud-chat-e2e-remediation-2026-09-21.md:12-34`; `.ai/reports/qa/M7-independent-qa-v10-cloud-chat-full-matrix-2026-09-21.md:7,24`.
- Observation: current persisted evidence records a hosted DeepSeek chat binding and live QA against it. The approved ADR explicitly disables a hosted profile until Human approval of provider, purpose, retention and region. No separate persisted approval artifact for those four decisions was found; the setup guide's statement that approval exists is an engineer-facing claim, not independent evidence.
- Impact: the candidate cannot demonstrate that questions and retrieved Confidential excerpts were authorized to cross the hosted-provider boundary. This is a release-blocking evidence gap; it becomes a data-boundary violation if the claimed approval does not exist.
- Owner/action: Human + DevOps. Record the exact provider, processing purpose, retention, region, allowed data class and credential/provisioning decision, or revert to a private/self-hosted approved profile. Do not treat QA delivery success as approval.
- Retest: Security re-audit the approval record and exact runtime binding, including egress destination and credential type.

### `SEC-004` — Medium — external runtime identity is mutable and not reproducible

- Family: dependencies/supply chain/SBOM.
- Locations: `deploy/compose.yaml:13,43`; `.env.example:14-20`; `README.md:15-18`.
- Observation: Compose hard-codes `pgvector/pgvector:pg16` and `n8nio/n8n:1.123.81` instead of consuming the declared image bindings. Neither image is digest-pinned; no dependency lock/resolution file or SBOM is present. README still describes `latest stable`, which conflicts with the exact-image requirement.
- Impact: a later pull can resolve a different image under the same tag, so the security review cannot be bound to a reproducible runtime or to a known transitive dependency set. This is not a proven image compromise, but it is an unresolved supply-chain release gate.
- Owner/action: DevOps. Consume canonical image variables only after validation, pin immutable digests, record source/version/update policy, generate an artifact-bound SBOM, and reconcile README/schema/Compose.
- Retest: inspect the exact rendered image references, digest provenance, SBOM and vulnerability evidence for the release artifact without pulling or executing images in the Security review.

### `SEC-005` — Medium — raw QA transcript artifacts are outside the declared release boundary

- Family: PII/logging/retention and artifact composition.
- Locations: untracked `evaluation/run_v10...` through `run_v16...` JSONL/config/summary artifacts; `.gitignore`; QA reports linked to those JSONL files.
- Observation: 35 evaluation files exist in the dirty worktree. The 11 JSONL runs contain fields such as `question`, `answer`, `sources`, `observed_ui`, and provider/Telegram row identifiers. The files are untracked and are not excluded by the current ignore rules. QA labels the dataset synthetic, but the files still carry unpublished internal-policy text and sandbox identifiers in a release-adjacent artifact boundary.
- Impact: a broad `git add` or portfolio bundle can publish internal policy excerpts and operational identifiers even though the approved portfolio profile allows only explicitly reclassified synthetic/minimized evidence.
- Owner/action: QA + Human. Keep raw run ledgers outside distributable artifacts or create a verified sanitized export; add a scoped ignore/release allowlist, review staged history, and remove/revoke any exposed identifier through the Human-owned cleanup process.
- Retest: inspect the exact staged/release file list and verify no raw question/answer/UI/identifier fields remain in the public or client bundle.

## 7. Uninspected or unverified boundaries

- n8n credential-store contents, registered Telegram webhook secret, actual webhook registration, provider retention/region controls, live DNS/redirect behavior, network firewall/egress policy, database catalog state, and production/demo-VPS configuration were not accessible and were not queried.
- No runtime exploit, fault injection, duplicate/concurrency test, clean-instance import/rebind, image pull, dependency vulnerability scan or SBOM generation was performed. These are gaps, not `PASS` evidence.
- The export says workflow 02 is active while its metadata says credential setup is incomplete; the deploy guide calls exports draft/unpublished. The real deployed state is therefore not statically reconciled.
- The local `http://host.docker.internal:11434` embedding path and temporary Caddy route are deployment-specific; no production transport/security claim is made for them.

## 8. Verdict and handoff

**Security verdict: `FAIL`.** `SEC-001` and `SEC-002` are proven static control failures against the approved least-privilege and exact-egress requirements. `SEC-003`–`SEC-005` add release-blocking evidence/data-boundary gaps. QA v16 semantic `PASS` does not reduce or replace this Security verdict.

No release, public publication, production import, credential handoff, or cleanup action is authorized by this report. Next owner is **DevOps/Engineer for privilege and egress remediation**, with **Human** to record the hosted-provider data decision; Security must re-audit the exact post-fix candidate before any Quality/Release decision.

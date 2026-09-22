# M7 Security Blocker Closure Attempt — 2026-09-22

## Status

`NOT_VERIFIED / SECURITY RE-AUDIT REQUIRED`.

This report records the additional work performed after Security re-audit v3.
It does not claim a Security pass and does not authorize release or
publication.

## SEC-003 — hosted-provider approval

The Human approval is already persisted in
`.ai/reports/security/M7-human-hosted-provider-approval-2026-09-22.md`.
No secret was read, copied, or added to this evidence.

Disposition: `IMPLEMENTER-CLOSED; SECURITY RE-AUDIT REQUIRED`.

## SEC-005R — candidate boundary

The local candidate is clean at commit
`b45107bc7b0980732e7f396bce0961f66132ff14` on `main`, with no uncommitted
changes at the time of this report. `git ls-files 'evaluation/run_*'` returned
no tracked evaluation-run artifacts. Old run files remain only as ignored local
copies and are outside the release tree; nothing was pushed or publicly
published.

Disposition: `IMPLEMENTER-CLOSED FOR LOCAL CANDIDATE`; any publication/history
decision remains a Release/Human gate.

## SEC-004 — supply-chain and vulnerability evidence

An independent read-only Trivy archive scan was run without a Docker socket,
using scanner image digest
`aquasec/trivy@sha256:26245f364b6f5d223003dc344ec1eb5eb8439052bfecb31d79aeba0c74344b3a`.
The scan used the vulnerability database fetched by Trivy on 2026-09-22,
severity `HIGH,CRITICAL`, and `--ignore-unfixed`.

| Image | Exact digest | Result |
|---|---|---|
| `n8nio/n8n:1.123.81` | `sha256:0d7b776e0867c415dcb382d24d371a3b0aa402fcba9a9a866f42474abdabf7da` | 30 findings: 27 HIGH, 3 CRITICAL; all reported findings had fixed versions |
| `pgvector/pgvector:pg16` | `sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b` | 25 findings: 24 HIGH, 1 CRITICAL; all reported findings had fixed versions |

The unpinned n8n `latest` candidate was also inspected only as a comparison:
version `2.40.5`, digest
`sha256:9f693fd5565539efd5e75ad168526c8041a6af516d9e50bc4d9cb1c9c5031523`,
and it still returned 26 findings (19 HIGH, 7 CRITICAL). It was not adopted.

Disposition: `OPEN`. Evidence now exists, but the exact pinned runtime images
have unresolved HIGH/CRITICAL findings and no independent signature/provenance
attestation was established. No image pin was changed blindly.

## SEC-002R — exact-origin egress

Runtime inspection still shows the application network as Docker `bridge` with
`internal=false`, subnet `172.22.0.0/16`, and no host/Docker egress allowlist.
n8n supports environment-driven global proxy agents, but no approved allowlist
proxy is deployed. The official Squid candidate could not be pulled after two
registry timeouts, so no partial network change was made.

Disposition: `OPEN`. A real egress gateway or host firewall policy is still
required, with exact allowlist for Telegram, DeepSeek, and host-local Ollama,
plus private/link-local/DNS-rebinding rejection and runtime proof.

## Handoff

The remaining blockers are now concrete rather than missing evidence:

1. DevOps/Security must provide or approve patched, attestable image digests (or
   an explicit vulnerability risk acceptance) for `SEC-004`.
2. DevOps must provide the approved egress gateway/host-firewall mechanism for
   `SEC-002R`; the current profile was intentionally left unchanged.
3. Security must re-audit the exact candidate after those two gates are closed.

No Telegram message, hosted-provider request, or production deployment was
performed by these checks.

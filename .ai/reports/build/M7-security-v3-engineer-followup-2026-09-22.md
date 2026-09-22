# M7 Security Re-audit v3 — Engineer Follow-up

Date: `2026-09-22`

Status: `VERIFIED BY IMPLEMENTER / SECURITY RE-AUDIT REQUIRED`

Finding source: `.ai/reports/security/M7-security-re-audit-v3-2026-09-22.md`.

## Actions completed

### SEC-003 — Human approval recorded

The explicit Human approval from this conversation is persisted in
`.ai/reports/security/M7-human-hosted-provider-approval-2026-09-22.md`.
It identifies provider, purpose, allowed/disallowed data class, retention
decision, region/transfer decision, credential decision, and test-only scope.
No secret was read or copied. The record is a governance approval, not a claim
about provider-side retention, region, or compliance facts.

### SEC-002R — verification performed; implementation blocker remains

Read-only runtime inspection found:

- Docker network driver: `bridge`.
- Docker network `internal`: `false`.
- No host/Docker egress allowlist or DNS-rebinding control is present in the
  current Compose profile.
- Workflow-level controls remain present: literal DeepSeek route,
  `followRedirect=false`, `followAllRedirects=false`, and local embedding route.

This is intentionally not marked closed. Enforcing a real allowlist requires a
reviewed egress gateway/host firewall design and would affect Telegram,
DeepSeek, and host-local Ollama reachability. No network policy was changed
blindly because that could break the approved test path.

### SEC-004 — registry/vulnerability test performed; evidence remains incomplete

Docker Buildx registry inspection returned the exact manifest digests already
used by Compose:

- `n8nio/n8n:1.123.81` →
  `sha256:0d7b776e0867c415dcb382d24d371a3b0aa402fcba9a9a866f42474abdabf7da`
- `pgvector/pgvector:pg16` →
  `sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b`

Docker Scout is installed but refused the CVE query because the Docker CLI is
not authenticated. `cosign`, `trivy`, `syft`, and `grype` are not available in
the current host environment. No vulnerability/signature result is invented;
SEC-004 remains open for a credentialed/approved supply-chain evidence run.

### SEC-005R — internal candidate boundary created

The approved project changes are captured in internal candidate commit
`b45107bc7b0980732e7f396bce0961f66132ff14` on local branch `main`; the
candidate is not pushed or publicly published. Existing evaluation-run
deletions remain recoverable in Git history and local ignored copies remain
outside the release tree. Release/Human must still decide whether that history
and the final allowlist are acceptable for any publication.

## Verification

- SEC-006 verifier previously exited `0`; Security v3 accepted its source
  remediation.
- Current n8n active workflow remains `02 — Telegram Grounded Q&A`.
- No Telegram or hosted-provider message was sent during this follow-up.

## Final handoff

Human approval is now persisted for SEC-003. DevOps/Security still own
SEC-002R and SEC-004. Release/Human own the publication/history decision for
SEC-005R. Global M7 Security remains `NOT_VERIFIED` until Security re-audits the
exact candidate and these remaining gates.

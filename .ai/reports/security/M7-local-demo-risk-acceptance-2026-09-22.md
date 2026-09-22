# M7 Local-Demo Residual-Risk Acceptance — 2026-09-22

## Decision

**Status:** `APPROVED BY HUMAN FOR LOCAL DEMO ONLY / SECURITY RE-AUDIT REQUIRED`.

On `2026-09-22`, the Human selected the Engineer's proposed recommendation 1
for this demo project:

> "oke aku pilih rekomendasi 1, mengingat ini project demo. beeritahun alasan
> tsb ke security di report nanti"

This records a scoped acceptance of the residual local-demo risk while the
Engineer implements an internal application network and a narrowly routed
egress gateway. It is not a claim that vulnerabilities, image provenance, or
the Security gate are closed.

## Reason for the scoped decision

The project is a local demonstration of an n8n RAG workflow. Its purpose is to
prove the system boundary and expected workflow behavior, not to publish a
public service or make a production-security claim. Replacing images blindly
would neither remove the demonstrated scanner findings nor preserve the
validated n8n/pgvector compatibility baseline.

The selected approach therefore contains, rather than conceals, the residual
risk:

1. n8n and PostgreSQL remain on an internal Docker network.
2. Only a dedicated gateway receives an external Docker network attachment.
3. The gateway exposes fixed paths for Telegram, the approved hosted chat
   provider, and host-local Ollama; every other path is denied.
4. Workflow URLs refer only to the internal gateway, not arbitrary Internet
   origins. Redirect following remains disabled on the HTTP nodes.
5. Container images stay digest-pinned. Known unresolved scan findings and the
   absence of independently reviewed signature/provenance evidence are
   explicitly residual risk for this demo, not remediated findings.

## Explicit limits

This decision does **not** approve:

- public hosting, production traffic, or a release;
- accepting new images without review;
- bypassing TLS for the hosted provider;
- adding general outbound access, a wildcard proxy, or arbitrary DNS targets;
- putting API keys, bot tokens, raw corpus excerpts, or message transcripts in
  source control or reports; or
- marking M7 Security, M8, or the release gate as passed.

Telegram live E2E remains separately conditional on an approved public HTTPS
`WEBHOOK_URL`. The `local-isolated` Compose profile intentionally leaves the
Telegram workflow inactive without that prerequisite.

## Required follow-up for Security

Security must re-audit the exact candidate after runtime verification of the
new network/gateway boundary. The reviewer should independently assess:

- actual Docker network attachment and `internal: true` behavior;
- gateway allowlist/deny behavior and whether its hostname handling remains
  acceptable for this demo profile;
- the exact pinned images and the recorded vulnerability/provenance limits;
- workflow and encrypted credential binding without exposing secrets; and
- whether this narrow local-demo acceptance is sufficient for the intended
  demonstration scope.

Until then, the correct aggregate status remains
`QA SEMANTIC PASS / SECURITY RE-AUDIT REQUIRED / NOT_VERIFIED`.

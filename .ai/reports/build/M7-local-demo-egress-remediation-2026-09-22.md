# M7 Local-Demo Egress Remediation — Engineer Evidence

Date: `2026-09-22`

Status: `VERIFIED BY IMPLEMENTER / SECURITY RE-AUDIT REQUIRED`.

This is a local-demo containment remediation for findings `SEC-002R` and
`SEC-004`. It is not a Security pass, production approval, release approval,
or Telegram E2E result.

## Scope and Human decision

The Human selected the proposed demo-only recommendation on `2026-09-22`.
The rationale and limits are persisted in
`.ai/reports/security/M7-local-demo-risk-acceptance-2026-09-22.md`.

The decision accepts documented residual image/supply-chain risk **only** for
this local demonstration while the implementation narrows outbound paths. It
does not waive independent Security review, permit public hosting, or permit
general outbound proxying.

## Implemented boundary

`deploy/compose.yaml` now creates two Docker networks:

| Network | `internal` | Attached containers |
|---|---:|---|
| `rag-local_rag-net-local` | `true` | `rag-n8n-local`, `rag-postgres-local`, `rag-egress-gateway-local` |
| `rag-local_rag-egress` | `false` | `rag-egress-gateway-local` only |

No host port is published by the gateway. n8n and PostgreSQL have only the
internal application network.

The dedicated gateway is Caddy image
`caddy:2.11.4@sha256:14a9c00d4e833ebc2b65d36515b37bde3b73f0b323a2663aaafc88953d8c4e3f`.
It runs non-root with a read-only root filesystem, `no-new-privileges`, all
capabilities dropped except the image-required `NET_BIND_SERVICE`, and
no-exec temporary config/data mounts.

The reviewed Caddy configuration has no forward-proxy directive and only these
fixed routes:

| Internal caller path | Fixed upstream | Purpose |
|---|---|---|
| `/telegram/...` | `https://api.telegram.org/...` | Telegram Bot API |
| `/deepseek/...` | `https://api.deepseek.com/...` | approved hosted chat |
| `/ollama/...` | `http://host.docker.internal:11434/...` | host-local EmbeddingGemma |
| all other paths | local `403` | deny by default |

The gateway discards its logs. Telegram's Bot API token is part of the URL
path; discarding logs prevents an upstream failure from recording that path in
container output. Health and route checks below remain available through status
codes without logging request URLs.

## Workflow and credential alignment

- `01 — Corpus Ingestion` now calls
  `http://egress-gateway:8080/ollama/v1/embeddings`.
- `02 — Telegram Grounded Q&A` now calls
  `http://egress-gateway:8080/ollama/api/embed` and
  `http://egress-gateway:8080/deepseek/chat/completions`.
- The runtime records for the known workflow IDs were checked after restart and
  show those same gateway URLs. Both workflows are inactive in
  `local-isolated`.
- The encrypted `telegramApi/telegram-demo-bot` credential was rewritten only
  at its `baseUrl` field to the internal `/telegram` route. The reusable helper
  uses n8n's own cipher, keeps the token in memory only, and prints only a
  pass/fail result. The post-change validation reported `VERIFIED`; no token
  was read into this report.
- The source workflow 02 is inactive because this local profile has no
  `WEBHOOK_URL` HTTPS origin. Telegram rejects loopback/HTTP webhooks. This is
  an intentional safe state, not a regression in the egress boundary.

Two inactive duplicate workflow records created by an earlier CLI import were
confirmed to have no execution or webhook rows, then removed by exact ID. The
two known project workflows and an unrelated `My workflow` record remain.
`deploy/WORKFLOW-IMPORT-GUIDE.md` now warns that `import:workflow` is for a
clean instance and creates a new record rather than updating an existing one.

## Runtime verification

All checks below were executed on the live local Docker stack after the Caddy
configuration was validated and the gateway recreated.

| Check | Observed result | Verdict |
|---|---|---|
| Compose rendering | `docker compose ... config --quiet` exited `0` | pass |
| n8n/PostgreSQL/gateway | all containers `healthy` | pass |
| attachment inventory | only gateway attached to `rag-local_rag-egress`; application network reports `internal=true` | pass |
| gateway health | `GET /healthz` from n8n → `200` | pass |
| deny default | `GET /not-allowed` from n8n → `403` | pass |
| host-local embedding | `GET /ollama/api/tags` from n8n through gateway → `200` after starting the stopped local Ollama service | pass |
| cloud route confinement | `GET /deepseek/models` through gateway → provider `401` without an API key | pass: route reached, no key exposed |
| direct bypass attempt | direct n8n request to `api.deepseek.com` failed DNS resolution | pass: no direct route from n8n |
| Telegram route reachability | unauthenticated gateway request reached Telegram and returned its normal non-success response | pass: route was not a local proxy bypass |
| credential binding | encrypted credential helper reported `VERIFIED` | pass |
| gateway log redaction | token-shaped test path produced no gateway log entry | pass |

No Telegram message, corpus content, API key, bot token, or hosted chat request
with project data was sent during these checks.

## Supply-chain evidence and residual risk

Trivy `0.56.2` scanned the Caddy image through a temporary Docker archive with
no Docker socket. The archive was deleted after scanning. Result:

| Image | Result (`HIGH,CRITICAL`, `--ignore-unfixed`) |
|---|---|
| Caddy `2.11.4` exact digest above | `17 HIGH`, `0 CRITICAL`; fixed versions were reported |
| n8n `1.123.81` exact digest | prior evidence: `27 HIGH`, `3 CRITICAL` |
| pgvector `pg16` exact digest | prior evidence: `24 HIGH`, `1 CRITICAL` |

The scan does **not** make the findings disappear. The Human local-demo risk
acceptance covers this explicitly constrained state only. Docker Scout still
requires a Docker login and no independent signature/provenance attestation is
claimed here.

## Security handoff

Security should re-audit the exact candidate and decide whether this gateway is
sufficient evidence for `SEC-002R`, and whether the scoped Human risk decision
is acceptable for the still-open `SEC-004` supply-chain finding. The aggregate
status remains `QA SEMANTIC PASS / SECURITY RE-AUDIT REQUIRED / NOT_VERIFIED`.

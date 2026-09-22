# M6 — Local-Isolated Deployment & Integration: Exit Report

- **Project:** Asisten Pengetahuan Internal Toko Makmur Jaya
- **Delivery Lane:** PROFESSIONAL
- **Role:** DevOps
- **Date:** 2026-09-14
- **Profile:** local-isolated (no Caddy, loopback only)

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Docker Compose | `deploy/compose.yaml` | ✅ |
| DB init script | `deploy/postgres-init/01-init.sh` | ✅ |
| DB init README | `deploy/postgres-init/README.md` | ✅ |
| Test env | `.env.test` | ✅ |
| Launcher | `deploy/start-local.sh` | ✅ |
| Stopper | `deploy/stop-local.sh` | ✅ |
| Workflow import guide | `deploy/WORKFLOW-IMPORT-GUIDE.md` | ✅ |
| README update | `README.md` (Quick Start → launcher) | ✅ |

## Validation Evidence

### Static (no daemon needed)

| Check | Command | Result |
|-------|---------|--------|
| Compose config valid | `docker compose config --quiet` | ✅ exit 0 |
| Image exists | `docker manifest inspect n8nio/n8n:1.62.1` | ✅ |
| Image exists | `docker manifest inspect pgvector/pgvector:pg16` | ✅ |
| No secrets in export | regex scan | ✅ 0 hits |

### Runtime (docker daemon up)

| Check | Command | Result |
|-------|---------|--------|
| n8n healthy | compose ps | ✅ healthy |
| postgres healthy | compose ps | ✅ healthy |
| n8n healthz | `curl 127.0.0.1:5678/healthz` | ✅ `{"status":"ok"}` |
| n8n UI | `curl 127.0.0.1:5678/` | ✅ 200 |
| Loopback only | `netstat -ano` | ✅ `127.0.0.1:5678` (no 0.0.0.0) |
| Postgres no host port | compose config | ✅ no ports |
| Corpus mount | `ls /files/docs` | ✅ 26 files |
| Workflow mount | `ls /import-workflows` | ✅ 2 JSONs |
| Security env | container env | ✅ restrict file access, block env, no diagnostics |

### Database initialization

| Check | Result |
|-------|--------|
| pgvector extension | ✅ v0.8.6 |
| Roles (n8n_app, rag_ingest, rag_runtime) | ✅ all LOGIN |
| Schemas (n8n, rag) | ✅ |
| Schema owners | ✅ n8n→n8n_app, rag→rag_ingest |
| RAG tables (5) | ✅ rag_settings, corpus_versions, documents, telegram_updates, safe_events |
| rag_settings row | ✅ config_revision='UNINITIALIZED' |

### Permission matrix (least-privilege verified)

| Operation | n8n_app | rag_ingest | rag_runtime |
|-----------|---------|-----------|-------------|
| CREATE in n8n schema | ✅ | ❌ | ❌ |
| SELECT in rag schema | ❌ | ✅ | ✅ |
| INSERT corpus (ingest) | ❌ | ✅ | ❌ |
| UPDATE telegram_updates.status | ❌ | ✅ | ✅ |
| INSERT safe_events | ❌ | ✅ | ✅ |
| UPDATE safe_events | ❌ | ✅ | ❌ |

## Bugs Found & Fixed During M6

| # | Bug | Fix |
|---|-----|-----|
| 1 | Init script created schemas before roles → `role "n8n_app" does not exist` | Reorder: extension → roles → DB grants → schemas → grants → tables |
| 2 | n8n_app missing DB-level CONNECT → `permission denied for database automation` | Add `GRANT CONNECT/CREATE ON DATABASE` |
| 3 | rag_runtime missing SELECT on future tables (GRANT ran before tables existed) | Add `ALTER DEFAULT PRIVILEGES ... GRANT SELECT TO rag_runtime` + explicit re-grant after table creation |

## Facts Discovered

- Init script must run as **.sh** (not .sql) to access container env vars for role passwords
- `docker-entrypoint-initdb.d` runs scripts alphabetically; only on **first** container start (empty volume)
- n8n image 1.62.1 uses `node` user; `/home/node/.n8n` writable volume required
- `cap_drop: ALL` + read_only:false works — n8n needs writable /home/node/.n8n

## Out of Scope (per architecture)

- ❌ Workflow import ke n8n (belum — menunggu credential + owner approval)
- ❌ AI provider credential binding
- ❌ Telegram webhook registration
- ❌ AI model profiling (timeout/similarity/dimension calibration)
- ❌ demo-vps profile deployment

## Handoff to Next Stage

- **Stack status:** running (project `rag-local`, containers `rag-n8n-local`, `rag-postgres-local`)
- **Stop:** `bash deploy/stop-local.sh` | **Remove volumes:** `... down -v`
- **Next owner:** Human/QA — workflow import + credential binding per `deploy/WORKFLOW-IMPORT-GUIDE.md`
- **Open items:** AI timeout budget (UNKNOWN), embedding dimension (UNKNOWN), similarity threshold (UNKNOWN) — Engineer calibration
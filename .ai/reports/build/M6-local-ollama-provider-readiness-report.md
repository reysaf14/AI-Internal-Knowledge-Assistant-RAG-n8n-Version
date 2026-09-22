# M6 — Local Ollama Provider Readiness Report

- **Date:** 2026-09-20
- **Role:** Engineer
- **Status:** VERIFIED BY IMPLEMENTER — host, container, and runtime binding pass; M7 QA/Security not started
- **Scope:** Local tester provider only. M7 QA and M8 release/cleanup are out of scope.

## Runtime inventory

Ollama `0.34.0` is reachable at `http://127.0.0.1:11434`.

| Model | Exact tag | Observed capability | Result |
|---|---|---|---|
| Qwen | `qwen3-8b-2k:latest` | chat/completion/thinking | `/v1/chat/completions` PASS with `reasoning_effort=none` |
| Gemma | `gemma4:e2b-it-qat` | chat/completion/vision | `/v1/chat/completions` PASS; cold probe about 30s |
| EmbeddingGemma | `embeddinggemma:300m-qat-q4_0` | embeddings | `/v1/embeddings` PASS; dimension `768`, probe about 681ms |

Historical note: Qwen custom tag was initially selected as the tester chat model because it produced a valid concise response in about 1.7s warm with thinking disabled. The current runtime binding is Gemma, selected for better warm-path latency on the 6GB GPU tester.

## Runtime rebinding addendum — 2026-09-20

For the n8n M6 tester target, the runtime binding was changed to `gemma4:e2b-it-qat` at Human request. This does not change the provider-neutral workflow contract or claim model quality. Direct warm probes measured `165–198ms` for a short prompt and `386–394ms` for a prompt near the runtime context bound; the embedding probe measured `150ms`; a request from the n8n container to Ollama returned HTTP 200 in `620ms`. The first cold Gemma probe was approximately `25.6s`, so cold-start behavior remains exploratory and the required M7 15-item benchmark is still pending.

## Workflow changes

`workflows/02-telegram-grounded-qa.json` now uses Ollama native `/api/chat` with `think: false`, `temperature: 0`, bounded `num_predict`, and `keep_alive: '10m'`. This is a local tester/runtime setting, not a quality claim.

`deploy/WORKFLOW-IMPORT-GUIDE.md` now documents the local binding:

- Base URL: `http://host.docker.internal:11434/v1` for credential compatibility; chat requests use native `/api/chat`
- Chat model: `gemma4:e2b-it-qat`
- Embedding model: `embeddinggemma:300m-qat-q4_0`
- Embedding dimension: `768`

## Remaining blockers / boundaries

1. Cold-start Gemma latency is approximately `25.6s`; warm probes are below `1s`, so the `<5s` result is not a cold-start guarantee.
2. The approved M7 15-item latency and semantic-quality benchmark has not been run.
3. Security review, Human quality/release decision, and temporary-tunnel cleanup remain outside this Engineer verdict.

## Validation boundary

Host and n8n-container provider probes pass; PostgreSQL corpus activation and workflow graph/runtime health also pass. This does not prove semantic QA acceptance, the required latency 15/15, Security, or Release.

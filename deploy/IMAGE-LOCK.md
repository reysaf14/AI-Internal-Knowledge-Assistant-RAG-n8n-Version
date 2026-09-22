# Runtime image lock

The local-isolated Compose profile consumes the immutable amd64 references in
`.env.test` and `.env.example`:

| Service | Reference | Digest source |
|---|---|---|
| n8n | `n8nio/n8n:1.123.81@sha256:0d7b776e0867c415dcb382d24d371a3b0aa402fcba9a9a866f42474abdabf7da` | Docker image actually used by `rag-n8n-local` |
| PostgreSQL + pgvector | `pgvector/pgvector:pg16@sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b` | Docker image actually used by `rag-postgres-local` |

The tag is retained for operator readability; the digest is authoritative.
Any image update must refresh the digest, `deploy/sbom.cdx.json`, and the
security evidence together. Do not replace these values with `latest` or an
unqualified tag.

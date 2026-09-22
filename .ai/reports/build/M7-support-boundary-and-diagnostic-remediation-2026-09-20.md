# M7 Support Boundary and Diagnostic Remediation — 2026-09-20

## Scope

This implementer remediation addresses the three non-model-limitation items from `.ai/reports/qa/M7-qa-model-limitation-triage-2026-09-20.md`:

- item 9: supported annual-leave question returned deterministic abstention;
- item 10: supported sick-leave question returned deterministic abstention;
- item 15: unsupported loan question received a related escalation/contact source.

The accepted local-Gemma limitations for items 2, 4, 5, 6, and 11 were not changed. No Telegram self-test was performed, per Human instruction; the next live verification belongs to the user and QA.

## Root-cause evidence

Read-only nearest-neighbor inspection against the active corpus showed that retrieval was present for the two supported abstentions:

| Item | Nearest active-corpus evidence | Distance | Interpretation |
|---:|---|---:|---|
| 9 | `20_Kebijakan_Cuti_dan_Izin_Karyawan.md` chunks 2, 4, 11 | `0.3023`, `0.3804`, `0.4326` | Source is inside the configured distance boundary (`<= 0.75`); failure was downstream of retrieval and required stage evidence. |
| 10 | `20_Kebijakan_Cuti_dan_Izin_Karyawan.md` chunks 4, 11, 9 | `0.4097`, `0.4261`, `0.4539` | Source is inside the configured distance boundary; deterministic abstention cannot be attributed to retrieval absence. |
| 15 | `19_Panduan_Eskalasi_Komplain_ke_Manajer.md` top candidates | `0.5336` and above | Related escalation content was close enough to enter evidence although no loan policy was present. |

The prior workflow had only similarity filtering plus model citation validation. A related document could therefore become an answer for an unsupported question, and a model abstention had no persisted stage-level reason.

## Changes applied

`workflows/02-telegram-grounded-qa.json` was updated to candidate v8 and deployed to workflow `02 — Telegram Grounded Q&A` (`IAOqkQsNamEJarHF`):

1. **Question-scoped support gate** in `Filter Evidence`
   - tokenizes the question and filtered evidence using normalized, provider-neutral lexical anchors;
   - ignores generic role/document terms such as `manajer`, `toko`, `karyawan`, and `prosedur`;
   - requires at least one topical question term to appear in the retrieved evidence;
   - when the gate fails, evidence is withheld and the deterministic abstention path is used before the LLM call.
   - For item 15, the topical terms `pinjaman`/`mengajukan` are not present in the escalation document, so the related-source path is expected to fail closed. This is a code-path fix, not yet Telegram E2E evidence.

2. **Explicit direct-fact instruction** in `Build Prompt`
   - tells the model to answer when the requested fact is explicitly present instead of abstaining merely because additional facts are absent;
   - preserves the existing citation-first, prompt-evidence-only, no-inference contract.
   - This targets items 9 and 10 without changing the corpus, threshold, or oracle.

3. **Sanitized stage diagnostics**
   - records candidate source/chunk identifiers and rounded distances;
   - records filtered evidence count, prompt evidence count, query-term overlap, support-gate status, model-response class, validator result, and final response status;
   - persists only a bounded diagnostic code in `rag.safe_events` with stage `grounding_diagnostic` and status `observed`; the diagnostic write is non-blocking so telemetry failure cannot suppress the Telegram response;
   - never persists prompt content, model answer text, Telegram payloads, credentials, or PII.

The workflow is now 37 nodes. Runtime `rag.rag_settings.config_revision` is `m7-support-gate-trace-2026-09-20-v8`. n8n's stored workflow is active and contains the support-gate, diagnostic, and validator markers.

No credential, corpus document, schema, embedding profile, similarity threshold, dataset oracle, or ingestion data changed.

## Verification boundary

Static verification passed:

- workflow JSON parses successfully;
- workflow contains 37 nodes and the expected diagnostic connections;
- active n8n database record contains `insufficient_query_overlap`, `grounding_diagnostic`, and `no_valid_citation` markers;
- active runtime revision is v8;
- the active corpus contains the expected source-20 and source-19 chunks.

No Telegram message, model generation, or full QA matrix was executed by Engineer in this remediation. Therefore items 9, 10, and 15 remain unverified at E2E level until QA reruns them.

## QA handoff

QA should run a focused check for items 9, 10, and 15 first, inspect the new `grounding_diagnostic` rows by `stage`, and then rerun the complete frozen 15-item matrix. The original v7 raw result remains authoritative for the approved rubric; the model-limitation disposition for items 2, 4, 5, 6, and 11 remains separate.

## Verdict

`VERIFIED BY IMPLEMENTER — V8 SUPPORT-BOUNDARY/DIAGNOSTIC REMEDIATION; M7 AGGREGATE REMAINS NOT_VERIFIED`

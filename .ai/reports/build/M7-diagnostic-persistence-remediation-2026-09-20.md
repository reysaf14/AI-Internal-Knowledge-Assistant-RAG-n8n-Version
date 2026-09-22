# M7 Diagnostic Persistence Remediation — 2026-09-20

## QA finding

The v8 full-matrix rerun confirmed that item 15 is fixed, but persisted `grounding_diagnostic` rows remained `0`. Items 9 and 10 still abstained, so QA could not determine whether the failure occurred in retrieval, prompt assembly, model output, or citation validation.

## Root-cause correction

The diagnostic PostgreSQL node used `INSERT ... RETURNING id`. The existing runtime telemetry contract only requires a write and does not consume a returned row. The diagnostic node also had to preserve the original workflow item for the next delivery node, so `RETURNING` added no functional value and created an avoidable failure surface in the telemetry-only path.

The query was changed to the same plain `INSERT` pattern already used by the working `Record Safe Event` node. `alwaysOutputData` and the existing context-restore step preserve the Telegram item. The diagnostic write remains non-blocking so telemetry cannot suppress a user response, but the persistence path no longer requests a result set from an insert-only operation.

## Applied runtime change

- Workflow: `02 — Telegram Grounded Q&A`
- Workflow ID: `IAOqkQsNamEJarHF`
- Candidate revision: `m7-support-gate-trace-2026-09-20-v9`
- `Record Grounding Diagnostic` now executes:
  `INSERT INTO rag.safe_events (...) VALUES (...)`
- `RETURNING id` removed.
- Workflow re-imported, activated, and n8n restarted.
- `rag.rag_settings.config_revision` updated to v9.

No corpus, evaluation oracle, credential, embedding profile, retrieval threshold, or model setting changed.

## Verification boundary

Static/runtime checks passed:

- workflow JSON parses successfully;
- workflow remains 37 nodes;
- active n8n workflow contains `grounding_diagnostic` and no `RETURNING id` in that diagnostic query;
- active runtime revision is v9;
- diagnostic node remains connected through context restoration to Telegram delivery.

No Telegram self-test or model generation was performed by Engineer. The first proof that a `grounding_diagnostic` row is actually persisted belongs to QA.

## QA handoff

QA should send one supported question that answers successfully and one supported question that abstains (items 9 and 10 are the required cases), then query `rag.safe_events` for `stage='grounding_diagnostic'`. Once both row types are visible with sanitized metadata, QA should rerun the full 15-item matrix.

## Verdict

`VERIFIED BY IMPLEMENTER — DIAGNOSTIC PERSISTENCE PATCH v9; M7 REMAINS NOT_VERIFIED PENDING QA EVIDENCE`

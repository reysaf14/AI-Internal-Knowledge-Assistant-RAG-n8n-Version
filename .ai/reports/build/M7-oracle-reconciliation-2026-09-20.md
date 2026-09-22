# M7 Oracle Reconciliation — 2026-09-20

## Decision

Human confirmed that the active corpus is the source of truth for the remaining QA oracle conflicts and approved replacement of the corpus-supported unsupported case. The evaluation oracle must follow the active corpus rather than retain contradictory synthetic answers.

## Applied change

`evaluation/qa-dataset.csv` now applies these decisions:

- Item 1 remains: `Toko buka pukul 07.00–21.00 setiap hari, termasuk hari Senin.`; canonical source `21_Kebijakan_Jadwal_Shift_Kerja.md`.
- Items 2, 4, 5, 6, 10, 11, and 12 now use answers derived from their active corpus sources.
- Item 14 (`Siapa nama pemilik toko?`) is replaced with `Bagaimana prosedur klaim biaya perjalanan dinas?`, marked `Unsupported,FALSE`, with no source.

For item 11, the expected answer intentionally uses only facts present in the K3 document: a fire extinguisher should be accessible, exits/escape routes must be clear, and people should know the emergency route. It does not retain unsupported APAR counts or simulation frequency.

## Boundary

No workflow, credential, runtime setting, corpus document, or database data was changed. The separate mock harness fixture still uses its own synthetic corpus and was not altered by this evaluation-oracle reconciliation. No Telegram self-test was performed.

## QA handoff

The 12+3 working dataset is now semantically scorable against the approved corpus-backed oracle. QA may run the full 15-item matrix sequentially against runtime v7. M7 remains `NOT_VERIFIED` until the complete semantic/source/abstention, latency, fault/concurrency, and security gates are executed.

## Status

`APPROVED BY HUMAN — READY FOR QA CONTINUATION`

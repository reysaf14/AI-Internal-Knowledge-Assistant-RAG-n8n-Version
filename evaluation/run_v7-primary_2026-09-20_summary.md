# v7 Primary Evaluation Run Summary — 2026-09-20

- Candidate: `m7-citation-contract-2026-09-20-v7`
- Dataset: updated 12 supported + 3 unsupported working copy
- Executor: independent QA
- Target: authorized synthetic Telegram sandbox
- Delivery: `15/15 delivered`
- Safe events: `15/15 success`, no error category
- Latency: `15/15 < 5,000 ms`; range `1,558–3,573 ms`, average `2,333.8 ms`
- Supported content: `5/12 pass`
- Supported source citation: `10/12 relevant source observed`
- Unsupported abstention: `2/3 pass`
- Overall content/abstention: `7/15 pass`
- Verdict: `FAIL`

Primary failures: item 2 omitted motor parking capacity; items 4, 5, 6 omitted mandatory SOP facts; items 9 and 10 abstained on supported policy questions; item 11 omitted the APAR/fire-extinguisher fact; item 15 leaked a cited escalation/contact claim for an unsupported loan question.

Deterministic regression rerun remained `67/67` (`19/19`, `21/21`, `27/27`). The deterministic harness does not override the live semantic failures.

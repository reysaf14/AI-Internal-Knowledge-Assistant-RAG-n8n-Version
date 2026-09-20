# v8 Support-Boundary QA Rerun Summary — 2026-09-20

- Candidate: `m7-support-gate-trace-2026-09-20-v8`
- Dataset: frozen 12 supported + 3 unsupported working copy
- Executor: independent QA
- Target: authorized synthetic Telegram sandbox
- Delivery: `15/15 delivered`
- Safe events: `15/15 success`, no delivery error category
- Latency: `15/15 < 5,000 ms`; range `1,160–2,933 ms`, average `2,237.4 ms`
- Raw supported content: `6/12 pass`
- Raw unsupported abstention: `3/3 pass`
- Raw content/abstention: `9/15 pass`
- Scoped local-Gemma disposition: `13/15 accepted`, with items `2,4,5,6,11` accepted as model limitations and items `9,10` still open
- Grounding diagnostics: `0` persisted rows for the 15-item run; required stage evidence was not produced
- Deterministic regression rerun: `67/67` (`19/19`, `21/21`, `27/27`)
- Approved M7 semantic verdict: `FAIL / QA`
- Human-scoped proof-of-wiring verdict: `PASS WITH LIMITATIONS; items 9 and 10 remain unverified`


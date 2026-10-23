# Dashboard snapshot

This directory contains a committed demonstration snapshot so the dashboard and its preflight checks can be inspected immediately. CSVs, SQLite tables and reports here belong to the smaller dashboard workflow, not the separate 12M-observation benchmark.

Regenerate from the repository root with `python src/main.py --offline`, then run `python src/preflight.py`. Reruns update timestamps and derived files; commit a refreshed snapshot only deliberately. `verification_summary.json` records the checks from its own generation time and is not the latest CI status.

Use [evidence/full](../evidence/full/) for the separate benchmark and [CI verification](../docs/ci_verification.md) for the executed workflows.

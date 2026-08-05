# Repository Instructions for AI Coding Assistants

This portfolio project demonstrates a human-governed AI-assisted analytics and team-enablement workflow.

## Priorities

1. Keep the interview demo deterministic and reliable.
2. Use public or synthetic data only.
3. Never imply access to Red Hat, customer, confidential, or production data.
4. Protect credentials and privacy.
5. Prefer minimal, explainable, reviewable changes.
6. Validate Python, SQL, analytical claims, and stakeholder wording.
7. Separate calculated facts from interpretation and recommended action.

## Required Completion Checks

- Run `python -m py_compile app.py src/main.py src/dashboard_utils.py src/preflight.py src/gtm_demo.py src/snowflake_adapter.py`.
- Run `python -m pytest -q`.
- Run `python src/main.py --offline` for deterministic interview data.
- Run `python src/preflight.py` and require a PASS result.
- Confirm the dashboard can start without external services.
- Keep Snowflake live actions optional, gated, and credential-dependent.
- Record material AI-assisted changes in `docs/ai_assistance_log.json`.

# Cursor Adoption Workflow

## Why Cursor is included

The project demonstrates how repository-aware AI assistance can be governed for an analytics team. Cursor project rules in `.cursor/rules/analytics-quality.mdc` encode persistent constraints for Python, Snowflake SQL, data privacy, testing, and stakeholder communication.

## Safe demo prompt

```text
Review @src/gtm_demo.py, @src/snowflake_adapter.py, and @sql/snowflake_gtm_analysis.sql.
Explain the data flow, identify one low-risk improvement, and propose the smallest patch.
Follow the project rules: use synthetic data only, do not expose credentials, do not execute destructive SQL, and provide verification steps. Do not change files until I approve the plan.
```

## Human review gate

1. Inspect which files Cursor used as context.
2. Review the proposed plan before allowing edits.
3. Inspect the diff line by line.
4. Reject unrelated or unsupported changes.
5. Run syntax checks and tests.
6. Verify the dashboard and analytical outputs manually.
7. Document the accepted, modified, and rejected suggestions.

## Team enablement use cases

- Explain an unfamiliar pipeline to a new analyst.
- Draft or review Snowflake SQL with repository context.
- Generate tests for an approved analytics change.
- Translate validated technical findings into stakeholder-ready language.
- Produce onboarding notes while preserving project-specific guardrails.

# Cursor Live Demo — 90 Seconds

Use this only after opening the repository in Cursor and confirming that the project rule is active.

## Safe prompt

```text
Review @src/gtm_demo.py, @src/snowflake_adapter.py, and @sql/snowflake_gtm_analysis.sql.
Explain the data flow in five bullets, identify one low-risk improvement, and propose the smallest patch.
Follow @Cursor Rules: synthetic data only, no credentials, no destructive SQL, and include verification steps.
Do not change files until I approve the plan.
```

## What to show

1. The prompt references exact repository files.
2. Cursor displays the applied project rule.
3. Cursor explains the end-to-end data flow.
4. Cursor proposes a plan before changing code.
5. You say: “I would review the plan and diff, run tests, and validate the analytics before accepting any change.”

## What not to do live

- Do not share a Snowflake account, credentials, or company data.
- Do not allow a large automatic refactor.
- Do not run destructive SQL.
- Do not depend on the AI response completing perfectly; keep screenshots or this documented workflow as backup.

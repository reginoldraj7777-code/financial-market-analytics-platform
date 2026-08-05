# Snowflake Integration Design

The core dashboard runs locally and does not require a Snowflake account. An optional adapter demonstrates production-aware integration without storing credentials in the repository.

## Architecture

`Synthetic/public source → Python validation and feature engineering → Snowflake staging/core table → governed SQL views → Streamlit stakeholder dashboard`

## Security and configuration

Credentials are read only from environment variables. No credential values are displayed or written to files.

Required variables:

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- one supported authentication configuration such as `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_AUTHENTICATOR`, or `SNOWFLAKE_TOKEN`

Optional:

- `SNOWFLAKE_ROLE`

Install the optional connector:

```bash
pip install -r requirements-snowflake.txt
```

The adapter applies a query tag, exposes a safe connectivity test, restricts the in-app query runner to `SELECT`/`WITH`, validates table identifiers, and requires an explicit user confirmation before any demo upload.

## Interview positioning

- The live connector is optional because the interview demo must remain stable.
- The project does not claim access to company data.
- The Snowflake layer demonstrates knowledge of cloud data warehousing, reusable reporting tables, window functions, `QUALIFY`, `COUNT_IF`, and governed Python-to-Snowflake workflows.

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
except Exception:  # optional interview/demo dependency
    snowflake = None
    write_pandas = None


REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]
AUTH_ENV_VARS = ["SNOWFLAKE_PASSWORD", "SNOWFLAKE_AUTHENTICATOR", "SNOWFLAKE_TOKEN"]


@dataclass(frozen=True)
class SnowflakeReadiness:
    connector_installed: bool
    required_fields_present: bool
    authentication_configured: bool
    missing_fields: tuple[str, ...]

    @property
    def live_ready(self) -> bool:
        return self.connector_installed and self.required_fields_present and self.authentication_configured


def connection_readiness() -> SnowflakeReadiness:
    missing = tuple(name for name in REQUIRED_ENV_VARS if not os.getenv(name))
    auth_configured = any(os.getenv(name) for name in AUTH_ENV_VARS)
    return SnowflakeReadiness(
        connector_installed=snowflake is not None,
        required_fields_present=not missing,
        authentication_configured=auth_configured,
        missing_fields=missing,
    )


def safe_connection_summary() -> dict[str, str]:
    """Return non-secret configuration metadata only."""
    return {
        "account_configured": "yes" if os.getenv("SNOWFLAKE_ACCOUNT") else "no",
        "user_configured": "yes" if os.getenv("SNOWFLAKE_USER") else "no",
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "not configured"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "not configured"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "not configured"),
        "role": os.getenv("SNOWFLAKE_ROLE", "account default"),
        "authenticator": os.getenv("SNOWFLAKE_AUTHENTICATOR", "password/token if configured"),
    }


def _connection_params() -> dict[str, Any]:
    readiness = connection_readiness()
    if not readiness.live_ready:
        raise RuntimeError(
            "Snowflake live mode is not configured. Install the optional connector and set the required environment variables."
        )

    params: dict[str, Any] = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
        "schema": os.environ["SNOWFLAKE_SCHEMA"],
        "session_parameters": {"QUERY_TAG": "portfolio_gtm_ai_adoption_demo"},
    }
    optional_map = {
        "SNOWFLAKE_PASSWORD": "password",
        "SNOWFLAKE_ROLE": "role",
        "SNOWFLAKE_AUTHENTICATOR": "authenticator",
        "SNOWFLAKE_TOKEN": "token",
    }
    for env_name, parameter_name in optional_map.items():
        value = os.getenv(env_name)
        if value:
            params[parameter_name] = value
    return params


def connect():
    if snowflake is None:
        raise RuntimeError('Install optional dependency: pip install "snowflake-connector-python[pandas]"')
    return snowflake.connector.connect(**_connection_params())


def test_connection() -> pd.DataFrame:
    query = """
    SELECT CURRENT_ACCOUNT() AS ACCOUNT,
           CURRENT_ROLE() AS ROLE,
           CURRENT_WAREHOUSE() AS WAREHOUSE,
           CURRENT_DATABASE() AS DATABASE,
           CURRENT_SCHEMA() AS SCHEMA,
           CURRENT_VERSION() AS SNOWFLAKE_VERSION
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetch_pandas_all()


def _validated_identifier(value: str) -> str:
    normalized = value.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,126}", normalized):
        raise ValueError("Snowflake identifier must use letters, numbers, and underscores and start with a letter.")
    return normalized


def upload_demo_dataframe(df: pd.DataFrame, table_name: str = "GTM_METRICS_DEMO") -> dict[str, Any]:
    if write_pandas is None:
        raise RuntimeError('Install optional dependency: pip install "snowflake-connector-python[pandas]"')
    table = _validated_identifier(table_name)
    upload_df = df.copy()
    upload_df.columns = [str(col).upper() for col in upload_df.columns]
    upload_df["WEEK_START"] = pd.to_datetime(upload_df["WEEK_START"]).dt.date

    with connect() as conn:
        columns_sql = """
            WEEK_START DATE,
            REGION VARCHAR,
            SEGMENT VARCHAR,
            PRODUCT_FAMILY VARCHAR,
            PIPELINE_VALUE_EUR FLOAT,
            BOOKINGS_EUR FLOAT,
            WIN_RATE FLOAT,
            CONVERSION_RATE FLOAT,
            ACTIVITY_COUNT INTEGER,
            NEW_OPPORTUNITIES INTEGER,
            FORECAST_COVERAGE FLOAT,
            EVENT_LABEL VARCHAR,
            EVENT_DRIVER VARCHAR,
            DATA_CLASSIFICATION VARCHAR,
            PIPELINE_CHANGE_4W FLOAT,
            BOOKINGS_CHANGE_4W FLOAT,
            WIN_RATE_CHANGE_4W FLOAT,
            ATTENTION_SCORE FLOAT,
            REQUIRES_REVIEW BOOLEAN
        """
        with conn.cursor() as cur:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns_sql})")
        success, chunks, rows, output = write_pandas(
            conn,
            upload_df,
            table,
            overwrite=True,
            quote_identifiers=True,
        )
    return {"success": success, "chunks": chunks, "rows": rows, "output": output, "table": table}


def run_readonly_query(sql: str) -> pd.DataFrame:
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT") and not normalized.startswith("WITH"):
        raise ValueError("The demo query runner allows only SELECT or WITH statements.")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetch_pandas_all()

# Time-Series Analytics & AI Adoption Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20Dashboard-EE0000)
![SQLite](https://img.shields.io/badge/SQLite-Local%20Analytics-lightgrey)
![Snowflake](https://img.shields.io/badge/Snowflake-Ready-29B5E8)
![Cursor](https://img.shields.io/badge/Cursor-Assisted%20Workflow-7C3AED)
![Data](https://img.shields.io/badge/Data-Public%20%2B%20Synthetic-22C55E)

An end-to-end analytics platform that converts multi-entity time-series data into validated metrics, explainable review flags, reusable SQL outputs, and stakeholder-ready insights.

The project uses public market data as a realistic time-series test environment and extends the same analytical operating model to clearly labelled synthetic EMEA GTM and operational datasets.

> **Data boundary:** No company, customer, confidential, or production data is used. The GTM and operational datasets are deterministic and synthetic. Snowflake integration is optional and disabled until explicitly configured.

![Dashboard overview](screenshots/dashboard_overview.png)

## Why this project exists

Analytical teams often have plenty of data but still need a reliable way to answer three practical questions:

1. What changed?
2. Why was it flagged?
3. What should an analyst review next?

The platform supports this workflow through transparent rules and review queues. It prioritises investigation; it does not automate business decisions or claim causality.

## Core workflow

```text
ingest → validate → engineer → detect → store → explain → review
```

- **Ingest:** Load public time-series data with deterministic offline fallback.
- **Validate:** Check structure, completeness, duplicates, ranges, and freshness.
- **Engineer:** Calculate returns, moving averages, volatility, drawdown, and comparison metrics.
- **Detect:** Apply explainable anomaly and prioritisation rules.
- **Store:** Persist reusable analytical outputs in CSV, SQLite, and SQL assets.
- **Explain:** Show the metric, threshold, and rule behind each review flag.
- **Review:** Keep final interpretation and action with the human analyst.

## Key capabilities

### Comparable analytics

- Indexed cross-entity performance comparison
- Moving averages and trend indicators
- Return, volatility, and drawdown analysis
- Transparent attention-score decomposition
- Correlation and benchmark views

### Explainable investigation

- Return-anomaly, volatility-spike, and high-volume rules
- Severity and review-priority queues
- Supporting metrics and thresholds for each flag
- Human follow-up questions before action
- Clear separation between observed facts and interpretation

### SQL and warehouse readiness

- Read-only SQLite analytical workspace
- Reusable SQL query templates
- Snowflake-ready schema and analysis scripts
- Environment-based connection configuration
- Safe live-mode gating and explicit confirmation before uploads

### Reliability and reproducibility

- Data-quality checks and generated reports
- Pipeline run metadata and file fingerprints
- Automated tests and preflight verification
- Deterministic synthetic datasets
- One-command Windows demo workflow

### Human-reviewed AI assistance

AI tools support bounded tasks such as repository understanding, debugging, SQL drafting, documentation, and first-pass summaries.

The repository records:

```text
problem → bounded prompt → AI contribution → human decision → verification → impact
```

AI suggestions are treated as proposals. The human owner reviews changes, validates outputs, protects data boundaries, and owns the final analytical or technical decision.

## Synthetic GTM extension

The same operating model is demonstrated with synthetic EMEA GTM concepts:

- regions, accounts, and products
- pipeline value and bookings
- win rate and regional comparisons
- explainable review queues
- stakeholder-ready summaries
- skill-gap and AI-enablement planning

This extension demonstrates transferability of the workflow without implying access to any organisation's internal data or systems.

## Dashboard sections

1. **Overview** — business framing, data quality, decision brief, and architecture
2. **Trends** — indexed comparisons, KPIs, risk drivers, and correlations
3. **Investigation** — rule catalogue, severity queue, and event drill-down
4. **SQL & Snowflake** — read-only queries, SQL assets, lineage, and readiness checks
5. **Reliability** — quality controls, tests, run metadata, and reproducibility evidence
6. **Operations** — synthetic service-health and incident-monitoring use cases
7. **AI Evidence** — auditable AI-assisted tasks, controls, prompts, and decisions
8. **GTM Studio** — synthetic regional KPIs, review queues, and adoption planning

## Quick start

### Windows

Double-click:

```text
RUN_INTERVIEW_DEMO_WINDOWS.bat
```

The script creates or reuses a virtual environment, installs dependencies, runs the pipeline, executes verification checks, and starts Streamlit.

### Manual setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python src/main.py
streamlit run app.py
```

### Verification

```bash
python -m pip install -r requirements-dev.txt
pytest
python src/preflight.py
```

## Optional Snowflake setup

The project works fully in local mode.

To enable the optional Snowflake connector:

```bash
python -m pip install -r requirements-snowflake.txt
```

Configure the documented `SNOWFLAKE_*` environment variables. Credentials are never stored in source code, and live actions remain disabled until the required configuration and explicit confirmation are present.

## Repository structure

```text
.
├── app.py
├── src/
│   ├── main.py
│   ├── dashboard_utils.py
│   ├── preflight.py
│   ├── gtm_demo.py
│   └── snowflake_adapter.py
├── sql/
├── docs/
├── outputs/
├── screenshots/
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── requirements-snowflake.txt
```

## Limitations

- The attention score is a transparent heuristic, not a predictive model.
- The synthetic GTM and operations datasets do not represent real organisational performance.
- Snowflake support is architecture- and SQL-ready; the default demonstration runs locally.
- Anomaly detection identifies patterns requiring review but does not determine business causality.

## Disclaimer

This project is for educational and portfolio demonstration purposes. It is not a production trading system and does not provide financial advice.

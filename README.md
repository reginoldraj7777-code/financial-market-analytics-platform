# Financial Market Analytics Platform

An end-to-end time-series analytics platform built with Python, SQL-ready exports, automated reporting, and an interactive Streamlit dashboard.

The project converts raw multi-entity market data into validated datasets, engineered indicators, explainable event flags, SQLite tables, reusable SQL queries, and dashboard insights.

## What this project solves

Raw time-series data is difficult to interpret directly. Analysts need a fast way to identify trend direction, volatility, abnormal movement, high-volume events, and risk changes across multiple entities. This project automates that workflow from data ingestion to visual reporting.

## Key features

- Multi-symbol time-series ingestion with offline fallback data
- Data validation and quality reporting
- Feature engineering: daily returns, moving averages, rolling volatility, drawdown, and risk score
- Explainable event detection for abnormal returns, volatility spikes, and high-volume events
- SQL-ready storage using SQLite
- Reusable SQL analysis queries
- Automated Markdown summary report
- Streamlit dashboard for overview, trend/risk analysis, event detection, SQL reports, and pipeline monitoring
- Synthetic system-telemetry extension to show that the same pipeline design can handle other timestamped operational signals

## Project structure

```text
financial-market-analytics-platform/
├── app.py                         # Streamlit dashboard layer
├── src/main.py                    # Data pipeline: ingestion, validation, features, events, SQL, reports
├── requirements.txt               # Python dependencies
├── docs/architecture.md           # Architecture notes
├── notebooks/README.md            # Notebook guidance
├── outputs/README.md              # Generated output description
├── screenshots/                   # Visual examples
└── tests/                         # Basic pipeline tests
```

## How to run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
streamlit run app.py
```

Then open the local Streamlit URL in your browser, usually:

```text
http://localhost:8501
```

## Generated outputs

After running the pipeline, the `outputs/` folder contains:

- `processed_stock_metrics.csv`
- `processed_data.csv`
- `simulated_system_telemetry.csv`
- `event_stream_log.csv`
- `analytics_pipeline.db`
- `automated_summary_report.md`
- `data_quality_report.md`
- `sql_analysis_queries.sql`
- `pipeline_run_log.json`

## Technical design

The project separates the pipeline from the dashboard:

- `src/main.py` prepares the data and generates reusable outputs.
- `app.py` reads those outputs and visualizes them.

This keeps the analytics logic reproducible and makes the dashboard easier to maintain.

## Tech stack

Python, pandas, NumPy, yfinance, SQLite, SQL, Plotly, Streamlit

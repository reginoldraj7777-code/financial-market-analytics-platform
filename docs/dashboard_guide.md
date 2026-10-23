# Dashboard guide

This Streamlit dashboard is the smaller public-market, synthetic operations and GTM demonstration. The 12M-observation API benchmark is documented separately in the [main README](../README.md).

![Dashboard overview](../screenshots/dashboard_overview.png)

## Start locally

After the Python 3.12 environment and development dependencies in the main README are installed, run these commands from the repository root:

```bash
python src/main.py --offline
python src/preflight.py
streamlit run app.py
```

On Windows, use [the launchers](../scripts/windows/README.md). Offline mode is deterministic and does not require external services. Live public-data retrieval is available through `python src/main.py`.

## Find a view

| View | Question it answers |
|---|---|
| Overview | What changed and which items need human context? |
| Trends | How do indexed performance, volatility and drawdown compare? |
| Investigation | Which rule triggered each flag, and what should be reviewed? |
| SQL & Snowflake | How can the prepared data be queried and reused? |
| Reliability | Which implemented quality checks passed? |
| Operations | How does the workflow apply to synthetic service telemetry? |
| AI Evidence | What assistance, decisions and verification were recorded? |
| GTM Studio | How do synthetic regional KPIs support investigation and team adoption? |

The attention score is a transparent heuristic, not a predictive model. Flags prioritize investigation and do not establish causality. Quality results cover the implemented checks, not universal data correctness.

For a guided presentation, use the [demo walkthrough](demo/walkthrough.md). For the optional warehouse path, read [Snowflake integration](SNOWFLAKE_INTEGRATION.md). The [AI adoption playbook](AI_ADOPTION_PLAYBOOK.md) describes a proposed team workflow, not measured organizational adoption.

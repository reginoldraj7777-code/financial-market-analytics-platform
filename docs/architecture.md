# System Architecture

This project follows a simple but production-style analytics architecture.  
The goal is to separate the data processing layer from the dashboard layer, so the pipeline can be tested, extended, and reused independently.

---

## High-Level Flow

```text
Raw Time-Series Data
        ↓
Data Ingestion
        ↓
Validation and Cleaning
        ↓
Feature Engineering
        ↓
Event and Pattern Detection
        ↓
CSV + SQLite + Report Outputs
        ↓
Interactive Streamlit Dashboard
```


---

## Design Decisions

- The processing pipeline is separated from the dashboard.
- The project uses explainable rule-based event detection.
- Outputs are exported as CSV, SQLite, SQL queries, and Markdown reports.
- The dashboard reads prepared outputs instead of doing heavy processing directly.

---

## Possible Extensions

- Scheduled pipeline execution
- Larger symbol coverage
- Database indexing
- API layer
- Cloud deployment
- Model-based event prediction

# Architecture

## Pipeline design

```text
Raw time-series data
    ↓
Ingestion with offline fallback
    ↓
Data validation and quality checks
    ↓
Feature engineering
    ↓
Explainable event detection
    ↓
CSV + SQLite exports
    ↓
Automated report + dashboard
```

## Main design decisions

1. **Pipeline-first structure**  
   The data pipeline runs independently of the dashboard. This makes the system easier to test and reuse.

2. **Explainable event detection**  
   Rule-based detection is used for transparency. Each flagged event can be explained using z-scores, volatility thresholds, or volume thresholds.

3. **SQL-ready output**  
   Results are exported to SQLite so the same processed data can be queried, reported, and integrated with other tools.

4. **Offline fallback**  
   The pipeline can still run without live API access by generating stable synthetic market-style data.

5. **Dashboard as consumption layer**  
   The dashboard only reads prepared outputs. It does not contain the main data-processing logic.

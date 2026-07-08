# Automated Analytics Summary Report

Generated: 2026-07-08 14:28

## Pipeline Summary

- Stock rows processed: 3,128
- Symbols/entities processed: 4
- Simulated stream batches: 13
- Return anomalies detected: 66
- Volatility spikes detected: 312
- High-volume events detected: 316

## Highest Latest Risk

- Symbol: NVDA
- Latest date: 2024-12-31
- Latest close: 183.24
- Risk score: 72.5/100
- Trend signal: Short-term upward / Above long MA

## Event Summary by Symbol

| Symbol   |   Return_Anomaly |   Volatility_Spike |   High_Volume_Event |
|:---------|-----------------:|-------------------:|--------------------:|
| AAPL     |               14 |                 78 |                  79 |
| MSFT     |               17 |                 78 |                  79 |
| NVDA     |               16 |                 78 |                  79 |
| TSLA     |               19 |                 78 |                  79 |

## Data Quality

- Required columns present: True
- Duplicate Date/Symbol rows: 0
- Missing columns: []

## Extension Note

The financial dataset is used because it is public and time-series based. The same pipeline pattern can be reusered to internal engineering telemetry: entity IDs, timestamps, signal values, anomaly rules, SQL-ready outputs, automated summaries, and dashboards.

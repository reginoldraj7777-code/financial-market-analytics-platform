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

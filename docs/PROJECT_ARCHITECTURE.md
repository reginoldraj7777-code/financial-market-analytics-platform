# Project Architecture

```mermaid
flowchart LR
    A[Public market data or deterministic fallback] --> B[Validation]
    B --> C[Feature engineering]
    C --> D[Explainable event detection]
    D --> E[CSV and SQLite]
    E --> F[Optional Snowflake table and governed view]
    E --> G[Streamlit decision dashboard]
    H[Synthetic operational data] --> B
    I[Synthetic EMEA GTM data] --> E
    J[AI evidence and Cursor rules] --> K[Human review and verification]
    K --> G
```

## Core Design Principles

1. Stable local demo with deterministic fallback.
2. Clear separation between public, synthetic, and optional live data.
3. Explainable rules instead of unsupported black-box conclusions.
4. Reusable SQL and storage outside the dashboard.
5. Human ownership of AI-assisted decisions.
6. Optional Snowflake integration without embedded credentials.
7. Version-controlled Cursor rules and auditable evidence.

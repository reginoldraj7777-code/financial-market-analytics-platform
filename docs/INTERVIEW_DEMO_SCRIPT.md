# Technical Interview Demo Script — 7 Minutes

## 0:00–0:35 — Opening

> Thank you for the opportunity. I will present a decision-intelligence and AI-adoption platform. The core engine converts raw multi-entity time-series data into validated metrics, explainable review flags, SQL-ready outputs, and stakeholder-focused insights. I use public market data for the reusable analytics engine and clearly labelled synthetic data for operational and EMEA GTM demonstrations.

## 0:35–1:30 — Overview

Show **Tab 1**.

> The first design decision was to start with the stakeholder question, not the chart. The command center shows data quality, the current risk state, critical review items, a calculated decision brief, and questions that require human context before action. The architecture covers ingestion, validation, feature engineering, detection, storage, explanation, and governance.

## 1:30–2:30 — Trend and Driver Analysis

Show **Tab 2**.

> Here I compare trends, volatility, drawdown, and a transparent attention score. The attention score is decomposed into volatility, drawdown, and anomaly contributions so it is explainable. I can also compare entities on an indexed basis and inspect correlations.

## 2:30–3:25 — Events and Investigation

Show **Tab 3**.

> The system does not claim causality. It creates an explainable analyst queue. Each event shows the triggered rule, observed facts, priority, and follow-up questions. The analyst decides whether to close, monitor, investigate, or escalate.

## 3:25–4:15 — SQL and Snowflake

Show **Tab 4**.

> The analytical outputs are reusable outside the dashboard. I provide read-only SQLite analysis, generated files, lineage, and a Snowflake-ready design. The Snowflake layer uses environment-based configuration, governed views, native SQL, and live actions are disabled unless all required configuration and authentication are present.

## 4:15–5:15 — AI Evidence

Show **Tab 7** and select **AI-001**.

> I wanted to demonstrate evidence rather than just claim that I used AI. This record shows the original problem, bounded prompt, AI contribution, my decisions, verification, and the final artifact. AI helped diagnose a missing dependency, but I confirmed the traceback, changed only dependency management, reran the entire pipeline, and verified the dashboard. The same evidence model covers Cursor and Snowflake work.

## 5:15–6:35 — GTM Studio

Show **Tab 8**.

> This is the role-specific layer. It uses synthetic EMEA GTM data for pipeline, bookings, win rate, conversion, and activity. It includes a regional review queue, an AI use-case builder, a 30–60–90 adoption plan, skill-gap mapping, Snowflake readiness, and Cursor-assisted workflows with repository rules and human review. The goal is not only individual productivity; it is repeatable team enablement with privacy, verification, and ownership.

## 6:35–7:00 — Close

> The main lesson is that AI can accelerate diagnosis, SQL development, and communication, but the analyst must remain responsible for data quality, assumptions, validation, privacy, and the final decision. That is the operating model I would bring to EMEA GTM Operations.

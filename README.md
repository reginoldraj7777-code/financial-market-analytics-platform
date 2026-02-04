# Financial Market Analytics Platform

Interactive time-series stock market analytics dashboard built using Python, MySQL, and Apache Superset for multi-stock trend and risk analysis.

---

## Overview

This project analyzes historical stock market data, computes technical indicators, and delivers interactive dashboards for comparative performance and volatility analysis across multiple stocks.

The platform combines SQL-based analytics with BI dashboard visualization to support exploratory financial analysis and decision insights.

---

## Key Features

- Time-series stock price analysis
- Technical indicator engineering (moving averages, volatility metrics)
- Multi-stock comparative performance tracking
- SQL-based analytical queries
- Interactive dashboards with filters and drill-down views
- Multi-chart visualization (line, candlestick, bar, scatter)

---

## Tech Stack

- Python
- Pandas
- NumPy
- MySQL
- SQL Analytics Queries
- Apache Superset
- Time-Series Financial Data Processing
- Dashboard Visualization

---

## Project Structure

data/ → Raw and processed stock datasets
notebooks/ → Analysis and feature engineering notebooks
src/ → Core data processing and query scripts
outputs/ → Generated charts and exports
requirements.txt → Python dependencies
---

## Data Processing Pipeline

1. Historical stock price data collected and cleaned
2. MySQL tables created for structured storage
3. Technical indicators computed (moving averages, volatility metrics)
4. SQL analytical queries built for derived metrics
5. Apache Superset connected to database
6. Interactive dashboards created with filters and drill-down analysis

---

## Example Analytics Supported

- Moving average trend signals
- Volatility comparison across multiple stocks
- Time-window performance tracking
- Cross-stock KPI comparison
- Multi-chart visual exploration

---

## How to Run

1. Clone the repository

git clone https://github.com/<your-username>/financial-market-analytics-platform

2. Install dependencies

pip install -r requirements.txt

3. Load datasets into MySQL tables
4. Run preprocessing scripts from src/
5. Connect Apache Superset to MySQL
6. Build dashboards using provided queries

---

## Project Outcome

This project delivers an end-to-end financial analytics platform that converts raw time-series stock data into decision-ready dashboards using SQL analytics and BI visualization tools.

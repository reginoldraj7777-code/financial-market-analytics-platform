from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import PipelineConfig, engineer_features, offline_stock_data, validate_dataframe


def test_engineered_columns_exist():
    cfg = PipelineConfig(symbols=["TSLA"], start_date="2022-01-01", end_date="2022-04-01")
    raw = offline_stock_data("TSLA", cfg.start_date, cfg.end_date)
    raw["Symbol"] = "TSLA"
    processed = engineer_features(raw, cfg)
    for col in ["Daily_Return", "SMA_20", "SMA_50", "Volatility_20", "Risk_Score", "Event_Label"]:
        assert col in processed.columns


def test_validation_passes_for_processed_data():
    cfg = PipelineConfig(symbols=["TSLA"], start_date="2022-01-01", end_date="2022-04-01")
    raw = offline_stock_data("TSLA", cfg.start_date, cfg.end_date)
    raw["Symbol"] = "TSLA"
    processed = engineer_features(raw, cfg)
    report = validate_dataframe(processed)
    assert report["required_columns_present"] is True
    assert report["duplicate_date_symbol_rows"] == 0

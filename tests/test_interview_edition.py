from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_all_interview_tabs_and_assets_are_present():
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    expected_tabs = [
        "1 Overview",
        "2 Trends",
        "3 Investigation",
        "4 SQL & Snowflake",
        "5 Reliability",
        "6 Operations",
        "7 AI Evidence",
        "8 GTM Studio",
    ]
    for label in expected_tabs:
        assert label in app

    for relative in [
        "docs/INTERVIEW_DEMO_SCRIPT.md",
        "docs/TECHNICAL_QA_BANK.md",
        "docs/DEMO_RISK_CHECKLIST.md",
        "RUN_INTERVIEW_DEMO_WINDOWS.bat",
        "PREFLIGHT_CHECK_WINDOWS.bat",
        ".streamlit/config.toml",
    ]:
        assert (ROOT / relative).exists(), relative


def test_preflight_summary_is_passed_after_build():
    path = ROOT / "outputs" / "verification_summary.json"
    assert path.exists()
    summary = json.loads(path.read_text(encoding="utf-8"))
    assert summary["status"] == "PASS"
    assert summary["data_quality_score"] == 100.0


def test_latest_ai_evidence_record_exists():
    data = json.loads((ROOT / "docs" / "ai_assistance_log.json").read_text(encoding="utf-8"))
    record = next(item for item in data["records"] if item["id"] == "AI-006")
    assert record["status"] == "Verified"
    assert len(record["verification"]) >= 5

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from .dashboard_utils import data_quality_checks, quality_score
except ImportError:  # Support direct execution: python src/preflight.py
    from dashboard_utils import data_quality_checks, quality_score

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
SUMMARY_PATH = OUTPUT_DIR / "verification_summary.json"


def run_command(command: list[str]) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def parse_pytest_summary(output: str) -> str:
    for line in reversed(output.splitlines()):
        if "passed" in line or "failed" in line or "error" in line:
            return line.strip()
    return "No pytest summary found"


def main() -> int:
    checks: list[dict[str, object]] = []

    compile_ok = True
    compile_error = ""
    for relative in ["app.py", "src/main.py", "src/gtm_demo.py", "src/snowflake_adapter.py", "src/dashboard_utils.py"]:
        try:
            py_compile.compile(str(ROOT / relative), doraise=True)
        except Exception as exc:  # pragma: no cover - operational script
            compile_ok = False
            compile_error = f"{relative}: {exc}"
            break
    checks.append({"name": "Python syntax", "passed": compile_ok, "detail": compile_error or "All core modules compiled"})

    pytest_ok, pytest_output = run_command([sys.executable, "-m", "pytest", "-q"])
    pytest_summary = parse_pytest_summary(pytest_output)
    checks.append({"name": "Automated tests", "passed": pytest_ok, "detail": pytest_summary})

    stock_path = OUTPUT_DIR / "processed_stock_metrics.csv"
    if stock_path.exists():
        stock_df = pd.read_csv(stock_path)
        quality = quality_score(stock_df)
        dq = data_quality_checks(stock_df)
        data_ok = bool(dq["Passed"].all())
        checks.append({"name": "Data quality", "passed": data_ok, "detail": f"Weighted gate score {quality:.0f}/100; {int(dq['Passed'].sum())}/{len(dq)} implemented checks passed"})
    else:
        quality = 0.0
        checks.append({"name": "Data quality", "passed": False, "detail": "processed_stock_metrics.csv missing"})

    required_artifacts = [
        "processed_stock_metrics.csv",
        "simulated_system_telemetry.csv",
        "synthetic_gtm_metrics.csv",
        "event_stream_log.csv",
        "analytics_pipeline.db",
        "automated_summary_report.md",
        "data_quality_report.md",
        "pipeline_run_log.json",
    ]
    missing = [name for name in required_artifacts if not (OUTPUT_DIR / name).exists()]
    checks.append({"name": "Required artifacts", "passed": not missing, "detail": "All present" if not missing else f"Missing: {', '.join(missing)}"})

    governance_files = [
        ROOT / ".cursor" / "rules" / "analytics-quality.mdc",
        ROOT / "docs" / "ai_assistance_log.json",
        ROOT / "docs" / "AI_ADOPTION_PLAYBOOK.md",
        ROOT / "sql" / "snowflake_gtm_schema.sql",
        ROOT / "sql" / "snowflake_gtm_analysis.sql",
    ]
    governance_missing = [str(path.relative_to(ROOT)) for path in governance_files if not path.exists()]
    checks.append({"name": "AI / Snowflake governance assets", "passed": not governance_missing, "detail": "All present" if not governance_missing else f"Missing: {', '.join(governance_missing)}"})

    passed = all(bool(item["passed"]) for item in checks)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "PASS" if passed else "FAIL",
        "tests_passed": pytest_summary,
        "data_quality_score": quality,
        "checks": checks,
        "demo_boundaries": [
            "Public market data and deterministic offline fallback",
            "Synthetic operational and GTM datasets",
            "No Red Hat, customer, or confidential data",
            "Snowflake live mode optional and disabled without explicit configuration",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "docs" / "ai_assistance_log.json"
EVIDENCE_PATH = ROOT / "docs" / "AI_ASSISTED_DEVELOPMENT_EVIDENCE.md"
PLAYBOOK_PATH = ROOT / "docs" / "AI_ADOPTION_PLAYBOOK.md"


def test_ai_evidence_assets_exist():
    assert LOG_PATH.exists()
    assert EVIDENCE_PATH.exists()
    assert PLAYBOOK_PATH.exists()


def test_ai_log_is_structured_and_verifiable():
    data = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    assert data["principle"].startswith("AI proposes")
    assert len(data["records"]) >= 5
    for record in data["records"]:
        for key in [
            "id",
            "title",
            "tool",
            "problem",
            "prompt_excerpt",
            "ai_contribution",
            "human_decisions",
            "verification",
            "impact",
            "artifacts",
        ]:
            assert record.get(key), f"Missing evidence field: {key}"
        assert len(record["verification"]) >= 1
        assert len(record["artifacts"]) >= 1


def test_dependency_fix_is_reproducible():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "tabulate" in requirements


def test_cursor_and_snowflake_evidence_records_exist():
    data = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    ids = {record["id"] for record in data["records"]}
    assert {"AI-004", "AI-005"}.issubset(ids)

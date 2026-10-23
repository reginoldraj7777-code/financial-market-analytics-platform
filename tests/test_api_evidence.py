import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.investigation import (
    fit_baseline,
    precision_top_decile,
    reviews_to_recall,
    run_benchmark,
    score_values,
)


def test_math_and_input_contracts():
    center, scale = fit_baseline(np.arange(100))
    assert center == 49.5 and scale > 0
    np.testing.assert_array_equal(score_values([99, 100, 120], 100, 2), [0.5, 0, 10])
    for values in [np.ones(20), np.arange(10), [np.nan] * 20, np.ones((20, 1))]:
        with pytest.raises(ValueError):
            fit_baseline(values)
    for values, scale in [([1], 0), ([np.inf], 1), ([[1]], 1)]:
        with pytest.raises(ValueError):
            score_values(values, 0, scale)
    assert precision_top_decile([False] * 9 + [True], range(10))["precision"] == 1
    for labels, scores in [([], []), ([True], [1, 2]), ([True], [np.nan])]:
        with pytest.raises(ValueError):
            precision_top_decile(labels, scores)
    assert reviews_to_recall([False, True, True], [1, 2, 0]) == 2
    assert reviews_to_recall([False], [0]) == 0
    for ordering, recall in [([0, 0], 0.9), ([0, 1], 0)]:
        with pytest.raises(ValueError):
            reviews_to_recall([True, False], ordering, recall)


def test_benchmark_reproducibility_and_label_isolation(tmp_path):
    first = run_benchmark(tmp_path / "a", 2, 500)
    second = run_benchmark(tmp_path / "b", 2, 500)
    assert first["input_sha256"] == second["input_sha256"]
    assert first["highest_alert_decile"] == second["highest_alert_decile"]
    assert first["review_simulation"] == second["review_simulation"]
    queue = json.loads((tmp_path / "a/review_queue.json").read_text())
    assert queue and all("label" not in row for row in queue)
    assert [row["score"] for row in queue] == sorted(
        [row["score"] for row in queue], reverse=True
    )
    with pytest.raises(ValueError):
        run_benchmark(tmp_path, 0, 100)


def test_api_missing_artifacts_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("EVIDENCE_DIR", str(tmp_path))
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    for endpoint in ["/metrics", "/alerts"]:
        assert client.get(endpoint).status_code == 503
    assert client.get("/alerts?limit=101").status_code == 422
    good = {"values": [99, 100, 101, 120], "center": 100, "scale": 2}
    result = client.post("/score", json=good)
    assert result.status_code == 200
    assert result.json()["flags"] == [False, False, False, True]
    assert result.json()["scores"] == [0.5, 0, 0.5, 10]
    for changes in [
        {"values": []},
        {"scale": 0},
        {"threshold": -1},
        {"values": [1] * 10001},
        {"center": "NaN"},
    ]:
        assert client.post("/score", json={**good, **changes}).status_code == 422
    assert (
        client.post(
            "/reviews",
            json={"observation_id": 1, "decision": "confirmed", "reviewer": "test"},
        ).status_code
        == 503
    )


def test_review_history_is_append_only(tmp_path, monkeypatch):
    monkeypatch.setenv("EVIDENCE_DIR", str(tmp_path))
    monkeypatch.setenv("REVIEW_DB", str(tmp_path / "db/reviews.db"))
    (tmp_path / "metrics.json").write_text('{"synthetic":true}')
    (tmp_path / "review_queue.json").write_text('[{"observation_id":7,"score":10}]')
    client = TestClient(app)
    assert client.get("/metrics").json()["synthetic"] is True
    assert client.get("/alerts?limit=1").json()["alerts"][0]["observation_id"] == 7
    assert client.get("/reviews").json()["reviews"] == []
    payload = {
        "observation_id": 7,
        "decision": "needs_context",
        "reviewer": "test reviewer",
        "note": "Check source before deciding",
    }
    first = client.post("/reviews", json=payload)
    assert first.status_code == 201
    assert (
        client.post("/reviews", json={**payload, "decision": "confirmed"}).status_code
        == 201
    )
    history = client.get("/reviews").json()["reviews"]
    assert (
        len(history) == 2
        and history[0]["decision"] == "confirmed"
        and history[1]["decision"] == "needs_context"
    )
    assert history[0]["review_id"] > history[1]["review_id"]
    assert (
        client.post("/reviews", json={**payload, "observation_id": 99}).status_code
        == 404
    )
    assert (
        client.post("/reviews", json={**payload, "decision": "autoresolve"}).status_code
        == 422
    )
    assert client.post("/reviews", json={**payload, "reviewer": ""}).status_code == 422

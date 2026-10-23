"""Local review API. No authentication: deploy only behind an authenticated gateway."""

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, FiniteFloat

from src.investigation import score_values

app = FastAPI(title="Time-Series Investigation API", version="1.0.0")


class ScoreRequest(BaseModel):
    values: list[FiniteFloat] = Field(min_length=1, max_length=10000)
    center: FiniteFloat
    scale: FiniteFloat = Field(gt=0)
    threshold: FiniteFloat = Field(default=2.5, gt=0)


class ReviewRequest(BaseModel):
    observation_id: int = Field(ge=0)
    decision: Literal["confirmed", "dismissed", "needs_context"]
    reviewer: str = Field(min_length=1, max_length=80)
    note: str = Field(default="", max_length=1000)


def artifact(name):
    path = Path(os.environ.get("EVIDENCE_DIR", "evidence/full")) / name
    if not path.is_file():
        raise HTTPException(
            503, "Run the benchmark to create evaluation artifacts first"
        )
    return json.loads(path.read_text())


def review_path():
    return Path(os.environ.get("REVIEW_DB", "data/reviews.db"))


@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}


@app.get("/metrics")
def metrics():
    return artifact("metrics.json")


@app.get("/alerts")
def alerts(limit: int = Query(20, ge=1, le=100)):
    return {
        "source": "synthetic",
        "decision": "human review required",
        "alerts": artifact("review_queue.json")[:limit],
    }


@app.post("/score")
def score(request: ScoreRequest):
    scores = score_values(request.values, request.center, request.scale)
    return {
        "scores": scores.tolist(),
        "flags": (scores >= request.threshold).tolist(),
        "threshold": request.threshold,
        "rule": "absolute robust z-score",
        "baseline": {"center": request.center, "scale": request.scale},
    }


@app.post("/reviews", status_code=201)
def record_review(request: ReviewRequest):
    if not any(
        entry["observation_id"] == request.observation_id
        for entry in artifact("review_queue.json")
    ):
        raise HTTPException(404, "Observation is not in the review queue")
    path = review_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {**request.model_dump(), "recorded_utc": datetime.now(UTC).isoformat()}
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)"
        )
        cursor = conn.execute(
            "INSERT INTO reviews (payload) VALUES (?)", (json.dumps(event),)
        )
        event["review_id"] = cursor.lastrowid
    return event


@app.get("/reviews")
def review_history(limit: int = Query(20, ge=1, le=100)):
    path = review_path()
    if not path.exists():
        return {"reviews": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT id, payload FROM reviews ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return {
        "reviews": [{**json.loads(payload), "review_id": key} for key, payload in rows]
    }

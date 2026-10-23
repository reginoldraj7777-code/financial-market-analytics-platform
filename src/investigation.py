"""Deterministic synthetic alert benchmark with labels isolated from scoring."""

import argparse
import hashlib
import json
import platform
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def fit_baseline(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 20 or not np.isfinite(values).all():
        raise ValueError("Baseline needs at least 20 finite one-dimensional values")
    center = float(np.median(values))
    scale = float(1.4826 * np.median(np.abs(values - center)))
    if scale <= 0:
        raise ValueError("Baseline must have positive dispersion")
    return center, scale


def score_values(values, center, scale):
    values = np.asarray(values, dtype=float)
    if (
        values.ndim != 1
        or not np.isfinite(values).all()
        or not np.isfinite(center)
        or not np.isfinite(scale)
        or scale <= 0
    ):
        raise ValueError(
            "Require finite one-dimensional values and a positive finite scale"
        )
    return np.abs(values - center) / scale


def precision_top_decile(labels, scores):
    labels, scores = np.asarray(labels, dtype=bool), np.asarray(scores, dtype=float)
    if (
        labels.ndim != 1
        or labels.shape != scores.shape
        or not len(labels)
        or not np.isfinite(scores).all()
    ):
        raise ValueError("Nonempty matching arrays required")
    k = int(np.ceil(len(labels) * 0.1))
    positives = int(labels[np.argsort(-scores, kind="stable")[:k]].sum())
    return {"reviewed": k, "true_positives": positives, "precision": positives / k}


def reviews_to_recall(labels, ordering, recall=0.9):
    labels, ordering = np.asarray(labels, dtype=bool), np.asarray(ordering, dtype=int)
    if not 0 < recall <= 1 or not np.array_equal(
        np.sort(ordering), np.arange(len(labels))
    ):
        raise ValueError("Require a full index permutation and recall in (0,1]")
    target = int(np.ceil(labels.sum() * recall))
    return (
        0
        if target == 0
        else int(np.searchsorted(np.cumsum(labels[ordering]), target) + 1)
    )


def run_benchmark(output, entities=32, observations_per_entity=375000, seed=20261018):
    if entities < 1 or observations_per_entity < 100:
        raise ValueError("Require positive entities and at least 100 observations each")
    started = time.perf_counter()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    digest, candidates, summaries = hashlib.sha256(), [], []
    for entity in range(entities):
        rng = np.random.default_rng(seed + entity)
        mean, sigma = 100 + entity * 3, 2 + entity * 0.1
        center, scale = fit_baseline(rng.normal(mean, sigma, 2000))
        labels = rng.random(observations_per_entity) < 0.015
        values = rng.normal(mean, sigma, observations_per_entity)
        values += (
            labels
            * rng.choice([-1, 1], observations_per_entity)
            * rng.uniform(3, 8, observations_per_entity)
            * sigma
        )
        scores = score_values(values, center, scale)
        selected = scores >= 2.5
        steps = np.flatnonzero(selected)
        candidates.append(
            pd.DataFrame(
                {
                    "observation_id": entity * observations_per_entity + steps,
                    "entity": entity,
                    "step": steps,
                    "value": values[selected],
                    "score": scores[selected],
                    "label": labels[selected],
                }
            )
        )
        summaries.append(
            {
                "entity": entity,
                "observations": observations_per_entity,
                "training_observations": 2000,
                "positives": int(labels.sum()),
                "alerts": int(selected.sum()),
                "detected_positives": int((selected & labels).sum()),
                "center": center,
                "scale": scale,
            }
        )
        digest.update(values.astype("<f8").tobytes())
        digest.update(labels.astype("u1").tobytes())
    frame = pd.concat(candidates, ignore_index=True)
    frame.to_csv(
        output / "labeled_candidates.csv.gz",
        index=False,
        compression={"method": "gzip", "mtime": 0},
    )
    pd.DataFrame(summaries).to_csv(output / "entity_results.csv", index=False)
    labels, scores = frame.label.to_numpy(), frame.score.to_numpy()
    ranked = np.argsort(-scores, kind="stable")
    chronological = np.lexsort((frame.entity, frame.step))
    baseline_reviews = reviews_to_recall(labels, chronological)
    ranked_reviews = reviews_to_recall(labels, ranked)
    queue = frame.iloc[ranked[:100]].drop(columns="label").to_dict(orient="records")
    for entry in queue:
        entry.update(rule="absolute robust z-score >= 2.5", status="pending_review")
    (output / "review_queue.json").write_text(json.dumps(queue, indent=2) + "\n")
    metrics = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "seed": seed,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "synthetic": True,
        "entities": entities,
        "observations": entities * observations_per_entity,
        "additional_training_observations": entities * 2000,
        "input_sha256": digest.hexdigest(),
        "candidate_alerts": len(frame),
        "detector_recall": sum(x["detected_positives"] for x in summaries)
        / max(1, sum(x["positives"] for x in summaries)),
        "highest_alert_decile": precision_top_decile(labels, scores),
        "review_simulation": {
            "target_recall_among_detected_positives": 0.9,
            "chronological_reviews": baseline_reviews,
            "ranked_reviews": ranked_reviews,
            "relative_reduction": 1 - ranked_reviews / baseline_reviews
            if baseline_reviews
            else 0,
            "assumption": "Equal cost per reviewed alert; simulated queue counts, not observed analyst time.",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "scope": "Stationary Gaussian synthetic data with independently sampled large injected spikes; deliberately simple benchmark, not production precision.",
    }
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("evidence/sample"))
    args = parser.parse_args()
    print(
        json.dumps(
            run_benchmark(
                args.output,
                **(
                    {}
                    if args.full
                    else {"entities": 4, "observations_per_entity": 3000}
                ),
            ),
            indent=2,
        )
    )

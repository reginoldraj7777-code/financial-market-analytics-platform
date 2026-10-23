"""Measure real HTTP requests; validate numerical outputs as well as status codes."""

import argparse
import concurrent.futures
import hashlib
import json
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
import numpy as np
import pandas as pd


def run(url, output, requests=1500, workers=8):
    if requests < 1 or workers < 1:
        raise ValueError("Positive request and worker counts required")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    payload = {"values": [99, 100, 101, 120] * 25, "center": 100, "scale": 2}
    expected_scores, expected_flags = (
        [0.5, 0, 0.5, 10] * 25,
        [False, False, False, True] * 25,
    )
    # Explicit local benchmark: ignore ambient HTTP proxy variables.
    with httpx.Client(timeout=10, trust_env=False) as client:

        def request(index):
            started = time.perf_counter()
            try:
                response = client.post(url.rstrip("/") + "/score", json=payload)
                result = response.json()
                success = (
                    response.status_code == 200
                    and result.get("scores") == expected_scores
                    and result.get("flags") == expected_flags
                )
                status = response.status_code
            except (httpx.HTTPError, ValueError):
                success, status = False, 0
            return {
                "request": index,
                "latency_ms": (time.perf_counter() - started) * 1000,
                "status": status,
                "success": success,
            }

        for index in range(20):
            if not request(-index - 1)["success"]:
                raise RuntimeError("Warmup failed validation")
        started = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            records = list(pool.map(request, range(requests)))
        elapsed = time.perf_counter() - started
    frame = pd.DataFrame(records)
    frame.to_csv(output / "http_requests.csv", index=False)
    result = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "requests": requests,
        "concurrency": workers,
        "warmup_requests_excluded": 20,
        "values_per_request": 100,
        "success_rate": float(frame.success.mean()),
        "p50_ms": float(np.percentile(frame.latency_ms, 50)),
        "p95_ms": float(np.percentile(frame.latency_ms, 95)),
        "p99_ms": float(np.percentile(frame.latency_ms, 99)),
        "elapsed_seconds": elapsed,
        "requests_per_second": requests / elapsed,
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "api_sha256": hashlib.sha256(
            (Path(__file__).resolve().parents[1] / "src/api.py").read_bytes()
        ).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "scope": "Local HTTP /score microbenchmark; not cloud availability or a production SLA.",
    }
    (output / "http_metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not frame.success.all():
        raise RuntimeError("One or more requests failed correctness validation")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="evidence/full")
    parser.add_argument("--requests", type=int, default=1500)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    run(args.url, args.output, args.requests, args.workers)

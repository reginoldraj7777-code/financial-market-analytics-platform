"""Visualize committed measurements, keeping scope visible."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

p = Path(__file__).resolve().parents[1] / "evidence/full"
m = json.loads((p / "metrics.json").read_text())
h = json.loads((p / "http_metrics.json").read_text())
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
    }
)
fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor="#f7fafc")
fig.suptitle(
    "Time-Series Investigation • Scale, review effort & API response",
    fontsize=18,
    fontweight="bold",
    x=0.06,
    ha="left",
)
e = pd.read_csv(p / "entity_results.csv")
axes[0].bar(e.entity, e.observations / 1000, color="#087f8c")
axes[0].set(
    title="12M observations / 32 synthetic assets",
    xlabel="Asset index",
    ylabel="Observations (thousands)",
)
r = m["review_simulation"]
axes[1].bar(
    ["Chronological", "Score-ranked"],
    [r["chronological_reviews"] / 1000, r["ranked_reviews"] / 1000],
    color=["#a9b8c7", "#087f8c"],
)
axes[1].set(
    title=f"{r['relative_reduction']:.1%} fewer simulated reviews",
    ylabel="Reviews to 90% of detected positives (thousands)",
)
lat = pd.read_csv(p / "http_requests.csv").latency_ms
axes[2].hist(lat, bins=35, color="#087f8c")
axes[2].axvline(
    h["p50_ms"], color="#e07726", linewidth=2, label=f"Median {h['p50_ms']:.1f} ms"
)
axes[2].legend(frameon=False)
axes[2].set(
    title=f"{h['requests']:,} local HTTP requests",
    xlabel="Response time (ms)",
    ylabel="Requests",
)
fig.text(
    0.06,
    0.025,
    "Synthetic injected-spike benchmark. Review counts assume equal cost. Local HTTP measurements do not establish a production SLA.",
    fontsize=10,
    color="#475569",
)
fig.tight_layout(rect=(0.03, 0.08, 1, 0.92), w_pad=3)
fig.savefig(p / "evaluation.png", dpi=150)

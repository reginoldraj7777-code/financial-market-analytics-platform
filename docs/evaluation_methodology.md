# Evaluation protocol

## Data and leakage controls

32 synthetic assets, each with 2,000 independent baseline observations followed by 375,000 evaluation observations. Seed 20261018 plus asset index. Stationary normal values use distinct means/scales. Independently sampled 1.5% anomaly labels inject random-sign spikes of 3–8 baseline standard deviations. This deliberately easy fixture tests plumbing and scale, not generalizable anomaly detection.

Fit median and 1.4826 × median absolute deviation on the preceding baseline only. Scoring receives values, center and scale, never labels. Absolute robust z-score ≥ 2.5 creates a candidate alert. Ground-truth labels are used only for evaluation and are removed from the human review queue.

## Metrics and denominators

Detection recall: detected injected anomalies / all injected anomalies. Precision: true anomalies among the highest-scored ceil(10% × candidate alerts), divided by that subset size. Stable ordering resolves ties. This is the top decile of alerts, not all 12M observations.

Compare score-ranked and step-then-asset chronological queues. Count reviews until each finds ceil(90% × detected positive alerts). Relative review reduction = 1 − ranked reviews / chronological reviews. Both queues use the same candidate set and recall target. This excludes missed anomalies and assumes equal cost per review, not actual analyst time.

The full candidate CSV is regenerated locally and ignored in Git. Small per-asset results, a 100-item review queue, hashes, source digest, dependency versions and metrics are committed. Repeated runs preserve semantic metrics and input hashes; timestamps and runtimes vary.

## HTTP protocol

Run Uvicorn over real loopback HTTP. Exclude 20 warmups; send 1,500 requests with eight concurrent workers, each containing 100 values. Validate all returned scores and flags, not just HTTP 200. Include failed requests in the success denominator and latency table. Record p50/p95/p99, source digests and platform. This local test omits internet latency, authentication, database writes and multi-tenant traffic. It cannot establish a production SLA.

## Coverage and deployment

The critical scope is exactly src.api and src.investigation, with branch measurement enabled; the report includes missed lines. Original dashboard tests run in the same suite. Docker is a non-root serving image; CI defines container testing, not live production delivery. Snowflake remains optional. Reviewer identity is self-reported until authentication is added; SQLite preserves history but is not tamper-proof storage.

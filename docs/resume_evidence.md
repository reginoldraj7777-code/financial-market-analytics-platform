# Résumé evidence map

October 2026 extension. Current reproducibility is not historical production proof.

| Claim | Current evidence | Exact boundary |
|---|---|---|
| 12M+ observations, 30+ assets | 12M test observations across 32 synthetic assets, plus 64K separate training values | Scale benchmark is separate from the original four-stock dashboard |
| 90% critical-path coverage | 96.34% combined line/branch coverage for src.api + src.investigation | Not whole-repository coverage |
| 87% highest-decile precision | 100% on a simple injected-spike fixture | Different dataset/protocol; exact historical 87% is not reproduced |
| 60% review effort reduction | 44.63% fewer reviews to 90% detected-positive recall | Equal per-alert cost assumption; not measured human time; 60% unsupported |
| FastAPI + Docker + CI/CD | Scoring/review endpoints, non-root Dockerfile, build/test workflow | Deployment source and CI only; no live cloud/CD deployment established |
| <300 ms median | 14.55 ms across 1,500 real local HTTP calls, concurrency 8 | 100 values/request; warmups excluded; environment-specific |
| 99.5% request success | 100.0% correct responses in that run | Not long-term availability or production reliability |

[Raw metrics](../evidence/full/metrics.json) · [HTTP metrics](../evidence/full/http_metrics.json) · [Tests](../tests/test_api_evidence.py)

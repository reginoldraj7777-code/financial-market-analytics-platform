# AI-Assisted Development Evidence

## Purpose

This document makes the use of AI during project development transparent, verifiable, and reusable. The project follows one principle:

> **AI proposes; the human owner reviews, tests, and owns the final decision.**

The evidence is not a claim that AI built the entire project. It documents specific tasks where an AI assistant supported debugging, documentation, design thinking, and business translation.

## Evidence Model

Every record contains:

1. **Problem** — the concrete task or failure.
2. **Prompt excerpt** — what was asked of the AI assistant.
3. **AI contribution** — suggestions or structure provided by AI.
4. **Human decision** — what was accepted, rejected, or changed.
5. **Verification** — tests, reruns, and manual checks.
6. **Impact** — the resulting improvement.
7. **Artifacts** — files that prove the implemented result.

## Evidence 1 — Missing Dependency Diagnosis

### Problem

The analytics pipeline failed during Markdown report generation with:

```text
ModuleNotFoundError: No module named 'tabulate'
ImportError: Missing optional dependency 'tabulate'.
```

The traceback pointed to `DataFrame.to_markdown()`.

### AI contribution

- Identified `tabulate` as an optional pandas dependency required by `to_markdown()`.
- Recommended both an immediate installation and a durable dependency update.
- Recommended rerunning the complete pipeline to verify all downstream outputs.

### Human decision and verification

- Confirmed the traceback before changing the project.
- Added `tabulate>=0.9.0` to `requirements.txt`.
- Reran the pipeline.
- Confirmed reports, SQLite output, processed files, and the Streamlit dashboard loaded correctly.

### Result

The reporting workflow was restored and the project setup became reproducible for a new user.

## Evidence 2 — Auditable AI Use and Team Enablement

### Problem

The project used AI support, but that support was not visible or reusable.

### AI contribution

- Proposed a dedicated dashboard tab for AI-development evidence.
- Structured a repeatable evidence model.
- Produced prompt templates and a responsible-use checklist.

### Human controls

- No external AI API is required during the demo.
- No confidential information, credentials, or company data is included.
- No unsupported time-saving claims are made.
- Every accepted suggestion has a verification step and artifact reference.

### Result

The dashboard now demonstrates not only AI usage, but also how AI adoption can be governed, documented, and taught to a team.

## Evidence 3 — GTM Transferability

The demonstration uses public financial time-series data. The architecture is reusable for GTM data:

| Project concept | GTM equivalent | Business use |
|---|---|---|
| Symbol | Region, account, product, segment, sales team | Compare entities |
| Time-series metric | Pipeline, win rate, bookings, activity | Track trends |
| Event flag | KPI drop, surge, stalled pipeline | Focus investigation |
| SQL-ready output | Regional reporting tables | Repeatable analysis |
| Dashboard | Executive business view | Stakeholder decisions |

This is a conceptual mapping only. The project does not claim to use Red Hat or customer data.

## Evidence 4 — Cursor Project Governance

Cursor support is implemented as a governed repository workflow, not as an unsupported claim that an AI editor created the entire project.

- `.cursor/rules/analytics-quality.mdc` encodes persistent rules for synthetic data, privacy, Snowflake safety, analytical correctness, testing, and minimal changes.
- `AGENTS.md` defines mandatory completion checks.
- `docs/CURSOR_WORKFLOW.md` contains an interview-ready repository prompt and a human review gate.

The human owner approves the plan, reviews the diff, runs tests, validates analytics, and owns the final decision.

## Evidence 5 — Snowflake-Ready GTM Integration

The project now includes:

- deterministic synthetic GTM metrics for regions, segments, products, pipeline, bookings, win rate, activity, conversion, and review events;
- a Snowflake Python adapter with environment-based configuration;
- a safe connection-readiness view that never reveals secrets;
- a read-only in-app query runner;
- an explicitly confirmed synthetic-data upload path;
- Snowflake-native schema, view, CTE, window, `QUALIFY`, `COUNT_IF`, and `DIV0` examples.

The default interview demo remains local and reliable. A live Snowflake connection is described as optional and is never claimed unless it is actually configured and tested.

---

## AI-006 — Interview-Grade Decision Intelligence Redesign

**Problem:** The project had strong individual analytics features, but the complete experience needed one coherent stakeholder story, clearer GTM relevance, stronger reliability evidence, and a safer interview launch workflow.

**AI support:** Proposed a project-wide information architecture, deterministic decision briefs, human-context questions, read-only SQL safeguards, an adoption plan, skill-gap mapping, and a preflight workflow.

**Human decisions:** Kept all boundaries explicit, retained public/synthetic data only, rejected unsupported productivity or live-Snowflake claims, and prioritized a stable seven-minute route.

**Verification:** Core modules compiled, the full pipeline ran, the complete test suite passed, the preflight summary passed with 100/100 data quality, and all dashboard data paths executed through a local test harness.

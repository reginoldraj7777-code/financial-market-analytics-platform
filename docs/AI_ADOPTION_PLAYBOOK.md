# Practical AI Adoption Playbook for an Analytics Team

## 1. Select a Safe, Valuable Use Case

Start with repetitive, reviewable work:

- Summarizing approved documents
- Drafting SQL or Python scaffolding
- Explaining errors and proposing debugging steps
- Structuring reports and presentations
- Turning a completed workflow into onboarding material

Avoid sensitive data, credentials, confidential customer information, and decisions that require unreviewed domain authority.

## 2. Define the Human Owner

Every AI-assisted task needs one person who owns:

- The input data
- The prompt and context
- The acceptance or rejection of suggestions
- Testing and factual verification
- The final business output

## 3. Use a Structured Prompt

A strong prompt should include:

1. Business or technical objective
2. Relevant context
3. Constraints
4. Required output format
5. Verification expectations
6. Explicit instruction not to invent missing facts

## 4. Validate Before Use

### Code

- Review changed lines
- Run automated tests
- Test edge cases
- Confirm dependencies
- Check security and secrets

### Analysis

- Recalculate key metrics
- Trace claims to source data
- Separate fact from interpretation
- Avoid causal claims without evidence

### Communication

- Check audience, tone, and terminology
- Remove unsupported statements
- Keep limitations visible

## 5. Document the Evidence

For each reusable AI use case, capture:

- Problem
- Prompt template
- AI contribution
- Human changes
- Verification
- Final artifact
- Known limitations

## 6. Enable the Team

A short onboarding session can follow this structure:

1. Show one approved use case
2. Demonstrate the prompt
3. Show a weak AI response and how to improve it
4. Demonstrate human verification
5. Share the reusable template
6. Collect skill gaps and questions
7. Update the playbook after feedback

## 7. GTM Operations Examples

- Convert regional KPI tables into a first-draft stakeholder summary
- Draft SQL for repeatable regional performance reporting
- Compare document versions and identify changed assumptions
- Create presentation outlines from validated findings
- Document recurring workflows for analyst onboarding
- Surface unusual KPI changes for human investigation

The AI should accelerate preparation and discovery. The analyst remains responsible for data quality, interpretation, business context, and the final recommendation.

## Snowflake + Cursor Team Use Case

1. Store validated regional KPI tables in Snowflake.
2. Use approved read-only queries for recurring analysis.
3. Use Cursor with version-controlled project rules to explain, review, or minimally improve SQL/Python workflows.
4. Ask for a plan before edits and require explicit verification steps.
5. Review diffs, run tests, validate metrics, and document decisions.
6. Use Gemini or NotebookLM only for approved synthesis tasks after the data and calculations are validated.
7. Never include credentials, confidential data, or unsupported causal conclusions in prompts.

## 8. 30–60–90 Day Adoption Plan

### First 30 Days — Discover

- Interview analysts and observe recurring workflows.
- Map approved tools, data boundaries, and escalation routes.
- Identify low-risk, high-frequency use cases.
- Establish baseline measures for time, quality, rework, and confidence.

### Days 31–60 — Pilot

- Run onboarding sessions with synthetic or approved non-sensitive data.
- Publish bounded prompts and human-verification checklists.
- Hold office hours and capture failure examples.
- Compare output quality and rework against the baseline.

### Days 61–90 — Scale

- Standardize approved workflows and reusable templates.
- Create champions and escalation paths.
- Add governance reviews and periodic refresh sessions.
- Report measured outcomes, limitations, and next candidate use cases.

## 9. Skill-Gap Assessment

Assess proficiency through observable evidence rather than self-ratings:

- Can the analyst create a bounded prompt with constraints and checks?
- Can the analyst trace every claim to an approved source?
- Can the analyst review a Cursor plan and diff before accepting changes?
- Can the analyst validate Snowflake SQL scope, windows, filters, and assumptions?
- Can the analyst translate validated findings into a decision-ready brief?

## 10. Measurement Framework

Measure adoption responsibly:

- Usage: active users and approved workflows used
- Quality: factual accuracy, review corrections, and rejected outputs
- Efficiency: baseline versus pilot preparation time
- Rework: number and type of human corrections
- Confidence: analyst ability to explain limitations and validation
- Business value: stakeholder usefulness and actionability

Never report hypothetical capacity scenarios as measured productivity gains.

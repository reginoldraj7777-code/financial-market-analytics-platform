# Recording Review and Final Demo Notes

## What was corrected after reviewing the full dashboard recording

- Shortened the eight tab labels so the navigation remains readable during screen sharing.
- Replaced broad “risk” wording with **attention score / review flag** wording to avoid implying prediction, causality, or financial advice.
- Fixed the truncated trend metric by using compact Upward / Downward / Neutral labels.
- Replaced the absolute-looking 100/100 headline with **5/5 implemented quality gates**, while retaining the weighted score in the reliability appendix.
- Removed a duplicated GTM mapping row.
- Added a concise portfolio implementation-scope section so personal ownership is immediately clear.
- Simplified the entity benchmark to the six columns that matter for discussion.
- Added severity/entity filters and a bounded review queue instead of a long event dropdown.
- Reframed low-priority alerts so they do not contradict the severity label.
- Reworked Snowflake status cards to communicate implemented assets and honest demo boundaries rather than showing an unfinished-looking “not configured” state.
- Wrapped long AI / Cursor prompts so they remain readable on screen.
- Moved hashes, downloads, detailed risk matrices, skill matrices, and hypothetical capacity calculations into an optional appendix.
- Hid write controls unless advanced mode is enabled or a live Snowflake connection is genuinely ready.
- Set the app to open with the sidebar collapsed for a cleaner first impression.

## Recommended 7–8 minute route

1. **Overview — 60 seconds**
   Explain the problem, quality gates, attention score boundary, implementation scope, and reusable architecture.
2. **Trends — 75 seconds**
   Show one chart, one comparison mode, and the transparent attention-score components.
3. **Investigation — 75 seconds**
   Filter the queue, open one event, and show observed facts plus human questions.
4. **AI Evidence — 90 seconds**
   Open one verified record: problem → bounded prompt → AI contribution → human decision → verification.
5. **GTM Studio — 2–3 minutes**
   Show synthetic regional KPIs, the analyst brief, one AI use case, and the Snowflake + Cursor operating model.

Use SQL, Reliability, and Operations only when the interviewer asks for more depth.

## Screen-share hygiene

- Close Gmail, YouTube, LinkedIn, and unrelated browser tabs before joining.
- Share only the browser tab or application window, not the entire desktop.
- Keep browser zoom at 90–100% and use full-screen mode if comfortable.
- Start the app at least 15 minutes before the interview.
- Keep the dashboard on Tab 1 and the project folder / Cursor ready in the background.
- Do not scroll through every section. Stop after each key point and invite a question.

## Claims to keep precise

- Say **Snowflake-ready design**, not live Snowflake deployment.
- Say **synthetic GTM demonstration**, not Red Hat or customer analysis.
- Say AI accelerated diagnosis, review, and documentation; you retained ownership of architecture, validation, and final output.
- Say 18 automated checks cover implemented project behaviours and assets, not production-grade test coverage.

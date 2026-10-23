# Windows launchers

These scripts locate the repository root relative to their own folder. Double-click a launcher or invoke it from the root with `scripts\windows\<filename>`.

| Script | Action |
|---|---|
| [RUN_INTERVIEW_DEMO_WINDOWS.bat](RUN_INTERVIEW_DEMO_WINDOWS.bat) | Install dependencies, build offline outputs, run preflight and start Streamlit |
| [RUN_DASHBOARD_WINDOWS.bat](RUN_DASHBOARD_WINDOWS.bat) | Start the dashboard workflow |
| [PREFLIGHT_CHECK_WINDOWS.bat](PREFLIGHT_CHECK_WINDOWS.bat) | Run the preflight workflow |
| [RUN_TESTS_WINDOWS.bat](RUN_TESTS_WINDOWS.bat) | Install development dependencies and run pytest |
| [CHECK_SNOWFLAKE_READINESS_WINDOWS.bat](CHECK_SNOWFLAKE_READINESS_WINDOWS.bat) | Inspect optional Snowflake readiness |

Python must be installed. Live Snowflake use requires your own configuration. The launchers were relocated with their root-directory handling updated; Windows execution is not part of the Linux CI checks.

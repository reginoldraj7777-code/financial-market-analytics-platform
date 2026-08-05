@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Please run RUN_DASHBOARD_WINDOWS.bat first to create the project environment.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python -c "from src.snowflake_adapter import connection_readiness, safe_connection_summary; r=connection_readiness(); print('Connector installed:', r.connector_installed); print('Required fields present:', r.required_fields_present); print('Authentication configured:', r.authentication_configured); print('Live ready:', r.live_ready); print('Missing fields:', ', '.join(r.missing_fields) or 'None'); print('Safe configuration:', safe_connection_summary())"
pause

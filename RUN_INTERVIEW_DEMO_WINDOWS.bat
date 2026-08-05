@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Time-Series Analytics and AI Adoption Platform - Preflight
echo ============================================================

if not exist ".venv\Scripts\python.exe" (
    echo [1/6] Creating Python 3.12 environment...
    py -3.12 -m venv .venv 2>nul
    if errorlevel 1 python -m venv .venv
) else (
    echo [1/6] Existing virtual environment found.
)

call ".venv\Scripts\activate.bat"

echo [2/6] Installing runtime and verification packages...
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
if errorlevel 1 goto :fail

echo [3/6] Running the complete analytics pipeline...
python src\main.py --offline
if errorlevel 1 goto :fail

echo [4/6] Running tests and preflight checks...
python src\preflight.py
if errorlevel 1 goto :fail

echo [5/6] Preflight passed.
echo [6/6] Starting the interview dashboard...
echo Recommended route: Tabs 1, 2, 3, 7, and 8. Use Tabs 4-6 only for questions.
python -m streamlit run app.py --browser.gatherUsageStats false
exit /b 0

:fail
echo.
echo PRE-FLIGHT FAILED. Review the message above before the interview.
pause
exit /b 1

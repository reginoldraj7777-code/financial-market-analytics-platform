@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv 2>nul
    if errorlevel 1 python -m venv .venv
)
call ".venv\Scripts\activate.bat"
python -m pip install -r requirements-dev.txt
python -m pytest -q
pause

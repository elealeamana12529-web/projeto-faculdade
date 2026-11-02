@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py app.py --demo
) else (
    python app.py --demo
)
if errorlevel 1 pause

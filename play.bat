@echo off
rem Double-click to play Geometry Pokemon Dash. Needs Python 3 and pygame
rem (pip install -r requirements.txt).
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 main.py
) else (
    python main.py
)

if errorlevel 1 (
    echo.
    echo The game could not start. Check that Python 3 is installed and run:
    echo     pip install -r requirements.txt
    pause
)

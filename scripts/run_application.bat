@echo off
setlocal

REM Navigate to project root
cd /d "%~dp0\.."
set "PROJECT_ROOT=%CD%"

echo ============================================================
echo French Vocab Optimizer v2.0 - Web Interface
echo ============================================================
echo.

REM Check if credentials file exists
if not exist credentials.json (
    echo WARNING: credentials.json not found in %PROJECT_ROOT%
    echo.
    echo You need Google API credentials to use this tool:
    echo   1. Go to: https://console.cloud.google.com/
    echo   2. Enable Google Sheets API
    echo   3. Create OAuth credentials
    echo   4. Download as credentials.json
    echo   5. Place in: %PROJECT_ROOT%
    echo.
    echo Press any key to continue anyway (will fail when accessing sheets)...
    pause
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo Please run: scripts\setup.bat
    echo.
    pause
    exit /b 1
)

REM Verify core dependencies
echo Verifying dependencies...
python -c "import flask, spacy, gspread" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Required packages not installed!
    echo Please run: scripts\setup.bat
    echo.
    pause
    exit /b 1
)

REM Verify core modules exist
python -c "from core.config import OptimizerConfig" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Core modules not found!
    echo Please ensure you have the complete v2.0 installation.
    echo.
    pause
    exit /b 1
)

echo All checks passed!
echo.
echo ============================================================
echo Starting Flask Web Server (v2.0 Enhanced Edition)
echo ============================================================
echo.
echo   URL: http://localhost:5000
echo.
echo   Features:
echo     ✓ Drag-and-drop file upload
echo     ✓ Real-time progress tracking
echo     ✓ 3 optimization algorithms
echo     ✓ Beautiful Tailwind CSS UI
echo.
echo   Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start Flask application from web_interface directory
cd web_interface
python app.py

endlocal
pause
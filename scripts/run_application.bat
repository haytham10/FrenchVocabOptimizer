@echo off
echo ============================================================
echo French Vocabulary Sentence Optimizer - Web Interface
echo ============================================================
echo.

REM Check if credentials file exists
if not exist credentials.json (
    echo WARNING: credentials.json not found!
    echo Please place your Google API credentials in this folder
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Flask not installed. Please run setup.bat first
    pause
    exit /b 1
)

echo Starting web server...
echo.
echo Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start Flask application
cd web_interface
python app.py

pause
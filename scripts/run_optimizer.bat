@echo off
setlocal

REM Navigate to project root
cd /d "%~dp0\.."
set "PROJECT_ROOT=%CD%"

echo ============================================================
echo French Vocab Optimizer v2.0 - Command Line Interface
echo ============================================================
echo.

REM Check if credentials file exists
if not exist credentials.json (
    echo WARNING: credentials.json not found in %PROJECT_ROOT%
    echo Google Sheets export will not work without credentials.
    echo.
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: scripts\setup.bat
    pause
    exit /b 1
)

REM Check for command line arguments
if "%~1"=="" (
    echo Usage: run_optimizer.bat [OPTIONS]
    echo.
    echo For CLI usage, use Python directly:
    echo.
    echo   Example:
    echo   python -c "from core.optimizer import EnhancedSentenceOptimizer; ..."
    echo.
    echo Recommended: Use the Web Interface instead
    echo   scripts\run_application.bat
    echo.
    echo For detailed CLI examples, see:
    echo   docs\README_NEW.md
    echo.
    echo v2.0 Features:
    echo   ✓ 3 algorithms: greedy, weighted_greedy, beam_search
    echo   ✓ 10x performance with smart caching
    echo   ✓ Rich 5-tab Google Sheets export
    echo.
    pause
    exit /b 0
)

REM Legacy command-line support (v1.0 compatibility)
echo Running optimizer (legacy mode)...
echo Note: For v2.0 features, use Python directly or web interface
echo.

REM Run optimizer with provided arguments
python optimizer.py %*

echo.
echo ============================================================
echo Processing complete!
echo ============================================================
echo.
echo To use v2.0 enhanced features:
echo   1. Use web interface: scripts\run_application.bat
echo   2. Or use Python: see docs\README_NEW.md for examples
echo.
pause
endlocal
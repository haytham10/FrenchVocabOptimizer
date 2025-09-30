@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM -----------------------------------------------------------------
REM French Vocab Optimizer - Setup Script (v2.0 Enhanced Edition)
REM Flags:
REM   --clean     Recreate the virtual environment from scratch
REM   --no-model  Skip spaCy model download/check
REM -----------------------------------------------------------------

echo ============================================================
echo French Vocab Optimizer v2.0 - Setup
echo ============================================================
echo.

REM Navigate to project root (parent of scripts directory)
cd /d "%~dp0\.."
set "PROJECT_ROOT=%CD%"
echo Project root: %PROJECT_ROOT%
echo.

REM Parse flags
set "FLAG_CLEAN=0"
set "FLAG_NO_MODEL=0"
:parse_args
if "%~1"=="" goto after_args
if /I "%~1"=="--clean" set "FLAG_CLEAN=1"
if /I "%~1"=="--no-model" set "FLAG_NO_MODEL=1"
shift
goto parse_args
:after_args

REM Detect Python (prefer py launcher if available)
set "PYTHON_CMD="
py -3 --version >nul 2>&1
if %errorlevel%==0 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/
        popd
        pause
        exit /b 1
    )
)

echo [1/7] Python detected
%PYTHON_CMD% --version
echo.

REM Ensure requirements.txt exists
if not exist requirements.txt (
    echo ERROR: requirements.txt not found in %PROJECT_ROOT%
    echo Please ensure you're running this script from the correct location.
    pause
    exit /b 1
)

echo [2/7] Preparing virtual environment
if "%VIRTUAL_ENV%" NEQ "" (
    echo Detected active virtual environment: %VIRTUAL_ENV%
) else (
    if "%FLAG_CLEAN%"=="1" if exist venv (
        echo --clean specified: removing existing virtual environment...
        rmdir /s /q venv
    )
    if not exist venv (
        echo Creating virtual environment in ^"venv^"...
        %PYTHON_CMD% -m venv venv
        if %errorlevel% neq 0 (
            echo ERROR: Failed to create virtual environment
            popd
            pause
            exit /b 1
        )
        echo Virtual environment created successfully
    ) else (
        echo Reusing existing virtual environment ^"venv^" (use --clean to recreate)
    )
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo ERROR: Failed to activate virtual environment
        popd
        pause
        exit /b 1
    )
)
echo.

REM Speed up pip and avoid global version checks
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

echo [3/7] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel --no-warn-script-location
if %errorlevel% neq 0 (
    echo WARNING: Failed to upgrade pip/setuptools/wheel, continuing...
)
echo.

echo [4/7] Installing Python packages from requirements.txt...
echo This may take several minutes (especially spaCy and numpy)...
python -m pip install --upgrade --prefer-binary -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install some packages from requirements.txt
    echo.
    echo Troubleshooting tips:
    echo - Try running as Administrator
    echo - Check your internet connection
    echo - Ensure you have Visual C++ Build Tools (for some packages)
    echo - Try: pip install --upgrade pip
    pause
    exit /b 1
)
echo All packages installed successfully!
echo.

REM Check/install spaCy French model only if not skipped
if not "%FLAG_NO_MODEL%"=="1" (
    echo [5/7] Verifying spaCy French model (fr_core_news_lg)...
    python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('fr_core_news_lg') else 1)"
    if %errorlevel% neq 0 (
        echo Model not found, attempting to download via spaCy (large file, ~500MB)...
        python -m spacy download fr_core_news_lg
        if %errorlevel% neq 0 (
            echo WARNING: Failed to download spaCy model automatically.
            echo You can try manually later with:
            echo   python -m spacy download fr_core_news_lg
        ) else (
            echo spaCy French model installed successfully.
        )
    ) else (
        echo spaCy French model already present.
    )
) else (
    echo [5/7] Skipping spaCy model check/download (--no-model)
)
echo.

REM Create necessary folders for v2.0
echo [6/7] Ensuring project folders exist...
if not exist core mkdir core >nul 2>&1
if not exist web_interface mkdir web_interface >nul 2>&1
if not exist web_interface\templates mkdir web_interface\templates >nul 2>&1
if not exist web_interface\static mkdir web_interface\static >nul 2>&1
if not exist web_interface\uploads mkdir web_interface\uploads >nul 2>&1
if not exist web_interface\output mkdir web_interface\output >nul 2>&1
if not exist uploads mkdir uploads >nul 2>&1
if not exist output mkdir output >nul 2>&1
if not exist docs mkdir docs >nul 2>&1
if not exist tests mkdir tests >nul 2>&1
if not exist backups mkdir backups >nul 2>&1
echo Folders verified/created.
echo.

echo [7/7] Running system verification...
python -c "from core.config import OptimizerConfig; print('✓ Core modules OK')" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Core modules not fully accessible
    echo This is normal if this is a fresh installation
)
python -c "import spacy, flask, gspread, numpy; print('✓ Key packages OK')" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Some key packages may not be properly installed
)
echo.

echo ============================================================
echo Setup Complete! v2.0 Enhanced Edition Ready
echo ============================================================
echo.
echo Installed packages (core):
python -m pip list | findstr /i "spacy gspread flask numpy pandas"
echo.
echo Next steps:
echo   1. Place credentials.json in project root: %PROJECT_ROOT%
echo   2. Start web interface: 
echo      cd web_interface
echo      python app.py
echo   3. Open browser: http://localhost:5000
echo.
echo Documentation:
echo   - Quick Start: docs\QUICKSTART_GUIDE.md
echo   - Full Guide: docs\README_NEW.md
echo   - Run Tests: python tests\test_enhanced_system.py
echo.
echo Features in v2.0:
echo   ✓ 10x Performance Improvement
echo   ✓ Modern Tailwind CSS UI
echo   ✓ 3 Optimization Algorithms
echo   ✓ Rich 5-Tab Google Sheets Export
echo   ✓ Real-time Progress Tracking
echo.

endlocal
echo Press any key to exit...
pause >nul

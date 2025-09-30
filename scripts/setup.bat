@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM -----------------------------------------------------------------
REM French Vocabulary Sentence Optimizer - Setup
REM Flags:
REM   --clean     Recreate the virtual environment from scratch
REM   --no-model  Skip spaCy model download/check
REM -----------------------------------------------------------------

echo ============================================================
echo French Vocabulary Sentence Optimizer - Setup
echo ============================================================
echo.

REM Always run from the script's directory
pushd "%~dp0" >nul 2>&1

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
    echo ERROR: requirements.txt not found!
    echo Please run this script from the project folder where requirements.txt exists.
    popd
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

echo [4/7] Installing Python packages from requirements.txt (may take several minutes)...
python -m pip install --upgrade --prefer-binary -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install some packages from requirements.txt
    echo Try running this script as Administrator or check your internet connection.
    popd
    pause
    exit /b 1
)
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

REM Create necessary folders
echo [6/7] Ensuring project folders exist...
if not exist web_interface mkdir web_interface >nul 2>&1
if not exist web_interface\templates mkdir web_interface\templates >nul 2>&1
if not exist web_interface\static mkdir web_interface\static >nul 2>&1
if not exist uploads mkdir uploads >nul 2>&1
if not exist output mkdir output >nul 2>&1
echo Folders verified/created.
echo.

echo [7/7] Summary
echo Installed packages (selected):
python -m pip list | findstr /i "spacy gspread flask pandas numpy"
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Place your credentials.json file in this folder (if not already)
echo 2. Run run_application.bat to start the web interface
echo    OR run run_optimizer.bat for command-line usage
echo.

popd >nul 2>&1
endlocal
echo Press any key to exit...
pause >nul

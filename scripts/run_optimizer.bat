@echo off
echo ============================================================
echo French Vocabulary Sentence Optimizer - Command Line
echo ============================================================
echo.

REM Check if credentials file exists
if not exist credentials.json (
    echo WARNING: credentials.json not found!
    echo Please place your Google API credentials in this folder
    echo.
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Check for command line arguments
if "%~1"=="" (
    echo Usage: run_optimizer.bat --words SHEET_URL --sentences FILE_PATH [--max 600]
    echo.
    echo Example:
    echo run_optimizer.bat --words "https://docs.google.com/spreadsheets/d/..." --sentences sentences.csv --max 600
    echo.
    echo Arguments:
    echo   --words      : Google Sheets URL or CSV file with 2000 word list
    echo   --sentences  : CSV or TXT file with sentences
    echo   --max        : Maximum sentences to select (default: 600)
    echo   --output     : Output folder for CSV backups (default: output)
    echo.
    pause
    exit /b 0
)

REM Run optimizer with provided arguments
python optimizer.py %*

echo.
echo ============================================================
echo Processing complete!
echo ============================================================
pause
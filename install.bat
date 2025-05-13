@echo off
REM Install script for YouTube Downloader on Windows

echo Installing YouTube Downloader...

REM Check Python version
python --version > NUL 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.7 or higher.
    echo Visit: https://www.python.org/downloads/
    exit /b 1
)

REM Create virtual environment if not already in one
if "%VIRTUAL_ENV%"=="" (
    echo Creating virtual environment...
    python -m venv venv
    
    REM Activate virtual environment
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    ) else (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create logs directory
if not exist logs mkdir logs

echo.
echo Installation complete!
echo Run the GUI version with: python youtube_downloader.py
echo Run the CLI version with: python youtube_downloader_bot.py "https://youtube.com/watch?v=VIDEO_ID"
echo.
pause
@echo off
echo Installing AI Vision Text API...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt

REM Copy config file
if not exist "config\config.py" (
    echo Creating config file...
    copy "config\config_example.py" "config\config.py"
    echo Please edit config\config.py with your settings
)

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Edit config\config.py with your API keys and model preferences
echo 2. Install and start LM Studio with your vision model
echo 3. Run: python src\app.py
echo.
pause
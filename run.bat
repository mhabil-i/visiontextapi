@echo off
echo Starting AI Vision Text API...

REM Check if config exists
if not exist "config\config.py" (
    echo ERROR: config\config.py not found
    echo Please copy config_example.py to config.py and configure it
    pause
    exit /b 1
)

REM Start the server
python src\app.py

pause
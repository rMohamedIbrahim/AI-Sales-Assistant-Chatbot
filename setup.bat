@echo off
echo ===============================================
echo  Two-Wheeler Sales VoiceBot - Windows Setup
echo ===============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python is installed
echo.

:: Run the setup script
echo Running setup script...
python setup.py

echo.
echo Setup completed!
echo.
echo To start the application:
echo 1. Update .env file with your Gmail credentials
echo 2. Run: uvicorn src.main:app --reload
echo 3. Open: http://localhost:8000/docs
echo.
pause

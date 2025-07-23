@echo off
echo ===============================================
echo  VoiceBot - Simple Windows Installation
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

:: Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

:: Clear pip cache to avoid conflicts
echo Clearing pip cache...
python -m pip cache purge

echo.
echo Installing core packages one by one...
echo.

:: Install packages individually to avoid conflicts
python -m pip install fastapi==0.104.1
python -m pip install uvicorn==0.24.0
python -m pip install python-multipart==0.0.6
python -m pip install python-dotenv==1.0.0
python -m pip install pydantic==2.5.0
python -m pip install pydantic-settings==2.1.0

echo.
echo Installing database packages...
python -m pip install aiosqlite==0.19.0
python -m pip install sqlalchemy==2.0.23

echo.
echo Installing speech packages...
python -m pip install SpeechRecognition==3.10.0
python -m pip install gTTS==2.4.0
python -m pip install pyttsx3==2.90

echo.
echo Installing utility packages...
python -m pip install langdetect==1.0.9
python -m pip install vaderSentiment==3.3.2
python -m pip install httpx==0.25.2
python -m pip install aiofiles==23.2.1
python -m pip install aiosmtplib==3.0.1
python -m pip install diskcache==5.6.3
python -m pip install prometheus-client==0.19.0

echo.
echo Creating necessary directories...
if not exist "data" mkdir data
if not exist "data\audio" mkdir data\audio
if not exist "logs" mkdir logs
if not exist "data\.cache" mkdir data\.cache

echo.
echo ===============================================
echo Installation completed!
echo ===============================================
echo.
echo Next steps:
echo 1. Update .env file with your Gmail credentials
echo 2. Run: python test_setup.py
echo 3. Start the app: uvicorn src.main:app --reload
echo 4. Open: http://localhost:8000/docs
echo.
echo Note: If you get audio errors, pyaudio may need manual installation
echo Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
echo.
pause

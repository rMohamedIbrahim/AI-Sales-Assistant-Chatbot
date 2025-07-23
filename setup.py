#!/usr/bin/env python3
"""
Setup script for Two-Wheeler Sales VoiceBot
This script will help you set up the project with all required dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("="*60)
    print("🎤 Two-Wheeler Sales VoiceBot Setup")
    print("="*60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/audio", 
        "logs",
        "data/.cache"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def setup_environment():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    print("\n⚙️ Creating .env file...")
    
    env_content = """# API Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000
API_VERSION=v1

# Security
SECRET_KEY=your_secure_secret_key_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=["*"]

# Database Configuration (SQLite - Free)
DB_TYPE=sqlite
DB_PATH=./data/voicebot.db

# Speech Configuration (Free APIs)
ENABLE_WEBSPEECH=true
DEFAULT_LANGUAGE=en-IN
SPEECH_TIMEOUT=10

# Cache Configuration (Filesystem - Free)
CACHE_TYPE=filesystem
CACHE_DIR=./data/.cache

# Performance Settings
MAX_CONCURRENT_CALLS=50
RESPONSE_TIMEOUT=3.0
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=3600

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO

# Email Configuration (Free SMTP - Gmail)
# Update these with your Gmail credentials
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
ENABLE_EMAIL_NOTIFICATIONS=false

# Storage Paths
DATA_DIR=./data
LOGS_DIR=./logs
AUDIO_STORAGE=./data/audio

# Free TTS Configuration
TTS_SERVICE=gtts
TTS_LANGUAGE_FALLBACK=en

# Supported Languages (Free)
SUPPORTED_LANGUAGES=["en-IN","hi-IN","ta-IN","te-IN","mr-IN","gu-IN","bn-IN"]
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("⚠️  Please update SMTP_USERNAME and SMTP_PASSWORD in .env for email notifications")

def install_audio_dependencies():
    """Install system audio dependencies"""
    system = platform.system().lower()
    
    print(f"\n🔊 Setting up audio dependencies for {system}...")
    
    if system == "linux":
        print("For Linux, you may need to install:")
        print("  sudo apt-get install portaudio19-dev python3-pyaudio")
        print("  sudo apt-get install espeak espeak-data libespeak1 libespeak-dev")
    elif system == "darwin":  # macOS
        print("For macOS, you may need to install:")
        print("  brew install portaudio")
    elif system == "windows":
        print("For Windows, pyaudio should install automatically")
        print("If it fails, download the wheel from:")
        print("  https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    
    print("✅ Audio dependencies info provided")

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import fastapi
        import uvicorn
        import sqlalchemy
        import speech_recognition
        import gtts
        import pyttsx3
        print("✅ All main dependencies imported successfully")
        
        # Test basic functionality
        import sqlite3
        conn = sqlite3.connect(":memory:")
        conn.close()
        print("✅ SQLite working")
        
        # Test TTS engine
        import pyttsx3
        engine = pyttsx3.init()
        engine.stop()
        print("✅ TTS engine initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Update .env file with your Gmail credentials (see FREE_API_SETUP_GUIDE.md)")
    print("2. Run the application: uvicorn src.main:app --reload")
    print("3. Open browser: http://localhost:8000/docs")
    print("4. Test the voice endpoints")
    print("\n📚 Documentation:")
    print("- API Setup Guide: FREE_API_SETUP_GUIDE.md")
    print("- API Documentation: http://localhost:8000/docs (after starting)")
    print("- Project README: README.md")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    check_python_version()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Audio dependencies info
    install_audio_dependencies()
    
    # Test installation
    if test_installation():
        show_next_steps()
    else:
        print("\n⚠️  Setup completed with warnings. Check error messages above.")

if __name__ == "__main__":
    main()

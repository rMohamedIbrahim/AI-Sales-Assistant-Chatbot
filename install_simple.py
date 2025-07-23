#!/usr/bin/env python3
"""
Simple dependency installer for VoiceBot
This script installs dependencies one by one to avoid conflicts
"""

import subprocess
import sys
import os

def install_package(package_name, description=""):
    """Install a single package"""
    print(f"📦 Installing {package_name}...")
    if description:
        print(f"   {description}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            package_name, "--no-deps", "--force-reinstall"
        ])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def install_with_deps(package_name, description=""):
    """Install a package with its dependencies"""
    print(f"📦 Installing {package_name} with dependencies...")
    if description:
        print(f"   {description}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    print("="*60)
    print("🚀 VoiceBot Simple Installer")
    print("="*60)
    print()
    
    # Core packages (install with dependencies)
    core_packages = [
        ("fastapi==0.104.1", "Web framework"),
        ("uvicorn==0.24.0", "ASGI server"),
        ("python-multipart==0.0.6", "File upload support"),
        ("python-dotenv==1.0.0", "Environment variables"),
        ("pydantic==2.5.0", "Data validation"),
        ("pydantic-settings==2.1.0", "Settings management"),
    ]
    
    print("🔧 Installing core web framework...")
    for package, desc in core_packages:
        if not install_with_deps(package, desc):
            print(f"⚠️  Warning: Failed to install {package}")
    
    # Database packages
    db_packages = [
        ("aiosqlite==0.19.0", "Async SQLite"),
        ("sqlalchemy==2.0.23", "Database ORM"),
    ]
    
    print("\n🗄️  Installing database packages...")
    for package, desc in db_packages:
        if not install_with_deps(package, desc):
            print(f"⚠️  Warning: Failed to install {package}")
    
    # Speech packages (may have system dependencies)
    speech_packages = [
        ("SpeechRecognition==3.10.0", "Speech recognition"),
        ("gTTS==2.4.0", "Google Text-to-Speech"),
        ("pyttsx3==2.90", "Offline TTS"),
    ]
    
    print("\n🎤 Installing speech packages...")
    for package, desc in speech_packages:
        if not install_with_deps(package, desc):
            print(f"⚠️  Warning: Failed to install {package}")
    
    # Utility packages
    util_packages = [
        ("langdetect==1.0.9", "Language detection"),
        ("vaderSentiment==3.3.2", "Sentiment analysis"),
        ("httpx==0.25.2", "HTTP client"),
        ("aiofiles==23.2.1", "Async file operations"),
        ("aiosmtplib==3.0.1", "Email support"),
        ("diskcache==5.6.3", "Disk caching"),
        ("prometheus-client==0.19.0", "Metrics"),
    ]
    
    print("\n🔧 Installing utility packages...")
    for package, desc in util_packages:
        if not install_with_deps(package, desc):
            print(f"⚠️  Warning: Failed to install {package}")
    
    print("\n" + "="*60)
    print("✅ Installation completed!")
    print()
    print("📝 Notes:")
    print("- If pyaudio failed to install, the speech recognition may not work")
    print("- You can install pyaudio manually if needed:")
    print("  pip install pyaudio")
    print("- Or download wheels from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    print()
    print("🎯 Next steps:")
    print("1. Update .env file with your credentials")
    print("2. Run: python test_setup.py")
    print("3. Start: uvicorn src.main:app --reload")
    print("="*60)

if __name__ == "__main__":
    main()

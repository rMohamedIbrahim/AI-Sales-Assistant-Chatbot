"""
Quick Fix for MySQL-python Installation Error
This script bypasses the problematic dependencies and installs only what we need.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print the result"""
    print(f"🔧 {description}...")
    try:
        subprocess.check_call(cmd, shell=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("=" * 50)
    print("🛠️  VoiceBot Quick Fix Installer")
    print("=" * 50)
    print()
    print("This will install only the essential packages")
    print("without problematic dependencies like MySQL-python")
    print()
    
    # Clean pip cache first
    print("🧹 Cleaning pip cache...")
    run_command(f"{sys.executable} -m pip cache purge", "Clearing cache")
    
    # Upgrade pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install packages one by one
    packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "aiosqlite==0.19.0",
        "sqlalchemy==2.0.23",
        "SpeechRecognition==3.10.0",
        "gTTS==2.4.0",
        "pyttsx3==2.90",
        "langdetect==1.0.9",
        "vaderSentiment==3.3.2",
        "httpx==0.25.2",
        "aiofiles==23.2.1",
        "prometheus-client==0.19.0"
    ]
    
    print("\n📦 Installing essential packages...")
    failed_packages = []
    
    for package in packages:
        print(f"\n   Installing {package}...")
        if not run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}"):
            failed_packages.append(package)
    
    # Create directories
    print("\n📁 Creating directories...")
    dirs = ["data", "data/audio", "logs", "data/.cache"]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Summary
    print("\n" + "=" * 50)
    if failed_packages:
        print(f"⚠️  Some packages failed to install: {failed_packages}")
        print("You can try installing them manually later")
    else:
        print("🎉 All essential packages installed successfully!")
    
    print("\n🚀 Next steps:")
    print("1. Update .env with your Gmail credentials")
    print("2. Test: python test_setup.py")
    print("3. Start: uvicorn src.main:app --reload")
    print("4. Visit: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    main()

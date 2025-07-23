"""
Test script to verify all components are working correctly.
Run this after setup to ensure everything is configured properly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_database():
    """Test database connection"""
    print("🗄️  Testing database connection...")
    try:
        from src.infrastructure.database import db_service
        await db_service.connect()
        print("✅ Database connection successful")
        await db_service.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_speech_service():
    """Test speech service"""
    print("🎤 Testing speech service...")
    try:
        from src.services.speech_service import speech_service
        
        # Test TTS
        test_text = "Hello, this is a test"
        audio_data = await speech_service.text_to_speech(test_text, use_online=False)
        print("✅ Text-to-speech working (offline)")
        
        # Test language support
        languages = speech_service.get_supported_languages()
        print(f"✅ Supported languages: {len(languages)}")
        
        return True
    except Exception as e:
        print(f"❌ Speech service test failed: {e}")
        return False

async def test_voice_service():
    """Test voice service"""
    print("🔊 Testing voice service...")
    try:
        from src.services.voice_service import voice_service
        
        # Test health check
        health = await voice_service.health_check()
        print(f"✅ Voice service health: {health}")
        
        return True
    except Exception as e:
        print(f"❌ Voice service test failed: {e}")
        return False

async def test_notification_service():
    """Test notification service"""
    print("📧 Testing notification service...")
    try:
        from src.services.notification_service import notification_service
        print("✅ Notification service loaded")
        return True
    except Exception as e:
        print(f"❌ Notification service test failed: {e}")
        return False

async def test_api_routes():
    """Test API routes can be imported"""
    print("🌐 Testing API routes...")
    try:
        from src.api import voice_routes, booking_routes, service_routes
        print("✅ All API routes imported successfully")
        return True
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("="*50)
    print("🧪 VoiceBot System Tests")
    print("="*50)
    
    tests = [
        test_database,
        test_speech_service,
        test_voice_service,
        test_notification_service,
        test_api_routes
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("="*50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready.")
        print("\n🚀 To start the application:")
        print("   uvicorn src.main:app --reload")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("💡 Try running: python setup.py")
    
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())

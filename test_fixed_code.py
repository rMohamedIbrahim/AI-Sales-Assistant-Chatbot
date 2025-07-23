"""
Test script to verify the fixed code works properly
"""
import asyncio
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_imports():
    """Test that all imports work"""
    try:
        print("Testing imports...")
        
        # Test main application
        from src.main import app
        print("✓ Main application imports successfully")
        
        # Test speech service
        from src.services.speech_service import FreeSpeechService
        speech_service = FreeSpeechService()
        print(f"✓ Speech service initialized (Speech available: {speech_service.speech_available})")
        
        # Test database
        from src.infrastructure.database import DatabaseService
        db_service = DatabaseService()
        health = await db_service.health_check()
        print(f"✓ Database service health check: {health}")
        
        # Test configuration
        from src.core.config import get_settings
        settings = get_settings()
        print(f"✓ Settings loaded successfully")
        
        print("\n🎉 All components imported and initialized successfully!")
        print("\nTo start the server, run:")
        print("uvicorn src.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_imports())

"""
Core configuration settings for the VoiceBot system.
Handles all environment variables and system-wide settings.
"""
from functools import lru_cache
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Two-Wheeler Sales VoiceBot"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database Configuration
    DB_TYPE: str = "sqlite"
    DB_PATH: str = "./data/voicebot.db"
    
    # Cache Configuration
    CACHE_TYPE: str = "filesystem"
    CACHE_DIR: str = "./data/.cache"

    # Speech Configuration
    DEFAULT_LANGUAGE: str = "en-IN"
    SPEECH_TIMEOUT: int = 10
    ENABLE_WEBSPEECH: bool = True
    TTS_SERVICE: str = "gtts"
    TTS_LANGUAGE_FALLBACK: str = "en"
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = [
        "en-IN", "hi-IN", "ta-IN", "te-IN", 
        "mr-IN", "gu-IN", "bn-IN"
    ]
    
    # Performance Settings
    MAX_CONCURRENT_CALLS: int = 50
    RESPONSE_TIMEOUT: float = 3.0
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600

    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"

    # Email Configuration (Free SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    ENABLE_EMAIL_NOTIFICATIONS: bool = False

    # Storage Configuration
    DATA_DIR: str = "./data"
    LOGS_DIR: str = "./logs"
    AUDIO_STORAGE: str = "./data/audio"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        for dir_path in [self.DATA_DIR, self.LOGS_DIR, self.AUDIO_STORAGE, self.CACHE_DIR]:
            os.makedirs(dir_path, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance to avoid reading the environment each time.
    """
    return Settings()

"""
Custom exceptions for the VoiceBot domain.
"""
from typing import Optional

class VoiceBotException(Exception):
    """Base exception for VoiceBot errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class SpeechRecognitionError(VoiceBotException):
    """Raised when speech recognition fails"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)

class TextToSpeechError(VoiceBotException):
    """Raised when text-to-speech conversion fails"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)

class LanguageNotSupportedError(VoiceBotException):
    """Raised when requested language is not supported"""
    def __init__(self, language: str):
        message = f"Language '{language}' is not supported"
        super().__init__(message, status_code=400)

class AuthenticationError(VoiceBotException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class RateLimitExceededError(VoiceBotException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)

class DatabaseError(VoiceBotException):
    """Raised when database operations fail"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message, status_code=500)

class CRMIntegrationError(VoiceBotException):
    """Raised when CRM integration fails"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message, status_code=502)

"""
Logging configuration for the VoiceBot system.
Implements structured logging with JSON format and proper log rotation.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict
from src.core.config import get_settings
import sys
import os
from logging.handlers import RotatingFileHandler

settings = get_settings()

class CustomJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': 'voicebot',
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add correlation ID if available - using getattr to avoid AttributeError
        correlation_id = getattr(record, 'correlation_id', None)
        if correlation_id:
            log_record['correlation_id'] = correlation_id
            
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record, default=str)

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records"""
    def __init__(self):
        super().__init__()
        self.correlation_id = None

    def filter(self, record):
        record.correlation_id = getattr(self, 'correlation_id', None)
        return True

def setup_logging() -> logging.Logger:
    """
    Configure logging with JSON formatting and proper handlers
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger("voicebot")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    # Create correlation ID filter
    correlation_filter = CorrelationIdFilter()
    logger.addFilter(correlation_filter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'voicebot.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create logger instance
logger = setup_logging()

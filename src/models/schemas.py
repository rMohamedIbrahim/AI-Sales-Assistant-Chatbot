"""
Pydantic models for request/response validation and serialization.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH_INDIA = "en-IN"
    HINDI = "hi-IN"
    TAMIL = "ta-IN"
    TELUGU = "te-IN"
    MARATHI = "mr-IN"
    GUJARATI = "gu-IN"
    BENGALI = "bn-IN"

class BookingStatus(str, Enum):
    """Booking status options"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ServiceStatus(str, Enum):
    """Service request status options"""
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Customer Models
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Booking Models
class BookingBase(BaseModel):
    customer_id: int
    vehicle_model: str = Field(..., min_length=1, max_length=100)
    preferred_date: datetime
    location: str = Field(..., min_length=2, max_length=200)

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    vehicle_model: Optional[str] = Field(None, min_length=1, max_length=100)
    preferred_date: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    status: Optional[BookingStatus] = None

class BookingResponse(BookingBase):
    id: int
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Service Models
class ServiceType(str, Enum):
    """Service types"""
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    WARRANTY = "warranty"
    INSPECTION = "inspection"

class ServiceBase(BaseModel):
    customer_id: int
    service_type: ServiceType
    description: str = Field(..., min_length=10, max_length=500)
    preferred_date: datetime
    vehicle_model: str = Field(..., min_length=1, max_length=100)

class ServiceCreate(ServiceBase):
    pass

class ServiceRequest(ServiceCreate):
    """Alias for backward compatibility"""
    pass

class ServiceRequestCreate(ServiceBase):
    """Service request creation schema"""
    pass

class ServiceUpdate(BaseModel):
    service_type: Optional[ServiceType] = None
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    preferred_date: Optional[datetime] = None
    vehicle_model: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[ServiceStatus] = None

class ServiceResponse(ServiceBase):
    id: int
    status: ServiceStatus
    created_at: datetime
    estimated_completion: Optional[datetime] = None

    class Config:
        from_attributes = True

# Interaction Models
class InteractionType(str, Enum):
    """Interaction types"""
    VOICE_CALL = "voice_call"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    BOOKING_INQUIRY = "booking_inquiry"
    SERVICE_INQUIRY = "service_inquiry"
    GENERAL_INQUIRY = "general_inquiry"

class InteractionBase(BaseModel):
    customer_id: Optional[int] = None
    type: InteractionType
    content: Optional[str] = None
    language: Optional[LanguageCode] = None
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)

class InteractionCreate(InteractionBase):
    pass

class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Speech Models
class SpeechToTextRequest(BaseModel):
    language: Optional[LanguageCode] = LanguageCode.ENGLISH_INDIA
    customer_id: Optional[int] = None

class SpeechToTextResponse(BaseModel):
    text: str
    language: LanguageCode
    confidence: float = Field(ge=0.0, le=1.0)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    language: Optional[LanguageCode] = LanguageCode.ENGLISH_INDIA
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0)

class TextToSpeechResponse(BaseModel):
    audio_url: str
    language: LanguageCode
    duration: Optional[float] = None

# Vehicle Models
class VehicleModel(BaseModel):
    name: str
    brand: str
    type: str  # scooter, motorcycle, etc.
    engine_capacity: str
    price_range: str
    features: List[str]

class VehicleInquiry(BaseModel):
    customer_id: Optional[int] = None
    vehicle_type: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_features: Optional[List[str]] = None

# API Response Models
class APIResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Health Check
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str

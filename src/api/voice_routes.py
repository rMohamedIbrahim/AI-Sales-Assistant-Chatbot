"""
Voice API routes for speech recognition and text-to-speech operations.
Handles audio processing, multilingual support, and conversation management.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import Response
from src.services.voice_service import voice_service
from src.models.schemas import (
    SpeechToTextRequest, SpeechToTextResponse,
    TextToSpeechRequest, TextToSpeechResponse,
    APIResponse, ErrorResponse
)
from src.utils.sentiment_analyzer import sentiment_analyzer
from src.infrastructure.database import db_service
from typing import Optional
import logging
from datetime import datetime
import base64

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, etc.)"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en-IN', 'hi-IN')"),
    customer_id: Optional[int] = Form(None, description="Customer ID for tracking")
):
    """
    Convert speech to text with language detection and sentiment analysis.
    
    - **audio**: Audio file in supported format (WAV, MP3, FLAC, etc.)
    - **language**: Optional language code. If not provided, will be auto-detected
    - **customer_id**: Optional customer ID for conversation tracking
    """
    try:
        # Validate file type
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )

        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty audio file"
            )

        # Process voice input
        result = await voice_service.process_voice_input(
            audio_data=audio_data,
            customer_id=customer_id,
            language=language
        )

        return SpeechToTextResponse(
            text=result["text"],
            language=result["language"],
            confidence=result["confidence"],
            sentiment_score=result["sentiment"]["score"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text conversion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Speech recognition failed: {str(e)}"
        )

@router.post("/text-to-speech")
async def text_to_speech(
    request: TextToSpeechRequest,
    customer_id: Optional[int] = Query(None, description="Customer ID for tracking")
):
    """
    Convert text to speech in the specified language.
    
    Returns audio data that can be played directly or saved as a file.
    """
    try:
        # Generate voice response
        result = await voice_service.generate_voice_response(
            text=request.text,
            language=request.language,
            customer_id=customer_id,
            use_online_tts=True
        )

        # Return audio as response
        return Response(
            content=result["audio_data"],
            media_type="audio/mp3",
            headers={
                "Content-Disposition": f"attachment; filename={result['audio_filename']}",
                "X-Audio-Language": result["language"],
                "X-Audio-Size": str(result["audio_size"]),
                "X-Interaction-ID": str(result["interaction_id"])
            }
        )

    except Exception as e:
        logger.error(f"Text-to-speech conversion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Text-to-speech conversion failed: {str(e)}"
        )

@router.post("/conversation", response_model=dict)
async def process_conversation(
    audio: UploadFile = File(..., description="Audio input"),
    customer_id: Optional[int] = Form(None, description="Customer ID"),
    language: Optional[str] = Form(None, description="Preferred language"),
    conversation_id: Optional[str] = Form(None, description="Conversation ID for context")
):
    """
    Process a complete conversation turn: speech input → text → response → speech output.
    
    This endpoint handles the full conversation pipeline and returns both text and audio response.
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        # Prepare context
        context = {
            "conversation_id": conversation_id,
            "turn_number": 1  # This would be tracked in a real implementation
        }

        # Process conversation turn
        result = await voice_service.process_conversation_turn(
            audio_data=audio_data,
            customer_id=customer_id,
            language=language,
            context=context
        )

        # Encode audio data as base64 for JSON response
        audio_base64 = base64.b64encode(result["response"]["voice"]["audio_data"]).decode('utf-8')

        return {
            "conversation_id": result.get("conversation_id"),
            "turn_number": result.get("turn_number"),
            "input": {
                "text": result["input"]["text"],
                "language": result["input"]["language"],
                "confidence": result["input"]["confidence"],
                "sentiment": result["input"]["sentiment"]
            },
            "response": {
                "text": result["response"]["text"],
                "language": result["response"]["voice"]["language"],
                "audio_base64": audio_base64,
                "audio_filename": result["response"]["voice"]["audio_filename"]
            },
            "timestamp": result["input"]["timestamp"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Conversation processing failed: {str(e)}"
        )

@router.get("/languages", response_model=dict)
async def get_supported_languages():
    """
    Get list of supported languages for speech recognition and text-to-speech.
    """
    try:
        languages = voice_service.get_supported_languages()
        
        # Map language codes to names
        language_info = {
            "en-IN": {"name": "English (India)", "native_name": "English"},
            "hi-IN": {"name": "Hindi", "native_name": "हिन्दी"},
            "ta-IN": {"name": "Tamil", "native_name": "தமிழ்"},
            "te-IN": {"name": "Telugu", "native_name": "తెలుగు"},
            "mr-IN": {"name": "Marathi", "native_name": "मराठी"},
            "gu-IN": {"name": "Gujarati", "native_name": "ગુજરાતી"},
            "bn-IN": {"name": "Bengali", "native_name": "বাংলা"}
        }

        supported_languages = []
        for lang_code in languages:
            if lang_code in language_info:
                supported_languages.append({
                    "code": lang_code,
                    "name": language_info[lang_code]["name"],
                    "native_name": language_info[lang_code]["native_name"]
                })

        return {
            "supported_languages": supported_languages,
            "default_language": voice_service.default_language,
            "total_count": len(supported_languages)
        }

    except Exception as e:
        logger.error(f"Failed to get supported languages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve supported languages"
        )

@router.get("/conversation/history/{customer_id}", response_model=dict)
async def get_conversation_history(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of recent interactions to retrieve")
):
    """
    Get conversation history for a specific customer.
    """
    try:
        history = await voice_service.get_conversation_history(customer_id, limit)
        
        return {
            "customer_id": customer_id,
            "total_interactions": len(history),
            "interactions": history
        }

    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation history"
        )

@router.post("/sentiment/analyze", response_model=dict)
async def analyze_text_sentiment(
    text: str = Form(..., description="Text to analyze"),
    customer_id: Optional[int] = Form(None, description="Customer ID for tracking")
):
    """
    Analyze sentiment of text input.
    
    Returns detailed sentiment scores and overall sentiment classification.
    """
    try:
        # Get detailed sentiment analysis
        sentiment_details = sentiment_analyzer.get_detailed_sentiment(text)
        
        # Store interaction if customer_id provided
        interaction_id = None
        if customer_id:
            try:
                interaction_data = {
                    "customer_id": customer_id,
                    "type": "sentiment_analysis",
                    "content": text,
                    "sentiment_score": sentiment_details["compound"]
                }
                interaction_id = await db_service.create_interaction(interaction_data)
            except Exception as e:
                logger.warning(f"Failed to store sentiment interaction: {e}")

        return {
            "text": text,
            "sentiment": sentiment_details,
            "interaction_id": interaction_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        )

@router.get("/health", response_model=dict)
async def voice_service_health():
    """
    Check health of voice service components.
    """
    try:
        health = await voice_service.health_check()
        
        overall_status = "healthy" if all(health.values()) else "unhealthy"
        
        return {
            "status": overall_status,
            "components": health,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

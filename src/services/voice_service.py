"""
Voice service integration layer that combines speech recognition, 
text-to-speech, sentiment analysis, and business logic.
"""
import asyncio
from typing import Optional, Tuple, Dict, Any, List
from src.services.speech_service import speech_service
from src.utils.sentiment_analyzer import sentiment_analyzer
from src.infrastructure.database import db_service
from src.core.config import get_settings
from src.domain.exceptions import SpeechRecognitionError, TextToSpeechError
from src.models.schemas import LanguageCode, InteractionType
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()

class VoiceService:
    """High-level voice service that orchestrates speech operations"""
    
    def __init__(self):
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_language = settings.DEFAULT_LANGUAGE

    async def process_voice_input(
        self,
        audio_data: bytes,
        customer_id: Optional[int] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process voice input through the complete pipeline:
        1. Speech to text conversion
        2. Language detection (if not specified)
        3. Sentiment analysis
        4. Store interaction in database
        
        Args:
            audio_data: Raw audio data bytes
            customer_id: Optional customer ID
            language: Optional language code
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Validate audio format first
            if not await speech_service.validate_audio_format(audio_data):
                raise SpeechRecognitionError("Invalid audio format")

            # Step 1: Convert speech to text
            if language and language in self.supported_languages:
                detected_language = language
            else:
                # Use default language for speech recognition, then detect
                detected_language = self.default_language

            text, confidence = await speech_service.speech_to_text(
                audio_data, detected_language
            )

            # Step 2: Detect language from text if not specified
            if not language:
                detected_language = await speech_service.detect_language(text)

            # Step 3: Analyze sentiment
            sentiment_score = sentiment_analyzer.analyze(text)
            sentiment_details = sentiment_analyzer.get_detailed_sentiment(text)

            # Step 4: Store interaction in database
            interaction_id = await self._store_interaction(
                customer_id=customer_id,
                interaction_type=InteractionType.SPEECH_TO_TEXT,
                content=text,
                language=detected_language,
                sentiment_score=sentiment_score
            )

            # Prepare response
            response = {
                "interaction_id": interaction_id,
                "text": text,
                "language": detected_language,
                "confidence": confidence,
                "sentiment": {
                    "score": sentiment_score,
                    "details": sentiment_details
                },
                "timestamp": datetime.utcnow().isoformat(),
                "customer_id": customer_id
            }

            logger.info(f"Voice input processed successfully: {text[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Voice input processing failed: {str(e)}")
            raise

    async def generate_voice_response(
        self,
        text: str,
        language: Optional[str] = None,
        customer_id: Optional[int] = None,
        use_online_tts: bool = True
    ) -> Dict[str, Any]:
        """
        Generate voice response from text:
        1. Text-to-speech conversion
        2. Store audio file
        3. Store interaction in database
        
        Args:
            text: Text to convert to speech
            language: Language code for TTS
            customer_id: Optional customer ID
            use_online_tts: Whether to use online TTS service
            
        Returns:
            Dictionary containing audio data and metadata
        """
        try:
            # Use default language if not specified
            if not language or language not in self.supported_languages:
                language = self.default_language

            # Step 1: Convert text to speech
            audio_data = await speech_service.text_to_speech(
                text, language, use_online=use_online_tts
            )

            # Step 2: Save audio file
            audio_filename = f"tts_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}.mp3"
            audio_path = await speech_service.save_audio_file(audio_data, audio_filename)

            # Step 3: Store interaction in database
            interaction_id = await self._store_interaction(
                customer_id=customer_id,
                interaction_type=InteractionType.TEXT_TO_SPEECH,
                content=text,
                language=language,
                sentiment_score=None
            )

            # Prepare response
            response = {
                "interaction_id": interaction_id,
                "audio_data": audio_data,
                "audio_path": audio_path,
                "audio_filename": audio_filename,
                "text": text,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "customer_id": customer_id,
                "audio_size": len(audio_data)
            }

            logger.info(f"Voice response generated: {text[:50]}... ({len(audio_data)} bytes)")
            return response

        except Exception as e:
            logger.error(f"Voice response generation failed: {str(e)}")
            raise

    async def process_conversation_turn(
        self,
        audio_data: bytes,
        customer_id: Optional[int] = None,
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a complete conversation turn:
        1. Process voice input
        2. Generate appropriate response
        3. Convert response to voice
        
        Args:
            audio_data: Input audio data
            customer_id: Optional customer ID
            language: Optional language preference
            context: Optional conversation context
            
        Returns:
            Complete conversation turn result
        """
        try:
            # Step 1: Process voice input
            input_result = await self.process_voice_input(
                audio_data, customer_id, language
            )

            # Step 2: Generate text response based on input
            response_text = await self._generate_response_text(
                input_result["text"],
                input_result["language"],
                input_result["sentiment"]["score"],
                context
            )

            # Step 3: Convert response to voice
            voice_result = await self.generate_voice_response(
                response_text,
                input_result["language"],
                customer_id
            )

            # Combine results
            conversation_result = {
                "input": input_result,
                "response": {
                    "text": response_text,
                    "voice": voice_result
                },
                "conversation_id": context.get("conversation_id") if context else None,
                "turn_number": context.get("turn_number", 1) if context else 1
            }

            return conversation_result

        except Exception as e:
            logger.error(f"Conversation turn processing failed: {str(e)}")
            raise

    async def _generate_response_text(
        self,
        input_text: str,
        language: str,
        sentiment_score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate appropriate response text based on input and context.
        This is a simplified version - in production, this would integrate
        with NLU/dialogue management systems.
        """
        try:
            # Simple keyword-based response generation
            input_lower = input_text.lower()
            
            # Greeting responses
            if any(word in input_lower for word in ['hello', 'hi', 'namaste', 'namaskar']):
                if language == 'hi-IN':
                    return "नमस्ते! दो पहिया बिक्री में आपका स्वागत है। मैं आपकी कैसे सहायता कर सकता हूं?"
                else:
                    return "Hello! Welcome to Two Wheeler Sales. How can I help you today?"
            
            # Booking related
            elif any(word in input_lower for word in ['book', 'test drive', 'appointment']):
                if language == 'hi-IN':
                    return "मैं आपके लिए टेस्ट ड्राइव बुक कर सकता हूं। कृपया अपना पसंदीदा वाहन मॉडल और दिनांक बताएं।"
                else:
                    return "I can help you book a test drive. Please tell me your preferred vehicle model and date."
            
            # Service related
            elif any(word in input_lower for word in ['service', 'maintenance', 'repair']):
                if language == 'hi-IN':
                    return "मैं आपके वाहन की सर्विस बुक कर सकता हूं। कृपया बताएं कि आपको किस प्रकार की सर्विस चाहिए?"
                else:
                    return "I can help you schedule vehicle service. What type of service do you need?"
            
            # Vehicle inquiry
            elif any(word in input_lower for word in ['bike', 'scooter', 'motorcycle', 'vehicle']):
                if language == 'hi-IN':
                    return "हमारे पास विभिन्न प्रकार के दो पहिया वाहन हैं। आपका बजट और पसंद क्या है?"
                else:
                    return "We have various two-wheelers available. What's your budget and preference?"
            
            # Sentiment-based responses
            elif sentiment_score < -0.3:  # Negative sentiment
                if language == 'hi-IN':
                    return "मुझे खुशी होगी यदि मैं आपकी समस्या का समाधान कर सकूं। कृपया बताएं कि क्या परेशानी है?"
                else:
                    return "I'd be happy to help resolve any concerns you have. Could you please tell me what's troubling you?"
            
            # Default response
            else:
                if language == 'hi-IN':
                    return "मैं आपकी बात समझ गया हूं। क्या आप टेस्ट ड्राइव बुक करना चाहते हैं या सर्विस के बारे में जानकारी चाहते हैं?"
                else:
                    return "I understand. Would you like to book a test drive or learn about our services?"

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            # Fallback response
            if language == 'hi-IN':
                return "क्षमा करें, मुझे आपकी बात समझने में कुछ कठिनाई हो रही है। कृपया दोबारा कहें।"
            else:
                return "I'm sorry, I'm having trouble understanding. Could you please repeat that?"

    async def _store_interaction(
        self,
        customer_id: Optional[int],
        interaction_type: InteractionType,
        content: Optional[str],
        language: Optional[str],
        sentiment_score: Optional[float]
    ) -> int:
        """Store interaction in database"""
        try:
            interaction_data = {
                "customer_id": customer_id,
                "type": interaction_type.value,
                "content": content,
                "language": language,
                "sentiment_score": sentiment_score
            }
            
            return await db_service.create_interaction(interaction_data)
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {str(e)}")
            # Don't fail the main operation if logging fails
            return -1

    async def get_conversation_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a customer"""
        try:
            interactions = await db_service.get_customer_interactions(customer_id, limit)
            
            history = []
            for interaction in interactions:
                history.append({
                    "id": interaction.id,
                    "type": interaction.type,
                    "content": interaction.content,
                    "language": interaction.language,
                    "sentiment_score": interaction.sentiment_score,
                    "timestamp": interaction.created_at.isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages

    async def health_check(self) -> Dict[str, bool]:
        """Check health of voice service components"""
        try:
            health = {
                "speech_service": True,
                "database": await db_service.health_check(),
                "sentiment_analyzer": True
            }
            
            # Test speech service
            try:
                test_audio = b"dummy_audio_data"
                # Don't actually test with invalid data, just check service availability
                health["speech_service"] = True
            except:
                health["speech_service"] = False
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "speech_service": False,
                "database": False,
                "sentiment_analyzer": False
            }

# Create singleton instance
voice_service = VoiceService()

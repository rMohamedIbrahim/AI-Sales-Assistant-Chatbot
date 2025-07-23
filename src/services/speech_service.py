"""
Free Speech service implementation using Google's free APIs and offline TTS.
Handles speech-to-text and text-to-speech operations using only free services.
"""
try:
    import speech_recognition as sr
except ImportError:
    sr = None
import pyttsx3
import tempfile
import os
import io
from gtts import gTTS
from typing import Tuple, Optional, BinaryIO
import asyncio
import aiofiles
from src.core.config import get_settings
from src.domain.exceptions import SpeechRecognitionError, TextToSpeechError
from src.models.schemas import LanguageCode
import logging
import wave
from langdetect import detect, DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)
settings = get_settings()

class FreeSpeechService:
    """Speech service using only free APIs and libraries"""
    
    def __init__(self):
        # Initialize speech recognition
        try:
            if sr is not None:
                self.recognizer = sr.Recognizer()
                self.speech_available = True
            else:
                self.recognizer = None
                self.speech_available = False
                logger.warning("SpeechRecognition library not available")
        except Exception as e:
            logger.error(f"Failed to initialize speech recognizer: {e}")
            self.recognizer = None
            self.speech_available = False
            
        # Initialize text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            self._configure_tts_engine()
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
        
        # Language mappings
        self.speech_to_text_langs = {
            "en-IN": "en-IN",
            "hi-IN": "hi-IN", 
            "ta-IN": "ta-IN",
            "te-IN": "te-IN",
            "mr-IN": "mr-IN",
            "gu-IN": "gu-IN",
            "bn-IN": "bn-IN"
        }
        
        self.gtts_langs = {
            "en-IN": "en",
            "hi-IN": "hi",
            "ta-IN": "ta", 
            "te-IN": "te",
            "mr-IN": "mr",
            "gu-IN": "gu",
            "bn-IN": "bn"
        }

    def _configure_tts_engine(self):
        """Configure the offline TTS engine"""
        try:
            if self.engine is None:
                logger.warning("TTS engine not available, skipping configuration")
                return
                
            # Set speech rate
            rate = self.engine.getProperty('rate')
            if isinstance(rate, (int, float)):
                self.engine.setProperty('rate', max(50, rate - 50))  # Slower speech, minimum 50
            
            # Set volume
            volume = self.engine.getProperty('volume')
            if isinstance(volume, (int, float)):
                self.engine.setProperty('volume', 0.9)
            
        except Exception as e:
            logger.warning(f"TTS engine configuration failed: {e}")

    async def speech_to_text(
        self, 
        audio_data: bytes,
        language: str = "en-IN"
    ) -> Tuple[str, float]:
        """
        Convert speech to text using Google's free Speech Recognition API.
        
        Args:
            audio_data: Binary audio data
            language: Language code (e.g., 'en-IN', 'hi-IN')
            
        Returns:
            Tuple containing:
            - Recognized text
            - Confidence score (estimated as 1.0 for free API)
        """
        if not self.speech_available or self.recognizer is None or sr is None:
            raise SpeechRecognitionError("Speech recognition service not available")
            
        try:
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.record(source)

                # Use Google's free speech recognition
                lang_code = self.speech_to_text_langs.get(language, "en-IN")
                
                # Use the recognizer with proper error handling
                try:
                    # The recognize_google method should be available in speech_recognition
                    text = self.recognizer.recognize_google(audio, language=lang_code)
                    logger.info(f"Speech recognized: '{text}' in language {lang_code}")
                    return str(text), 1.0  # Free API doesn't provide confidence
                    
                except AttributeError as attr_error:
                    logger.error(f"Speech recognition method not available: {attr_error}")
                    raise SpeechRecognitionError("Google Speech Recognition not available in this installation")
                except sr.UnknownValueError:
                    logger.error("Speech could not be understood")
                    raise SpeechRecognitionError("Speech could not be understood") 
                except sr.RequestError as req_error:
                    logger.error(f"Google Speech Recognition service error: {req_error}")
                    raise SpeechRecognitionError(f"Speech recognition service error: {req_error}")
                except Exception as recognition_error:
                    logger.error(f"Speech recognition error: {recognition_error}")
                    raise SpeechRecognitionError(f"Recognition failed: {recognition_error}")

            finally:
                # Clean up temp file
                try:
                    os.remove(temp_file_path)
                except:
                    pass

        except sr.UnknownValueError:
            logger.error("Speech could not be understood")
            raise SpeechRecognitionError("Speech could not be understood")
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition service error: {e}")
            raise SpeechRecognitionError(f"Speech recognition service error: {e}")
        except Exception as e:
            logger.error(f"Speech recognition error: {str(e)}")
            raise SpeechRecognitionError(f"Speech recognition failed: {e}")

    async def text_to_speech_gtts(
        self,
        text: str,
        language: str = "en-IN"
    ) -> bytes:
        """
        Convert text to speech using Google Text-to-Speech (free).
        
        Args:
            text: Text to convert to speech
            language: Language code
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            # Map language code to gTTS language
            gtts_lang = self.gtts_langs.get(language, "en")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            audio_data = audio_buffer.read()
            logger.info(f"Generated TTS audio for text: '{text[:50]}...' in language {gtts_lang}")
            
            return audio_data

        except Exception as e:
            logger.error(f"gTTS error: {str(e)}")
            raise TextToSpeechError(f"Text-to-speech failed: {e}")

    async def text_to_speech_offline(
        self,
        text: str,
        language: str = "en-IN"
    ) -> bytes:
        """
        Convert text to speech using offline pyttsx3.
        
        Args:
            text: Text to convert to speech
            language: Language code (ignored for offline TTS)
            
        Returns:
            Audio data as bytes (WAV format)
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file_path = temp_file.name

            try:
                # Generate speech to file
                await asyncio.to_thread(self._generate_offline_speech, text, temp_file_path)
                
                # Read the generated audio file
                async with aiofiles.open(temp_file_path, 'rb') as audio_file:
                    audio_data = await audio_file.read()

                logger.info(f"Generated offline TTS audio for text: '{text[:50]}...'")
                return audio_data

            finally:
                # Clean up temp file
                try:
                    os.remove(temp_file_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"Offline TTS error: {str(e)}")
            raise TextToSpeechError(f"Offline text-to-speech failed: {e}")

    def _generate_offline_speech(self, text: str, output_path: str):
        """Helper method to generate speech using pyttsx3"""
        try:
            if self.engine is None:
                raise TextToSpeechError("TTS engine not available")
                
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
        except Exception as e:
            raise TextToSpeechError(f"Offline speech generation failed: {e}")

    async def text_to_speech(
        self,
        text: str,
        language: str = "en-IN",
        use_online: bool = True
    ) -> bytes:
        """
        Convert text to speech with fallback options.
        
        Args:
            text: Text to convert to speech
            language: Language code
            use_online: Whether to use online TTS (gTTS) first
            
        Returns:
            Audio data as bytes
        """
        if use_online:
            try:
                return await self.text_to_speech_gtts(text, language)
            except Exception as e:
                logger.warning(f"Online TTS failed, falling back to offline: {e}")
                return await self.text_to_speech_offline(text, language)
        else:
            return await self.text_to_speech_offline(text, language)

    async def detect_language(self, text: str) -> str:
        """
        Detect the language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code
        """
        try:
            # Use langdetect to determine the language
            detected_lang = detect(text)
            
            # Map ISO 639-1 codes to our supported format
            language_mapping = {
                'en': 'en-IN',
                'hi': 'hi-IN',
                'ta': 'ta-IN',
                'te': 'te-IN',
                'mr': 'mr-IN',
                'gu': 'gu-IN',
                'bn': 'bn-IN'
            }
            
            mapped_lang = language_mapping.get(detected_lang, 'en-IN')
            logger.info(f"Detected language: {detected_lang} -> {mapped_lang}")
            
            return mapped_lang

        except Exception as e:
            logger.warning(f"Language detection failed: {e}, defaulting to en-IN")
            return 'en-IN'

    async def save_audio_file(self, audio_data: bytes, filename: str) -> str:
        """
        Save audio data to file in audio storage directory.
        
        Args:
            audio_data: Audio data bytes
            filename: Name for the file
            
        Returns:
            Full path to saved file
        """
        try:
            # Ensure audio storage directory exists
            os.makedirs(settings.AUDIO_STORAGE, exist_ok=True)
            
            file_path = os.path.join(settings.AUDIO_STORAGE, filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)
            
            logger.info(f"Audio file saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            raise

    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return list(self.speech_to_text_langs.keys())

    async def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validate if audio data is in a supported format.
        
        Args:
            audio_data: Audio data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Create temporary file to test
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # Try to read as audio file if speech recognition is available
                if sr is not None and self.recognizer is not None:
                    with sr.AudioFile(temp_file_path) as source:
                        self.recognizer.record(source, duration=0.1)
                    return True
                else:
                    # Basic validation by checking file header
                    if len(audio_data) > 44:  # Minimum WAV header size
                        return audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE'
                    return False
                
            except Exception:
                return False
                
            finally:
                try:
                    os.remove(temp_file_path)
                except:
                    pass

        except Exception:
            return False

# Create singleton instance
speech_service = FreeSpeechService()

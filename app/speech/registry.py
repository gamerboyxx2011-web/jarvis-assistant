"""Speech provider construction."""

from app.speech.base import STTProvider, TTSProvider
from app.speech.openai import OpenAISpeechProvider


class SpeechProviderRegistry:
    def create_stt(self) -> STTProvider:
        return OpenAISpeechProvider()

    def create_tts(self) -> TTSProvider:
        return OpenAISpeechProvider()


speech_provider_registry = SpeechProviderRegistry()

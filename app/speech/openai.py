"""OpenAI hosted STT and TTS adapters using httpx."""
import asyncio
from collections.abc import Callable
import httpx
from app.config import settings
from app.errors import SpeechProviderError, SpeechProviderTimeoutError
from app.speech.models import AudioInput, SynthesizedAudio, Transcription
class OpenAISpeechProvider:
    def __init__(self, *, api_key=None, base_url=None, stt_model=None, tts_model=None, tts_voice=None, tts_format=None, timeout=None, client_factory: Callable[[], httpx.AsyncClient]=httpx.AsyncClient):
        self.api_key=settings.OPENAI_API_KEY if api_key is None else api_key
        self.base_url=(settings.OPENAI_API_BASE_URL if base_url is None else base_url).rstrip("/")
        self.stt_model=settings.OPENAI_STT_MODEL if stt_model is None else stt_model
        self.tts_model=settings.OPENAI_TTS_MODEL if tts_model is None else tts_model
        self.tts_voice=settings.OPENAI_TTS_VOICE if tts_voice is None else tts_voice
        self.tts_format=settings.OPENAI_TTS_FORMAT if tts_format is None else tts_format
        self.timeout=settings.OPENAI_SPEECH_TIMEOUT if timeout is None else timeout
        self._client_factory=client_factory
    def _headers(self):
        if not self.api_key.strip(): raise SpeechProviderError("OpenAI speech provider is not configured")
        return {"Authorization":f"Bearer {self.api_key}"}
    async def transcribe(self, audio: AudioInput) -> Transcription:
        try:
            async with self._client_factory() as client:
                response=await client.post(f"{self.base_url}/audio/transcriptions",headers=self._headers(),data={"model":self.stt_model,"response_format":"json"},files={"file":(audio.filename,audio.data,audio.content_type)},timeout=self.timeout)
                if not response.is_success:
                    await response.aread(); raise SpeechProviderError(f"OpenAI transcription returned HTTP {response.status_code}")
                payload=response.json(); text=payload.get("text") if isinstance(payload,dict) else None
                if not isinstance(text,str) or not text.strip(): raise SpeechProviderError("OpenAI transcription returned no text")
                return Transcription(text.strip())
        except asyncio.CancelledError: raise
        except SpeechProviderError: raise
        except httpx.TimeoutException as exc: raise SpeechProviderTimeoutError("OpenAI transcription timed out") from exc
        except (httpx.HTTPError,ValueError) as exc: raise SpeechProviderError("OpenAI transcription failed") from exc
    async def synthesize(self, text: str) -> SynthesizedAudio:
        try:
            async with self._client_factory() as client:
                response=await client.post(f"{self.base_url}/audio/speech",headers={**self._headers(),"Content-Type":"application/json"},json={"model":self.tts_model,"voice":self.tts_voice,"input":text,"response_format":self.tts_format},timeout=self.timeout)
                if not response.is_success:
                    await response.aread(); raise SpeechProviderError(f"OpenAI speech synthesis returned HTTP {response.status_code}")
                if not response.content: raise SpeechProviderError("OpenAI speech synthesis returned no audio")
                return SynthesizedAudio(response.content,{"mp3":"audio/mpeg","opus":"audio/ogg","aac":"audio/aac","flac":"audio/flac","wav":"audio/wav","pcm":"audio/pcm"}.get(self.tts_format,"application/octet-stream"))
        except asyncio.CancelledError: raise
        except SpeechProviderError: raise
        except httpx.TimeoutException as exc: raise SpeechProviderTimeoutError("OpenAI speech synthesis timed out") from exc
        except httpx.HTTPError as exc: raise SpeechProviderError("OpenAI speech synthesis failed") from exc

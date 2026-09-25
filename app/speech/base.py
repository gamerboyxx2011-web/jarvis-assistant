"""Provider-neutral speech contracts."""
from typing import Protocol, runtime_checkable
from app.speech.models import AudioInput, SynthesizedAudio, Transcription
@runtime_checkable
class STTProvider(Protocol):
    async def transcribe(self, audio: AudioInput) -> Transcription: ...
@runtime_checkable
class TTSProvider(Protocol):
    async def synthesize(self, text: str) -> SynthesizedAudio: ...

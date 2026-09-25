"""Provider-neutral speech request and result models."""
from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class AudioInput:
    data: bytes
    filename: str
    content_type: str
@dataclass(frozen=True, slots=True)
class Transcription:
    text: str
@dataclass(frozen=True, slots=True)
class SynthesizedAudio:
    data: bytes
    content_type: str

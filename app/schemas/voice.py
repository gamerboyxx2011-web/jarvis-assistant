"""Internal events for the dedicated voice SSE pipeline."""
from dataclasses import dataclass
from typing import Literal
@dataclass(frozen=True, slots=True)
class VoiceConversation:
    conversation_id: str
    created: bool
    type: Literal["conversation"] = "conversation"
@dataclass(frozen=True, slots=True)
class VoiceTranscript:
    text: str
    type: Literal["transcript"] = "transcript"
@dataclass(frozen=True, slots=True)
class VoiceTextDelta:
    content: str
    type: Literal["text"] = "text"
@dataclass(frozen=True, slots=True)
class VoiceAudio:
    sequence: int
    content_type: str
    data: bytes
    type: Literal["audio"] = "audio"
@dataclass(frozen=True, slots=True)
class VoiceError:
    message: str
    phase: Literal["stt", "llm", "tts", "voice"]
    type: Literal["error"] = "error"
@dataclass(frozen=True, slots=True)
class VoiceCompleted:
    type: Literal["completed"] = "completed"
VoiceEvent = VoiceConversation | VoiceTranscript | VoiceTextDelta | VoiceAudio | VoiceError | VoiceCompleted

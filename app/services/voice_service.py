"""Controlled voice loop over the existing ChatService."""
import asyncio, logging, re
from collections.abc import AsyncIterator
from app.config import settings
from app.errors import SpeechProviderError
from app.schemas.chat import ChatRequest
from app.schemas.events import ResponseCompleted, ResponseDelta, ResponseError
from app.schemas.voice import VoiceAudio, VoiceCompleted, VoiceConversation, VoiceError, VoiceEvent, VoiceTextDelta, VoiceTranscript
from app.speech.models import AudioInput
logger=logging.getLogger(__name__)
_END=re.compile(r"[.!?](?:[\"')\]]+)?(?:\s+|$)")
class VoiceService:
    def __init__(self, stt_provider, tts_provider, chat_service, conversation_store, *, phrase_chars=None):
        self._stt=stt_provider; self._tts=tts_provider; self._chat=chat_service; self._store=conversation_store; self._limit=phrase_chars or settings.VOICE_TTS_PHRASE_CHARS
    async def stream_voice(self, audio: AudioInput, conversation_id: str|None=None) -> AsyncIterator[VoiceEvent]:
        try: transcript=(await self._stt.transcribe(audio)).text.strip()
        except asyncio.CancelledError: raise
        except Exception:
            logger.warning("Speech transcription failed"); yield VoiceError("Speech transcription failed","stt"); return
        if not transcript: yield VoiceError("No speech was recognized","stt"); return
        created=conversation_id is None
        if created: conversation_id=(await self._store.create(transcript if len(transcript)<=60 else transcript[:57]+"…")).id
        yield VoiceConversation(conversation_id,created); yield VoiceTranscript(transcript)
        buffer=""; sequence=0; tts_ok=True
        async for event in self._chat.stream_chat(ChatRequest(message=transcript,conversation_id=conversation_id)):
            if isinstance(event,ResponseDelta):
                yield VoiceTextDelta(event.content); buffer+=event.content; phrases,buffer=_take_phrases(buffer,self._limit,False)
                if tts_ok:
                    for phrase in phrases:
                        try: audio_out=await self._tts.synthesize(phrase)
                        except asyncio.CancelledError: raise
                        except Exception:
                            tts_ok=False; yield VoiceError("Speech playback is unavailable; text response preserved","tts"); break
                        yield VoiceAudio(sequence,audio_out.content_type,audio_out.data); sequence+=1
            elif isinstance(event,ResponseError): yield VoiceError(event.message,"llm"); return
            elif isinstance(event,ResponseCompleted):
                phrases,_=_take_phrases(buffer,self._limit,True)
                if tts_ok:
                    for phrase in phrases:
                        try: audio_out=await self._tts.synthesize(phrase)
                        except asyncio.CancelledError: raise
                        except Exception:
                            yield VoiceError("Speech playback is unavailable; text response preserved","tts"); break
                        yield VoiceAudio(sequence,audio_out.content_type,audio_out.data); sequence+=1
                yield VoiceCompleted(); return
def _take_phrases(text,limit,final):
    out=[]; remaining=text
    while remaining:
        match=_END.search(remaining)
        if match: end=match.end()
        elif len(remaining)>=limit:
            split=remaining.rfind(" ",0,limit+1); end=split if split>0 else limit
        elif final: end=len(remaining)
        else: break
        phrase=remaining[:end].strip(); remaining=remaining[end:].lstrip()
        if phrase: out.append(phrase)
    return out,remaining

import asyncio
import pytest
from app.errors import SpeechProviderError
from app.schemas.events import ResponseCompleted, ResponseDelta
from app.schemas.voice import VoiceAudio, VoiceCompleted, VoiceConversation, VoiceError, VoiceTextDelta, VoiceTranscript
from app.services.voice_service import VoiceService, _take_phrases
from app.speech.models import AudioInput, SynthesizedAudio, Transcription
class STT:
    async def transcribe(self,audio): return Transcription("Hello voice")
class TTS:
    def __init__(self,fail=False): self.texts=[]; self.fail=fail
    async def synthesize(self,text):
        self.texts.append(text)
        if self.fail: raise SpeechProviderError("secret")
        return SynthesizedAudio(text.encode(),"audio/mpeg")
class Store:
    async def create(self,title): return type("C",(),{"id":"new-id"})()
class Chat:
    async def stream_chat(self,request):
        self.request=request; yield ResponseDelta("First sentence. "); yield ResponseDelta("Second sentence!"); yield ResponseCompleted()
@pytest.mark.asyncio
async def test_voice_loop_creates_conversation_and_orders_audio():
    chat,tts=Chat(),TTS(); events=[x async for x in VoiceService(STT(),tts,chat,Store()).stream_voice(AudioInput(b"audio","a.webm","audio/webm"))]
    assert events[:2]==[VoiceConversation("new-id",True),VoiceTranscript("Hello voice")]
    assert [x.content for x in events if isinstance(x,VoiceTextDelta)]==["First sentence. ","Second sentence!"]
    assert [x.sequence for x in events if isinstance(x,VoiceAudio)]==[0,1]
    assert tts.texts==["First sentence.","Second sentence!"] and isinstance(events[-1],VoiceCompleted)
@pytest.mark.asyncio
async def test_tts_failure_preserves_text_and_completion():
    events=[x async for x in VoiceService(STT(),TTS(True),Chat(),Store()).stream_voice(AudioInput(b"a","a","audio/webm"),"existing")]
    assert any(isinstance(x,VoiceError) and x.phase=="tts" for x in events)
    assert len([x for x in events if isinstance(x,VoiceTextDelta)])==2 and isinstance(events[-1],VoiceCompleted)
class CancelSTT:
    async def transcribe(self,audio): raise asyncio.CancelledError
@pytest.mark.asyncio
async def test_cancellation_propagates():
    with pytest.raises(asyncio.CancelledError): _=[x async for x in VoiceService(CancelSTT(),TTS(),Chat(),Store()).stream_voice(AudioInput(b"a","a","audio/webm"))]
def test_phrase_buffering():
    phrases,left=_take_phrases("One. Two is deliberately long",10,False)
    assert phrases==["One.","Two is"] and left=="deliberately long"

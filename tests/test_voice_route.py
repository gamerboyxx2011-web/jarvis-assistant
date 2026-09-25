import base64
import pytest
from app.main import app
from app.routes.voice import get_voice_service
from app.schemas.voice import VoiceAudio, VoiceCompleted, VoiceConversation, VoiceTranscript
class FakeVoiceService:
    async def stream_voice(self,audio,conversation_id=None):
        assert audio.data==b"audio" and conversation_id=="conversation-id"
        yield VoiceConversation(conversation_id,False); yield VoiceTranscript("hello"); yield VoiceAudio(0,"audio/mpeg",b"mp3"); yield VoiceCompleted()
@pytest.fixture(autouse=True)
def override():
    app.dependency_overrides[get_voice_service]=lambda:FakeVoiceService(); yield; app.dependency_overrides.clear()
@pytest.mark.asyncio
async def test_dedicated_voice_multipart_sse(client):
    response=await client.post("/api/voice",data={"duration_seconds":"1","conversation_id":"conversation-id"},files={"audio":("clip.webm",b"audio","audio/webm")})
    assert response.status_code==200 and response.text.count("data: [DONE]")==1
    assert base64.b64encode(b"mp3").decode() in response.text
@pytest.mark.asyncio
async def test_voice_rejects_invalid_audio(client):
    r=await client.post("/api/voice",data={"duration_seconds":"1"},files={"audio":("x.txt",b"x","text/plain")}); assert r.status_code==415
    r=await client.post("/api/voice",data={"duration_seconds":"1"},files={"audio":("x.webm",b"","audio/webm")}); assert r.status_code==422

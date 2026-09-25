import json
import httpx
import pytest
import respx
from app.errors import SpeechProviderError
from app.speech.models import AudioInput
from app.speech.openai import OpenAISpeechProvider
@pytest.mark.asyncio
@respx.mock
async def test_openai_stt_returns_final_text():
    route=respx.post("https://api.openai.com/v1/audio/transcriptions").mock(return_value=httpx.Response(200,json={"text":" final words "}))
    result=await OpenAISpeechProvider(api_key="key",stt_model="whisper-test").transcribe(AudioInput(b"abc","clip.webm","audio/webm"))
    assert result.text=="final words" and route.called and b"whisper-test" in route.calls.last.request.content
@pytest.mark.asyncio
@respx.mock
async def test_openai_tts_returns_mp3_and_sends_config():
    route=respx.post("https://api.openai.com/v1/audio/speech").mock(return_value=httpx.Response(200,content=b"mp3"))
    result=await OpenAISpeechProvider(api_key="key",tts_model="tts-test").synthesize("Hello.")
    assert result.data==b"mp3" and result.content_type=="audio/mpeg"
    assert json.loads(route.calls.last.request.content)["input"]=="Hello."
@pytest.mark.asyncio
@respx.mock
async def test_openai_speech_error_is_sanitized():
    respx.post("https://api.openai.com/v1/audio/transcriptions").mock(return_value=httpx.Response(401,text="secret body"))
    with pytest.raises(SpeechProviderError) as exc: await OpenAISpeechProvider(api_key="key").transcribe(AudioInput(b"a","a.webm","audio/webm"))
    assert "secret body" not in str(exc.value)

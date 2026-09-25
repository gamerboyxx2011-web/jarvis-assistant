"""Dedicated push-to-talk voice SSE route."""
import asyncio, base64, json, logging
from dataclasses import asdict
from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from app.config import settings
from app.history.dependencies import get_conversation_store
from app.history.store import SQLiteConversationStore
from app.providers.registry import provider_registry
from app.schemas.voice import VoiceAudio
from app.services.chat_service import ChatService
from app.services.voice_service import VoiceService
from app.speech.models import AudioInput
from app.speech.registry import speech_provider_registry
router=APIRouter(); logger=logging.getLogger(__name__)
_ALLOWED={"audio/webm","audio/ogg","audio/mp4","audio/mpeg","audio/wav","audio/x-wav"}
def get_voice_service(store:Annotated[SQLiteConversationStore,Depends(get_conversation_store)])->VoiceService:
    return VoiceService(speech_provider_registry.create_stt(),speech_provider_registry.create_tts(),ChatService(provider_registry.create(),store),store)
@router.post("/voice")
async def voice_endpoint(audio:Annotated[UploadFile,File(...)],duration_seconds:Annotated[float,Form(gt=0,le=60)],service:Annotated[VoiceService,Depends(get_voice_service)],conversation_id:Annotated[str|None,Form()]=None)->StreamingResponse:
    content_type=(audio.content_type or "").split(";",1)[0].lower()
    if content_type not in _ALLOWED:
        await audio.close(); raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,detail="Unsupported audio type")
    try: data=await audio.read(settings.VOICE_MAX_UPLOAD_BYTES+1)
    finally: await audio.close()
    if not data: raise HTTPException(status_code=422,detail="Audio recording is empty")
    if len(data)>settings.VOICE_MAX_UPLOAD_BYTES: raise HTTPException(status_code=413,detail="Audio recording exceeds 25 MB")
    input_audio=AudioInput(data,audio.filename or "recording",content_type)
    async def generate():
        try:
            async for event in service.stream_voice(input_audio,conversation_id):
                payload=asdict(event)
                if isinstance(event,VoiceAudio): payload["data"]=base64.b64encode(event.data).decode("ascii")
                yield f"data: {json.dumps(payload)}\n\n"
        except asyncio.CancelledError: raise
        except Exception:
            logger.error("Unexpected voice route failure"); yield f"data: {json.dumps({'type':'error','phase':'voice','message':'Internal voice error'})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(generate(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","Connection":"keep-alive"})

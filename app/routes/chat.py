"""Streaming chat route with optional conversation history."""

import asyncio
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.history.dependencies import get_conversation_store
from app.history.store import SQLiteConversationStore
from app.providers.registry import provider_registry
from app.schemas.chat import ChatRequest
from app.schemas.events import ResponseDelta, ResponseError
from app.services.chat_service import ChatService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_chat_service(
    store: Annotated[SQLiteConversationStore, Depends(get_conversation_store)],
) -> ChatService:
    return ChatService(provider_registry.create(), store)


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> StreamingResponse:
    async def generate_response():
        try:
            async for event in service.stream_chat(request):
                if isinstance(event, ResponseDelta):
                    yield f"data: {json.dumps({'content': event.content})}\n\n"
                elif isinstance(event, ResponseError):
                    yield f"data: {json.dumps({'error': event.message})}\n\n"
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.error("Unexpected chat route failure")
            yield f"data: {json.dumps({'error': 'Internal chat error'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

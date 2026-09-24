"""Stateless streaming chat route."""

import asyncio
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.providers.registry import provider_registry
from app.schemas.chat import ChatRequest
from app.schemas.events import ResponseDelta, ResponseError
from app.services.chat_service import ChatService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_chat_service() -> ChatService:
    """Build the request service using the registry's default provider."""
    return ChatService(provider_registry.create())


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> StreamingResponse:
    """Serialize internal chat events into the stable public SSE contract."""

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
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

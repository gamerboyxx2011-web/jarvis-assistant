"""Stateless streaming chat route."""

import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.ai.client import NVIDIAClient, NVIDIAClientError
from app.schemas.chat import ChatRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    """Stream a single NVIDIA NIM response as server-sent events."""

    async def generate_response():
        try:
            client = NVIDIAClient()
            async for chunk in client.chat_completion(
                message=request.message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                content = choices[0].get("delta", {}).get("content", "")
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
        except NVIDIAClientError as exc:
            logger.warning("NVIDIA chat request failed: %s", exc)
            yield f"data: {json.dumps({'error': 'AI provider request failed'})}\n\n"
        except Exception:
            logger.exception("Unexpected chat generation failure")
            yield f"data: {json.dumps({'error': 'Internal chat error'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

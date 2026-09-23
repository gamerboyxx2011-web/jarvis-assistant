"""
JARVIS AI Assistant V3 - Chat Route
"""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.ai.client import NVIDIAClient
from app.config import settings

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(request: dict):
    """
    Chat endpoint that communicates with NVIDIA NIM AI and streams the response.

    Expects JSON with:
    - message: The user's message
    - temperature: Optional sampling temperature (default: 0.7)
    - max_tokens: Optional maximum tokens to generate

    Returns:
        StreamingResponse: Server-sent events stream of the AI response
    """
    # Validate request
    if "message" not in request or not request["message"].strip():
        raise HTTPException(status_code=400, detail="Message is required")

    user_message = request["message"].strip()
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens")

    # Check if NVIDIA NIM is configured
    if not settings.NVIDIA_API_KEY or not settings.NVIDIA_API_KEY.strip():
        raise HTTPException(
            status_code=503,
            detail="NVIDIA NIM AI is not configured. Please set NVIDIA_API_KEY in .env file"
        )

    # Create NVIDIA client
    nvidia_client = NVIDIAClient()

    async def generate_response():
        """Generate streaming response from NVIDIA NIM."""
        try:
            async for chunk in nvidia_client.chat_completion(
                message=user_message,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                # Extract content from chunk if available
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        # Format as Server-Sent Event
                        yield f"data: {json.dumps({'content': content})}\n\n"
        except Exception as e:
            # Yield error as SSE
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # Yield [DONE] to signal end of stream
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

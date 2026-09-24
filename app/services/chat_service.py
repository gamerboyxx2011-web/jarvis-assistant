"""Provider-neutral chat orchestration."""

import asyncio
import logging
from collections.abc import AsyncIterator

from app.errors import ProviderError
from app.providers.base import ChatProvider
from app.providers.models import ProviderChatRequest, ProviderDelta, ProviderUsage
from app.schemas.chat import ChatRequest
from app.schemas.events import (
    ResponseCompleted,
    ResponseDelta,
    ResponseError,
    ResponseEvent,
    ResponseStarted,
    Usage,
)

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, provider: ChatProvider) -> None:
        self._provider = provider

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[ResponseEvent]:
        yield ResponseStarted()
        usage: Usage | None = None
        provider_request = ProviderChatRequest(
            message=request.message,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        try:
            async for item in self._provider.stream_chat(provider_request):
                if isinstance(item, ProviderDelta):
                    yield ResponseDelta(content=item.content)
                elif isinstance(item, ProviderUsage):
                    usage = Usage(
                        input_tokens=item.input_tokens,
                        output_tokens=item.output_tokens,
                        total_tokens=item.total_tokens,
                    )
        except asyncio.CancelledError:
            raise
        except ProviderError as exc:
            logger.warning("AI provider request failed (%s)", type(exc).__name__)
            yield ResponseError(message="AI provider request failed")
            return
        except Exception:
            logger.error("Unexpected chat service failure")
            yield ResponseError(message="Internal chat error")
            return

        yield ResponseCompleted(usage=usage)

"""Provider-neutral chat orchestration."""

import asyncio
import logging
from collections.abc import AsyncIterator

from app.errors import ProviderError
from app.history.models import ConversationNotFoundError
from app.history.store import SQLiteConversationStore
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
    def __init__(
        self,
        provider: ChatProvider,
        conversation_store: SQLiteConversationStore | None = None,
    ) -> None:
        self._provider = provider
        self._conversation_store = conversation_store

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[ResponseEvent]:
        yield ResponseStarted()
        usage: Usage | None = None
        conversation_id = str(request.conversation_id) if request.conversation_id else None

        if conversation_id is not None:
            if self._conversation_store is None:
                yield ResponseError(message="Conversation history is unavailable")
                return
            try:
                await self._conversation_store.get(conversation_id)
            except ConversationNotFoundError:
                yield ResponseError(message="Conversation not found")
                return

        provider_request = ProviderChatRequest(
            message=request.message,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        assistant_parts: list[str] = []

        try:
            async for item in self._provider.stream_chat(provider_request):
                if isinstance(item, ProviderDelta):
                    assistant_parts.append(item.content)
                    yield ResponseDelta(content=item.content)
                elif isinstance(item, ProviderUsage):
                    usage = Usage(
                        item.input_tokens, item.output_tokens, item.total_tokens
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

        if conversation_id is not None and assistant_parts:
            try:
                await self._conversation_store.append_exchange(
                    conversation_id, request.message, "".join(assistant_parts)
                )
            except ConversationNotFoundError:
                yield ResponseError(message="Conversation not found")
                return

        yield ResponseCompleted(usage=usage)

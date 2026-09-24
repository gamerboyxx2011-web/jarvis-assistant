import asyncio

import pytest

from app.errors import ProviderError
from app.providers.models import (
    ProviderChatRequest,
    ProviderDelta,
    ProviderInfo,
    ProviderUsage,
)
from app.schemas.chat import ChatRequest
from app.schemas.events import (
    ResponseCompleted,
    ResponseDelta,
    ResponseError,
    ResponseStarted,
    Usage,
)
from app.services.chat_service import ChatService


class FakeProvider:
    def __init__(self, items=()):
        self.items = items
        self.requests: list[ProviderChatRequest] = []

    @property
    def info(self):
        return ProviderInfo("fake", "fake-model", True, frozenset(), frozenset())

    async def stream_chat(self, request: ProviderChatRequest):
        self.requests.append(request)
        for item in self.items:
            yield item


@pytest.mark.asyncio
async def test_service_normalizes_provider_items_and_usage():
    provider = FakeProvider(
        [
            ProviderDelta("Hi"),
            ProviderDelta(" there"),
            ProviderUsage(input_tokens=2, output_tokens=3, total_tokens=5),
        ]
    )
    service = ChatService(provider)
    request = ChatRequest(message="Hello", temperature=0.5, max_tokens=25)

    events = [event async for event in service.stream_chat(request)]

    assert provider.requests == [ProviderChatRequest("Hello", 0.5, 25)]
    assert events == [
        ResponseStarted(),
        ResponseDelta(content="Hi"),
        ResponseDelta(content=" there"),
        ResponseCompleted(usage=Usage(2, 3, 5)),
    ]


class FailedProvider(FakeProvider):
    async def stream_chat(self, request: ProviderChatRequest):
        if False:
            yield ProviderDelta("")
        raise ProviderError("sensitive provider diagnostic")


@pytest.mark.asyncio
async def test_service_sanitizes_provider_failures():
    events = [
        event
        async for event in ChatService(FailedProvider()).stream_chat(
            ChatRequest(message="Hello")
        )
    ]
    assert events == [
        ResponseStarted(),
        ResponseError(message="AI provider request failed"),
    ]
    assert "sensitive provider diagnostic" not in repr(events)


class CancelledProvider(FakeProvider):
    async def stream_chat(self, request: ProviderChatRequest):
        if False:
            yield ProviderDelta("")
        raise asyncio.CancelledError


@pytest.mark.asyncio
async def test_service_preserves_cancellation():
    service = ChatService(CancelledProvider())
    iterator = service.stream_chat(ChatRequest(message="Hello"))
    assert await anext(iterator) == ResponseStarted()
    with pytest.raises(asyncio.CancelledError):
        await anext(iterator)

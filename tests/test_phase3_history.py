import asyncio
import os

os.environ.setdefault("NVIDIA_API_KEY", "test-key")

import pytest

from app.errors import ProviderError
from app.history.store import SQLiteConversationStore
from app.providers.models import (
    ProviderChatRequest,
    ProviderDelta,
    ProviderInfo,
    ProviderMessage,
)
from app.schemas.chat import ChatRequest
from app.schemas.events import ResponseDelta, ResponseError, ResponseStarted
from app.services.chat_service import ChatService


class FakeProvider:
    def __init__(self):
        self.requests = []

    @property
    def info(self):
        return ProviderInfo("fake", "fake", True, frozenset(), frozenset())

    async def stream_chat(self, request: ProviderChatRequest):
        self.requests.append(request)
        yield ProviderDelta("answer")


class FailedProvider(FakeProvider):
    async def stream_chat(self, request: ProviderChatRequest):
        self.requests.append(request)
        if False:
            yield ProviderDelta("")
        raise ProviderError("upstream failure")


class CancelledProvider(FakeProvider):
    async def stream_chat(self, request: ProviderChatRequest):
        self.requests.append(request)
        if False:
            yield ProviderDelta("")
        raise asyncio.CancelledError


class PartiallyCancelledProvider(FakeProvider):
    async def stream_chat(self, request: ProviderChatRequest):
        self.requests.append(request)
        yield ProviderDelta("partial")
        raise asyncio.CancelledError


def message_pairs(conversation):
    return [(item.role, item.content) for item in conversation.messages]


@pytest.mark.asyncio
async def test_store_persists_complete_exchange(tmp_path):
    path = str(tmp_path / "history.db")
    store = SQLiteConversationStore(path)
    created = await store.create("Test")
    await store.append_exchange(created.id, "hello", "hi")
    loaded = await store.get(created.id)
    assert message_pairs(loaded) == [("user", "hello"), ("assistant", "hi")]
    reloaded = SQLiteConversationStore(path)
    assert (await reloaded.get(created.id)).messages == loaded.messages


@pytest.mark.asyncio
async def test_service_looks_up_conversation_and_appends_exchange(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    conversation = await store.create()
    await store.append_exchange(conversation.id, "first", "reply")
    provider = FakeProvider()

    _ = [event async for event in ChatService(provider, store).stream_chat(
        ChatRequest(message="next", conversation_id=conversation.id)
    )]

    assert provider.requests == [ProviderChatRequest(
        "next",
        history=(
            ProviderMessage("user", "first"),
            ProviderMessage("assistant", "reply"),
        ),
    )]
    assert message_pairs(await store.get(conversation.id)) == [
        ("user", "first"),
        ("assistant", "reply"),
        ("user", "next"),
        ("assistant", "answer"),
    ]


@pytest.mark.asyncio
async def test_user_message_is_persisted_before_provider_stream_starts(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    conversation = await store.create()

    class InspectingProvider(FakeProvider):
        async def stream_chat(self, request: ProviderChatRequest):
            assert message_pairs(await store.get(conversation.id)) == [("user", "hello")]
            assert request.history == ()
            async for item in super().stream_chat(request):
                yield item

    events = [event async for event in ChatService(InspectingProvider(), store).stream_chat(
        ChatRequest(message="hello", conversation_id=conversation.id)
    )]

    assert any(isinstance(event, ResponseDelta) for event in events)
    assert message_pairs(await store.get(conversation.id)) == [
        ("user", "hello"),
        ("assistant", "answer"),
    ]


@pytest.mark.asyncio
async def test_provider_failure_persists_only_user_message(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    conversation = await store.create()
    events = [event async for event in ChatService(FailedProvider(), store).stream_chat(
        ChatRequest(message="hello", conversation_id=conversation.id)
    )]
    assert events == [ResponseStarted(), ResponseError(message="AI provider request failed")]
    assert message_pairs(await store.get(conversation.id)) == [("user", "hello")]


@pytest.mark.asyncio
async def test_cancellation_propagates_and_persists_only_user_message(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    conversation = await store.create()
    iterator = ChatService(CancelledProvider(), store).stream_chat(
        ChatRequest(message="hello", conversation_id=conversation.id)
    )
    assert await anext(iterator) == ResponseStarted()
    with pytest.raises(asyncio.CancelledError):
        await anext(iterator)
    assert message_pairs(await store.get(conversation.id)) == [("user", "hello")]


@pytest.mark.asyncio
async def test_partial_assistant_output_is_not_persisted_on_cancellation(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    conversation = await store.create()
    iterator = ChatService(PartiallyCancelledProvider(), store).stream_chat(
        ChatRequest(message="hello", conversation_id=conversation.id)
    )
    assert await anext(iterator) == ResponseStarted()
    assert await anext(iterator) == ResponseDelta(content="partial")
    with pytest.raises(asyncio.CancelledError):
        await anext(iterator)
    assert message_pairs(await store.get(conversation.id)) == [("user", "hello")]


@pytest.mark.asyncio
async def test_existing_stateless_service_contract_is_unchanged():
    provider = FakeProvider()
    _ = [event async for event in ChatService(provider).stream_chat(
        ChatRequest(message=" hello ")
    )]
    assert provider.requests == [ProviderChatRequest("hello")]

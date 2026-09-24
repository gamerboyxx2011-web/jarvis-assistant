import os

os.environ.setdefault("NVIDIA_API_KEY", "test-key")

import pytest

from app.history.store import SQLiteConversationStore
from app.providers.models import ProviderChatRequest, ProviderDelta, ProviderInfo
from app.schemas.chat import ChatRequest
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


@pytest.mark.asyncio
async def test_store_persists_complete_exchange(tmp_path):
    path = str(tmp_path / "history.db")
    store = SQLiteConversationStore(path)
    created = await store.create("Test")
    await store.append_exchange(created.id, "hello", "hi")
    loaded = await store.get(created.id)
    assert [(item.role, item.content) for item in loaded.messages] == [
        ("user", "hello"),
        ("assistant", "hi"),
    ]
    reloaded = SQLiteConversationStore(path)
    assert (await reloaded.get(created.id)).messages == loaded.messages


@pytest.mark.asyncio
async def test_service_sends_history_and_appends_exchange(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    conversation = await store.create()
    await store.append_exchange(conversation.id, "first", "reply")
    provider = FakeProvider()

    _ = [
        event
        async for event in ChatService(provider, store).stream_chat(
            ChatRequest(message="next", conversation_id=conversation.id)
        )
    ]

    assert [(item.role, item.content) for item in provider.requests[0].messages] == [
        ("user", "first"),
        ("assistant", "reply"),
        ("user", "next"),
    ]
    loaded = await store.get(conversation.id)
    assert [(item.role, item.content) for item in loaded.messages][-2:] == [
        ("user", "next"),
        ("assistant", "answer"),
    ]


@pytest.mark.asyncio
async def test_existing_stateless_service_contract_is_unchanged():
    provider = FakeProvider()
    _ = [
        event
        async for event in ChatService(provider).stream_chat(
            ChatRequest(message=" hello ")
        )
    ]
    assert provider.requests == [ProviderChatRequest("hello")]

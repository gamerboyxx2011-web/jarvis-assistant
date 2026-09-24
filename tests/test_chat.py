import json

import pytest

from app.errors import ProviderError
from app.main import app
from app.providers.models import ProviderChatRequest, ProviderDelta, ProviderInfo
from app.routes.chat import get_chat_service
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


def override_service(provider):
    app.dependency_overrides[get_chat_service] = lambda: ChatService(provider)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_streams_compatible_content_and_one_done(client):
    provider = FakeProvider([ProviderDelta("Hi"), ProviderDelta(" there")])
    override_service(provider)

    response = await client.post(
        "/api/chat",
        json={"message": " Hello ", "temperature": 0.5, "max_tokens": 25},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.text.count("data: [DONE]") == 1
    assert f"data: {json.dumps({'content': 'Hi'})}" in response.text
    assert f"data: {json.dumps({'content': ' there'})}" in response.text
    assert "response.started" not in response.text
    assert "response.delta" not in response.text
    assert "response.completed" not in response.text
    assert provider.requests == [ProviderChatRequest("Hello", 0.5, 25)]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": ""},
        {"message": "   "},
        {"message": 123},
        {"message": "hello", "temperature": -0.1},
        {"message": "hello", "temperature": 2.1},
        {"message": "hello", "max_tokens": 0},
        {"message": "hello", "max_tokens": 8193},
        {"message": "hello", "unexpected": True},
    ],
)
async def test_chat_rejects_invalid_requests(client, payload):
    response = await client.post("/api/chat", json=payload)
    assert response.status_code == 422


class FailedProvider(FakeProvider):
    async def stream_chat(self, request: ProviderChatRequest):
        if False:
            yield ProviderDelta("")
        raise ProviderError("upstream secret diagnostic")


@pytest.mark.asyncio
async def test_provider_error_is_sanitized_and_done_once(client):
    override_service(FailedProvider())
    response = await client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert f"data: {json.dumps({'error': 'AI provider request failed'})}" in response.text
    assert "upstream secret diagnostic" not in response.text
    assert "response.error" not in response.text
    assert response.text.count("data: [DONE]") == 1


@pytest.mark.asyncio
async def test_empty_provider_stream_still_finishes_once(client):
    override_service(FakeProvider())
    response = await client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.text == "data: [DONE]\n\n"

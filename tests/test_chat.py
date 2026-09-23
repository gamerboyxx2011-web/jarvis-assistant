import json

import pytest

from app.ai.client import NVIDIAClient, NVIDIAClientError


@pytest.mark.asyncio
async def test_chat_streams_content_and_one_done(client, monkeypatch):
    async def fake_completion(self, message, temperature=0.7, max_tokens=None):
        assert message == "Hello"
        assert temperature == 0.5
        assert max_tokens == 25
        yield {"choices": [{"delta": {"content": "Hi"}}]}
        yield {"choices": [{"delta": {"content": " there"}}]}

    monkeypatch.setattr(NVIDIAClient, "chat_completion", fake_completion)
    response = await client.post(
        "/api/chat",
        json={"message": " Hello ", "temperature": 0.5, "max_tokens": 25},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.text.count("data: [DONE]") == 1
    assert f"data: {json.dumps({'content': 'Hi'})}" in response.text
    assert f"data: {json.dumps({'content': ' there'})}" in response.text


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


@pytest.mark.asyncio
async def test_provider_error_is_sanitized_and_done_once(client, monkeypatch):
    async def failed_completion(self, message, temperature=0.7, max_tokens=None):
        if False:
            yield {}
        raise NVIDIAClientError("upstream secret diagnostic")

    monkeypatch.setattr(NVIDIAClient, "chat_completion", failed_completion)
    response = await client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert "AI provider request failed" in response.text
    assert "upstream secret diagnostic" not in response.text
    assert response.text.count("data: [DONE]") == 1

import json
from pathlib import Path

import httpx
import pytest
import respx

from app.main import app
from app.providers.model_catalog import CHAT_MODELS, DEFAULT_MODEL_ID, SUPPORTED_MODEL_IDS
from app.providers.models import ProviderChatRequest, ProviderInfo
from app.providers.nvidia import NVIDIAProvider
from app.routes.chat import get_chat_service
from app.services.chat_service import ChatService


class CapturingProvider:
    def __init__(self):
        self.requests = []

    @property
    def info(self):
        return ProviderInfo("fake", DEFAULT_MODEL_ID, True, frozenset(), frozenset())

    async def stream_chat(self, request):
        self.requests.append(request)
        if False:
            yield


def test_all_four_models_are_registered_and_default_is_flash():
    assert [model.id for model in CHAT_MODELS] == [
        "z-ai/glm-5-3-flash",
        "nvidia/nemotron-3.5-lightning-30b-a3b",
        "z-ai/glm-5-3",
        "nvidia/nemotron-3-ultra-550b-a55b",
    ]
    assert len(SUPPORTED_MODEL_IDS) == 4
    assert DEFAULT_MODEL_ID == "z-ai/glm-5-3-flash"


@pytest.mark.asyncio
@pytest.mark.parametrize("model", sorted(SUPPORTED_MODEL_IDS))
@respx.mock
async def test_each_selected_model_reaches_nvidia(model):
    route = respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, text="data: [DONE]\n\n")
    )
    _ = [item async for item in NVIDIAProvider(api_key="test-key").stream_chat(ProviderChatRequest("Hi", model=model))]
    assert json.loads(route.calls.last.request.content)["model"] == model


@pytest.mark.asyncio
async def test_chat_defaults_model_and_rejects_invalid_selection(client):
    provider = CapturingProvider()
    app.dependency_overrides[get_chat_service] = lambda: ChatService(provider)
    try:
        response = await client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 200
        assert provider.requests[0].model == DEFAULT_MODEL_ID
        invalid = await client.post("/api/chat", json={"message": "Hello", "model": "unsupported/model"})
        assert invalid.status_code == 422
        assert len(provider.requests) == 1
    finally:
        app.dependency_overrides.clear()


def test_frontend_selector_preserves_existing_chat_contract():
    root = Path(__file__).parents[1] / "app" / "static"
    html = (root / "index.html").read_text()
    script = (root / "app.js").read_text()
    assert 'id="model-select"' in html
    assert all(model.id in html for model in CHAT_MODELS)
    assert "sessionStorage" in script
    assert "model:e.model.value" in script
    assert 'fetch("/api/chat"' in script
    assert "conversation_id:conversationId" in script
    assert 'fetch("/api/voice"' in script

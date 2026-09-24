import asyncio

import httpx
import pytest
import respx

from app.errors import ProviderError, ProviderTimeoutError
from app.providers.models import ProviderChatRequest, ProviderDelta, ProviderUsage
from app.providers.nvidia import NVIDIAProvider


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_adapter_preserves_request_and_parses_stream():
    route = respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            text=(
                "event: ignored\n"
                "data:\n\n"
                "data: {not-json}\n\n"
                "data: []\n\n"
                'data: {"choices":[]}\n\n'
                'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
                'data: {"choices":[{"delta":{"content":""}}]}\n\n'
                'data: {"usage":{"prompt_tokens":2,"completion_tokens":3,"total_tokens":5}}\n\n'
                "data: [DONE]\n\n"
            ),
        )
    )
    provider = NVIDIAProvider(api_key="test-key")
    request = ProviderChatRequest("Hi", temperature=0.25, max_tokens=42)

    items = [item async for item in provider.stream_chat(request)]

    assert route.called
    sent = route.calls.last.request
    assert sent.headers["authorization"] == "Bearer test-key"
    assert sent.headers["content-type"] == "application/json"
    assert str(sent.url) == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert sent.content
    assert items == [
        ProviderDelta(content="Hello"),
        ProviderUsage(input_tokens=2, output_tokens=3, total_tokens=5),
    ]


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_adapter_omits_optional_max_tokens():
    route = respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, text="data: [DONE]\n\n")
    )
    provider = NVIDIAProvider(api_key="test-key")
    _ = [item async for item in provider.stream_chat(ProviderChatRequest("Hi"))]
    assert b"max_tokens" not in route.calls.last.request.content


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_http_error_is_sanitized():
    respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        return_value=httpx.Response(401, text="sensitive upstream body")
    )
    provider = NVIDIAProvider(api_key="test-key")
    with pytest.raises(ProviderError) as exc_info:
        _ = [item async for item in provider.stream_chat(ProviderChatRequest("Hi"))]
    assert "sensitive upstream body" not in str(exc_info.value)
    assert "401" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_timeout_is_sanitized():
    respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        side_effect=httpx.ReadTimeout("sensitive timeout detail")
    )
    provider = NVIDIAProvider(api_key="test-key")
    with pytest.raises(ProviderTimeoutError, match="timed out") as exc_info:
        _ = [item async for item in provider.stream_chat(ProviderChatRequest("Hi"))]
    assert "sensitive timeout detail" not in str(exc_info.value)


class _CancelledStream:
    async def __aenter__(self):
        raise asyncio.CancelledError

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _CancelledClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def stream(self, *args, **kwargs):
        return _CancelledStream()


@pytest.mark.asyncio
async def test_nvidia_adapter_preserves_cancellation():
    provider = NVIDIAProvider(
        api_key="test-key", client_factory=lambda: _CancelledClient()
    )
    with pytest.raises(asyncio.CancelledError):
        _ = [item async for item in provider.stream_chat(ProviderChatRequest("Hi"))]

import httpx
import pytest
import respx

from app.ai.client import NVIDIAClient, NVIDIAClientError
from app.errors import ProviderError
from app.providers.models import ProviderChatRequest, ProviderDelta
from app.providers.nvidia import NVIDIAProvider


@pytest.mark.asyncio
@respx.mock
async def test_old_client_and_new_adapter_preserve_stream_content_parity():
    stream = (
        "event: ignored\n"
        "data:\n\n"
        "data: {not-json}\n\n"
        'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
        'data: {"choices":[]}\n\n'
        'data: {"choices":[{"delta":{"content":" world"}}]}\n\n'
        "data: [DONE]\n\n"
    )
    respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        side_effect=[
            httpx.Response(200, text=stream),
            httpx.Response(200, text=stream),
        ]
    )

    old_chunks = [chunk async for chunk in NVIDIAClient().chat_completion("Hi")]
    new_items = [
        item
        async for item in NVIDIAProvider().stream_chat(ProviderChatRequest("Hi"))
    ]

    old_content = [
        chunk["choices"][0].get("delta", {}).get("content", "")
        for chunk in old_chunks
        if chunk.get("choices")
    ]
    new_content = [item.content for item in new_items if isinstance(item, ProviderDelta)]
    assert new_content == old_content == ["Hello", " world"]


@pytest.mark.asyncio
@respx.mock
async def test_old_client_and_new_adapter_preserve_sanitized_http_error_parity():
    respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        side_effect=[
            httpx.Response(503, text="sensitive upstream detail"),
            httpx.Response(503, text="sensitive upstream detail"),
        ]
    )

    with pytest.raises(NVIDIAClientError) as old_error:
        _ = [chunk async for chunk in NVIDIAClient().chat_completion("Hi")]
    with pytest.raises(ProviderError) as new_error:
        _ = [
            item
            async for item in NVIDIAProvider().stream_chat(ProviderChatRequest("Hi"))
        ]

    assert "503" in str(old_error.value)
    assert "503" in str(new_error.value)
    assert "sensitive upstream detail" not in str(old_error.value)
    assert "sensitive upstream detail" not in str(new_error.value)

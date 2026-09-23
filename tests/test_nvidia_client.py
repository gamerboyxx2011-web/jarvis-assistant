import httpx
import pytest
import respx

from app.ai.client import NVIDIAClient, NVIDIAClientError


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_client_streams_valid_chunks_and_skips_malformed(capsys):
    route = respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            text=(
                "data: {not-json}\n\n"
                'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
                "data: [DONE]\n\n"
            ),
        )
    )
    chunks = [chunk async for chunk in NVIDIAClient().chat_completion("Hi")]
    assert route.called
    assert chunks == [{"choices": [{"delta": {"content": "Hello"}}]}]
    captured = capsys.readouterr()
    assert "NVIDIA_RAW" not in captured.out
    assert "Hello" not in captured.out


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_http_error_is_sanitized():
    respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        return_value=httpx.Response(401, text="sensitive upstream body")
    )
    with pytest.raises(NVIDIAClientError) as exc_info:
        _ = [chunk async for chunk in NVIDIAClient().chat_completion("Hi")]
    assert "sensitive upstream body" not in str(exc_info.value)
    assert "401" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_nvidia_timeout_is_sanitized():
    respx.post("https://integrate.api.nvidia.com/v1/chat/completions").mock(
        side_effect=httpx.ReadTimeout("timed out")
    )
    with pytest.raises(NVIDIAClientError, match="timed out"):
        _ = [chunk async for chunk in NVIDIAClient().chat_completion("Hi")]

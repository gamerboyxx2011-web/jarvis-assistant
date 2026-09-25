"""NVIDIA NIM adapter for the OpenAI-compatible chat API."""

import asyncio
import json
from collections.abc import AsyncIterator, Callable
from typing import Any

import httpx

from app.config import settings
from app.errors import ProviderError, ProviderTimeoutError
from app.providers.models import (
    ProviderChatRequest,
    ProviderDelta,
    ProviderInfo,
    ProviderStreamItem,
    ProviderUsage,
)


class NVIDIAProvider:
    """Stream provider-neutral chat items from NVIDIA NIM."""

    name = "nvidia"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        client_factory: Callable[[], httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        self.api_key = settings.NVIDIA_API_KEY if api_key is None else api_key
        configured_base_url = settings.NVIDIA_API_BASE_URL if base_url is None else base_url
        self.base_url = configured_base_url.rstrip("/")
        self.model = settings.NVIDIA_MODEL if model is None else model
        self.timeout = timeout
        self._client_factory = client_factory

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            model=self.model,
            configured=bool(self.api_key.strip()),
            supported_options=frozenset({"message", "temperature", "max_tokens"}),
            capabilities=frozenset({"streaming", "usage"}),
        )

    async def stream_chat(
        self, request: ProviderChatRequest
    ) -> AsyncIterator[ProviderStreamItem]:
        url = f"{self.base_url}/chat/completions"
        messages = [
            {"role": message.role, "content": message.content}
            for message in request.history
        ]
        messages.append({"role": "user", "content": request.message})
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self._client_factory() as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                ) as response:
                    if not response.is_success:
                        await response.aread()
                        raise ProviderError(
                            f"NVIDIA NIM returned HTTP {response.status_code}"
                        )

                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        if not data:
                            continue

                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        if not isinstance(chunk, dict):
                            continue

                        choices = chunk.get("choices", [])
                        if choices and isinstance(choices[0], dict):
                            delta = choices[0].get("delta", {})
                            if isinstance(delta, dict):
                                content = delta.get("content", "")
                                if isinstance(content, str) and content:
                                    yield ProviderDelta(content=content)

                        usage = chunk.get("usage")
                        if isinstance(usage, dict):
                            yield ProviderUsage(
                                input_tokens=_optional_int(usage.get("prompt_tokens")),
                                output_tokens=_optional_int(usage.get("completion_tokens")),
                                total_tokens=_optional_int(usage.get("total_tokens")),
                            )
        except asyncio.CancelledError:
            raise
        except ProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("NVIDIA NIM request timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderError("NVIDIA NIM request failed") from exc


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None

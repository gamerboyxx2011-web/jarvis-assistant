"""NVIDIA NIM client for the OpenAI-compatible chat API."""

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import settings


class NVIDIAClientError(Exception):
    """Sanitized NVIDIA client failure safe for internal classification."""


class NVIDIAClient:
    """Stream chat completions from NVIDIA NIM."""

    def __init__(self) -> None:
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_API_BASE_URL.rstrip("/")
        self.model = settings.NVIDIA_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        message: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                ) as response:
                    if not response.is_success:
                        await response.aread()
                        raise NVIDIAClientError(
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
                        if isinstance(chunk, dict):
                            yield chunk
        except NVIDIAClientError:
            raise
        except httpx.TimeoutException as exc:
            raise NVIDIAClientError("NVIDIA NIM request timed out") from exc
        except httpx.HTTPError as exc:
            raise NVIDIAClientError("NVIDIA NIM request failed") from exc

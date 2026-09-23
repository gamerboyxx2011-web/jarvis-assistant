"""
JARVIS AI Assistant V3 - NVIDIA NIM AI Client Abstraction
"""

import json
from typing import AsyncGenerator, Dict, Any
import httpx
from app.config import settings


class NVIDIAClient:
    """Client for communicating with NVIDIA NIM AI through OpenAI-compatible API."""

    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_API_BASE_URL
        self.model = settings.NVIDIA_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(
        self,
        message: str,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a chat completion request to NVIDIA NIM and stream the response.

        Args:
            message: The user's message
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Dictionary containing chunks of the AI response
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": temperature,
            "stream": True
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0
            ) as response:
                if not response.is_success:
                    # Read response body for diagnostic information
                    response_body = await response.aread()
                    # Include NVIDIA NIM's error response in the exception message
                    error_msg = f"NVIDIA NIM API error {response.status_code}: {response_body.decode('utf-8', errors='ignore')}"
                    raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)

                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        print(f"NVIDIA_RAW: {data}")

                        if data.strip() == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
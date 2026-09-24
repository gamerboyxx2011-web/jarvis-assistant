"""Minimal protocol implemented by chat providers."""

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from app.providers.models import ProviderChatRequest, ProviderInfo, ProviderStreamItem


@runtime_checkable
class ChatProvider(Protocol):
    @property
    def info(self) -> ProviderInfo:
        """Return provider identity, configuration, and capabilities."""
        ...

    def stream_chat(self, request: ProviderChatRequest) -> AsyncIterator[ProviderStreamItem]:
        """Stream provider-neutral chat items."""
        ...

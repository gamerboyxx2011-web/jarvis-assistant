"""Provider-neutral request and stream models."""

from dataclasses import dataclass
from typing import Literal

from app.providers.model_catalog import DEFAULT_MODEL_ID


@dataclass(frozen=True, slots=True)
class ProviderMessage:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True, slots=True)
class ProviderChatRequest:
    message: str
    temperature: float = 0.7
    max_tokens: int | None = None
    history: tuple[ProviderMessage, ...] = ()
    model: str = DEFAULT_MODEL_ID


@dataclass(frozen=True, slots=True)
class ProviderDelta:
    content: str


@dataclass(frozen=True, slots=True)
class ProviderUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


ProviderStreamItem = ProviderDelta | ProviderUsage


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    name: str
    model: str
    configured: bool
    supported_options: frozenset[str]
    capabilities: frozenset[str]

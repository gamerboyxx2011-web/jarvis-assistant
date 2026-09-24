"""Conversation history domain models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Message:
    role: str
    content: str
    created_at: str


@dataclass(frozen=True, slots=True)
class Conversation:
    id: str
    title: str | None
    created_at: str
    updated_at: str
    messages: tuple[Message, ...] = ()


class ConversationNotFoundError(LookupError):
    """Raised when a conversation ID does not exist."""

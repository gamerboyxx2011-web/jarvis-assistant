"""Public conversation-history schemas."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.history.models import Conversation


class CreateConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    id: str
    title: str | None
    created_at: str
    updated_at: str
    messages: list[MessageResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, conversation: Conversation) -> "ConversationResponse":
        return cls(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageResponse(
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in conversation.messages
            ],
        )

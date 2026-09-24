"""Conversation history management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.history.dependencies import get_conversation_store
from app.history.models import ConversationNotFoundError
from app.history.store import SQLiteConversationStore
from app.schemas.conversations import CreateConversationRequest, ConversationResponse

router = APIRouter()
Store = Annotated[SQLiteConversationStore, Depends(get_conversation_store)]


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    request: CreateConversationRequest, store: Store
) -> ConversationResponse:
    return ConversationResponse.from_domain(await store.create(request.title))


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(store: Store) -> list[ConversationResponse]:
    return [ConversationResponse.from_domain(item) for item in await store.list()]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str, store: Store
) -> ConversationResponse:
    try:
        conversation = await store.get(conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    return ConversationResponse.from_domain(conversation)


@router.delete(
    "/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_conversation(conversation_id: str, store: Store) -> Response:
    try:
        await store.delete(conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)

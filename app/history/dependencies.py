"""Conversation store dependency."""

from functools import lru_cache

from app.config import settings
from app.history.store import SQLiteConversationStore


@lru_cache(maxsize=1)
def get_conversation_store() -> SQLiteConversationStore:
    return SQLiteConversationStore(settings.HISTORY_DB_PATH)

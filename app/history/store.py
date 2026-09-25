"""SQLite-backed conversation history storage."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from app.history.models import Conversation, ConversationNotFoundError, Message


class SQLiteConversationStore:
    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        if database_path != ":memory:":
            Path(database_path).expanduser().resolve().parent.mkdir(
                parents=True, exist_ok=True
            )
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS messages_conversation_id_id
                ON messages(conversation_id, id);
                """
            )

    async def create(self, title: str | None = None) -> Conversation:
        return await asyncio.to_thread(self._create, title)

    def _create(self, title: str | None) -> Conversation:
        conversation_id = str(uuid4())
        timestamp = _utc_now()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (conversation_id, title, timestamp, timestamp),
            )
        return Conversation(conversation_id, title, timestamp, timestamp)

    async def list(self) -> list[Conversation]:
        return await asyncio.to_thread(self._list)

    def _list(self) -> list[Conversation]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, created_at, updated_at FROM conversations "
                "ORDER BY updated_at DESC, id"
            ).fetchall()
        return [_conversation_from_row(row) for row in rows]

    async def get(self, conversation_id: str) -> Conversation:
        return await asyncio.to_thread(self._get, conversation_id)

    def _get(self, conversation_id: str) -> Conversation:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if row is None:
                raise ConversationNotFoundError(conversation_id)
            message_rows = connection.execute(
                "SELECT role, content, created_at FROM messages "
                "WHERE conversation_id = ? ORDER BY id",
                (conversation_id,),
            ).fetchall()
        return _conversation_from_row(
            row,
            tuple(
                Message(item["role"], item["content"], item["created_at"])
                for item in message_rows
            ),
        )

    async def append_message(
        self,
        conversation_id: str,
        role: Literal["user", "assistant"],
        content: str,
    ) -> None:
        await asyncio.to_thread(self._append_message, conversation_id, role, content)

    def _append_message(
        self,
        conversation_id: str,
        role: Literal["user", "assistant"],
        content: str,
    ) -> None:
        timestamp = _utc_now()
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if exists is None:
                raise ConversationNotFoundError(conversation_id)
            connection.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) "
                "VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, timestamp),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conversation_id),
            )

    async def append_exchange(
        self, conversation_id: str, user_content: str, assistant_content: str
    ) -> None:
        await asyncio.to_thread(
            self._append_exchange, conversation_id, user_content, assistant_content
        )

    def _append_exchange(
        self, conversation_id: str, user_content: str, assistant_content: str
    ) -> None:
        timestamp = _utc_now()
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if exists is None:
                raise ConversationNotFoundError(conversation_id)
            connection.executemany(
                "INSERT INTO messages (conversation_id, role, content, created_at) "
                "VALUES (?, ?, ?, ?)",
                [
                    (conversation_id, "user", user_content, timestamp),
                    (conversation_id, "assistant", assistant_content, timestamp),
                ],
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conversation_id),
            )

    async def delete(self, conversation_id: str) -> None:
        await asyncio.to_thread(self._delete, conversation_id)

    def _delete(self, conversation_id: str) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM conversations WHERE id = ?", (conversation_id,)
            )
            if cursor.rowcount == 0:
                raise ConversationNotFoundError(conversation_id)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conversation_from_row(
    row: sqlite3.Row, messages: Sequence[Message] = ()
) -> Conversation:
    return Conversation(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        messages=tuple(messages),
    )

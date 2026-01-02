"""Conversation memory and persistence using SQLite."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from enum import Enum

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class ConversationType(str, Enum):
    """Types of conversations for personal agent."""
    DAILY_CHECKIN = "daily_checkin"
    WEEKLY_REVIEW = "weekly_review"
    ROUTINE = "routine"
    FINANCE = "finance"
    GOALS = "goals"
    GENERAL = "general"


class ConversationManager:
    """Manages conversation persistence using SQLite."""

    def __init__(self, db_path: str = None):
        """Initialize conversation manager.

        Args:
            db_path: Path to SQLite database. Defaults to data/conversations.db
        """
        if db_path is None:
            # Get project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "conversations.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_type_created 
                ON conversations(type, created_at DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created 
                ON conversations(created_at DESC)
            """)
            conn.commit()
        finally:
            conn.close()

    def create_conversation(
        self,
        conv_type: ConversationType | str,
        title: str = None,
        messages: list[BaseMessage] = None,
    ) -> str:
        """Create a new conversation.

        Args:
            conv_type: Type of conversation (see ConversationType enum)
            title: Optional conversation title
            messages: Optional initial messages

        Returns:
            Conversation ID (UUID)
        """
        conv_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        messages = messages or []
        messages_json = json.dumps(
            [self._message_to_dict(msg) for msg in messages]
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO conversations 
                (id, type, title, created_at, updated_at, messages, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (conv_id, conv_type.value if isinstance(conv_type, ConversationType) else str(conv_type), title, now, now, messages_json, "{}"),
            )
            conn.commit()

        return conv_id

    def save_conversation(
        self,
        conv_id: str,
        messages: list[BaseMessage],
        title: str = None,
    ) -> None:
        """Save or update conversation.

        Args:
            conv_id: Conversation ID
            messages: List of messages to save
            title: Optional updated title
        """
        now = datetime.utcnow().isoformat()
        messages_json = json.dumps(
            [self._message_to_dict(msg) for msg in messages]
        )

        with sqlite3.connect(self.db_path) as conn:
            # Check if conversation exists
            cursor = conn.execute(
                "SELECT id FROM conversations WHERE id = ?", (conv_id,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                if title:
                    conn.execute(
                        """
                        UPDATE conversations 
                        SET messages = ?, updated_at = ?, title = ?
                        WHERE id = ?
                        """,
                        [messages_json, now, title, conv_id],
                    )
                else:
                    conn.execute(
                        """
                        UPDATE conversations 
                        SET messages = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        [messages_json, now, conv_id],
                    )
            else:
                # Create if doesn't exist
                created_at = now
                conv_type_val = conv_type.value if isinstance(conv_type, ConversationType) else str(conv_type)
                messages_json_val = messages_json
                metadata = "{}"

                conn.execute(
                    """
                    INSERT INTO conversations 
                    (id, type, title, created_at, updated_at, messages, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conv_id,
                        conv_type_val,
                        title,
                        created_at,
                        now,
                        messages_json_val,
                        metadata,
                    ),
                )

            conn.commit()

    def load_conversation(self, conv_id: str) -> Optional[dict[str, Any]]:
        """Load conversation by ID.

        Args:
            conv_id: Conversation ID

        Returns:
            Conversation dict with messages, or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, type, title, created_at, updated_at, messages, metadata
                FROM conversations WHERE id = ?
                """,
                (conv_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "type": row[1],
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4],
            "messages": self._deserialize_messages(json.loads(row[5])),
            "metadata": json.loads(row[6]),
        }

    def get_latest_conversation(
        self, conv_type: ConversationType | str = None
    ) -> Optional[dict[str, Any]]:
        """Get the most recent conversation.

        Args:
            conv_type: Optional conversation type filter

        Returns:
            Latest conversation dict, or None if none found
        """
        with sqlite3.connect(self.db_path) as conn:
            if conv_type:
                conv_type_val = conv_type.value if isinstance(conv_type, ConversationType) else str(conv_type)
                query = """
                    SELECT id, type, title, created_at, updated_at, messages, metadata
                    FROM conversations 
                    WHERE type = ?
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                cursor = conn.execute(query, (conv_type_val,))
            else:
                query = """
                    SELECT id, type, title, created_at, updated_at, messages, metadata
                    FROM conversations 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                cursor = conn.execute(query)

            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "type": row[1],
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4],
            "messages": self._deserialize_messages(json.loads(row[5])),
            "metadata": json.loads(row[6]),
        }

    def list_conversations(
        self,
        conv_type: ConversationType | str = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List conversations.

        Args:
            conv_type: Optional type filter
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of conversation dicts (without full message history for performance)
        """
        with sqlite3.connect(self.db_path) as conn:
            if conv_type:
                conv_type_val = conv_type.value if isinstance(conv_type, ConversationType) else str(conv_type)
                query = """
                    SELECT id, type, title, created_at, updated_at
                    FROM conversations 
                    WHERE type = ?
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                cursor = conn.execute(query, (conv_type_val, limit, offset))
            else:
                query = """
                    SELECT id, type, title, created_at, updated_at
                    FROM conversations 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                cursor = conn.execute(query, (limit, offset))

            rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "type": row[1],
                "title": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
            for row in rows
        ]

    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation.

        Args:
            conv_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM conversations WHERE id = ?", (conv_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_today_checkin(self) -> Optional[dict[str, Any]]:
        """Get today's daily check-in conversation."""
        return self.get_latest_conversation(ConversationType.DAILY_CHECKIN)

    def get_week_review(self) -> Optional[dict[str, Any]]:
        """Get latest weekly review conversation."""
        return self.get_latest_conversation(ConversationType.WEEKLY_REVIEW)

    @staticmethod
    def _message_to_dict(message: BaseMessage) -> dict[str, Any]:
        """Convert LangChain message to dictionary."""
        return {
            "type": message.__class__.__name__,
            "content": message.content,
        }

    @staticmethod
    def _deserialize_messages(data: list[dict]) -> list[BaseMessage]:
        """Convert dictionary list back to LangChain messages."""
        messages = []
        for item in data:
            if item["type"] == "HumanMessage":
                messages.append(HumanMessage(content=item["content"]))
            elif item["type"] == "AIMessage":
                messages.append(AIMessage(content=item["content"]))
        return messages

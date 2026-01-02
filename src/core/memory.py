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
            # Habit tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS habit_logs (
                    id TEXT PRIMARY KEY,
                    habit_id TEXT NOT NULL,
                    logged_date TEXT NOT NULL,
                    completed BOOLEAN NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_habit_date 
                ON habit_logs(habit_id, logged_date DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_logged_date 
                ON habit_logs(logged_date DESC)
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

    # Habit tracking methods
    
    def log_habit(
        self,
        habit_id: str,
        completed: bool,
        logged_date: str = None,
        notes: str = None,
    ) -> str:
        """Log a habit completion for a specific date.
        
        Args:
            habit_id: ID of the habit to log
            completed: Whether the habit was completed (True/False)
            logged_date: Date to log for (ISO format, defaults to today)
            notes: Optional notes about the habit
            
        Returns:
            Log entry ID
        """
        if logged_date is None:
            logged_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        log_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO habit_logs
                (id, habit_id, logged_date, completed, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (log_id, habit_id, logged_date, completed, notes, created_at),
            )
            conn.commit()
        
        return log_id
    
    def get_habit_for_date(self, habit_id: str, date: str) -> Optional[dict[str, Any]]:
        """Get habit log for a specific date.
        
        Args:
            habit_id: ID of the habit
            date: Date in ISO format (YYYY-MM-DD)
            
        Returns:
            Habit log dict or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, habit_id, logged_date, completed, notes, created_at
                FROM habit_logs
                WHERE habit_id = ? AND logged_date = ?
                """,
                (habit_id, date),
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "habit_id": row[1],
            "logged_date": row[2],
            "completed": bool(row[3]),
            "notes": row[4],
            "created_at": row[5],
        }
    
    def get_habits_for_date(self, date: str) -> list[dict[str, Any]]:
        """Get all habit logs for a specific date.
        
        Args:
            date: Date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of habit logs
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, habit_id, logged_date, completed, notes, created_at
                FROM habit_logs
                WHERE logged_date = ?
                ORDER BY created_at DESC
                """,
                (date,),
            )
            rows = cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "habit_id": row[1],
                "logged_date": row[2],
                "completed": bool(row[3]),
                "notes": row[4],
                "created_at": row[5],
            }
            for row in rows
        ]
    
    def get_habit_stats(self, habit_id: str, days: int = 7) -> dict[str, Any]:
        """Get habit statistics for the past N days.
        
        Args:
            habit_id: ID of the habit
            days: Number of days to look back (default: 7 for weekly)
            
        Returns:
            Stats dict with completion info
        """
        from datetime import timedelta
        
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=days - 1)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT logged_date, completed
                FROM habit_logs
                WHERE habit_id = ? AND logged_date >= ?
                ORDER BY logged_date DESC
                """,
                (habit_id, start_date.isoformat()),
            )
            rows = cursor.fetchall()
        
        completed_count = sum(1 for row in rows if row[1])
        total_count = len(rows)
        
        # Calculate streak
        streak = 0
        if rows and rows[0][1]:  # If most recent is completed
            for row in rows:
                if row[1]:
                    streak += 1
                else:
                    break
        
        return {
            "habit_id": habit_id,
            "days_tracked": days,
            "completed": completed_count,
            "total": total_count,
            "completion_rate": (completed_count / days * 100) if days > 0 else 0,
            "current_streak": streak,
            "logs": rows,
        }
    
    def get_all_habits_stats(self, days: int = 7) -> dict[str, Any]:
        """Get statistics for all habits.
        
        Args:
            days: Number of days to look back (default: 7 for weekly)
            
        Returns:
            Dict with stats for each habit
        """
        from src.core.habits import HabitTracker
        
        stats = {}
        for habit in HabitTracker.get_all_habits():
            stats[habit.id] = self.get_habit_stats(habit.id, days=days)
        
        return stats
    
    def get_habit_summary(self, days: int = 7) -> str:
        """Get formatted summary of habits for display.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Formatted string with habit summary
        """
        from src.core.habits import HabitTracker
        
        all_stats = self.get_all_habits_stats(days=days)
        
        lines = []
        lines.append(f"\n📊 Habit Summary - Last {days} days")
        lines.append("=" * 50)
        
        for habit in HabitTracker.get_all_habits():
            stats = all_stats[habit.id]
            completed = stats["completed"]
            rate = stats["completion_rate"]
            streak = stats["current_streak"]
            
            status = "✓" if rate >= 80 else "✗" if rate < 50 else "~"
            bar = "█" * int(rate / 10) + "░" * (10 - int(rate / 10))
            
            lines.append(f"\n{status} {habit.name}")
            lines.append(f"   {completed}/{stats['total']} days | {bar} {rate:.0f}%")
            if streak > 0:
                lines.append(f"   🔥 {streak} day streak")
        
        lines.append("\n" + "=" * 50)
        return "\n".join(lines)

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

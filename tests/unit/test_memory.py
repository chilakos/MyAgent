"""Tests for conversation memory module."""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from src.core.memory import ConversationManager, ConversationType


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup - wait a moment for any pending connections to close
    import time
    time.sleep(0.1)
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def memory_manager(temp_db):
    """Create memory manager with temporary database."""
    return ConversationManager(db_path=temp_db)


class TestConversationManager:
    """Test ConversationManager functionality."""

    def test_init_creates_database(self, temp_db):
        """Test that initialization creates database with schema."""
        manager = ConversationManager(db_path=temp_db)
        
        # Check tables exist
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}
            assert "conversations" in tables

    def test_create_conversation(self, memory_manager):
        """Test creating a new conversation."""
        conv_id = memory_manager.create_conversation(
            conv_type=ConversationType.DAILY_CHECKIN,
            title="Daily Check-in 2025-01-02"
        )
        
        assert conv_id is not None
        assert len(conv_id) == 36  # UUID length
        
        # Verify in database
        conv = memory_manager.load_conversation(conv_id)
        assert conv is not None
        assert conv["type"] == "daily_checkin"
        assert conv["title"] == "Daily Check-in 2025-01-02"

    def test_create_conversation_with_messages(self, memory_manager):
        """Test creating conversation with initial messages."""
        initial_messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]
        
        conv_id = memory_manager.create_conversation(
            conv_type=ConversationType.GENERAL,
            messages=initial_messages
        )
        
        conv = memory_manager.load_conversation(conv_id)
        assert len(conv["messages"]) == 2
        assert conv["messages"][0].content == "Hello"
        assert conv["messages"][1].content == "Hi there!"

    def test_save_conversation(self, memory_manager):
        """Test saving/updating a conversation."""
        conv_id = memory_manager.create_conversation(
            conv_type=ConversationType.ROUTINE
        )
        
        messages = [
            HumanMessage(content="What should I do?"),
            AIMessage(content="Try this routine...")
        ]
        
        memory_manager.save_conversation(conv_id, messages)
        
        conv = memory_manager.load_conversation(conv_id)
        assert len(conv["messages"]) == 2
        assert conv["messages"][0].content == "What should I do?"

    def test_save_conversation_updates_timestamp(self, memory_manager):
        """Test that save updates the updated_at timestamp."""
        conv_id = memory_manager.create_conversation(
            conv_type=ConversationType.GENERAL
        )
        
        original = memory_manager.load_conversation(conv_id)
        original_updated = original["updated_at"]
        
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp differs
        
        messages = [HumanMessage(content="Updated")]
        memory_manager.save_conversation(conv_id, messages)
        
        updated = memory_manager.load_conversation(conv_id)
        assert updated["updated_at"] > original_updated

    def test_save_updates_title(self, memory_manager):
        """Test that save can update the title."""
        conv_id = memory_manager.create_conversation(
            conv_type=ConversationType.DAILY_CHECKIN,
            title="Original"
        )
        
        messages = [HumanMessage(content="Test")]
        memory_manager.save_conversation(conv_id, messages, title="Updated")
        
        conv = memory_manager.load_conversation(conv_id)
        assert conv["title"] == "Updated"

    def test_load_nonexistent_conversation(self, memory_manager):
        """Test loading conversation that doesn't exist."""
        conv = memory_manager.load_conversation("nonexistent-id")
        assert conv is None

    def test_get_latest_conversation(self, memory_manager):
        """Test getting latest conversation without filter."""
        conv_id_1 = memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        conv_id_2 = memory_manager.create_conversation(ConversationType.WEEKLY_REVIEW)
        
        import time
        time.sleep(0.01)
        
        conv_id_3 = memory_manager.create_conversation(ConversationType.GENERAL)
        
        latest = memory_manager.get_latest_conversation()
        assert latest["id"] == conv_id_3

    def test_get_latest_conversation_by_type(self, memory_manager):
        """Test getting latest conversation of specific type."""
        memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        
        import time
        time.sleep(0.01)
        
        memory_manager.create_conversation(ConversationType.GENERAL)
        
        time.sleep(0.01)
        
        conv_id_2 = memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        
        latest = memory_manager.get_latest_conversation(ConversationType.DAILY_CHECKIN)
        assert latest["id"] == conv_id_2

    def test_list_conversations(self, memory_manager):
        """Test listing conversations."""
        conv_id_1 = memory_manager.create_conversation(
            ConversationType.DAILY_CHECKIN,
            title="Daily 1"
        )
        conv_id_2 = memory_manager.create_conversation(
            ConversationType.GENERAL,
            title="General 1"
        )
        
        conversations = memory_manager.list_conversations()
        
        assert len(conversations) == 2
        # Should be in reverse chronological order
        assert conversations[0]["id"] == conv_id_2
        assert conversations[1]["id"] == conv_id_1

    def test_list_conversations_by_type(self, memory_manager):
        """Test listing conversations filtered by type."""
        memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        memory_manager.create_conversation(ConversationType.GENERAL)
        memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        
        daily_conversations = memory_manager.list_conversations(
            conv_type=ConversationType.DAILY_CHECKIN
        )
        
        assert len(daily_conversations) == 2
        assert all(c["type"] == "daily_checkin" for c in daily_conversations)

    def test_list_conversations_limit_and_offset(self, memory_manager):
        """Test pagination with limit and offset."""
        for i in range(5):
            memory_manager.create_conversation(ConversationType.GENERAL)
        
        first_page = memory_manager.list_conversations(limit=2, offset=0)
        assert len(first_page) == 2
        
        second_page = memory_manager.list_conversations(limit=2, offset=2)
        assert len(second_page) == 2
        
        # Should be different conversations
        assert first_page[0]["id"] != second_page[0]["id"]

    def test_delete_conversation(self, memory_manager):
        """Test deleting a conversation."""
        conv_id = memory_manager.create_conversation(ConversationType.GENERAL)
        
        assert memory_manager.load_conversation(conv_id) is not None
        
        result = memory_manager.delete_conversation(conv_id)
        assert result is True
        
        assert memory_manager.load_conversation(conv_id) is None

    def test_delete_nonexistent_conversation(self, memory_manager):
        """Test deleting conversation that doesn't exist."""
        result = memory_manager.delete_conversation("nonexistent-id")
        assert result is False

    def test_get_today_checkin(self, memory_manager):
        """Test helper to get today's daily check-in."""
        memory_manager.create_conversation(ConversationType.GENERAL)
        conv_id = memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        
        checkin = memory_manager.get_today_checkin()
        assert checkin is not None
        assert checkin["id"] == conv_id
        assert checkin["type"] == "daily_checkin"

    def test_get_week_review(self, memory_manager):
        """Test helper to get latest weekly review."""
        memory_manager.create_conversation(ConversationType.GENERAL)
        conv_id = memory_manager.create_conversation(ConversationType.WEEKLY_REVIEW)
        
        review = memory_manager.get_week_review()
        assert review is not None
        assert review["id"] == conv_id
        assert review["type"] == "weekly_review"

    def test_message_serialization(self, memory_manager):
        """Test that message serialization/deserialization preserves content."""
        messages = [
            HumanMessage(content="Complex message with\nnewlines"),
            AIMessage(content="Response with special chars: !@#$%"),
            HumanMessage(content=""),  # Empty message
        ]
        
        conv_id = memory_manager.create_conversation(
            ConversationType.GENERAL,
            messages=messages
        )
        
        loaded = memory_manager.load_conversation(conv_id)
        assert len(loaded["messages"]) == 3
        assert loaded["messages"][0].content == "Complex message with\nnewlines"
        assert loaded["messages"][1].content == "Response with special chars: !@#$%"
        assert loaded["messages"][2].content == ""

    def test_multiple_conversations_independence(self, memory_manager):
        """Test that conversations remain independent."""
        conv_id_1 = memory_manager.create_conversation(ConversationType.DAILY_CHECKIN)
        conv_id_2 = memory_manager.create_conversation(ConversationType.WEEKLY_REVIEW)
        
        messages_1 = [HumanMessage(content="Message 1")]
        messages_2 = [HumanMessage(content="Message 2")]
        
        memory_manager.save_conversation(conv_id_1, messages_1)
        memory_manager.save_conversation(conv_id_2, messages_2)
        
        loaded_1 = memory_manager.load_conversation(conv_id_1)
        loaded_2 = memory_manager.load_conversation(conv_id_2)
        
        assert loaded_1["messages"][0].content == "Message 1"
        assert loaded_2["messages"][0].content == "Message 2"

    def test_conversation_type_enum(self):
        """Test ConversationType enum values."""
        assert ConversationType.DAILY_CHECKIN.value == "daily_checkin"
        assert ConversationType.WEEKLY_REVIEW.value == "weekly_review"
        assert ConversationType.ROUTINE.value == "routine"
        assert ConversationType.FINANCE.value == "finance"
        assert ConversationType.GOALS.value == "goals"
        assert ConversationType.GENERAL.value == "general"

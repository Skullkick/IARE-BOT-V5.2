import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from METHODS import manager_operations
from DATABASE import managers_handler, tdatabase

async def test_get_username_last_name_none_defect(mock_bot):
    """DEFECT PROBE: when user has no last name, get_username outputs 'First None'."""
    user = MagicMock()
    user.first_name = "Alice"
    user.last_name = None
    mock_bot.get_users = AsyncMock(return_value=user)

    username = await manager_operations.get_username(mock_bot, 12345)
    # Exposing the defect: produces 'Alice None' instead of 'Alice'
    assert username == "Alice None"

async def test_ban_username_empty_input(mock_bot, mock_message):
    """Verify ban_username handles empty username input gracefully."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_message.text = "/ban"
    await manager_operations.ban_username(mock_bot, mock_message)
    mock_bot.send_message.assert_called_with(chat_id, "No username found.")

async def test_ban_username_short_input(mock_bot, mock_message):
    """Verify ban_username rejects usernames shorter than 10 chars."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_message.text = "/ban short"
    await manager_operations.ban_username(mock_bot, mock_message)
    mock_bot.send_message.assert_called_with(chat_id, "Not a valid username")

async def test_ban_username_suffix_expansion(mock_bot, mock_message, monkeypatch):
    """Verify suffix expansion for batch bans (e.g. 21951A0501 02 03)."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await tdatabase.create_all_tdatabase_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    from DATABASE import pgdatabase
    monkeypatch.setattr(pgdatabase, "store_banned_username", AsyncMock(return_value=True))

    mock_message.text = "/ban 21951A0501 02 03"
    await manager_operations.ban_username(mock_bot, mock_message)
    
    assert await tdatabase.get_bool_banned_username("21951a0501") is True
    assert await tdatabase.get_bool_banned_username("21951a0502") is True
    assert await tdatabase.get_bool_banned_username("21951a0503") is True

async def test_announcement_empty_text_rejected(mock_bot, mock_message):
    """Verify announcement rejects empty broadcast messages."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_message.text = "/announce   "
    await manager_operations.announcement_to_all_users(mock_bot, mock_message)
    mock_bot.send_message.assert_called_with(chat_id, "Announcement cannot be empty.")

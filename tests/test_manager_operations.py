import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from METHODS import manager_operations
from DATABASE import managers_handler, tdatabase

async def test_get_username_last_name_none_handled(mock_bot):
    """Verify get_username handles users without last name without producing 'First None'."""
    user = MagicMock()
    user.first_name = "Alice"
    user.last_name = None
    mock_bot.get_users = AsyncMock(return_value=user)

    username = await manager_operations.get_username(mock_bot, 12345)
    assert username == "Alice"

    # User with last name
    user.last_name = "Smith"
    username_full = await manager_operations.get_username(mock_bot, 12345)
    assert username_full == "Alice Smith"

    # User with no first or last name
    user.first_name = None
    user.last_name = None
    username_unknown = await manager_operations.get_username(mock_bot, 12345)
    assert username_unknown == "Unknown"

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

async def test_announcement_broadcast_with_floodwait_retry(mock_bot, mock_message, monkeypatch):
    """Verify announcement queue processes all items even when FloodWait is encountered."""
    from pyrogram.errors import FloodWait
    from DATABASE import pgdatabase, user_settings

    admin_chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await user_settings.create_user_settings_tables()
    await managers_handler.store_as_admin("Admin", admin_chat_id)

    monkeypatch.setattr(pgdatabase, "get_all_chat_ids", AsyncMock(return_value=[1001, 1002]))

    flood_triggered = False

    async def mock_send_message(chat_id, text, *args, **kwargs):
        nonlocal flood_triggered
        if chat_id == 1001 and not flood_triggered:
            flood_triggered = True
            raise FloodWait(0.01)
        return MagicMock(id=99)

    mock_bot.send_message = AsyncMock(side_effect=mock_send_message)
    mock_bot.edit_message_text = AsyncMock()

    mock_message.text = "/announce Important system update"
    await manager_operations.announcement_to_all_users(mock_bot, mock_message)

    assert flood_triggered is True
    # Initial status message + 1 failed FloodWait + 2 successful messages
    assert mock_bot.send_message.call_count >= 3


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


async def test_verification_to_add_maintainer_forwarded_text_success(mock_bot, mock_message):
    """Verify admin forwarding a text message prompts for maintainer addition."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_target_user = MagicMock()
    mock_target_user.id = 555666
    mock_target_user.first_name = "Bob"
    mock_target_user.last_name = "Smith"
    mock_target_user.username = "bob_smith"

    mock_message.forward_date = 1600000000
    mock_message.forward_from = mock_target_user
    mock_message.text = "Hey check this out"

    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert args[0] == chat_id
    assert "Would you like to add Bob Smith as Maintainer." in args[1]
    assert kwargs.get("reply_markup") is not None


async def test_verification_to_add_maintainer_forwarded_media_no_text(mock_bot, mock_message):
    """Verify admin forwarding media (photo/document/sticker with message.text=None) still prompts."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_target_user = MagicMock()
    mock_target_user.id = 777888
    mock_target_user.first_name = "Charlie"
    mock_target_user.last_name = None
    mock_target_user.username = "charlie_brown"

    mock_message.forward_date = 1600000000
    mock_message.forward_from = mock_target_user
    mock_message.text = None
    mock_message.photo = MagicMock()
    mock_message.caption = "Photo caption"

    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert args[0] == chat_id
    assert "Would you like to add Charlie as Maintainer." in args[1]
    assert kwargs.get("reply_markup") is not None


async def test_verification_to_add_maintainer_forward_privacy_hidden(mock_bot, mock_message):
    """Verify forwarded message with forward_sender_name explains privacy settings."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_message.forward_date = 1600000000
    mock_message.forward_from = None
    mock_message.forward_sender_name = "Secret User"
    mock_message.text = "Hello from hidden profile"

    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "privacy settings hide their user ID" in args[1]
    assert "Secret User" in args[1]


async def test_verification_to_add_maintainer_forward_from_chat(mock_bot, mock_message):
    """Verify forwarded message from a channel informs admin it is not a user."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    channel_mock = MagicMock()
    channel_mock.title = "IARE Updates Channel"
    mock_message.forward_date = 1600000000
    mock_message.forward_from = None
    mock_message.forward_sender_name = None
    mock_message.forward_from_chat = channel_mock
    mock_message.text = "Channel broadcast text"

    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "from a channel or group" in args[1]
    assert "IARE Updates Channel" in args[1]


async def test_verification_to_add_maintainer_reply_to_message(mock_bot, mock_message):
    """Verify replying to a user's message with /add_maintainer resolves target user."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    reply_user = MagicMock()
    reply_user.id = 999111
    reply_user.first_name = "Diana"
    reply_user.last_name = "Prince"
    reply_user.username = "wonder_diana"

    replied_msg = MagicMock()
    replied_msg.forward_date = None
    replied_msg.forward_from = None
    replied_msg.forward_sender_name = None
    replied_msg.from_user = reply_user

    mock_message.forward_date = None
    mock_message.forward_from = None
    mock_message.forward_sender_name = None
    mock_message.forward_from_chat = None
    mock_message.reply_to_message = replied_msg
    mock_message.text = "/add_maintainer"

    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "Would you like to add Diana Prince as Maintainer." in args[1]


async def test_verification_to_add_maintainer_command_args_and_usage(mock_bot, mock_message):
    """Verify /add_maintainer with chat_id argument and empty usage instructions."""
    chat_id = mock_message.chat.id
    await managers_handler.create_required_bot_manager_tables()
    await managers_handler.store_as_admin("Admin", chat_id)

    mock_bot.get_users = AsyncMock(return_value=MagicMock(first_name="Ethan", last_name="Hunt", username="ethan"))

    mock_message.forward_date = None
    mock_message.forward_from = None
    mock_message.forward_sender_name = None
    mock_message.forward_from_chat = None
    mock_message.reply_to_message = None

    # Test with valid chat_id and custom name
    mock_message.text = "/add_maintainer 12345678 Ethan Custom"
    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    args, kwargs = mock_bot.send_message.call_args
    assert "Would you like to add Ethan Custom as Maintainer." in args[1]

    # Test with empty command
    mock_bot.send_message.reset_mock()
    mock_message.text = "/add_maintainer"
    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    args, kwargs = mock_bot.send_message.call_args
    assert "How to add a maintainer" in args[1]


async def test_verification_to_add_maintainer_non_admin_ignored(mock_bot, mock_message):
    """Verify non-admin caller is completely ignored."""
    await managers_handler.create_required_bot_manager_tables()
    # Not storing chat_id as admin
    mock_message.text = "/add_maintainer 12345"
    await manager_operations.verification_to_add_maintainer(mock_bot, mock_message)
    mock_bot.send_message.assert_not_called()


async def test_start_add_maintainer_button_limits_callback_data():
    """Verify button callback_data is strictly <= 64 bytes even with a very long name."""
    from Buttons import manager_buttons

    long_name = "Super Long Name With Many Characters That Exceeds Normal Lengths Easily"
    markup = await manager_buttons.start_add_maintainer_button(9876543210, long_name)
    yes_btn = markup.inline_keyboard[0][0]
    cb_bytes = yes_btn.callback_data.encode("utf-8")
    assert len(cb_bytes) <= 64
    assert yes_btn.callback_data.startswith("manager_add_maintainer_by_admin-")
    assert yes_btn.callback_data.endswith("-9876543210")


async def test_get_server_stats_updated_ui(monkeypatch):
    """Verify get_server_stats returns updated UI formatted code block with stats."""
    import psutil

    stats_str = await manager_operations.get_server_stats(traditional_ui=False)
    assert "```SERVER STATS" in stats_str
    assert "⫷" in stats_str
    assert "CPU" in stats_str
    assert "Memory" in stats_str
    assert "Bot RAM" in stats_str
    assert "Disk" in stats_str
    assert "Network" in stats_str
    assert "Uptime" in stats_str
    assert "⫸" in stats_str


async def test_get_server_stats_traditional_ui():
    """Verify get_server_stats returns traditional UI bold markdown formatted stats."""
    stats_str = await manager_operations.get_server_stats(traditional_ui=True)
    assert "**SERVER STATS**" in stats_str
    assert "```" not in stats_str
    assert "● **CPU:**" in stats_str
    assert "● **Memory:**" in stats_str
    assert "● **Bot RAM:**" in stats_str
    assert "● **Disk:**" in stats_str
    assert "● **Network:**" in stats_str
    assert "● **Uptime:**" in stats_str


async def test_get_server_stats_docker_none_cpu_freq(monkeypatch):
    """Verify get_server_stats handles psutil.cpu_freq() returning None in Docker / Coolify."""
    import psutil
    monkeypatch.setattr(psutil, "cpu_freq", lambda: None)

    # Should not raise AttributeError: 'NoneType' object has no attribute 'current'
    stats_updated = await manager_operations.get_server_stats(traditional_ui=False)
    assert "```SERVER STATS" in stats_updated
    assert "CPU" in stats_updated
    assert "MHz" not in stats_updated

    stats_trad = await manager_operations.get_server_stats(traditional_ui=True)
    assert "**SERVER STATS**" in stats_trad
    assert "● **CPU:**" in stats_trad


async def test_get_server_stats_resilience_to_psutil_exceptions(monkeypatch):
    """Verify get_server_stats gracefully handles network or disk metric exceptions."""
    import psutil
    monkeypatch.setattr(psutil, "net_io_counters", lambda: None)
    monkeypatch.setattr(psutil, "disk_usage", MagicMock(side_effect=Exception("Disk access denied")))

    stats_str = await manager_operations.get_server_stats(traditional_ui=True)
    assert "**SERVER STATS**" in stats_str
    assert "● **Disk:** N/A" in stats_str
    assert "● **Network:** N/A" in stats_str



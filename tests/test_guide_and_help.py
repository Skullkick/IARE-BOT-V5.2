import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from Buttons import buttons
from METHODS import operations
from DATABASE import managers_handler

def test_guide_keyboards_structure():
    student_kb = buttons.get_guide_keyboard(is_manager=False)
    callbacks = [btn.callback_data for row in student_kb.inline_keyboard for btn in row]
    assert "help_login" in callbacks
    assert "help_attendance" in callbacks
    assert "help_labs" in callbacks
    assert "help_settings" in callbacks
    assert "help_tricks" in callbacks
    assert "help_close" in callbacks
    assert "help_admin" not in callbacks

    manager_kb = buttons.get_guide_keyboard(is_manager=True)
    mgr_callbacks = [btn.callback_data for row in manager_kb.inline_keyboard for btn in row]
    assert "help_admin" in mgr_callbacks
    assert "help_close" in mgr_callbacks

@pytest.mark.asyncio
async def test_help_command_sends_protected_message_for_student():
    mock_bot = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.chat.id = 12345

    with patch.object(managers_handler, "fetch_admin_chat_ids", new_callable=AsyncMock) as mock_admins, \
         patch.object(managers_handler, "fetch_maintainer_chat_ids", new_callable=AsyncMock) as mock_maintainers:
        mock_admins.return_value = [99999]
        mock_maintainers.return_value = [88888]

        await operations.help_command(mock_bot, mock_msg)

        mock_bot.send_message.assert_awaited_once()
        args, kwargs = mock_bot.send_message.call_args
        assert args[0] == 12345
        assert kwargs["protect_content"] is True
        assert kwargs["reply_markup"] is not None
        callbacks = [btn.callback_data for row in kwargs["reply_markup"].inline_keyboard for btn in row]
        assert "help_admin" not in callbacks

@pytest.mark.asyncio
async def test_help_command_includes_admin_options_for_admin():
    mock_bot = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.chat.id = 99999

    with patch.object(managers_handler, "fetch_admin_chat_ids", new_callable=AsyncMock) as mock_admins, \
         patch.object(managers_handler, "fetch_maintainer_chat_ids", new_callable=AsyncMock) as mock_maintainers:
        mock_admins.return_value = [99999]
        mock_maintainers.return_value = []

        await operations.help_command(mock_bot, mock_msg)

        mock_bot.send_message.assert_awaited_once()
        args, kwargs = mock_bot.send_message.call_args
        assert args[0] == 99999
        assert kwargs["protect_content"] is True
        callbacks = [btn.callback_data for row in kwargs["reply_markup"].inline_keyboard for btn in row]
        assert "help_admin" in callbacks

@pytest.mark.asyncio
@pytest.mark.parametrize("callback_data, expected_title", [
    ("help_login", "GUIDE: LOGIN & ACCOUNTS"),
    ("help_attendance", "GUIDE: ATTENDANCE, BUNK & BIOMETRIC"),
    ("help_labs", "GUIDE: LAB RECORDS & UPLOADS"),
    ("help_settings", "GUIDE: SETTINGS & PREFERENCES"),
    ("help_tricks", "GUIDE: TIPS & ACCOUNT TRICKS"),
])
async def test_help_sections_callbacks(callback_data, expected_title):
    mock_bot = AsyncMock()
    mock_query = AsyncMock()
    mock_query.data = callback_data
    mock_query.message.chat.id = 12345
    mock_query.from_user.id = 12345

    await buttons.callback_function(mock_bot, mock_query)

    mock_query.edit_message_text.assert_awaited_once()
    called_text = mock_query.edit_message_text.call_args[0][0]
    assert expected_title in called_text

@pytest.mark.asyncio
async def test_help_admin_callback_for_authorized_manager():
    mock_bot = AsyncMock()
    mock_query = AsyncMock()
    mock_query.data = "help_admin"
    mock_query.message.chat.id = 99999
    mock_query.from_user.id = 99999

    with patch.object(managers_handler, "fetch_admin_chat_ids", new_callable=AsyncMock) as mock_admins, \
         patch.object(managers_handler, "fetch_maintainer_chat_ids", new_callable=AsyncMock) as mock_maintainers:
        mock_admins.return_value = [99999]
        mock_maintainers.return_value = []

        await buttons.callback_function(mock_bot, mock_query)

        mock_query.edit_message_text.assert_awaited_once()
        called_text = mock_query.edit_message_text.call_args[0][0]
        assert "GUIDE: ADMIN & MAINTAINER COMMANDS" in called_text

@pytest.mark.asyncio
async def test_help_admin_callback_denies_unauthorized_user():
    mock_bot = AsyncMock()
    mock_query = AsyncMock()
    mock_query.data = "help_admin"
    mock_query.message.chat.id = 12345
    mock_query.from_user.id = 12345

    with patch.object(managers_handler, "fetch_admin_chat_ids", new_callable=AsyncMock) as mock_admins, \
         patch.object(managers_handler, "fetch_maintainer_chat_ids", new_callable=AsyncMock) as mock_maintainers:
        mock_admins.return_value = [99999]
        mock_maintainers.return_value = [88888]

        await buttons.callback_function(mock_bot, mock_query)

        mock_query.edit_message_text.assert_awaited_once()
        called_text = mock_query.edit_message_text.call_args[0][0]
        assert "ACCESS DENIED" in called_text or "Access Denied" in called_text
        assert "GUIDE: ADMIN & MAINTAINER COMMANDS" not in called_text

@pytest.mark.asyncio
async def test_help_menu_callback_respects_authorization():
    mock_bot = AsyncMock()
    
    # Unauthorized student
    mock_query_student = AsyncMock()
    mock_query_student.data = "help_menu"
    mock_query_student.message.chat.id = 12345
    mock_query_student.from_user.id = 12345

    with patch.object(managers_handler, "fetch_admin_chat_ids", new_callable=AsyncMock) as mock_admins, \
         patch.object(managers_handler, "fetch_maintainer_chat_ids", new_callable=AsyncMock) as mock_maintainers:
        mock_admins.return_value = [99999]
        mock_maintainers.return_value = []

        await buttons.callback_function(mock_bot, mock_query_student)
        mock_query_student.edit_message_text.assert_awaited_once()
        student_kb = mock_query_student.edit_message_text.call_args[1]["reply_markup"]
        student_callbacks = [btn.callback_data for row in student_kb.inline_keyboard for btn in row]
        assert "help_admin" not in student_callbacks

    # Authorized manager
    mock_query_mgr = AsyncMock()
    mock_query_mgr.data = "help_menu"
    mock_query_mgr.message.chat.id = 99999
    mock_query_mgr.from_user.id = 99999

    with patch.object(managers_handler, "fetch_admin_chat_ids", new_callable=AsyncMock) as mock_admins, \
         patch.object(managers_handler, "fetch_maintainer_chat_ids", new_callable=AsyncMock) as mock_maintainers:
        mock_admins.return_value = [99999]
        mock_maintainers.return_value = []

        await buttons.callback_function(mock_bot, mock_query_mgr)
        mock_query_mgr.edit_message_text.assert_awaited_once()
        mgr_kb = mock_query_mgr.edit_message_text.call_args[1]["reply_markup"]
        mgr_callbacks = [btn.callback_data for row in mgr_kb.inline_keyboard for btn in row]
        assert "help_admin" in mgr_callbacks

@pytest.mark.asyncio
async def test_help_close_deletes_message():
    mock_bot = AsyncMock()
    mock_query = AsyncMock()
    mock_query.data = "help_close"

    await buttons.callback_function(mock_bot, mock_query)
    mock_query.message.delete.assert_awaited_once()

@pytest.mark.asyncio
async def test_guide_text_updated_vs_traditional_ui():
    # Test all topics in both UI modes
    topics = ["main", "login", "attendance", "labs", "settings", "tricks", "admin"]
    for topic in topics:
        text_updated = buttons.get_guide_text(topic, traditional_ui=False)
        text_trad = buttons.get_guide_text(topic, traditional_ui=True)
        assert text_updated.startswith("```")
        assert text_updated.endswith("```")
        assert "⫷" in text_updated
        assert not text_trad.startswith("```")
        assert "**GUIDE:" in text_trad or "USER GUIDE" in text_trad

@pytest.mark.asyncio
async def test_help_command_respects_traditional_ui():
    mock_bot = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.chat.id = 55555

    from DATABASE import user_settings
    with patch.object(user_settings, "fetch_ui_bool", new_callable=AsyncMock) as mock_ui:
        mock_ui.return_value = (1,)  # Traditional UI
        await operations.help_command(mock_bot, mock_msg)
        called_text = mock_bot.send_message.call_args.kwargs.get("text") or mock_bot.send_message.call_args[0][1]
        assert not called_text.startswith("```")
        assert "USER GUIDE" in called_text

@pytest.mark.asyncio
async def test_help_callbacks_respect_traditional_ui():
    mock_bot = AsyncMock()
    mock_query = AsyncMock()
    mock_query.data = "help_login"
    mock_query.message.chat.id = 55555

    from DATABASE import user_settings
    with patch.object(user_settings, "fetch_ui_bool", new_callable=AsyncMock) as mock_ui:
        mock_ui.return_value = (1,)  # Traditional UI
        await buttons.callback_function(mock_bot, mock_query)
        called_text = mock_query.edit_message_text.call_args[0][0]
        assert not called_text.startswith("```")
        assert "**GUIDE: LOGIN & ACCOUNTS**" in called_text

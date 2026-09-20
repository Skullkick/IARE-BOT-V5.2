import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock
from METHODS import labs_handler, operations, lab_operations

def test_labs_handler_remove_pdf_file_signature():
    """Verify labs_handler.remove_pdf_file requires (bot, chat_id).
    
    DEFECT PROBE: In main.py:125, delete_pdf calls:
        await labs_handler.remove_pdf_file(chat_id)
    with only 1 argument. This test verifies that remove_pdf_file requires 2 arguments.
    """
    sig = inspect.signature(labs_handler.remove_pdf_file)
    params = list(sig.parameters.keys())
    assert params == ["bot", "chat_id"]
    # Calling with only 1 argument raises TypeError
    with pytest.raises(TypeError):
        labs_handler.remove_pdf_file(12345)  # Missing 'bot' argument

def test_auto_login_by_database_signature():
    """Verify operations.auto_login_by_database signature.
    
    DEFECT PROBE: In lab_operations.py:32, it calls:
        await operations.auto_login_by_database(bot, "message", chat_id)
    passing the string literal "message" instead of the message object.
    """
    sig = inspect.signature(operations.auto_login_by_database)
    params = list(sig.parameters.keys())
    assert params == ["bot", "message", "chat_id"]

@pytest.mark.asyncio
async def test_delete_pdf_invokes_remove_pdf_file_with_bot():
    """Verify main.delete_pdf passes (bot, chat_id) to remove_pdf_file."""
    import main
    from unittest.mock import AsyncMock, MagicMock, patch

    mock_bot = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.chat.id = 999888

    with patch("METHODS.labs_handler.remove_pdf_file", new_callable=AsyncMock) as mock_remove:
        mock_remove.return_value = True
        await main.delete_pdf(mock_bot, mock_msg)
        mock_remove.assert_awaited_once_with(mock_bot, 999888)

@pytest.mark.asyncio
async def test_add_maintainer_filter_is_command_only():
    """Verify add_maintainer handler does not trigger on arbitrary forwarded messages."""
    import main
    import inspect
    from pyrogram.handlers import MessageHandler

    # Find the handler for add_maintainer in bot.dispatcher
    found_handler = None
    for group in main.bot.dispatcher.groups.values():
        for handler in group:
            if isinstance(handler, MessageHandler) and handler.callback == main.add_maintainer:
                found_handler = handler
                break

    assert found_handler is not None
    # Verify the filter is strictly for command "add_maintainer" and doesn't match raw forwarded messages
    mock_forwarded_msg = MagicMock()
    mock_forwarded_msg.forward_date = 1234567890
    mock_forwarded_msg.text = "Just a forwarded meme text"
    mock_forwarded_msg.command = None

    # Filters in Pyrogram can be sync or async callables accepting (client, message)
    if callable(found_handler.filters):
        old_me = getattr(main.bot, "me", None)
        main.bot.me = MagicMock(username="test_bot")
        try:
            res = found_handler.filters(main.bot, mock_forwarded_msg)
            if inspect.isawaitable(res):
                res = await res
            assert bool(res) is False, "Filter should NOT match arbitrary forwarded messages"
        finally:
            main.bot.me = old_me


@pytest.mark.asyncio
async def test_forwarded_message_from_admin_invokes_verification(monkeypatch):
    """Verify forwarded_message_from_admin triggers verification_to_add_maintainer for admin."""
    import main
    from METHODS import manager_operations
    from DATABASE import managers_handler

    mock_bot = MagicMock()
    mock_msg = MagicMock()
    mock_msg.chat.id = 112233
    mock_msg.text = "Forwarded message"

    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[112233]))
    monkeypatch.setattr(manager_operations, "verification_to_add_maintainer", AsyncMock())

    await main.forwarded_message_from_admin(mock_bot, mock_msg)
    manager_operations.verification_to_add_maintainer.assert_awaited_once_with(mock_bot, mock_msg)

    # When sender is not an admin, verification is not called
    manager_operations.verification_to_add_maintainer.reset_mock()
    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[999999]))
    await main.forwarded_message_from_admin(mock_bot, mock_msg)
    manager_operations.verification_to_add_maintainer.assert_not_called()




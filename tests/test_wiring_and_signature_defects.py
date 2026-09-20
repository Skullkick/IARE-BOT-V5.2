import inspect
import pytest
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

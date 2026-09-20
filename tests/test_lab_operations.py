import pytest
from bs4 import BeautifulSoup
from METHODS import lab_operations
from DATABASE import user_settings, tdatabase

async def test_fetch_available_labs_missing_delimiter_handled(mock_bot, mock_message, monkeypatch):
    """Verify options missing ' - ' separator are parsed gracefully without IndexError."""
    chat_id = mock_message.chat.id
    await user_settings.create_user_settings_tables()
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, '{"username": "test", "cookies": {}}', "test")

    # HTML with an option that lacks ' - '
    html_without_hyphen = """
    <html>
    <body>
    <select id="ddlsub_code">
        <option value="">Select Lab</option>
        <option value="1">InvalidFormatWithoutHyphen</option>
    </select>
    </body>
    </html>
    """
    async def mock_fetch(url, cookies):
        return html_without_hyphen
    monkeypatch.setattr(lab_operations, "async_fetch_page", mock_fetch)

    res = await lab_operations.fetch_available_labs(mock_bot, mock_message)
    assert isinstance(res, dict)
    assert res == {"InvalidFormatWithoutHyphen": "1"}

async def test_get_week_details_empty_tr_defect():
    """DEFECT PROBE: table row without <td> raises unhandled IndexError in get_week_details."""
    html_with_empty_tr = """
    <table>
    <tr><th>Week</th><th>Name</th></tr>
    <tr><!-- empty row with no td --></tr>
    </table>
    """
    submitted_records = ({}, [])
    with pytest.raises(IndexError):
        await lab_operations.get_week_details(
            html_with_empty_tr,
            submitted_records,
            all_weeks_numbers_bool=True,
            submitted_weeks_bool=False,
            not_submitted_weeks_bool=False,
            can_delete_weeks_bool=False
        )

async def test_get_week_details_duplicate_entries():
    """Verify get_week_details handles weeks with multiple submissions."""
    html = """
    <table>
    <tr><th>Week</th></tr>
    <tr><td>Week 1</td></tr>
    <tr><td>Week 2</td></tr>
    <tr><td>Week 3</td></tr>
    </table>
    """
    # Week 1 has 2 submissions
    submitted_records = (
        {
            "1": [{"mark": 10}, {"mark": 8}],
            "2": [{"mark": 9}]
        },
        []
    )
    submitted_weeks = await lab_operations.get_week_details(
        html,
        submitted_records,
        all_weeks_numbers_bool=False,
        submitted_weeks_bool=True,
        not_submitted_weeks_bool=False,
        can_delete_weeks_bool=False
    )
    # Line 107-109 appends for each entry, resulting in [1, 1, 2] instead of deduplicated [1, 2]
    assert submitted_weeks == [1, 1, 2]

async def test_get_marks_by_week_exempted():
    """Verify exempted weeks return None for marks."""
    submitted_records = (
        {"1": [{"mark": 10}], "2": [{"mark": 8}]},
        [2]  # Week 2 is exempted
    )
    mark_1 = await lab_operations.get_marks_by_week(submitted_records, 1)
    mark_2 = await lab_operations.get_marks_by_week(submitted_records, 2)
    assert mark_1 == 10
    assert mark_2 is None

async def test_upload_lab_record_high_compression_prompt(mock_bot, mock_message, monkeypatch, tmp_path):
    """Verify that upload_lab_record pauses and sends a 3-button prompt when high compression occurs."""
    from METHODS import labs_handler, pdf_compressor
    chat_id = mock_message.chat.id

    async def mock_check_above_1mb(cid):
        return True

    async def mock_check_recieved(bot, cid):
        return True, False

    async def mock_compress(bot, cid):
        # Set metrics indicating high compression
        pdf_compressor._COMPRESSION_METRICS[str(cid)] = {
            "chat_id": cid,
            "tier_index": 3,
            "quality": 35,
            "max_dimension": 800,
            "grayscale": True,
            "initial_size": 10 * 1024 * 1024,
            "final_size": 800 * 1024,
            "is_high_compression": True,
        }
        return True

    async def mock_check_after(cid):
        return False, 0.8

    monkeypatch.setattr(labs_handler, "check_pdf_size_above_1mb", mock_check_above_1mb)
    monkeypatch.setattr(labs_handler, "check_recieved_pdf_file", mock_check_recieved)
    monkeypatch.setattr(labs_handler, "check_pdf_size_after_compression", mock_check_after)
    monkeypatch.setattr(pdf_compressor, "compress_pdf", mock_compress)

    # Call upload_lab_record
    await lab_operations.upload_lab_record(
        mock_bot,
        mock_message,
        title="Test Title",
        subject_code="CS101",
        week_no=1,
        bypass_confirmation=False,
    )

    # Assert that prompt message was sent with inline keyboard containing the 3 buttons
    assert mock_bot.send_message.call_count >= 2
    last_call = mock_bot.send_message.call_args
    assert "High Compression Notice" in last_call[0][1]
    reply_markup = last_call[1]["reply_markup"]
    callbacks = [btn.callback_data for row in reply_markup.inline_keyboard for btn in row]
    assert "confirm_lab_upload" in callbacks
    assert "resend_lab_pdf" in callbacks
    assert "cancel_complete_lab_operation" in callbacks
    assert len(reply_markup.inline_keyboard) == 2
    assert [btn.text for btn in reply_markup.inline_keyboard[0]] == ["Confirm", "Resend"]
    assert [btn.text for btn in reply_markup.inline_keyboard[1]] == ["Cancel"]

async def test_lab_confirmation_callbacks(mock_bot, monkeypatch):
    """Verify confirm_lab_upload, resend_lab_pdf, and cancel_complete_lab_operation callbacks."""
    from Buttons import buttons
    from METHODS import labs_handler, pdf_compressor
    from unittest.mock import AsyncMock, MagicMock

    chat_id = 777
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_lab_info(chat_id, "Exp 1", "SUB101", 1, get_title=True)
    await tdatabase.store_pdf_status(chat_id, 0)
    pdf_compressor._COMPRESSION_METRICS[str(chat_id)] = {"is_high_compression": True}

    mock_cb = MagicMock()
    mock_cb.message = MagicMock()
    mock_cb.message.chat.id = chat_id
    mock_cb.message.delete = AsyncMock()
    mock_cb.answer = AsyncMock()
    mock_cb.edit_message_text = AsyncMock()

    # 1. Test resend_lab_pdf callback
    mock_cb.data = "resend_lab_pdf"
    await buttons.callback_function(mock_bot, mock_cb)
    status = await tdatabase.fetch_pdf_status(chat_id)
    assert int(status) == 1  # Re-armed for new PDF intake
    assert pdf_compressor.get_compression_metrics(chat_id) == {}  # Metrics cleared
    assert mock_cb.edit_message_text.called

    # 2. Test cancel_complete_lab_operation callback
    mock_cb.data = "cancel_complete_lab_operation"
    await buttons.callback_function(mock_bot, mock_cb)
    info = await tdatabase.fetch_required_lab_info(chat_id)
    assert info is None  # Entire row wiped
    status = await tdatabase.fetch_pdf_status(chat_id)
    assert status is None  # Status cleared
    assert mock_cb.edit_message_text.called


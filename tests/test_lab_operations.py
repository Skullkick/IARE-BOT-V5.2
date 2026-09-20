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

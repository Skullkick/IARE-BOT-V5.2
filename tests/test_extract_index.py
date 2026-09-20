import pytest
from CONFIGURE import extract_index
from DATABASE import tdatabase

VALID_ATTENDANCE_HTML = """
<html>
<body>
<table>
<thead>
<tr>
    <th>S.No</th>
    <th>Course Code</th>
    <th>Course Name</th>
    <th>Type</th>
    <th>Short Name</th>
    <th>Conducted</th>
    <th>Attended</th>
    <th>Attendance %</th>
    <th>Status</th>
</tr>
</thead>
<tbody>
<tr><td>1</td><td>CS501</td><td>Operating Systems</td><td>Core</td><td>OS</td><td>40</td><td>35</td><td>87.5</td><td>Regular</td></tr>
</tbody>
</table>
</body>
</html>
"""

MISSING_HEADER_ATTENDANCE_HTML = """
<html>
<body>
<table>
<thead>
<tr>
    <th>S.No</th>
    <th>Course Code</th>
    <th>Course Name</th>
    <!-- Missing Conducted, Attended, Attendance %, Status -->
</tr>
</thead>
</table>
</body>
</html>
"""

NO_THEAD_HTML = """
<html>
<body>
<table>
<tbody>
<tr><td>No thead here</td></tr>
</tbody>
</table>
</body>
</html>
"""

async def test_get_attendance_indexes_valid_html(mock_bot, mock_message, monkeypatch):
    """Verify standard HTML yields expected 5-tuple column indices."""
    chat_id = mock_message.chat.id
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, '{"username": "test", "cookies": {}}', "test")

    async def mock_fetch(url, cookies):
        return VALID_ATTENDANCE_HTML
    monkeypatch.setattr(extract_index, "async_fetch_page", mock_fetch)

    res = await extract_index.get_attendance_indexes(mock_bot, mock_message)
    # Course Name: 2, Conducted: 5, Attended: 6, Attendance %: 7, Status: 8
    assert res == (2, 5, 6, 7, 8)

async def test_get_attendance_indexes_missing_header_defect(mock_bot, mock_message, monkeypatch):
    """DEFECT PROBE: missing required headers catches KeyError and reports to user."""
    chat_id = mock_message.chat.id
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, '{"username": "test", "cookies": {}}', "test")

    async def mock_fetch(url, cookies):
        return MISSING_HEADER_ATTENDANCE_HTML
    monkeypatch.setattr(extract_index, "async_fetch_page", mock_fetch)

    res = await extract_index.get_attendance_indexes(mock_bot, mock_message)
    assert res is None
    mock_bot.send_message.assert_called_once()
    assert "Error :" in mock_bot.send_message.call_args[0][1]

async def test_get_attendance_indexes_no_thead_crash(mock_bot, mock_message, monkeypatch):
    """DEFECT PROBE: table without <thead> causes AttributeError when accessing data.thead.tr."""
    chat_id = mock_message.chat.id
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, '{"username": "test", "cookies": {}}', "test")

    async def mock_fetch(url, cookies):
        return NO_THEAD_HTML
    monkeypatch.setattr(extract_index, "async_fetch_page", mock_fetch)

    res = await extract_index.get_attendance_indexes(mock_bot, mock_message)
    assert res is None
    mock_bot.send_message.assert_called_once()
    assert "Error :" in mock_bot.send_message.call_args[0][1]

async def test_get_pat_indexes_missing_table_unhandled_crash(mock_bot, mock_message, monkeypatch):
    """DEFECT PROBE: get_pat_indexes lacks try/except and crashes with unhandled IndexError when < 3 tables exist."""
    chat_id = mock_message.chat.id
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, '{"username": "test", "cookies": {}}', "test")

    # Only 1 table on the page instead of required 3
    async def mock_fetch(url, cookies):
        return "<html><body><table><tr><th>Only 1 Table</th></tr></table></body></html>"
    monkeypatch.setattr(extract_index, "async_fetch_page", mock_fetch)

    with pytest.raises(IndexError):
        await extract_index.get_pat_indexes(mock_bot, mock_message)

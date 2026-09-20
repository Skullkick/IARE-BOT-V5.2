import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from METHODS import operations, portal_client
from DATABASE import user_settings, tdatabase, pgdatabase

async def test_integration_ui_mode_none_handled_gracefully(mock_bot, mock_message):
    """VERIFIED: When user has no prior settings, operations.logout executes without TypeError."""
    chat_id = mock_message.chat.id
    await user_settings.create_user_settings_tables()
    await tdatabase.create_all_tdatabase_tables()
    
    # Should execute cleanly without raising TypeError: 'NoneType' object is not subscriptable
    await operations.logout(mock_bot, mock_message)
    assert mock_bot.send_message.called

async def test_integration_banned_user_rejected_on_autologin(mock_bot, mock_message, monkeypatch):
    """Integration Test: Banned user attempting auto-login gets blocked and purged."""
    chat_id = 40001
    username = "21951A0588"
    password = "some_password"

    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()

    # Store credentials and ban the user
    await tdatabase.store_credentials_in_database(chat_id, username, password)
    await tdatabase.store_banned_username(username.lower())

    # Mock postgres removal so network is not attempted
    monkeypatch.setattr(pgdatabase, "remove_saved_credentials_silent", AsyncMock(return_value=True))

    res = await operations.auto_login_by_database(mock_bot, mock_message, chat_id)
    assert res is False

    # Credentials should be purged from local database
    assert await tdatabase.fetch_credentials_from_database(chat_id) == (None, None)

async def test_integration_logout_clears_session_and_cache(mock_bot, mock_message):
    """Integration Test: Logout removes session and flushes portal cache when settings and full session payload exist."""
    chat_id = mock_message.chat.id
    username = "21951A0512"

    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, json.dumps({"username": username, "cookies": {}, "headers": {}}), username)
    portal_client._PORTAL_CACHE[(chat_id, "attendance")] = "<html>cached</html>"

    await operations.logout(mock_bot, mock_message)

    # Verify session is wiped
    assert await tdatabase.load_user_session(chat_id) is None
    # Verify cache is evicted
    assert (chat_id, "attendance") not in portal_client._PORTAL_CACHE
    mock_message.reply.assert_called_with("Logout successful.")

async def test_integration_logout_missing_headers_leaves_stale_session_defect(mock_bot, mock_message):
    """DEFECT PROBE: When session payload lacks 'headers', logout refuses to purge the session.
    
    In operations.py:230:
        if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
            ...
            return
    If a session only contains 'username' and 'cookies' (e.g. from an external login or API token),
    logout treats the user as unauthenticated and returns without deleting the session, leaving stale credentials!
    """
    chat_id = mock_message.chat.id
    username = "21951A0512"

    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()
    # Missing 'headers' key
    await tdatabase.store_user_session(chat_id, json.dumps({"username": username, "cookies": {}}), username)

    await operations.logout(mock_bot, mock_message)

    # Session was NOT deleted despite user calling logout!
    stale_session = await tdatabase.load_user_session(chat_id)
    assert stale_session is not None, "Defect confirmed: stale session was not purged"


async def test_integration_attendance_chunking_for_telegram_limit(mock_bot, mock_message, monkeypatch):
    """Integration Test: Large course lists exceeding 4000 chars are split into safe chunks."""
    chat_id = mock_message.chat.id
    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, json.dumps({"username": "test", "cookies": {}}), "test")

    # Generate an HTML table with 40 courses to exceed 4000 characters
    rows_html = ""
    for i in range(40):
        rows_html += f"<tr><td>{i+1}</td><td>C{i:03d}</td><td>Advanced Deep Learning Course Number {i:02d}</td><td>Core</td><td>ADL</td><td>50</td><td>45</td><td>90.0</td><td>Regular</td></tr>"

    large_html = f"""
    <html>
    <body>
    <table class="table table-striped table-bordered table-hover table-head-fixed responsive"><thead><tr><th>Dummy</th></tr></thead></table>
    <table class="table table-striped table-bordered table-hover table-head-fixed responsive">
    <thead>
    <tr>
        <th>S.No</th><th>Code</th><th>Course Name</th><th>Type</th><th>Short</th>
        <th>Conducted</th><th>Attended</th><th>Attendance %</th><th>Status</th>
    </tr>
    </thead>
    <tbody>
    {rows_html}
    </tbody>
    </table>
    </body>
    </html>
    """

    async def mock_fetch(url, cookies, chat_id=None, cache_action=None):
        return large_html
    monkeypatch.setattr(operations, "async_fetch_page", mock_fetch)

    await operations.attendance(mock_bot, mock_message)

    # Because full_msg > 4000, send_message should have been called multiple times (header, chunks, footer)
    assert mock_bot.send_message.call_count >= 3
    # Verify none of the sent message chunks exceed Telegram's 4096 character limit
    for call in mock_bot.send_message.call_args_list:
        msg_text = call[0][1]
        assert len(msg_text) <= 4096

async def test_integration_banned_user_fail_closed_when_pg_fails(mock_bot, mock_message, monkeypatch):
    """Security Test: Banned user auto-login fails closed even if PostgreSQL raises an exception."""
    chat_id = 40002
    username = "21951A0599"
    password = "secret_password"

    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()

    await tdatabase.store_credentials_in_database(chat_id, username, password)
    await tdatabase.store_banned_username(username.lower())

    # Simulate Postgres completely crashing / throwing exception
    monkeypatch.setattr(pgdatabase, "remove_saved_credentials_silent", AsyncMock(side_effect=Exception("DB Connection Timeout")))

    res = await operations.auto_login_by_database(mock_bot, mock_message, chat_id)
    # Must fail closed: return False, NEVER authenticate the banned user
    assert res is False
    assert await tdatabase.fetch_credentials_from_database(chat_id) == (None, None)

async def test_perform_sync_labs_data_success(mock_bot, monkeypatch):
    """Verify perform_sync_labs_data parses postgres rows and persists them to SQLite without TypeError."""
    from DATABASE import managers_handler
    await tdatabase.create_all_tdatabase_tables()
    await managers_handler.create_required_bot_manager_tables()
    
    mock_pg_data = [
        (50001, "A5501", "Week 1, Week 2"),
        (50002, "A5502", "Week 1"),
    ]
    monkeypatch.setattr(pgdatabase, "get_all_lab_subjects_and_weeks_data", AsyncMock(return_value=mock_pg_data))

    await operations.perform_sync_labs_data(mock_bot)

    info1 = await tdatabase.fetch_required_lab_info(50001)
    info2 = await tdatabase.fetch_required_lab_info(50002)
    assert info1 is not None
    assert info1[1] == "A5501"
    assert info2 is not None
    assert info2[1] == "A5502"


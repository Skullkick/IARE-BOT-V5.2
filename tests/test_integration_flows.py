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

async def test_integration_logout_missing_headers_clears_session(mock_bot, mock_message):
    """Verify that when session payload lacks 'headers', logout purges the session successfully."""
    chat_id = mock_message.chat.id
    username = "21951A0512"

    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()
    # Missing 'headers' key - only contains username and cookies
    await tdatabase.store_user_session(chat_id, json.dumps({"username": username, "cookies": {}}), username)

    await operations.logout(mock_bot, mock_message)

    # Session is now properly deleted
    session = await tdatabase.load_user_session(chat_id)
    assert session is None
    mock_message.reply.assert_called_with("Logout successful.")

async def test_integration_logout_user_and_remove_purges_stale_session(mock_bot, mock_message):
    """Verify logout_user_and_remove always purges session row even when cookies are missing."""
    chat_id = mock_message.chat.id
    username = "21951A0513"

    await user_settings.create_user_settings_tables()
    await tdatabase.create_all_tdatabase_tables()
    # Malformed session without cookies
    await tdatabase.store_user_session(chat_id, json.dumps({"username": username}), username)

    await operations.logout_user_and_remove(mock_bot, mock_message)

    assert await tdatabase.load_user_session(chat_id) is None
    mock_bot.send_message.assert_called_with(chat_id, text="You are already logged out.")


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

async def test_delete_subjects_and_weeks_data_lifecycle(mock_bot):
    """Verify delete_subjects_and_weeks_data cleans up user upload info without AttributeError."""
    chat_id = 60001
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_lab_info(chat_id, title="Exp 1", subject_code="CS501", week_index=1, get_title=True)
    assert await tdatabase.fetch_required_lab_info(chat_id) is not None

    # Call the alias used by Buttons/buttons.py:970
    await tdatabase.delete_subjects_and_weeks_data(chat_id)
    assert await tdatabase.fetch_required_lab_info(chat_id) is None

async def test_sync_databases_end_to_end(mock_bot, monkeypatch):
    """Verify sync_databases synchronizes all tables from PostgreSQL to local SQLite."""
    from DATABASE import managers_handler
    await user_settings.create_user_settings_tables()
    await tdatabase.create_all_tdatabase_tables()
    await managers_handler.create_required_bot_manager_tables()

    # Mock all PostgreSQL responses with exact schema
    monkeypatch.setattr(pgdatabase, "get_all_index_values", AsyncMock(return_value=[("attendance", '{"Course Name": 1}')]))
    monkeypatch.setattr(pgdatabase, "get_bot_managers_data", AsyncMock(return_value=[
        (77777, True, False, "SuperAdmin", "all", True, True, True, True, True, True, True, True, True, True)
    ]))
    monkeypatch.setattr(pgdatabase, "get_all_credentials", AsyncMock(return_value=[(77777, "21951A0590", "password_123")]))
    monkeypatch.setattr(pgdatabase, "get_all_user_settings", AsyncMock(return_value=[(77777, 80.0, 75.0, False, True)]))
    monkeypatch.setattr(pgdatabase, "get_all_banned_usernames", AsyncMock(return_value=[("21951A0599",)]))
    monkeypatch.setattr(pgdatabase, "get_all_cgpa_trackers", AsyncMock(return_value=[]))
    monkeypatch.setattr(pgdatabase, "get_all_cie_tracker_data", AsyncMock(return_value=[]))
    monkeypatch.setattr(pgdatabase, "get_all_reports", AsyncMock(return_value=[]))

    # Execute sync
    await operations.sync_databases(mock_bot)

    # Verify synced data in SQLite
    creds = await tdatabase.fetch_credentials_from_database(77777)
    assert creds == ("21951A0590", "password_123")
    assert await tdatabase.get_bool_banned_username("21951A0599") is True
    assert 77777 in await managers_handler.fetch_admin_chat_ids()

async def test_sync_databases_postgres_down_fail_safe(mock_bot, monkeypatch):
    """Verify sync_databases handles PostgreSQL outage gracefully without unhandled exceptions."""
    from DATABASE import managers_handler
    await user_settings.create_user_settings_tables()
    await tdatabase.create_all_tdatabase_tables()
    await managers_handler.create_required_bot_manager_tables()

    # Simulate Postgres failure returning False or raising exception
    monkeypatch.setattr(pgdatabase, "get_all_index_values", AsyncMock(side_effect=Exception("Connection refused")))
    monkeypatch.setattr(pgdatabase, "get_bot_managers_data", AsyncMock(return_value=False))
    monkeypatch.setattr(pgdatabase, "get_all_credentials", AsyncMock(return_value=False))
    monkeypatch.setattr(pgdatabase, "get_all_user_settings", AsyncMock(return_value=False))
    monkeypatch.setattr(pgdatabase, "get_all_banned_usernames", AsyncMock(side_effect=Exception("Timeout")))
    monkeypatch.setattr(pgdatabase, "get_all_cgpa_trackers", AsyncMock(return_value=False))
    monkeypatch.setattr(pgdatabase, "get_all_cie_tracker_data", AsyncMock(return_value=False))
    monkeypatch.setattr(pgdatabase, "get_all_reports", AsyncMock(return_value=False))

    # Should complete safely without crashing
    await operations.sync_databases(mock_bot)


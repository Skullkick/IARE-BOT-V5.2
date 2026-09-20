"""
Comprehensive multi-phase test suite for iare_mcp_server.py.

Covers:
- Phase 1: Diagnostic tools (check_portal_status, read_recent_errors, get_system_health)
- Phase 2: Report retrieval and profile context (get_pending_reports, get_user_profile_context)
- Phase 3: One-shot ticket resolution, concurrency protection, and Telegram API error handling
- Phase 4: End-to-end MCP protocol invocation via mcp.call_tool()
"""

import os
import json
import sqlite3
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

import iare_mcp_server
from DATABASE import tdatabase, pgdatabase, managers_handler, user_settings


# ---------------------------------------------------------------------------
# Phase 1: Diagnostic Tools
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_check_portal_status_success(monkeypatch):
    """Verify check_portal_status reports online and latency when portal responds 200."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    async def mock_get(*args, **kwargs):
        return mock_resp

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await iare_mcp_server.check_portal_status()
    assert result["online"] is True
    assert result["status_code"] == 200
    assert result["error"] is None
    assert isinstance(result["latency_ms"], int)


@pytest.mark.asyncio
async def test_check_portal_status_timeout(monkeypatch):
    """Verify check_portal_status catches TimeoutException and reports 504."""
    async def mock_get(*args, **kwargs):
        raise httpx.TimeoutException("Connection timed out")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await iare_mcp_server.check_portal_status()
    assert result["online"] is False
    assert result["status_code"] == 504
    assert "timed out" in result["error"]


@pytest.mark.asyncio
async def test_check_portal_status_network_error(monkeypatch):
    """Verify check_portal_status catches generic network failure and reports 0."""
    async def mock_get(*args, **kwargs):
        raise Exception("DNS resolution failed")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await iare_mcp_server.check_portal_status()
    assert result["online"] is False
    assert result["status_code"] == 0
    assert "DNS resolution failed" in result["error"]


@pytest.mark.asyncio
async def test_read_recent_errors(tmp_path):
    """Verify read_recent_errors safely tails and filters log files."""
    log_file = str(tmp_path / "test_bot_errors.log")

    # Non-existent file
    missing_result = await iare_mcp_server.read_recent_errors(log_file=str(tmp_path / "nonexistent.log"))
    assert "does not exist" in missing_result[0]

    # Create dummy log with various chat IDs
    sample_lines = [
        "2026-09-20 10:00:00 [ERROR] chat_id 11111: Failed to parse attendance table\n",
        "2026-09-20 10:01:00 [ERROR] chat_id 22222: Lab PDF exceeded 1MB\n",
        "2026-09-20 10:02:00 [ERROR] chat_id 11111: Network timeout connecting to portal\n",
    ]
    with open(log_file, "w", encoding="utf-8") as f:
        f.writelines(sample_lines)

    # Filtered by chat_id 11111
    filtered = await iare_mcp_server.read_recent_errors(lines=10, user_chat_id=11111, log_file=log_file)
    assert len(filtered) == 2
    assert all("11111" in line for line in filtered)

    # Filtered by chat_id 33333 (no matches)
    empty_filtered = await iare_mcp_server.read_recent_errors(lines=10, user_chat_id=33333, log_file=log_file)
    assert empty_filtered == ["No matching error entries found."]

    # Unfiltered tail
    unfiltered = await iare_mcp_server.read_recent_errors(lines=2, log_file=log_file)
    assert len(unfiltered) == 2


@pytest.mark.asyncio
async def test_get_system_health():
    """Verify get_system_health retrieves valid host resource stats."""
    health = await iare_mcp_server.get_system_health()
    assert "cpu_percent" in health
    assert "memory_used_mb" in health
    assert "memory_total_mb" in health
    assert "memory_percent" in health
    assert "disk_percent" in health
    assert health["memory_total_mb"] > 0


# ---------------------------------------------------------------------------
# Phase 2: Report Retrieval & Profile Context
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_pending_reports():
    """Verify get_pending_reports queries unresolved reports from SQLite."""
    await tdatabase.create_all_tdatabase_tables()

    # Store 1 pending report and 1 resolved report
    await tdatabase.store_reports("rep_001", "student1", "Cannot see CIE marks", 12345, None, None, 0)
    await tdatabase.store_reports("rep_002", "student2", "Attendance issue", 67890, "Fixed", "Admin", 1)

    reports = await iare_mcp_server.get_pending_reports(limit=10)
    assert len(reports) == 1
    assert reports[0]["report_id"] == "rep_001"
    assert reports[0]["username"] == "student1"
    assert reports[0]["chat_id"] == 12345
    assert reports[0]["reply_status"] == 0
    assert reports[0]["submitted_date"] is not None
    assert len(reports[0]["submitted_date"]) >= 10


@pytest.mark.asyncio
async def test_get_user_profile_context():
    """Verify get_user_profile_context inspects session, username, and ban status."""
    await tdatabase.create_all_tdatabase_tables()
    chat_id = 998877

    # 1. Unregistered user
    ctx_empty = await iare_mcp_server.get_user_profile_context(chat_id)
    assert ctx_empty["username"] == "Not Registered"
    assert ctx_empty["has_active_session"] is False
    assert ctx_empty["is_banned"] is False

    # 2. Registered with active session
    session_payload = {"username": "21951A0501", "cookies": {"PHPSESSID": "dummy"}}
    await tdatabase.store_user_session(chat_id, json.dumps(session_payload), "21951A0501")

    ctx_registered = await iare_mcp_server.get_user_profile_context(chat_id)
    assert ctx_registered["username"] == "21951A0501"
    assert ctx_registered["has_active_session"] is True
    assert ctx_registered["is_banned"] is False

    # 3. Banned user
    await tdatabase.store_banned_username("21951A0501")
    ctx_banned = await iare_mcp_server.get_user_profile_context(chat_id)
    assert ctx_banned["is_banned"] is True


# ---------------------------------------------------------------------------
# Phase 3: One-Shot Ticket Resolution & Concurrency Protection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_reply_validation_errors():
    """Verify send_reply rejects empty input and non-existent reports."""
    await tdatabase.create_all_tdatabase_tables()

    # Empty resolution
    res_empty = await iare_mcp_server.send_reply("rep_xyz", "")
    assert res_empty["success"] is False
    assert res_empty["status"] == "invalid_input"

    # Not found
    res_not_found = await iare_mcp_server.send_reply("rep_nonexistent", "A valid resolution text")
    assert res_not_found["success"] is False
    assert res_not_found["status"] == "not_found"


@pytest.mark.asyncio
async def test_send_reply_success_with_telegram_mock(monkeypatch):
    """Verify send_reply dispatches Telegram HTTP call, updates DB, and alerts managers."""
    await tdatabase.create_all_tdatabase_tables()
    report_id = "rep_success_101"
    user_chat_id = 555666

    await tdatabase.store_reports(report_id, "student_tester", "Attendance not updating", user_chat_id, None, None, 0)

    # Mock environment and manager fetch
    monkeypatch.setenv("BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[88888]))
    monkeypatch.setattr(managers_handler, "fetch_maintainer_chat_ids", AsyncMock(return_value=[99999]))

    dispatched_messages = []

    async def mock_post(self, url, json=None, **kwargs):
        dispatched_messages.append({"url": url, "payload": json})
        resp = MagicMock()
        resp.status_code = 200
        resp.text = '{"ok": true}'
        return resp

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    resolution = "The college server was down. It is now restored. Please refresh."
    res = await iare_mcp_server.send_reply(report_id, resolution)

    assert res["success"] is True
    assert res["status"] == "resolved"
    assert res["sent_to_chat_id"] == user_chat_id

    # Verify report in SQLite is marked as replied by AI Assistant with IST replied_date
    db_report = await tdatabase.load_reports(report_id)
    assert db_report[6] == 1  # reply_status
    assert db_report[4] == resolution  # replied_message
    assert db_report[5] == "AI Assistant"  # replied_maintainer
    assert db_report[8] is not None  # replied_date
    assert len(db_report[8]) >= 10

    # Verify Telegram API calls: 1 to student, 1 to admin (88888), 1 to maintainer (99999)
    target_chats = [msg["payload"]["chat_id"] for msg in dispatched_messages]
    assert user_chat_id in target_chats
    assert 88888 in target_chats
    assert 99999 in target_chats


@pytest.mark.asyncio
async def test_send_reply_concurrency_guard(monkeypatch):
    """Verify send_reply aborts if an admin already marked the report as resolved."""
    await tdatabase.create_all_tdatabase_tables()
    report_id = "rep_already_done"
    user_chat_id = 777888

    # Pre-mark report as replied by an admin (reply_status = 1)
    await tdatabase.store_reports(report_id, "student_tester", "Attendance not updating", user_chat_id, "Admin reply", "Admin_Alice", 1)

    monkeypatch.setenv("BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    post_called = False

    async def mock_post(self, url, **kwargs):
        nonlocal post_called
        post_called = True
        return MagicMock(status_code=200)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    res = await iare_mcp_server.send_reply(report_id, "AI duplicate answer")
    assert res["success"] is False
    assert res["status"] == "already_resolved"
    assert post_called is False  # Ensure no Telegram message was sent


@pytest.mark.asyncio
async def test_send_reply_telegram_api_error(monkeypatch):
    """Verify send_reply handles Telegram API rejection without marking report resolved."""
    await tdatabase.create_all_tdatabase_tables()
    report_id = "rep_err_403"
    user_chat_id = 111222

    await tdatabase.store_reports(report_id, "student_tester", "Issue", user_chat_id, None, None, 0)
    monkeypatch.setenv("BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

    # Simulate Telegram API error (e.g., bot blocked by user)
    async def mock_post(self, url, **kwargs):
        resp = MagicMock()
        resp.status_code = 403
        resp.text = '{"ok": false, "description": "Forbidden: bot was blocked by the user"}'
        return resp

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    res = await iare_mcp_server.send_reply(report_id, "Resolution")
    assert res["success"] is False
    assert res["status"] == "telegram_error"

    # Verify report status in DB remains 0 (unresolved)
    db_report = await tdatabase.load_reports(report_id)
    assert db_report[6] == 0


# ---------------------------------------------------------------------------
# Phase 4: End-to-End MCP Protocol Invocation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mcp_server_call_tool_e2e(monkeypatch):
    """Verify tools can be invoked via the native MCPServer.call_tool() protocol interface."""
    # Mock check_portal_status
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    monkeypatch.setattr(httpx.AsyncClient, "get", AsyncMock(return_value=mock_resp))

    # Invoke check_portal_status via MCP protocol
    mcp_result = await iare_mcp_server.mcp.call_tool("check_portal_status", {})
    assert not mcp_result.is_error
    assert len(mcp_result.content) > 0
    # Content text is JSON string representation of the tool output
    data = json.loads(mcp_result.content[0].text.replace("'", '"'))
    assert data["online"] is True
    assert data["status_code"] == 200

    # Invoke get_system_health via MCP protocol
    health_result = await iare_mcp_server.mcp.call_tool("get_system_health", {})
    assert not health_result.is_error
    health_data = json.loads(health_result.content[0].text.replace("'", '"'))
    assert "cpu_percent" in health_data


# ---------------------------------------------------------------------------
# Phase 5: Announcement Tools
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_draft_announcement_validation():
    """Verify draft_announcement rejects empty text."""
    res = await iare_mcp_server.draft_announcement("")
    assert res["success"] is False
    assert res["status"] == "invalid_input"


@pytest.mark.asyncio
async def test_draft_announcement_formatting_and_preview(monkeypatch):
    """Verify draft_announcement formats dual-UI templates and sends preview to admins."""
    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[12345]))
    monkeypatch.setattr(managers_handler, "fetch_maintainer_chat_ids", AsyncMock(return_value=[67890]))
    monkeypatch.setenv("BOT_TOKEN", "mock_bot_token_abc")

    preview_calls = []

    async def mock_post(self, url, json=None, **kwargs):
        preview_calls.append(json)
        resp = MagicMock()
        resp.status_code = 200
        return resp

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    raw_text = "Portal maintenance tonight from 10 PM to 12 AM."
    res = await iare_mcp_server.draft_announcement(raw_text, send_preview=True)

    assert res["success"] is True
    assert "```ANNOUNCEMENT\nPortal maintenance" in res["formatted_updated_ui"]
    assert "**ANNOUNCEMENT**\n\nPortal maintenance" in res["formatted_traditional_ui"]
    assert res["preview_sent_to_managers"] is True
    assert res["manager_recipients_count"] == 2

    # Verify preview sent to both managers
    dispatched_cids = [c["chat_id"] for c in preview_calls]
    assert 12345 in dispatched_cids
    assert 67890 in dispatched_cids
    assert all("[ANNOUNCEMENT PREVIEW" in c["text"] for c in preview_calls)


@pytest.mark.asyncio
async def test_broadcast_announcement_validation():
    """Verify broadcast_announcement rejects empty text and invalid targets."""
    res_empty = await iare_mcp_server.broadcast_announcement("")
    assert res_empty["status"] == "error"
    assert "cannot be empty" in res_empty["reason"]

    res_target = await iare_mcp_server.broadcast_announcement("Test", target="invalid_scope")
    assert res_target["status"] == "error"
    assert "Invalid target" in res_target["reason"]


@pytest.mark.asyncio
async def test_broadcast_announcement_admins_target(monkeypatch):
    """Verify broadcast_announcement targeting 'admins' only sends to managers."""
    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[101]))
    monkeypatch.setattr(managers_handler, "fetch_maintainer_chat_ids", AsyncMock(return_value=[202]))
    monkeypatch.setenv("BOT_TOKEN", "mock_bot_token_abc")

    sent_targets = []

    async def mock_post(self, url, json=None, **kwargs):
        sent_targets.append(json["chat_id"])
        resp = MagicMock()
        resp.status_code = 200
        return resp

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    res = await iare_mcp_server.broadcast_announcement("Emergency Server Reboot", target="admins", reason="reboot")

    assert res["status"] == "completed"
    assert res["target"] == "admins"
    assert res["total_recipients"] == 2
    assert res["successful"] == 2
    assert res["failed"] == 0
    assert 101 in sent_targets
    assert 202 in sent_targets


@pytest.mark.asyncio
async def test_broadcast_announcement_all_target_with_ui_mode(monkeypatch):
    """Verify broadcast_announcement to 'all' respects individual user UI preferences."""
    await tdatabase.create_all_tdatabase_tables()
    await user_settings.create_user_settings_tables()

    # User 303 in sessions table (traditional UI)
    session_data = json.dumps({"username": "21951A0501"})
    await tdatabase.store_user_session(303, session_data, "21951A0501")
    await user_settings.set_user_default_settings(303)
    await user_settings.set_traditional_ui_true(303)  # 1 = traditional UI

    # User 404 in Postgres (updated UI default)
    monkeypatch.setattr(pgdatabase, "get_all_chat_ids", AsyncMock(return_value=[404]))
    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[101]))
    monkeypatch.setattr(managers_handler, "fetch_maintainer_chat_ids", AsyncMock(return_value=[]))
    monkeypatch.setenv("BOT_TOKEN", "mock_bot_token_abc")

    messages_by_chat = {}

    async def mock_post(self, url, json=None, **kwargs):
        cid = json["chat_id"]
        messages_by_chat[cid] = json["text"]
        resp = MagicMock()
        resp.status_code = 200
        return resp

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    res = await iare_mcp_server.broadcast_announcement("Portal back online!", target="all")

    assert res["status"] == "completed"
    assert res["successful"] >= 3

    # User 303 selected traditional UI -> starts with **ANNOUNCEMENT**
    assert "**ANNOUNCEMENT**" in messages_by_chat[303]

    # User 404 default UI -> code block ```ANNOUNCEMENT
    assert "```ANNOUNCEMENT" in messages_by_chat[404]


@pytest.mark.asyncio
async def test_broadcast_announcement_floodwait_retry(monkeypatch):
    """Verify broadcast_announcement catches HTTP 429, sleeps, and retries successfully."""
    monkeypatch.setattr(managers_handler, "fetch_admin_chat_ids", AsyncMock(return_value=[999]))
    monkeypatch.setattr(managers_handler, "fetch_maintainer_chat_ids", AsyncMock(return_value=[]))
    monkeypatch.setenv("BOT_TOKEN", "mock_bot_token_abc")

    call_count = 0

    async def mock_post(self, url, json=None, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = MagicMock()
        if call_count == 1:
            # First attempt: FloodWait 429
            resp.status_code = 429
            resp.json = MagicMock(return_value={"parameters": {"retry_after": 0.01}})
            return resp
        # Second attempt: Success 200
        resp.status_code = 200
        return resp

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    res = await iare_mcp_server.broadcast_announcement("Test Rate Limit", target="admins")

    assert res["status"] == "completed"
    assert res["successful"] == 1
    assert call_count >= 2  # Proves retry happened after 429


@pytest.mark.asyncio
async def test_start_mcp_server_toggle(monkeypatch):
    """Verify start_mcp_server_if_enabled in main.py respects ENABLE_MCP_SERVER."""
    import main

    # 1. Disabled by default
    monkeypatch.delenv("ENABLE_MCP_SERVER", raising=False)
    proc_disabled = main.start_mcp_server_if_enabled()
    assert proc_disabled is None

    # 2. Disabled explicitly
    monkeypatch.setenv("ENABLE_MCP_SERVER", "false")
    proc_false = main.start_mcp_server_if_enabled()
    assert proc_false is None

    # 3. Enabled (mocking subprocess.Popen)
    monkeypatch.setenv("ENABLE_MCP_SERVER", "true")
    mock_popen = MagicMock(pid=99999, poll=MagicMock(return_value=None))
    monkeypatch.setattr(main.subprocess, "Popen", MagicMock(return_value=mock_popen))

    proc_enabled = main.start_mcp_server_if_enabled()
    assert proc_enabled is not None
    assert proc_enabled.pid == 99999

    # Cleanup shutdown test
    main.stop_mcp_server()
    assert main._MCP_PROCESS is None


# ---------------------------------------------------------------------------
# Phase 6: Password Protection & Authentication Tests
# ---------------------------------------------------------------------------

def test_mcp_auth_middleware_rejected_when_password_required():
    """Verify requests to SSE app without or with wrong password return 401 Unauthorized."""
    from starlette.testclient import TestClient

    app = iare_mcp_server.get_sse_app_with_auth(password="vault_secret_999")
    client = TestClient(app)

    # 1. No credentials
    r1 = client.get("/sse")
    assert r1.status_code == 401
    assert "Unauthorized" in r1.text

    # 2. Wrong query parameter
    r2 = client.get("/sse?password=wrong_pass")
    assert r2.status_code == 401

    # 3. Wrong Bearer header
    r3 = client.get("/sse", headers={"Authorization": "Bearer wrong_token"})
    assert r3.status_code == 401

    # 4. Wrong X-MCP-Password header
    r4 = client.get("/sse", headers={"X-MCP-Password": "wrong_token"})
    assert r4.status_code == 401


def test_mcp_auth_middleware_accepted_when_password_valid():
    """Verify requests with valid password pass the authentication middleware."""
    from starlette.testclient import TestClient

    app = iare_mcp_server.get_sse_app_with_auth(password="vault_secret_999")
    client = TestClient(app)

    # 1. Valid via Bearer token (post to messages router)
    r1 = client.post("/messages?session_id=s1", headers={"Authorization": "Bearer vault_secret_999"}, json={"test": 1})
    assert r1.status_code != 401  # Passes auth middleware

    # 2. Valid via X-MCP-Password header
    r2 = client.post("/messages?session_id=s1", headers={"X-MCP-Password": "vault_secret_999"}, json={"test": 1})
    assert r2.status_code != 401

    # 3. Valid via query string ?password=
    r3 = client.post("/messages?session_id=s1&password=vault_secret_999", json={"test": 1})
    assert r3.status_code != 401


def test_mcp_auth_middleware_disabled_when_no_password():
    """Verify open access when MCP_PASSWORD is not set."""
    from starlette.testclient import TestClient

    app = iare_mcp_server.get_sse_app_with_auth(password=None)
    client = TestClient(app)

    # Without any password, request reaches the handler and does not return 401
    r = client.post("/messages?session_id=s1", json={"test": 1})
    assert r.status_code != 401

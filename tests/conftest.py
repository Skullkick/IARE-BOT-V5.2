import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from DATABASE import user_settings, tdatabase, managers_handler

@pytest.fixture(autouse=True)
def isolate_databases(tmp_path, monkeypatch):
    """Isolate all SQLite databases to a clean temporary directory per test."""
    db_user_settings = str(tmp_path / "test_user_settings.db")
    db_sessions = str(tmp_path / "test_user_sessions.db")
    db_total_users = str(tmp_path / "test_total_users.db")
    db_reports = str(tmp_path / "test_reports.db")
    db_labuploads = str(tmp_path / "test_labuploads.db")
    db_credentials = str(tmp_path / "test_credentials.db")
    db_managers = str(tmp_path / "test_managers.db")

    monkeypatch.setattr(user_settings, "SETTINGS_DATABASE", db_user_settings)
    monkeypatch.setattr(tdatabase, "DATABASE_FILE", db_sessions)
    monkeypatch.setattr(tdatabase, "TOTAL_USERS_DATABASE_FILE", db_total_users)
    monkeypatch.setattr(tdatabase, "REPORTS_DATABASE_FILE", db_reports)
    monkeypatch.setattr(tdatabase, "LAB_UPLOAD_DATABASE_FILE", db_labuploads)
    monkeypatch.setattr(tdatabase, "CREDENTIALS_DATABASE", db_credentials)
    monkeypatch.setattr(managers_handler, "MANAGERS_DATABASE", db_managers)

    yield tmp_path

@pytest.fixture
def mock_bot():
    """Create a mock Pyrogram Client."""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(id=101))
    bot.edit_message_text = AsyncMock(return_value=MagicMock(id=102))
    bot.download_media = AsyncMock(return_value="mock_path.pdf")
    user = MagicMock()
    user.first_name = "Test"
    user.last_name = "User"
    bot.get_users = AsyncMock(return_value=user)
    return bot

@pytest.fixture
def mock_message():
    """Create a mock Pyrogram Message."""
    msg = MagicMock()
    msg.chat = MagicMock()
    msg.chat.id = 123456789
    msg.text = "/test"
    msg.document = None
    msg.message_id = 999
    msg.id = 999
    msg.reply = AsyncMock()
    msg.reply_text = AsyncMock()
    msg.edit_message_text = AsyncMock()
    msg.download = AsyncMock()
    msg.delete = AsyncMock()
    return msg

import asyncio
import json
import sqlite3
import pytest
from DATABASE import tdatabase
from METHODS import crypto_helper

async def test_tdatabase_table_initialization():
    """Verify all temporary tables are created properly."""
    await tdatabase.create_all_tdatabase_tables()
    session = await tdatabase.load_user_session(12345)
    assert session is None

async def test_tdatabase_session_lifecycle():
    """Verify session storing, loading, and deletion."""
    await tdatabase.create_all_tdatabase_tables()
    chat_id = 98765
    payload = {"cookies": {"PHPSESSID": "xyz123"}, "username": "21951A0501"}
    
    await tdatabase.store_user_session(chat_id, json.dumps(payload), "21951A0501")
    loaded = await tdatabase.load_user_session(chat_id)
    assert loaded == payload

    # Update session
    payload_updated = {"cookies": {"PHPSESSID": "new_cookie"}, "username": "21951A0501"}
    await tdatabase.store_user_session(chat_id, json.dumps(payload_updated), "21951A0501")
    loaded_updated = await tdatabase.load_user_session(chat_id)
    assert loaded_updated == payload_updated

    # Delete session
    await tdatabase.delete_user_session(chat_id)
    assert await tdatabase.load_user_session(chat_id) is None

async def test_tdatabase_credentials_encryption_at_rest():
    """Verify credentials stored in credentials.db are encrypted with Fernet and decrypted on retrieval."""
    await tdatabase.create_all_tdatabase_tables()
    chat_id = 55555
    username = "21951A0599"
    plain_password = "SuperSecretPassword#123"

    await tdatabase.store_credentials_in_database(chat_id, username, plain_password)

    # Directly inspect raw SQLite database row to assert encryption at rest
    with sqlite3.connect(tdatabase.CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM credentials WHERE chat_id = ?", (chat_id,))
        raw_stored_password = cursor.fetchone()[0]

    assert raw_stored_password != plain_password
    assert crypto_helper.is_encrypted(raw_stored_password)

    # Fetch through API, should return plaintext
    fetched_user, fetched_pass = await tdatabase.fetch_credentials_from_database(chat_id)
    assert fetched_user == username
    assert fetched_pass == plain_password

async def test_tdatabase_banned_users():
    """Verify ban list operations: storing, checking, and case insensitivity."""
    await tdatabase.create_all_tdatabase_tables()
    username = "21951A05BANNED"

    assert await tdatabase.get_bool_banned_username(username) is False
    await tdatabase.store_banned_username(username.lower())
    
    assert await tdatabase.get_bool_banned_username(username.lower()) is True
    assert await tdatabase.get_bool_banned_username(username.upper()) is True

    await tdatabase.remove_banned_username(username.lower())
    assert await tdatabase.get_bool_banned_username(username.lower()) is False

async def test_tdatabase_reports_workflow():
    """Verify user report logging, pending triage, maintainer replying, and cleanup."""
    await tdatabase.create_all_tdatabase_tables()
    unique_id = "rep-1001"
    chat_id = 44444

    await tdatabase.store_reports(unique_id, "user_01", "Bot timed out on attendance", chat_id, None, None, 0)
    
    pending = await tdatabase.load_allreports()
    assert any(r[0] == unique_id for r in pending)

    # Update with reply
    await tdatabase.store_reports(unique_id, None, None, None, "Fixed, please retry", "Maintainer_Bob", 1)
    
    pending_after = await tdatabase.load_allreports()
    assert not any(r[0] == unique_id for r in pending_after)

    replied = await tdatabase.load_all_replied_reports()
    assert any(r[0] == unique_id for r in replied)

async def test_tdatabase_total_users_unique_constraint():
    """Verify total_users handles duplicate usernames gracefully."""
    await tdatabase.create_all_tdatabase_tables()
    
    await tdatabase.store_username("21951A0501")
    await tdatabase.store_username("21951A0501")  # duplicate insert
    
    users = await tdatabase.fetch_usernames_total_users_db()
    assert users.count("21951A0501") == 1

async def test_tdatabase_concurrent_operations():
    """Concurrency test: Multiple tasks reading and writing to SQLite."""
    await tdatabase.create_all_tdatabase_tables()

    async def op(idx):
        cid = 20000 + idx
        uname = f"21951A{idx:04d}"
        await tdatabase.store_user_session(cid, json.dumps({"username": uname}), uname)
        await tdatabase.store_credentials_in_database(cid, uname, f"pass_{idx}")
        await tdatabase.store_username(uname)
        s = await tdatabase.load_user_session(cid)
        assert s["username"] == uname

    tasks = [op(i) for i in range(25)]
    await asyncio.gather(*tasks)

async def test_tdatabase_corrupt_session_json():
    """Verify loading corrupted JSON session raises or is handled."""
    await tdatabase.create_all_tdatabase_tables()
    chat_id = 77777
    with sqlite3.connect(tdatabase.DATABASE_FILE) as conn:
        conn.cursor().execute("INSERT INTO sessions (chat_id, session_data, user_id) VALUES (?, ?, ?)",
                              (chat_id, "{CORRUPTED_JSON_WITHOUT_QUOTES", "user"))
        conn.commit()

    with pytest.raises(json.JSONDecodeError):
        await tdatabase.load_user_session(chat_id)

async def test_store_lab_info_lifecycle():
    """Verify storing, updating, and querying lab info in SQLite."""
    await tdatabase.create_all_tdatabase_tables()
    chat_id = 88888

    # New insert with get_title=True (verifying 4-value insert bugfix)
    await tdatabase.store_lab_info(chat_id, title="Exp 1", subject_code="CS501", week_index=1, get_title=True)
    info = await tdatabase.fetch_required_lab_info(chat_id)
    assert info == ("Exp 1", "CS501", 1)

    # Update existing row
    await tdatabase.store_lab_info(chat_id, title="Exp 1 Updated", subject_code="CS502", week_index=2, get_title=True)
    info_updated = await tdatabase.fetch_required_lab_info(chat_id)
    assert info_updated == ("Exp 1 Updated", "CS502", 2)

    # Calling with kwargs (backward compatibility for sync routine)
    chat_id_2 = 88889
    await tdatabase.store_lab_info(chat_id_2, subject_index=None, week_index=None, subjects="IT501", weeks="W1")
    info_kwargs = await tdatabase.fetch_required_lab_info(chat_id_2)
    assert info_kwargs[1] == "IT501"


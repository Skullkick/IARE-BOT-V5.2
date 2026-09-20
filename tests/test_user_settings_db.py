import asyncio
import sqlite3
import pytest
from DATABASE import user_settings

async def test_user_settings_table_creation():
    """Verify tables are created cleanly and can be queried."""
    await user_settings.create_user_settings_tables()
    settings = await user_settings.fetch_user_settings(99999)
    assert settings is None

async def test_user_default_settings():
    """Verify default settings row initialization."""
    await user_settings.create_user_settings_tables()
    chat_id = 12345
    await user_settings.set_user_default_settings(chat_id)
    
    settings = await user_settings.fetch_user_settings(chat_id)
    assert settings is not None
    # Schema: (chat_id, attendance_threshold, biometric_threshold, traditional_ui, extract_title)
    assert settings[0] == chat_id
    assert settings[1] == 75  # default attendance
    assert settings[2] == 75  # default biometric
    assert settings[3] == 0   # default traditional_ui
    assert settings[4] == 1   # default extract_title

async def test_threshold_clamping_boundaries():
    """Verify threshold clamping boundaries [35, 95]."""
    await user_settings.create_user_settings_tables()
    chat_id = 54321
    await user_settings.set_user_default_settings(chat_id)

    # Test under minimum (< 35)
    await user_settings.set_attendance_threshold(chat_id, 10)
    res = await user_settings.fetch_attendance_threshold(chat_id)
    assert res[0] == 35

    # Test over maximum (> 95)
    await user_settings.set_attendance_threshold(chat_id, 120)
    res = await user_settings.fetch_attendance_threshold(chat_id)
    assert res[0] == 95

    # Test biometric clamping under minimum
    await user_settings.set_biometric_threshold(chat_id, -5)
    res = await user_settings.fetch_biometric_threshold(chat_id)
    assert res[0] == 35

    # Test biometric clamping over maximum
    await user_settings.set_biometric_threshold(chat_id, 100)
    res = await user_settings.fetch_biometric_threshold(chat_id)
    assert res[0] == 95

async def test_ui_and_title_extract_toggles():
    """Verify toggles for traditional UI and title extraction."""
    await user_settings.create_user_settings_tables()
    chat_id = 77777
    await user_settings.set_user_default_settings(chat_id)

    await user_settings.set_traditional_ui_true(chat_id)
    assert (await user_settings.fetch_ui_bool(chat_id))[0] == 1

    await user_settings.set_traditional_ui_as_false(chat_id)
    assert (await user_settings.fetch_ui_bool(chat_id))[0] == 0

    await user_settings.set_extract_title_as_false(chat_id)
    assert (await user_settings.fetch_extract_title_bool(chat_id))[0] == 0

    await user_settings.set_extract_title_as_true(chat_id)
    assert (await user_settings.fetch_extract_title_bool(chat_id))[0] == 1

async def test_store_user_settings_unclamped_defect():
    """DEFECT PROBE: store_user_settings bypasses clamping [35, 95]."""
    await user_settings.create_user_settings_tables()
    chat_id = 88888
    # Directly store out-of-range thresholds 0 and 100
    await user_settings.store_user_settings(chat_id, attendance_threshold=100, biometric_threshold=0, ui=1, title_mode=1)
    
    settings = await user_settings.fetch_user_settings(chat_id)
    # Exposing the discrepancy: store_user_settings does NOT clamp!
    assert settings[1] == 100
    assert settings[2] == 0

async def test_set_default_attendance_indexes_idempotency():
    """Verify that calling set_default_attendance_indexes multiple times is idempotent."""
    await user_settings.create_user_settings_tables()
    await user_settings.set_default_attendance_indexes()
    
    # Second call is idempotent and does not raise IntegrityError
    await user_settings.set_default_attendance_indexes()
    idx = await user_settings.get_attendance_index_values()
    assert idx is not None
    assert idx["course_name"] == 2

async def test_concurrent_user_settings_writes():
    """Concurrency test: Verify multiple coroutines writing settings simultaneously."""
    await user_settings.create_user_settings_tables()

    async def worker(uid):
        await user_settings.set_user_default_settings(uid)
        await user_settings.set_attendance_threshold(uid, 80 + (uid % 15))
        await user_settings.set_traditional_ui_true(uid)
        val = await user_settings.fetch_attendance_threshold(uid)
        assert val is not None

    tasks = [worker(i) for i in range(1000, 1030)]
    await asyncio.gather(*tasks)

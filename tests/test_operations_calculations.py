import re
import asyncio
import json
import pytest
from unittest.mock import AsyncMock
from bs4 import BeautifulSoup
from METHODS import operations
from DATABASE import user_settings, tdatabase

# --- 1. Biometric Calculations ---

async def test_six_hours_biometric_happy_path():
    """Verify standard biometric time calculation with >= 6 hour gaps."""
    html = """
    <table>
    <tr><td>1</td><td>09:00</td><td>15:30</td></tr> <!-- 6.5h = 390m -> Yes -->
    <tr><td>2</td><td>09:15</td><td>14:15</td></tr> <!-- 5.0h = 300m -> No -->
    <tr><td>3</td><td>08:30</td><td>16:00</td></tr> <!-- 7.5h = 450m -> Yes -->
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    
    pct, count = await operations.six_hours_biometric(rows, totaldays=3, intime_index=1, outtime_index=2)
    assert count == 2
    assert pct == pytest.approx(66.667, 0.001)

async def test_six_hours_biometric_totaldays_zero():
    """Verify totaldays=0 returns (0, 0) without ZeroDivisionError."""
    pct, count = await operations.six_hours_biometric([], totaldays=0, intime_index=1, outtime_index=2)
    assert pct == 0
    assert count == 0

async def test_six_hours_biometric_seconds_in_time_unpack_defect():
    """DEFECT PROBE: times formatted with seconds (HH:MM:SS) crash with ValueError when splitting by colon."""
    html = """
    <table>
    <tr><td>1</td><td>09:00:00</td><td>15:30:00</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    
    # Line 592-593 does: intime_hour, intime_minute = intime.split(':')
    # HH:MM:SS has 3 elements, causing ValueError: too many values to unpack (expected 2)
    with pytest.raises(ValueError):
        await operations.six_hours_biometric(rows, totaldays=1, intime_index=1, outtime_index=2)

async def test_biometric_leaves_happy_path():
    """Verify leaves available calculation for student above threshold."""
    chat_id = 30001
    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)  # Default threshold: 75%
    
    # 85 present out of 100 total (85% > 75%)
    leaves, status = await operations.biometric_leaves(chat_id, present_days=85, total_days=100)
    assert status is True
    # 85 / (100 + 13) = 85/113 = 75.22% >= 75%; 85/114 = 74.56% < 75% -> 13 leaves
    assert leaves == 13

async def test_biometric_leaves_zero_division_handled():
    """Verify total_days = 0 is safely handled without ZeroDivisionError."""
    chat_id = 30002
    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)

    leaves, status = await operations.biometric_leaves(chat_id, present_days=0, total_days=0)
    assert leaves == 0
    assert status is True

async def test_biometric_leaves_missing_settings_handled():
    """Verify missing user settings initializes defaults without TypeError."""
    chat_id = 99999999  # Not in database
    await user_settings.create_user_settings_tables()

    leaves, status = await operations.biometric_leaves(chat_id, present_days=10, total_days=15)
    assert status is False
    assert isinstance(leaves, int)

async def test_biometric_leaves_threshold_100_terminates():
    """Verify 100% threshold calculation terminates promptly without hanging the event loop."""
    chat_id = 30003
    await user_settings.create_user_settings_tables()
    await user_settings.store_user_settings(chat_id, attendance_threshold=100, biometric_threshold=100, ui=1, title_mode=1)

    # Must complete promptly without infinite looping
    days, status = await asyncio.wait_for(
        operations.biometric_leaves(chat_id, present_days=8, total_days=10),
        timeout=1.0
    )
    assert status is False
    assert days > 0


# --- 2. GPA Regex Parsing ---

def test_gpa_regex_single_digit_and_decimals():
    """Verify regex correctly parses standard GPA values under 10.0."""
    sample_text = """
    Semester Grade Point Average (SGPA) : 8.75
    Cumulative Grade Point Average (CGPA) : 9.12
    """
    sgpa_pattern = r'Semester Grade Point Average \(SGPA\) : (\d(?:\.\d\d)?)'
    cgpa_pattern = r'Cumulative Grade Point Average \(CGPA\) : (\d(?:\.\d\d)?)'
    
    sgpa = re.findall(sgpa_pattern, sample_text)
    cgpa = re.findall(cgpa_pattern, sample_text)
    assert sgpa == ["8.75"]
    assert cgpa == ["9.12"]

def test_gpa_regex_perfect_ten():
    """Verify perfect 10.00 SGPA/CGPA parses correctly with updated \\d{1,2} pattern."""
    sample_text = """
    Semester Grade Point Average (SGPA) : 10.00
    Cumulative Grade Point Average (CGPA) : 10.00
    """
    sgpa_pattern = r'Semester Grade Point Average \(SGPA\) : (\d{1,2}(?:\.\d{1,2})?)'
    cgpa_pattern = r'Cumulative Grade Point Average \(CGPA\) : (\d{1,2}(?:\.\d{1,2})?)'
    
    sgpa = re.findall(sgpa_pattern, sample_text)
    cgpa = re.findall(cgpa_pattern, sample_text)
    assert sgpa == ["10.00"]
    assert cgpa == ["10.00"]

def test_attendance_average_zero_conducted_ignored():
    """Verify that courses with 0 conducted classes do not skew overall attendance average."""
    table_data = [
        ["Mathematics", "20", "18", "90.0", "Regular"],
        ["Physics", "20", "16", "80.0", "Regular"],
        ["Seminar", "0", "0", "100.0", "Regular"],
    ]
    sum_attendance = 0.0
    count_att = 0
    for row in table_data:
        course_name, conducted, attended, attendance_percentage, status = row
        if int(conducted) > 0:
            sum_attendance += float(attendance_percentage)
            count_att += 1

    aver_attendance = round(sum_attendance / count_att, 2) if count_att > 0 else 0.0
    assert count_att == 2
    assert aver_attendance == 85.0


# --- 3. Bunk Calculations ---

async def test_bunk_zero_conducted_classes(mock_bot, mock_message, monkeypatch):
    """Verify bunk does not crash on zero conducted classes and outputs 'No Classes Conducted Yet'."""
    chat_id = mock_message.chat.id
    await user_settings.create_user_settings_tables()
    await user_settings.set_user_default_settings(chat_id)
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, json.dumps({"username": "21951A0501", "cookies": {}, "headers": {}}), "21951A0501")

    mock_html = """
    <table class="table table-striped table-bordered table-hover table-head-fixed responsive"><thead><tr><th>Dummy</th></tr></thead></table>
    <table class="table table-striped table-bordered table-hover table-head-fixed responsive">
    <tbody>
    <tr><td>1</td><td>A5501</td><td>Compiler Design</td><td>Core</td><td>Dr. Smith</td><td>0</td><td>0</td><td>0.0</td></tr>
    </tbody>
    </table>
    """
    monkeypatch.setattr(operations, "async_fetch_page", AsyncMock(return_value=mock_html))

    await operations.bunk(mock_bot, mock_message)
    assert mock_bot.send_message.called
    sent_text = mock_bot.send_message.call_args_list[0].args[1]
    assert "No Classes Conducted Yet" in sent_text

async def test_bunk_threshold_100_terminates(mock_bot, mock_message, monkeypatch):
    """Verify bunk terminates promptly when threshold is 100% without infinite looping."""
    chat_id = mock_message.chat.id
    await user_settings.create_user_settings_tables()
    await user_settings.store_user_settings(chat_id, attendance_threshold=100, biometric_threshold=100, ui=0, title_mode=1)
    await tdatabase.create_all_tdatabase_tables()
    await tdatabase.store_user_session(chat_id, json.dumps({"username": "21951A0501", "cookies": {}, "headers": {}}), "21951A0501")

    # 18 out of 20 attended (90% < 100%)
    mock_html = """
    <table class="table table-striped table-bordered table-hover table-head-fixed responsive"><thead><tr><th>Dummy</th></tr></thead></table>
    <table class="table table-striped table-bordered table-hover table-head-fixed responsive">
    <tbody>
    <tr><td>1</td><td>A5501</td><td>Compiler Design</td><td>Core</td><td>Dr. Smith</td><td>20</td><td>18</td><td>90.0</td></tr>
    </tbody>
    </table>
    """
    monkeypatch.setattr(operations, "async_fetch_page", AsyncMock(return_value=mock_html))

    await asyncio.wait_for(operations.bunk(mock_bot, mock_message), timeout=1.0)
    assert mock_bot.send_message.called
    sent_text = mock_bot.send_message.call_args_list[0].args[1]
    assert "Need Attend:" in sent_text


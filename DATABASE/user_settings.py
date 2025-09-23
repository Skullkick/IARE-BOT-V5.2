"""
User settings and index configuration storage using SQLite.

This module encapsulates read/write operations for:
- Per-user preferences in the `user_settings` table (thresholds, UI style, title extraction)
- HTML parsing indices in the `index_values` table, stored as JSON by name

Database file: `user_settings.db` in the working directory.

Tables
- user_settings(chat_id INTEGER PRIMARY KEY,
                attendance_threshold INTEGER DEFAULT 75,
                biometric_threshold INTEGER DEFAULT 75,
                traditional_ui BOOLEAN DEFAULT 0,
                extract_title BOOLEAN DEFAULT 1)
- index_values(name TEXT PRIMARY KEY,
               index_ TEXT)  # JSON-serialized dictionary of index values

Notes
- All functions are declared async for consistency with the surrounding codebase,
  but internally perform synchronous SQLite operations.
- Threshold setters clamp values to [35, 95].
- Index sets accept dictionaries of column indices keyed by semantic names.
"""

import sqlite3,json

SETTINGS_DATABASE = "user_settings.db"


async def create_user_settings_tables():
    """Create both `user_settings` and `index_values` tables if missing."""
    await create_user_settings_table()
    await create_indexes_table()

async def create_user_settings_table():
    """Create the `user_settings` table with default columns and values."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                chat_id INTEGER PRIMARY KEY,
                attendance_threshold INTEGER DEFAULT 75,
                biometric_threshold INTEGER DEFAULT 75,
                traditional_ui BOOLEAN DEFAULT 0,
                extract_title BOOLEAN DEFAULT 1  
            )
        """)
        conn.commit()

async def create_indexes_table():
    """Create the `index_values` table for JSON-encoded index dictionaries."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS index_values(
                       name TEXT PRIMARY KEY,
                       index_ TEXT
            )
        """)
        conn.commit()


async def set_user_default_settings(chat_id):
    """Ensure a `user_settings` row exists for `chat_id` with default values.

    Parameters:
    - chat_id: Telegram chat id used as the primary key.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        # Check if the chat_id already exists
        cursor.execute("SELECT * FROM user_settings WHERE chat_id = ?", (chat_id,))
        existing_row = cursor.fetchone()
        if existing_row:
            # Chat_id already exists, do not set default values
            return
        else:
            # Chat_id doesn't exist, insert default values
            cursor.execute("INSERT OR REPLACE INTO user_settings (chat_id) VALUES (?)",
                           (chat_id,))
            conn.commit()

async def fetch_user_settings(chat_id):
    """Fetch the complete settings row for `chat_id`.

    Returns:
    - tuple | None: (chat_id, attendance_threshold, biometric_threshold, traditional_ui, extract_title)
      or None if not found.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE chat_id = ?", (chat_id,))
        settings = cursor.fetchone()
        return settings

async def set_attendance_threshold(chat_id,attendance_threshold):
    """Set attendance threshold for `chat_id`, clamped to [35, 95]."""
    if attendance_threshold > 95:
        attendance_threshold = 95
    if attendance_threshold < 35:
        attendance_threshold = 35
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET attendance_threshold = ? WHERE chat_id = ?", (attendance_threshold, chat_id))
        conn.commit()

async def set_biometric_threshold(chat_id,biometric_threshold):
    """Set biometric threshold for `chat_id`, clamped to [35, 95]."""
    if biometric_threshold > 95:
        biometric_threshold = 95
    if biometric_threshold < 35:
        biometric_threshold = 35
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET biometric_threshold = ? WHERE chat_id = ?",(biometric_threshold,chat_id))
        conn.commit()

async def set_traditional_ui_true(chat_id):
    """Enable traditional UI for `chat_id` (set to 1)."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET traditional_ui = 1 WHERE chat_id = ?",(chat_id,))
        conn.commit()

async def set_traditional_ui_as_false(chat_id):
    """Disable traditional UI for `chat_id` (set to 0)."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET traditional_ui = 0 WHERE chat_id = ?",(chat_id,))
        conn.commit()

async def set_extract_title_as_true(chat_id):
    """Enable automatic title extraction for `chat_id` (set to 1)."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET extract_title = 1 WHERE chat_id = ?",(chat_id,))
        conn.commit()


async def set_extract_title_as_false(chat_id):
    """Disable automatic title extraction for `chat_id` (set to 0)."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET extract_title = 0 WHERE chat_id = ?",(chat_id,))
        conn.commit()

async def delete_user_settings(chat_id):
    """Delete the `user_settings` row for `chat_id`.

    Returns:
    - bool: True on success, False if an error occurred.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE * FROM user_settings WHERE chat_id = ?",(chat_id,))
            conn.commit()
            return True
        except:
            return False

async def clear_user_settings_table():
    """Remove all rows from the `user_settings` table (destructive)."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_settings")
        conn.commit()

async def fetch_extract_title_bool(chat_id):
    """Return `(extract_title,)` for `chat_id` (1 or 0), or None if missing."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT extract_title FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value

async def fetch_biometric_threshold(chat_id):
    """Return `(biometric_threshold,)` for `chat_id`, or None if missing."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT biometric_threshold FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value

async def fetch_attendance_threshold(chat_id):
    """Return `(attendance_threshold,)` for `chat_id`, or None if missing."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT attendance_threshold FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value

async def fetch_ui_bool(chat_id):
    """Return `(traditional_ui,)` for `chat_id` (1 or 0), or None if missing."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT traditional_ui FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value
    
async def store_user_settings(chat_id,attendance_threshold,biometric_threshold,ui,title_mode):
    """Upsert a complete settings row for `chat_id`.

    Parameters:
    - chat_id: Primary key
    - attendance_threshold: int (will be stored as-is)
    - biometric_threshold: int (will be stored as-is)
    - ui: 1 for traditional UI, 0 for updated UI
    - title_mode: 1 for auto title extraction, 0 to disable
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        # Check if the chat_id already exists
        cursor.execute('SELECT * FROM user_settings WHERE chat_id = ?', (chat_id,))
        existing_row = cursor.fetchone()
        if existing_row:
            # If chat_id exists, update the row
            cursor.execute("""UPDATE user_settings 
            SET attendance_threshold = ?,
                biometric_threshold = ?,
                traditional_ui = ?,
                extract_title = ?
            WHERE chat_id = ?
        """,
        (attendance_threshold,biometric_threshold,ui,title_mode,chat_id))
        else:
            # If chat_id does not exist, insert a new row
            cursor.execute("""INSERT INTO user_settings (chat_id,attendance_threshold,biometric_threshold,traditional_ui,extract_title) VALUES (?,?,?,?,?)""",
                           (chat_id,attendance_threshold,biometric_threshold,ui,title_mode))
        conn.commit()
async def set_default_attendance_indexes():
    """Insert default attendance indices into `index_values` if needed.

    Keys: course_name, attendance_percentage, conducted_classes, attended_classes, status.
    Updated on 15-05-2024; update if the HTML structure changes.
    """
    name = "ATTENDANCE_INDEX_VALUES"
    course_name_index = 2
    attendance_percentage_index = 7
    conducted_classes_index = 5
    attended_classes_index = 6
    status = 8
    all_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : status
    }
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO index_values (name,index_) VALUES (?,?)", (name,json.dumps(all_attendance_indexes)))
        conn.commit()
async def set_default_biometric_indexes():
    """Insert default biometric indices into `index_values` if needed.

    Keys: status, intime, outtime. Updated on 15-05-2024.
    """
    name = "BIOMETRIC_INDEX_VALUES"
    status_index = 6
    intime_index = 4
    outtime_index = 5
    all_biometric_index = {
        'status' : status_index,
        'intime' : intime_index,
        'outtime' : outtime_index
    }
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO index_values (name,index_) VALUES (?,?)", (name,json.dumps(all_biometric_index)))
        conn.commit()

async def set_default_pat_attendance_indexes():
    """Insert default PAT attendance indices into `index_values` if needed.

    Keys: course_name, attendance_percentage, conducted_classes, attended_classes, status.
    Updated on 15-05-2024.
    """
    name = "PAT_INDEX_VALUES"
    course_name_index = 2
    conducted_classes_index = 3
    attended_classes_index = 4
    pat_attendance_percentage_index = 5
    pat_status = 6
    pat_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : pat_attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : pat_status
    }
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO index_values (name,index_) VALUES (?,?)", (name,json.dumps(pat_attendance_indexes)))
        conn.commit()

async def set_attendance_indexes(
        course_name_index,
        conducted_classes_index,
        attended_classes_index,
        attendance_percentage_index,
        status_index):
    """Upsert attendance index dictionary into `index_values`.

    Parameters are integer column indices for the respective keys.
    """
    name = "ATTENDANCE_INDEX_VALUES"
    all_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status':status_index
    }
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(all_attendance_indexes), name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name, json.dumps(all_attendance_indexes)))
            conn.commit()
    except Exception as e:
        print(f"Error updating the attendance index values : {e}")

async def set_biometric_indexes(intime_index,outtime_index,status_index):
    """Upsert biometric index dictionary into `index_values`.

    Parameters are integer column indices for status, intime, outtime.
    """
    name = "BIOMETRIC_INDEX_VALUES"
    all_biometric_index = {
        'status' : status_index,
        'intime' : intime_index,
        'outtime' : outtime_index
    }
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(all_biometric_index),name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name,json.dumps(all_biometric_index)))
            conn.commit()
    except Exception as e:
        print(f"Error updating biometric index values : {e}")

async def set_pat_attendance_indexes(course_name_index,
    conducted_classes_index,
    attended_classes_index,
    pat_attendance_percentage_index,
    pat_status):
    """Upsert PAT attendance index dictionary into `index_values`.

    Parameters are integer column indices for the respective keys.
    """
    name = "PAT_INDEX_VALUES"
    pat_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : pat_attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : pat_status
    }
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(pat_attendance_indexes),name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name,json.dumps(pat_attendance_indexes)))
            conn.commit()
    except Exception as e:
        print(f"Error updating pat attendance index values : {e}")

async def get_attendance_index_values():
    """Return the attendance indices dictionary or None if not set."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT index_ FROM index_values WHERE name = ?", ("ATTENDANCE_INDEX_VALUES",))
        result = cursor.fetchone()
        
        if result:
            attendance_indexes = json.loads(result[0])
            return attendance_indexes
        else:
            return None

async def get_pat_attendance_index_values():
    """Return the PAT attendance indices dictionary or None if not set."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT index_ FROM index_values WHERE name = ?", ("PAT_INDEX_VALUES",))
        result = cursor.fetchone()
        
        if result:
            pat_attendance_indexes = json.loads(result[0])
            return pat_attendance_indexes
        else:
            return None
        
async def get_biometric_index_values():
    """Return the biometric indices dictionary or None if not set."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT index_ FROM index_values WHERE name = ?", ("BIOMETRIC_INDEX_VALUES",))
        result = cursor.fetchone()
        if result:
            biometric_indexes = json.loads(result[0])
            return biometric_indexes
        else:
            return None

async def store_index_values_to_restore(name,indexes_dictionary):
    """Upsert an index dictionary under `name` into `index_values`.

    Typically used when restoring indices from the cloud database.
    """
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(indexes_dictionary),name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name,json.dumps(indexes_dictionary)))
            conn.commit()
    except Exception as e:
        print(f"Error restoring index values : {e}")

async def clear_indexes_table():
    """Delete all rows from `index_values` (destructive)."""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM index_values")
        conn.commit()

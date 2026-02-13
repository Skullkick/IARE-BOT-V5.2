"""
Bot manager metadata and trackers stored in SQLite.

This module manages three tables in `managers.db`:
- bot_managers: admin/maintainer flags, names, and fine-grained access toggles
- cgpa_tracker: track per-user CGPA updates (status, current_cgpa)
- cie_tracker: track per-user CIE updates (status, current_cie_marks)

Tracker scope and status:
- CGPA and CIE trackers are intended only for Admins/Maintainers and only to
    track their own performance (self-tracking). They are not a general feature
    for all users.
- Current status: UNDER MAINTENANCE (known issues). Open for fixes; storage
    functions remain in place while higher-level logic is being revised.

All functions are async for consistency with the codebase, but perform
synchronous SQLite operations internally. Functions generally return booleans,
lists, or tuples of primitive types; no side effects beyond the DB writes.
"""

import sqlite3,json


MANAGERS_DATABASE = "managers.db"

async def create_required_bot_manager_tables():
    """Create all required tables (bot_managers, cgpa_tracker, cie_tracker)."""
    await create_bot_managers_tables()
    await create_cgpa_tracker_table()
    await create_cie_tracker_table()

async def create_bot_managers_tables():
    """Create the `bot_managers` table for admin/maintainer and access flags.

    Columns include admin/maintainer booleans, manager name, control_access
    (e.g., 'Full' or 'limited'), and per-feature access toggles.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_managers (
                chat_id INTEGER PRIMARY KEY,
                admin BOOLEAN DEFAULT 0,
                maintainer BOOLEAN DEFAULT 0,
                name TEXT,
                control_access TEXT,
                access_users BOOLEAN DEFAULT 1,
                announcement BOOLEAN DEFAULT 0,
                configure BOOLEAN DEFAULT 0,
                show_reports BOOLEAN DEFAULT 0,
                reply_reports BOOLEAN DEFAULT 0,
                clear_reports BOOLEAN DEFAULT 0,
                ban_username BOOLEAN DEFAULT 0,
                unban_username BOOLEAN DEFAULT 0,
                manage_maintainers BOOLEAN DEFAULT 0,
                logs BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
async def create_cgpa_tracker_table():
    """Create the `cgpa_tracker` table (chat_id, status, current_cgpa).

    Usage note: This tracker is restricted to Admins/Maintainers for
    self-tracking only and is currently under maintenance.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cgpa_tracker (
                chat_id INTEGER PRIMARY KEY,
                status BOOLEAN DEFAULT 0,
                current_cgpa TEXT
            )
        """)
        conn.commit()

async def create_cie_tracker_table():
    """Create the `cie_tracker` table (chat_id, status, current_cie_marks).

    Usage note: This tracker is restricted to Admins/Maintainers for
    self-tracking only and is currently under maintenance.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cie_tracker (
                chat_id INTEGER PRIMARY KEY,
                status BOOLEAN DEFAULT 0,
                current_cie_marks TEXT
            )
        """)
        conn.commit()

async def store_cgpa_tracker_details(chat_id,status,current_cgpa):
    """Upsert CGPA tracker details (status, current_cgpa) for `chat_id`.

    Scope: Admins/Maintainers self-tracking only. Feature under maintenance.
    Returns True on success, False on error.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cgpa_tracker WHERE chat_id = ?",(chat_id,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE cgpa_tracker SET status = ?,current_cgpa = ? WHERE chat_id = ?",(status,current_cgpa,chat_id))
            else:
                cursor.execute("INSERT INTO cgpa_tracker (chat_id,status,current_cgpa) VALUES (?,?,?)",(chat_id,status,str(current_cgpa)))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error storing cgpa tracker details : {e}")
        return False
async def remove_cgpa_tracker_details(chat_id):
    """Delete CGPA tracker row for `chat_id` if it exists; return bool.

    Scope: Admins/Maintainers self-tracking only. Feature under maintenance.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cgpa_tracker WHERE chat_id = ?",(chat_id,))
            data = cursor.fetchone()
            if data:
                cursor.execute("DELETE FROM cgpa_tracker WHERE chat_id = ?",(chat_id,))
                conn.commit()
                return True
            else:
                return False
    except Exception as e:
        print(f"Error deleting the cgpa_tracker details : {e}")

async def get_all_cgpa_tracker_chat_ids():
    """Return list of all chat_ids present in the CGPA tracker table.

    Diagnostic helper primarily for maintenance/administration.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM cgpa_tracker")
            tracker_chat_ids = [row[0] for row in cursor.fetchall()]
            return tracker_chat_ids
    except Exception as e:
        print(f"Error retrieving all the chat_ids from cgpa_tracker : {e}")
        return False

async def get_cgpa_tracker_details(chat_id):
    """Return `(status, current_cgpa)` for `chat_id`, or None if missing.

    Scope: Admins/Maintainers self-tracking only. Feature under maintenance.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status,current_cgpa FROM cgpa_tracker WHERE chat_id = ?",(chat_id,))
            tracker_details = cursor.fetchone()
            if tracker_details:
                return tracker_details
            else:
                return None
    except Exception as e:
        print(f"Error retrieving the cgpa tracker details : {e}")
        return False


async def store_cie_tracker_details(chat_id,status,current_cie_marks):
    """Upsert CIE tracker details (status, current_cie_marks) for `chat_id`.

    Scope: Admins/Maintainers self-tracking only. Feature under maintenance.
    Returns True on success, False on error.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cie_tracker WHERE chat_id = ?",(chat_id,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE cie_tracker SET status = ?,current_cie_marks = ? WHERE chat_id = ?",(status,current_cie_marks,chat_id))
            else:
                cursor.execute("INSERT INTO cie_tracker (chat_id,status,current_cie_marks) VALUES (?,?,?)",(chat_id,status,str(current_cie_marks)))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error storing cie tracker details : {e}")
        return False
async def remove_cie_tracker_details(chat_id):
    """Delete CIE tracker row for `chat_id` if it exists; return bool.

    Scope: Admins/Maintainers self-tracking only. Feature under maintenance.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cie_tracker WHERE chat_id = ?",(chat_id,))
            data = cursor.fetchone()
            if data:
                cursor.execute("DELETE FROM cie_tracker WHERE chat_id = ?",(chat_id,))
                conn.commit()
                return True
            else:
                return False
    except Exception as e:
        print(f"Error deleting the cie_tracker details : {e}")

async def get_all_cie_tracker_chat_ids():
    """Return list of all chat_ids present in the CIE tracker table.

    Diagnostic helper primarily for maintenance/administration.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM cie_tracker")
            tracker_chat_ids = [row[0] for row in cursor.fetchall()]
            return tracker_chat_ids
    except Exception as e:
        print(f"Error retrieving all the chat_ids from cie_tracker : {e}")
        return False

async def get_cie_tracker_details(chat_id):
    """Return `(status, current_cie_marks)` for `chat_id`, or None if missing.

    Scope: Admins/Maintainers self-tracking only. Feature under maintenance.
    """
    try:
        with sqlite3.connect(MANAGERS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status,current_cie_marks FROM cie_tracker WHERE chat_id = ?",(chat_id,))
            tracker_details = cursor.fetchone()
            if tracker_details:
                return tracker_details
            else:
                return None
    except Exception as e:
        print(f"Error retrieving the cie tracker details : {e}")
        return False

async def store_as_admin(name,chat_id):
    """Upsert admin record with `admin=1`, name, and `control_access='Full'`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT OR REPLACE INTO bot_managers 
                       (chat_id,admin,name,control_access) VALUES (?,?,?,?)""",(chat_id,1,name,'Full'))
        conn.commit()

async def store_as_maintainer(name,chat_id):
    """Upsert maintainer record with `maintainer=1`, name, `control_access='limited'`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO bot_managers (chat_id,maintainer,name,control_access) VALUES (?,?,?,?)",(chat_id,1,name,'limited'))
        conn.commit()

async def fetch_admin_chat_ids():
    """Return list of chat_ids where `admin=1`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM bot_managers WHERE admin = ?",(1,))
        admin_chat_ids = [row[0] for row in cursor.fetchall()]
        return admin_chat_ids

async def fetch_maintainer_chat_ids():
    """Return list of chat_ids where `maintainer=1`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM bot_managers WHERE maintainer = ?",(1,))
        maintainer_chat_ids = [row[0] for row in cursor.fetchall()]
        return maintainer_chat_ids
async def fetch_name(chat_id):
    """Return manager name for `chat_id`, or None if not found."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM bot_managers WHERE chat_id = ?",(chat_id,))
        name = cursor.fetchone()
        if name is not None:
            return name[0]

async def store_name(chat_id,name):
    """Update the `name` for a manager identified by `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET name = ? WHERE chat_id = ?",(name,chat_id))
        conn.commit()

async def remove_maintainer(chat_id):
    """Delete a manager row where `chat_id` and `maintainer=1`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bot_managers WHERE chat_id= ? AND maintainer = ?",(chat_id,1))
        conn.commit()

async def remove_admin(chat_id):
    """Delete a manager row where `chat_id` and `admin=1`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bot_managers WHERE chat_id = ? AND admin = ?",(chat_id,1))
        conn.commit()

async def get_control_access(chat_id):
    """Return `control_access` string (e.g., 'Full' or 'limited') for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT control_access FROM bot_managers WHERE chat_id = ?",(chat_id,))
        control_access  = cursor.fetchone()
        if control_access is not None:
            return control_access[0]

async def get_access_data(chat_id):
    """Return a tuple of access flags for `chat_id` or None if missing.

    Order: (access_users, announcement, configure, show_reports, reply_reports,
    clear_reports, ban_username, unban_username, manage_maintainers, logs)
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT access_users,
                   announcement,
                   configure,
                   show_reports,
                   reply_reports,
                   clear_reports,
                   ban_username,
                   unban_username,
                   manage_maintainers,
                   logs 
            FROM bot_managers 
            WHERE chat_id = ?
        """, (chat_id,))
        access_data = cursor.fetchone()
        return access_data
async def set_access_users_true(chat_id):
    """Set `access_users=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET access_users = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_access_users_false(chat_id):
    """Set `access_users=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET access_users = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_announcement_access_true(chat_id):
    """Set `announcement=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET announcement = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_configure_access_true(chat_id):
    """Set `configure=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET configure = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_show_reports_access_true(chat_id):
    """Set `show_reports=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET show_reports = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_reply_reports_access_true(chat_id):
    """Set `reply_reports=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET reply_reports = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_clear_reports_access_true(chat_id):
    """Set `clear_reports=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET clear_reports = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_ban_username_access_true(chat_id):
    """Set `ban_username=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET ban_username = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_unban_username_access_true(chat_id):
    """Set `unban_username=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET unban_username = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_manage_maintainers_access_true(chat_id):
    """Set `manage_maintainers=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET manage_maintainers = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_logs_access_true(chat_id):
    """Set `logs=1` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET logs = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_all_access_true(chat_id):
    """Set all per-feature access flags to 1 for `chat_id` (full access)."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bot_managers 
            SET access_users = ?,
                announcement = ?,
                configure = ?,
                show_reports = ?,
                reply_reports = ?,
                clear_reports = ?,
                ban_username = ?,
                unban_username = ?,
                manage_maintainers = ?,
                logs = ?
            WHERE chat_id = ?
        """, (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, chat_id))
        conn.commit()
async def set_configure_access_false(chat_id):
    """Set `configure=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET configure = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_announcement_access_false(chat_id):
    """Set `announcement=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET announcement = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()


async def set_show_reports_access_false(chat_id):
    """Set `show_reports=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET show_reports = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_reply_reports_access_false(chat_id):
    """Set `reply_reports=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET reply_reports = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_clear_reports_access_false(chat_id):
    """Set `clear_reports=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET clear_reports = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_ban_username_access_false(chat_id):
    """Set `ban_username=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET ban_username = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_unban_username_access_false(chat_id):
    """Set `unban_username=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET unban_username = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_manage_maintainers_access_false(chat_id):
    """Set `manage_maintainers=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET manage_maintainers = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_logs_access_false(chat_id):
    """Set `logs=0` for `chat_id`."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET logs = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()
async def store_bot_managers_data_in_database(chat_id, admin, maintainer,name,control_access,access_users,announcement,
                                              configure,show_reports,reply_reports,clear_reports,ban_username,unban_username,manage_maintainers,logs):
    """Upsert a complete bot manager record.

    Parameters mirror table columns, enabling full replace or update semantics.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        # Check if the chat_id already exists
        cursor.execute('SELECT * FROM bot_managers WHERE chat_id = ?', (chat_id,))
        existing_row = cursor.fetchone()
        if existing_row:
            # If chat_id exists, update the row
            cursor.execute("""UPDATE bot_managers 
            SET admin = ?,
                maintainer = ?,
                name = ?,
                control_access = ?,
                access_users = ?,
                announcement = ?,
                configure = ?,
                show_reports = ?,
                reply_reports = ?,
                clear_reports = ?,
                ban_username = ?,
                unban_username = ?,
                manage_maintainers = ?,
                logs = ?
            WHERE chat_id = ?
        """,
                           (admin, maintainer,name,control_access,access_users,announcement,
                          configure,show_reports,reply_reports,clear_reports,ban_username,unban_username,manage_maintainers,logs, chat_id))
        else:
            # If chat_id does not exist, insert a new row
            cursor.execute("""INSERT INTO bot_managers 
                            (chat_id, admin, maintainer, name, control_access, access_users, announcement,
                            configure, show_reports, reply_reports, clear_reports, ban_username, unban_username,
                            manage_maintainers, logs) 
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (chat_id, admin, maintainer, name, control_access, access_users, announcement,
                            configure, show_reports, reply_reports, clear_reports, ban_username, unban_username,
                            manage_maintainers, logs))
        conn.commit()

async def clear_bot_managers_data():
    """Delete all rows from `bot_managers` (destructive)."""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bot_managers")
        conn.commit()

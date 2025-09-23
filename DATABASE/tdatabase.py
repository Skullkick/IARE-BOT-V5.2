"""
Temporary/local SQLite databases used by the bot.

This module centralizes all short-lived, node-local storage that the bot
relies on for day-to-day operation. The current server restarts roughly
every 24 hours, so all data in these databases is considered ephemeral and
can be lost at restart. Nothing here should be treated as a durable source
of truth.

Datastores managed in this file:
- user_sessions.db: Per-chat temporary session blobs and cached user_id.
- total_users.db: List of usernames that have interacted with the bot.
- reports.db: Pending and replied user reports for maintainers.
- labuploads.db: Transient state for lab PDF uploads (subject/week/title).
- credentials.db: Local copy of usernames/passwords and banned usernames.

Notes
- All functions are async to match the surrounding bot codebase, though the
    underlying sqlite3 calls are synchronous. Callers can await to keep a
    coherent async flow.
- Do not store sensitive data here long-term; this layer is for convenience
    and UX only.
"""

import sqlite3, json
import os
DATABASE_FILE = "user_sessions.db"

TOTAL_USERS_DATABASE_FILE = "total_users.db"

REPORTS_DATABASE_FILE = "reports.db"

LAB_UPLOAD_DATABASE_FILE = "labuploads.db"

CREDENTIALS_DATABASE = "credentials.db"


async def create_all_tdatabase_tables():
    """Create all required tables across the temporary/local databases.

    This is a convenience initializer that ensures every lightweight
    datastore used by the bot exists with the expected schema before use.
    Safe to call multiple times; each table is created with
    ``CREATE TABLE IF NOT EXISTS``.
    """
    await create_user_sessions_tables()
    await create_total_users_table()
    await create_reports_table()
    await create_lab_upload_table()
    await create_tables_credentials()
    await create_banned_users_table()
async def create_user_sessions_tables():
    """
    Create the ``sessions`` table in ``user_sessions.db`` if missing.

    Schema
    - chat_id: INTEGER PRIMARY KEY — Telegram chat id
    - session_data: TEXT — JSON-encoded session payload
    - user_id: TEXT — Optional cached user id
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id INTEGER PRIMARY KEY,
                session_data TEXT,
                user_id TEXT
            )
        """)
        conn.commit()

#The usernames accessed this bot
async def create_total_users_table():
    """
    Create the ``users`` table in ``total_users.db`` if missing.

    Tracks unique usernames that have interacted with the bot. Useful for
    aggregate stats and announcements.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE
            )
        """)
        conn.commit()


async def create_reports_table():
    """Create the ``pending_reports`` table in ``reports.db`` if missing.

    Stores both pending (reply_status = 0) and replied (reply_status = 1)
    reports. Maintainers can fetch pending items for triage and update the
    reply fields when responding.

    Columns
    - unique_id: TEXT PRIMARY KEY — Stable id for a report thread
    - user_id: TEXT — Sender identifier (free-form)
    - message: TEXT — Original report content
    - chat_id: INTEGER — Chat the report came from
    - replied_message: TEXT — Maintainer reply text (if any)
    - replied_maintainer: TEXT — Who replied
    - reply_status: BOOLEAN — 0 = pending, 1 = replied
    """
    with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_reports(
                       unique_id TEXT PRIMARY KEY,
                       user_id TEXT,
                       message TEXT,
                       chat_id INTEGER,
                       replied_message TEXT,
                       replied_maintainer TEXT,
                       reply_status BOOLEAN
            )
        """)
        conn.commit()

async def create_lab_upload_table():
    """Create the ``lab_upload_info`` table in ``labuploads.db`` if missing.

    Holds in-progress selections for lab uploads on a per-chat basis:
    subject choice, week index, chosen title, and flags that steer the
    upload workflow.

    Columns
    - chat_id: TEXT PRIMARY KEY — Telegram chat id
    - title: TEXT — Experiment title (optional)
    - subject: TEXT — Subject code/identifier
    - week_index: INTEGER — Selected week index
    - pdf_status: TEXT — Workflow state/flag for PDF reception
    - get_title: BOOLEAN — Whether to prompt/expect a title
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_upload_info (
                chat_id TEXT PRIMARY KEY,
                title TEXT,
                subject TEXT,
                week_index INTEGER,
                pdf_status TEXT,
                get_title BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()

async def create_tables_credentials():
    """
    Create the necessary tables to store credentials in ``credentials.db``.

    Tables
    - credentials(chat_id INTEGER PRIMARY KEY, username TEXT, password TEXT)
    - banned_users(username TEXT PRIMARY KEY) — created by a sibling helper
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        # Create a table to store user sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        """)
        conn.commit()


async def create_banned_users_table():
    """
    Create the ``banned_users`` table in ``credentials.db`` if missing.
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS banned_users (
                username TEXT PRIMARY KEY
            )
        """)
        conn.commit()

async def fetch_usernames_total_users_db():
    """Return all usernames seen by the bot from ``total_users.db``.

    :return: List of usernames (strings). Empty list if none found.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        usernames = [row[0] for row in cursor.fetchall()]
    return usernames


async def fetch_number_of_total_users_db():
    """Return the count of distinct usernames stored in ``total_users.db``.

    :return: Total number of users as an integer.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_count = cursor.fetchone()[0]
    return total_count
        

async def store_user_session(chat_id, session_data, user_id):
    """
    Store the user session data in ``user_sessions.db``.

    Parameters:
        chat_id (int): The chat ID of the user.
        session_data (str): JSON-formatted string containing the session data.
        user_id (str): Optional cached user identifier to store alongside.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sessions (chat_id, session_data, user_id) VALUES (?, ?, ?)",
                       (chat_id, session_data, user_id))
        
        conn.commit()

async def load_user_session(chat_id):
    """Load and decode a user's session from ``user_sessions.db``.

    The stored JSON is parsed to a dict. If the payload does not contain a
    ``username`` key, ``None`` is returned to signal an incomplete session.

    :param chat_id: Telegram chat id.
    :return: Dict with session fields or ``None`` if not found/incomplete.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT session_data FROM sessions WHERE chat_id=?", (chat_id,))
        result = cursor.fetchone()
        if result:
            session_data = json.loads(result[0])
            # Check if the session data contains the 'username'
            if 'username' in session_data:
                return session_data
            else:
                return None

async def load_username(chat_id):
    """Fetch the full ``sessions`` row for a chat id.

    Useful when callers need all stored columns (``chat_id, session_data, user_id``)
    without parsing. Returns ``None`` if the chat id is not present.

    :param chat_id: Telegram chat id.
    :return: Tuple row or ``None``.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE chat_id=?", (chat_id,))
        row = cursor.fetchone()
        if row:
            return row
        else:
            return None

async def delete_user_session(chat_id):
    """
    Delete the user session data from the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE chat_id=?", (chat_id,))
        conn.commit()

async def clear_sessions_table():
    """
    Clear all rows from the ``sessions`` table in ``user_sessions.db``.

    Warning: This removes every stored session for every user.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE * FROM sessions")
        conn.commit()

async def store_username(username):
    """
    Store a username in the total_users table.

    Parameters:
        username (str): The username to store.
    """
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)",
                       (username,))
        conn.commit()


async def store_lab_info(chat_id,title,subject_code,week_index,get_title:bool):
    """Store or update transient lab-upload selections for a chat.

    - If a row for ``chat_id`` exists, only non-None fields are updated.
    - If no row exists, a new one is inserted. When ``get_title`` is True,
      ``title`` is expected and will be stored as well.

    :param chat_id: Chat ID of the user.
    :param title: Title of the experiment (optional; used when ``get_title``).
    :param subject_code: Selected subject/subject code.
    :param week_index: Selected week index.
    :param get_title: Whether to store/update the ``title`` value now.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            if subject_code is not None:
                cursor.execute('UPDATE lab_upload_info SET subject = ? WHERE chat_id = ?', (subject_code, chat_id))
            if week_index is not None:
                cursor.execute('UPDATE lab_upload_info SET week_index = ? WHERE chat_id = ?', (week_index, chat_id))
            if get_title is True:
                if title is not None:
                    cursor.execute('UPDATE lab_upload_info SET title = ? WHERE chat_id = ?', (title, chat_id))
            # if subjects is not None:
            #     cursor.execute('UPDATE lab_upload_info SET subjects = ? WHERE chat_id = ?', (subjects, chat_id))
        else:
            if get_title is True:
                cursor.execute('INSERT INTO lab_upload_info (chat_id, title, subject, week_index) VALUES (?, ?, ?)',
                        (chat_id, title, subject_code, week_index))
            else:
                cursor.execute('INSERT INTO lab_upload_info (chat_id, subject, week_index) VALUES (?, ?, ?)',
                        (chat_id, subject_code, week_index))

        conn.commit()

async def store_subject_code(chat_id,subject_code):
    """Persist the selected subject code for a given chat.

    :param chat_id: Chat id of the user.
    :param subject_code: Selected subject code to store.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET subject = ? WHERE chat_id = ?', (subject_code, chat_id))
        conn.commit()
async def delete_subject_code(chat_id):
    """Clear the stored subject code for the given chat, if present.

    :param chat_id: Chat id of the user whose subject code is to be cleared.
    :return: True if a row existed and was updated, else False.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET subject = ? WHERE chat_id = ?', (None, chat_id))
            return True
        else:
            return False


async def store_week_index(chat_id,week_index):
    """Persist the selected week index for a given chat.

    :param chat_id: Chat id of the user.
    :param week_index: Selected week index to store.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET week_index = ? WHERE chat_id = ?', (week_index, chat_id))
        conn.commit()

async def store_title(chat_id,title):
    """Store or upsert the experiment title for a given chat.

    :param chat_id: Chat id of the user.
    :param title: Experiment title to store.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title = ? WHERE chat_id = ?', (title, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, title) VALUES (?, ?)',
            (chat_id, title))
        conn.commit()

async def store_pdf_status(chat_id,status):
    """Store or upsert the PDF intake status flag for a chat.

    :param chat_id: Chat id of the user.
    :param status: Status/flag value to store.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET pdf_status = ? WHERE chat_id = ?', (status, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, pdf_status) VALUES (?, ?)',
            (chat_id, status))
        conn.commit()

async def store_title_status(chat_id,status):
    """Store or upsert the "prompt for title" flag for a chat.

    :param chat_id: Chat id of the user.
    :param status: Boolean-like flag indicating whether to get the title.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET get_title = ? WHERE chat_id = ?', (status, chat_id))
        else:
            cursor.execute('INSERT INTO lab_upload_info (chat_id, get_title) VALUES (?, ?)',
            (chat_id, status))
        conn.commit()

async def fetch_required_lab_info(chat_id):
    """Fetch the trio (title, subject, week_index) for the given chat.

    :param chat_id: Chat id of the user.
    :return: Tuple (title, subject, week_index) or ``None`` if not found.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title,subject, week_index FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        lab_info = cursor.fetchone()
        if lab_info:
            return lab_info
        else:
            return None

async def  fetch_title_lab_info(chat_id):
    """Fetch only the title from ``lab_upload_info`` for the given chat.

    :param chat_id: Chat id of the user.
    :return: Tuple containing the title, or ``None`` if not found.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        title_info = cursor.fetchone()
        if title_info:
            return title_info
        else:
            return None


async def fetch_pdf_status(chat_id):
    """Get the stored PDF intake status flag for a chat.

    :param chat_id: Chat id of the user.
    :return: Stored status value or ``None`` if not present.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pdf_status FROM lab_upload_info WHERE chat_id = ?',(chat_id,))
        pdf_status = cursor.fetchone()
        if pdf_status:
            return pdf_status[0]
        else:
            return None

async def fetch_title_status(chat_id):
    """Get the stored "prompt for title" flag for a chat.

    :param chat_id: Chat id of the user.
    :return: Boolean-like value or ``None`` if not present.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT get_title FROM lab_upload_info WHERE chat_id = ?',(chat_id,))
        title_status = cursor.fetchone()
        if title_status:
            return title_status[0]
        else:
            return None

async def delete_title_status_info(chat_id):
    """Clear the stored "prompt for title" flag for the given chat.

    :param chat_id: Chat id of the user.
    :return: True if a row existed and was updated, else False.
    """

    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET get_title = ? WHERE chat_id = ?', (None, chat_id))
            return True
        else:
            return False
async def delete_pdf_status_info(chat_id):
    """Clear the stored PDF intake status for the given chat.

    :param chat_id: Chat id of the user.
    :return: True if a row existed and was updated, else False.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET pdf_status = ? WHERE chat_id = ?', (None, chat_id))
            return True
        else:
            return False

async def delete_indexes_and_title_info(chat_id):
    """Clear title, subject, and week index selections for the given chat.

    :param chat_id: Chat id of the user.
    :return: True if a row existed and was updated; otherwise, None.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title = ?, subject = ?, week_index = ? WHERE chat_id = ?', (None,None,None, chat_id))
            conn.commit()
            return True

async def delete_lab_upload_data(chat_id):
    """Delete the entire ``lab_upload_info`` row for the given chat id."""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lab_upload_info WHERE chat_id=?",(chat_id,))
        conn.commit()

async def delete_labs_subjects_weeks_all_users():
    """
    Clear the entire ``lab_upload_info`` table for all users/chats.
    """
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE * FROM lab_upload_info")
        conn.commit()

async def store_credentials_in_database(chat_id, username, password):
    """Upsert a chat's credentials into ``credentials.db``.

    If a row for ``chat_id`` exists it is updated, otherwise a new row is
    inserted.

    :param chat_id: Chat id of the user.
    :param username: Username to store.
    :param password: Password to store.
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        # Check if the chat_id already exists
        cursor.execute('SELECT * FROM credentials WHERE chat_id = ?', (chat_id,))
        existing_row = cursor.fetchone()
        if existing_row:
            # If chat_id exists, update the row
            cursor.execute('UPDATE credentials SET username = ?, password = ? WHERE chat_id = ?',
                           (username, password, chat_id))
        else:
            # If chat_id does not exist, insert a new row
            cursor.execute("INSERT INTO credentials (chat_id, username, password) VALUES (?, ?, ?)",
                           (chat_id, username, password))
        conn.commit()

async def fetch_row_count_credentials_database():
    """
    This Function is used to fetch the number of rows present in the credentials database.
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM credentials")
        total_count = cursor.fetchone()[0]
    return total_count

async def fetch_credentials_from_database(chat_id):
    """
    This Function is used to fetch the username and password based on the chat_id of the user from the database.
    :param chat_id: Chat_id of the user based on the message
    :return: returns tuple containing username and password"""
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username,password FROM credentials WHERE chat_id = ?", (chat_id,))
        credentials = cursor.fetchone()
        if credentials is None:
            return None,None
        return credentials

async def fetch_username_from_credentials(chat_id):
    """
    This Function is used to fetch the username from the local database
    :param chat_id: Chat_id of the user
    :return: Returns the username"""
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM credentials WHERE chat_id = ?",(chat_id,))
        username = cursor.fetchone()
        if username is None:
            return None
        return username[0]

async def check_chat_id_in_database(chat_id):
    """
    This Function is used to check whether the chat_id is present in the database or not.
    If the chat_id is present in the database then it returns true
    :chat_id: Chat id of the user based on the message recieved
    :return: return a boolean value"""
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM credentials WHERE chat_id = ?)",
            (chat_id,)
        )
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    
async def delete_user_credentials(chat_id):
    """
    Delete the user credentials data from the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
    """
    try:
        with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM credentials WHERE chat_id=?", (chat_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error removing creddentials from the database : {e}")
        return False

async def clear_credentials_table():
    """
    This function is used to clear all the rows in credentials table in the database
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials")
        conn.commit()
        return True


async def get_chat_ids_of_the_banned_username(username):
    """
    This Function is used to get the chat_id of the banned username from the credentails database
    :param username: Username of the user
    :return: Returns chat id of the username
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM credentials WHERE LOWER(username) LIKE LOWER(?) || '%'",(f"{username}",))
        chat_ids = [row[0] for row in cursor.fetchall()]
        return chat_ids

async def delete_banned_username_credentials_data(username):
    """
    This function is used to delete the row of banned user from the credentials database
    :username: Username of the banned user
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials WHERE LOWER(?) LIKE LOWER(username || '%')",(f"{username}",))
        print("deleted successfully")
        conn.commit()
async def fetch_row_count_banned_user_database():
    """
    This function is used to fetch the number of rows present in the banned users database
    :return: Returns the number of rows in int.
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM banned_users")
        total_count = cursor.fetchone()[0]
    return total_count

async def clear_banned_usernames_table():
    """
    This function is used to clear all the rows in banned_users table in the database
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM banned_users")
        conn.commit()
        return True

async def store_banned_username(username):
    """
    This Function is used to store the banned username in the database
    :param username : Username of the banned user.
    Note : Store the banned username by converting it to lowercase or uppercase
    """
    banned_username = username.lower()  # Convert username to lowercase
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        try:
            # Check if the username already exists in the database
            cursor.execute('SELECT 1 FROM banned_users WHERE username = ?', (banned_username,))
            if cursor.fetchone() is None:
                # Insert the username if it does not exist in the database
                cursor.execute('INSERT INTO banned_users (username) VALUES (?)', (banned_username,))
                conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error storing banned users to local database: {e}")

async def get_all_banned_usernames():
    """
    This Function is used to get all the banned usernames
    :return: Returns a tuple containing all the usernames
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM banned_users")
        # print(cursor.fetchall())
        banned_usernames = [row[0] for row in cursor.fetchall()]
        return banned_usernames

async def remove_banned_username(username):
    """
    This Function is used to remove the banned username,
    Basically this means unban of the user
    :param username : Username of the user
    Note : While deleting send the username in the same letter case when it is stored in the database
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM banned_users WHERE username = ?',(username,))
        conn.commit()

async def get_bool_banned_username(username):
    """
    This function is used to know whether a username is banned username or not.
    :param username: Username of the user.
    :return: Boolean value.
    True - User is banned
    False - User is not banned
    """
    with sqlite3.connect(CREDENTIALS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM banned_users WHERE LOWER(?) LIKE LOWER(username || "%")',(f"{username}",))
        row = cursor.fetchone()
        if row:
            return True
        else:
            return False
async def fetch_row_count_reports_database():
    """
    This function is used to fetch the number of rows present in the reports database
    :return: Returns the number of rows in int.
    """
    with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pending_reports")
        total_count = cursor.fetchone()[0]
    return total_count

async def store_reports(unique_id, user_id, message, chat_id, 
                        replied_message, replied_maintainer, reply_status):
    """Insert or update a user report in ``reports.db``.

    If a report with the same ``unique_id`` already exists, only the
    non-None fields provided will be updated. Otherwise, a new record is
    inserted.

    :param unique_id: Stable report/thread identifier.
    :param user_id: Sender identifier (optional).
    :param message: The original report text (optional for updates).
    :param chat_id: Chat id from which the report came (optional for updates).
    :param replied_message: Maintainer reply text (optional).
    :param replied_maintainer: Who replied (optional).
    :param reply_status: 0 for pending, 1 for replied.
    """
    try:
        with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
            c = conn.cursor()
            
            # Check if the report with the unique_id already exists
            c.execute("SELECT * FROM pending_reports WHERE unique_id = ?", (unique_id,))
            existing_report = c.fetchone()
            
            if existing_report:
                # Update existing report fields if they are provided
                if user_id is not None:
                    c.execute("UPDATE pending_reports SET user_id = ? WHERE unique_id = ?", (user_id, unique_id))
                if message is not None:
                    c.execute("UPDATE pending_reports SET message = ? WHERE unique_id = ?", (message, unique_id))
                if chat_id is not None:
                    c.execute("UPDATE pending_reports SET chat_id = ? WHERE unique_id = ?", (chat_id, unique_id))
                if replied_message is not None:
                    c.execute("UPDATE pending_reports SET replied_message = ? WHERE unique_id = ?", (replied_message, unique_id))
                if replied_maintainer is not None:
                    c.execute("UPDATE pending_reports SET replied_maintainer = ? WHERE unique_id = ?", (replied_maintainer, unique_id))
                if reply_status is not None:
                    c.execute("UPDATE pending_reports SET reply_status = ? WHERE unique_id = ?", (reply_status, unique_id))
            else:
                # Insert new report if it doesn't exist
                c.execute("INSERT INTO pending_reports (unique_id, user_id, message, chat_id, replied_message, replied_maintainer, reply_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (unique_id, user_id, message, chat_id, replied_message, replied_maintainer, reply_status))
            
            conn.commit()
    except Exception as e:
        print(f"Error storing the report message {e}")

async def load_reports(unique_id):
    """Fetch a single report row by ``unique_id`` from ``reports.db``.

    :param unique_id: The report/thread identifier.
    :return: Tuple row if found; otherwise None.
    """
    with sqlite3.connect(REPORTS_DATABASE_FILE ) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pending_reports WHERE unique_id=?",(unique_id,))
        row = cursor.fetchone()
        return row
    
async def load_allreports():
    """Return all pending reports (``reply_status = 0``).

    :return: List of tuples (unique_id, user_id, message, chat_id).
    """
    with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT unique_id, user_id, message, chat_id FROM pending_reports WHERE reply_status = 0")
        all_messages = cursor.fetchall()
        return all_messages

async def load_all_replied_reports():
    """Return all replied reports (``reply_status = 1``).

    :return: List of tuples for every replied report.
    """
    with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pending_reports WHERE reply_status = 1")
        all_messages = cursor.fetchall()
        return all_messages



async def delete_report(unique_id):
    """Delete the report row that matches ``unique_id`` from ``reports.db``."""
    with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending_reports WHERE unique_id=?",(unique_id,))
        conn.commit()
async def clear_reports():
    """Clear all rows from the ``pending_reports`` table."""
    with sqlite3.connect(REPORTS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending_reports")
        conn.commit()

async def pg_bool_to_sqlite_bool(pgbool):
    """
    Convert a Python/PG boolean into an integer suitable for SQLite.

    :param pgbool: Truthy/falsy value.
    :return: 1 if truthy else 0.
    """
    return 1 if pgbool else 0

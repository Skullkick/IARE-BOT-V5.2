# This file is used to store userdata temporarily in local storage
# Current server restarts every 24hrs So all the data present in the databases will be lost
import sqlite3, json
import os
DATABASE_FILE = "user_sessions.db"

TOTAL_USERS_DATABASE_FILE = "total_users.db"

REPORTS_DATABASE_FILE = "reports.db"

LAB_UPLOAD_DATABASE_FILE = "labuploads.db"

CREDENTIALS_DATABASE = "credentials.db"


async def create_all_tdatabase_tables():
    await create_user_sessions_tables()
    await create_total_users_table()
    await create_reports_table()
    await create_lab_upload_table()
    await create_tables_credentials()
    await create_banned_users_table()
async def create_user_sessions_tables():
    """
    Create the necessary tables in the SQLite database.
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
    Create the total_users table in the SQLite database.
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
    Create the necessary tables to store credentails in the SQLite database.
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
    Create the banned_users table in the SQLite database.
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
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        usernames = [row[0] for row in cursor.fetchall()]
    return usernames


async def fetch_number_of_total_users_db():
    with sqlite3.connect(TOTAL_USERS_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_count = cursor.fetchone()[0]
    return total_count
        

async def store_user_session(chat_id, session_data, user_id):
    """
    Store the user session data in the SQLite database.

    Parameters:
        chat_id (int): The chat ID of the user.
        session_data (str): JSON-formatted string containing the session data.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sessions (chat_id, session_data, user_id) VALUES (?, ?, ?)",
                       (chat_id, session_data, user_id))
        
        conn.commit()

async def load_user_session(chat_id):
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
    Clear all rows from the sessions table.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions")
        conn.commit()
async def store_lab_info(chat_id,title,subject_code,week_index,get_title:bool):
    """Store lab information in the database.
    
    :param chat_id: Chat ID of the user.
    :param title: Title of the experiment.
    :param subject_code: Selected subject index.
    :param week_index: Selected week index.
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
    """This function is used to store the subject in the database to retrieve later

    :param chat_id: chat_id of the user based on the message received from the user.
    :param subject_code: Selected subject_code is stored in the database"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET subject = ? WHERE chat_id = ?', (subject_code, chat_id))
        conn.commit()
async def delete_subject_code(chat_id):
    """
    This function is used to delete the stored subject code from the database
    
    :param subject_code: Code of the selected subject
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
    """This function is used to store the week_index in the database to retrieve later

    :param chat_id: chat_id of the user based on the message received from the user.
    :param week_index: Selected week_index is stored in the database"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET week_index = ? WHERE chat_id = ?', (week_index, chat_id))
        conn.commit()

async def store_title(chat_id,title):
    """This function is used to store the title in the database to use later

    :param chat_id: chat_id of the user based on the message received from the user.
    :param title: Title is stored in the database"""
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
    """This function is used to store the pdf status

    :param chat_id: chat_id of the user based on the message received from the user.
    :param status: Boolean"""
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
    """This function is used to store the title status

    :param chat_id: chat_id of the user based on the message received from the user
    :param status: Boolean"""
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
    """This function is used to fetch the title,subject,week_index from the database

    :param chat_id: chat_id of the user based on the messagee."""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title,subject, week_index FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        lab_info = cursor.fetchone()
        if lab_info:
            return lab_info
        else:
            return None

async def  fetch_title_lab_info(chat_id):
    """This Function is used to fetch the title from the lab_upload_info

    :param chat_id: The chat_id of the user
    :return: title_info"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        title_info = cursor.fetchone()
        if title_info:
            return title_info
        else:
            return None


async def fetch_pdf_status(chat_id):
    """This Function is used to get the status of the pdf, This is necessary for receiving the pdf from the user

    :param chat_id: chat_id of the user based on message.
    :return: pdf_status"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pdf_status FROM lab_upload_info WHERE chat_id = ?',(chat_id,))
        pdf_status = cursor.fetchone()
        if pdf_status:
            return pdf_status[0]
        else:
            return None

async def fetch_title_status(chat_id):
    """This Function is used to get the status of the title, This is necessary for receiving the title from the user

    :param chat_id: chat_id of the user based on message.
    :return: title_status"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT get_title FROM lab_upload_info WHERE chat_id = ?',(chat_id,))
        title_status = cursor.fetchone()
        if title_status:
            return title_status[0]
        else:
            return None

async def delete_title_status_info(chat_id):
    """This function removes the status of the title from the database

    :param chat_id: chat_id of the user based on the message received."""

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
    """This Function is used to remove the pdf status of a specified user in the database
    
    :param chat_id: chat_id of the user
    :return: Boolean"""
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
    """This function deletes the selected index values and the title information stored in the database
    :param chat_id: chat_id of the user"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lab_upload_info WHERE chat_id = ?', (chat_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute('UPDATE lab_upload_info SET title = ?, subject = ?, week_index = ? WHERE chat_id = ?', (None,None,None, chat_id))
            conn.commit()
            return True

async def delete_lab_upload_data(chat_id):
    """This function is used to delete the row of a user based on chat_id in lab_upload_info table"""
    with sqlite3.connect(LAB_UPLOAD_DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lab_upload_info WHERE chat_id=?",(chat_id,))
        conn.commit()

async def store_credentials_in_database(chat_id, username, password):
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

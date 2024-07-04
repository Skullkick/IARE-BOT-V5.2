import sqlite3,json

SETTINGS_DATABASE = "user_settings.db"


async def create_user_settings_tables():
    """
    This function is used to create the tables which consists of user settings and index configurations
    
    - user settings table
    - indexes table
    """
    await create_user_settings_table()
    await create_indexes_table()

async def create_user_settings_table():
    """
    Create the necessary tables for settings in the SQLite database.
    """
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
    """
    Create the necessary table for the index values in sqlite database
    """
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
    """
    Create a row for user based on chat_id and default setting values
    :param chat_id: Chat id of the user based on the message sent."""
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
    """
    This function is used to fetch the settings from the database
    :param chat_id: Chat Id of the user based on the message sent
    :return: returns a tuple containing all the settings
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE chat_id = ?",(chat_id,))
        settings = cursor.fetchone()
        return settings

async def set_attendance_threshold(chat_id,attendance_threshold):
    """This function is used to set the attendance threshold manually based on present chat_id
    :param chat_id: Chat Id of the user based on the message
    :param attendance_threshold: Value of the attendance threshold"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET attendance_threshold = ? WHERE chat_id = ?", (attendance_threshold, chat_id))
        conn.commit()

async def set_biometric_threshold(chat_id,biometric_threshold):
    """This function is used to set the attendance threshold manually
    :param chat_id: Chat Id of the user based on the message
    :param biometric_threshold: Value of the biometric threshold"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET biometric_threshold = ? WHERE chat_id = ?",(biometric_threshold,chat_id))
        conn.commit()

async def set_traditional_ui_true(chat_id):
    """This function is used to set the traditional ui as true
    :param chat_id: Chat Id of the user based on the message"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET traditional_ui = 1 WHERE chat_id = ?",(chat_id,))
        conn.commit()

async def set_traditional_ui_as_false(chat_id):
    """This function is used to set the traditional ui as false
    :param chat_id: Chat Id of the user based on the message"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET traditional_ui = 0 WHERE chat_id = ?",(chat_id,))
        conn.commit()

async def set_extract_title_as_true(chat_id):
    """This function is used to set the traditional ui as true
    :param chat_id: Chat Id of the user based on the message"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET extract_title = 1 WHERE chat_id = ?",(chat_id,))
        conn.commit()


async def set_extract_title_as_false(chat_id):
    """This function is used to set the traditional ui as false
    :param chat_id: Chat Id of the user based on the message"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET extract_title = 0 WHERE chat_id = ?",(chat_id,))
        conn.commit()

async def delete_user_settings(chat_id):
    """
    This Function is used to delete the user settings data based on the chat_id
    :param chat_id: Chat id of the user based on the message sent by the user.
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
    """This function is used to clear all the user settings in the settings database"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_settings")
        conn.commit()

async def fetch_extract_title_bool(chat_id):
    """
    This function is used to know whether the user wants the title to be automatically extracted or not.
    :param chat_id: Chat id of the user based on the message he sent.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT extract_title FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value

async def fetch_biometric_threshold(chat_id):
    """
    This function is used to fetch the biometric threshold based on chat_id.
    :param chat_id: Chat id of the user based on the message he sent.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT biometric_threshold FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value

async def fetch_attendance_threshold(chat_id):
    """
    This function is used to fetch the biometric threshold based on chat_id.
    :param chat_id: Chat id of the user based on the message he sent.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT attendance_threshold FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value

async def fetch_ui_bool(chat_id):
    """
    This function is used to know whether the user wants traditional ui or updated ui.
    :param chat_id: Chat id of the user based on the message he sent.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT traditional_ui FROM user_settings WHERE chat_id = ?",(chat_id,))
        value = cursor.fetchone()
        return value
    
async def store_user_settings(chat_id,attendance_threshold,biometric_threshold,ui,title_mode):
    """
    This function is used to store the user settings data when retrieved from the pgdatabase
    :param chat_id: Chat id of the user
    :param attendance_threshold: Attendance threshold of the user
    :param biometric_threshold: Biometric threshold of the user
    :param title_mode: To know whether title extraction is automatic or not
    :param ui: Traditional ui or not
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

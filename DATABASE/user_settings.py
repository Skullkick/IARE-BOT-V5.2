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

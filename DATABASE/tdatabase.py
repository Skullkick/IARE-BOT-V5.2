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

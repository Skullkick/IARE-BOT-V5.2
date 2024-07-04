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

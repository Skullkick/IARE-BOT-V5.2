import sqlite3,json


MANAGERS_DATABASE = "managers.db"

async def create_required_bot_manager_tables():
    await create_bot_managers_tables()
    await create_cgpa_tracker_table()
    await create_cie_tracker_table()

async def create_bot_managers_tables():
    """
    This function creates bot managers table 

    bot_managers table consists of admin and maintainer
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

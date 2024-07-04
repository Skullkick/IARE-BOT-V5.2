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
async def create_cgpa_tracker_table():
    """
    This function is used to create a table in MANAGERS_DATABASE 
    columns :
    
    - chat_id
    - status
    - current_cgpa
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
    """
    This function is used to create a table in MANAGERS_DATABASE 
    columns :
    
    - chat_id
    - status
    - current_cie_marks
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
    """

    This function is used to store the cgpa_tracker details
    :param chat_id: Chat id of the user
    :param status: Boolean value which is used to stop the tracker
    :param current_cgpa: Current cgpa of the user
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
    """
    This function is used to remove the row in cgpa_tracker table based on the chat_id
    :param chat_id: Chat id of the user
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
    """
    This function is used to return all the chat_id that are present in the cgpa tracker table
    :return: returns a tuple which contains all the chat_ids
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
    """
    This function is used to get the tracker details from the database
    :param chat_id: Chat id of the user
    :return: returns a tuple
    
    tuple:
    - status
    - current_cgpa
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

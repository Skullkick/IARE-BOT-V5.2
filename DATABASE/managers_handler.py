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


async def store_cie_tracker_details(chat_id,status,current_cie_marks):
    """

    This function is used to store the cie_tracker details
    :param chat_id: Chat id of the user
    :param status: Boolean value which is used to stop the tracker
    :param current_cie_marks: Current cie marks of the user
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
    """
    This function is used to remove the row in cie_tracker table based on the chat_id
    :param chat_id: Chat id of the user
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
    """
    This function is used to return all the chat_id that are present in the cie tracker table
    :return: returns a tuple which contains all the chat_ids
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
    """
    This function is used to get the tracker details from the database
    :param chat_id: Chat id of the user
    :return: returns a tuple
    
    tuple:
    - status
    - current_cie
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
    """
    Perform storing the user as admin.
    :param chat_id: chat id based on the message
    :param name: Name of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT OR REPLACE INTO bot_managers 
                       (chat_id,admin,name,control_access) VALUES (?,?,?,?)""",(chat_id,1,name,'Full'))
        conn.commit()

async def store_as_maintainer(name,chat_id):
    """
    Perform storing the user as maintainer
    :param chat_id: Chat id of the maintainer.
    :param name: Name of the user"""
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO bot_managers (chat_id,maintainer,name,control_access) VALUES (?,?,?,?)",(chat_id,1,name,'limited'))
        conn.commit()

async def fetch_admin_chat_ids():
    """
    Fetch the admin chat_ids
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM bot_managers WHERE admin = ?",(1,))
        admin_chat_ids = [row[0] for row in cursor.fetchall()]
        return admin_chat_ids

async def fetch_maintainer_chat_ids():
    """
    Fetch the Maintainer chat ids
    :return: returns all the maintainer chat_ids in a tuple
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM bot_managers WHERE maintainer = ?",(1,))
        maintainer_chat_ids = [row[0] for row in cursor.fetchall()]
        return maintainer_chat_ids
async def fetch_name(chat_id):
    """
    Fetch the Name of the user from database based on chat_id
    :param chat_id: Chat id of the manager.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM bot_managers WHERE chat_id = ?",(chat_id,))
        name = cursor.fetchone()
        if name is not None:
            return name[0]

async def store_name(chat_id,name):
    """
    Perform storing the name of the manager
    :param chat_id: Chat id of the manager.
    :param name: Name of the manager
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET name = ? WHERE chat_id = ?",(name,chat_id))
        conn.commit()

async def remove_maintainer(chat_id):
    """
    Remove a maintainer based on the chat_id
    :param chat_id: Chat id of the maintainer
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bot_managers WHERE chat_id= ? AND maintainer = ?",(chat_id,1))
        conn.commit()

async def remove_admin(chat_id):
    """
    Remove a admin based on the chat_id
    :param chat_id : Chat id of the admin
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bot_managers WHERE chat_id = ? AND admin = ?",(chat_id,1))
        conn.commit()

async def get_control_access(chat_id):
    """
    This Function is used to get the details of the control access.
    :param chat_id : Chat id of the user.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT control_access FROM bot_managers WHERE chat_id = ?",(chat_id,))
        control_access  = cursor.fetchone()
        if control_access is not None:
            return control_access[0]

async def get_access_data(chat_id):
    """
    This function is used to get the access data based on the chat_id
    :param chat_id : Chat id of the user 
    :return: Returns a tuple containg boolean access data values.
    :tuple boolean values: access_users,announcement,configure,show_reports,reply_reports,clear_reports,
    ban_username,unban username,manage_maintainers,logs
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
    """
    This function is used to set the access users to true.
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET access_users = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_access_users_false(chat_id):
    """
    This function is used to set the access users to false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET access_users = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_announcement_access_true(chat_id):
    """
    This function is used to set the announcement to true and can be used to know whether the manager has access to the announcements or not.
    :param chat_id : Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET announcement = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_configure_access_true(chat_id):
    """
    This function is used to set the configure value to true.
    :param chat_id : Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET configure = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_show_reports_access_true(chat_id):
    """
    This Function is used to set the show requests access as true.
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET show_reports = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_reply_reports_access_true(chat_id):
    """This Function is used to set the reply_reports access as true
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET reply_reports = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_clear_reports_access_true(chat_id):
    """
    This Function is used to set the clear requests access as true
    :param chat_id: chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET clear_reports = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_ban_username_access_true(chat_id):
    """
    This function is used to set the ban username access as true
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET ban_username = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_unban_username_access_true(chat_id):
    """
    This Function is used to set the unban username access as true
    :param chat_id: Chat id of the user.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET unban_username = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_manage_maintainers_access_true(chat_id):
    """
    This function is used to set the manage_maintainers access as true
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET manage_maintainers = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_logs_access_true(chat_id):
    """
    This Function is used to set the logs access as true
    :param chat_id: Chat id of the user.
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET logs = ? WHERE chat_id = ?",(1,chat_id))
        conn.commit()

async def set_all_access_true(chat_id):
    """
    This Function is used to set all access data parameters as true, Mainly used if we want to give full access.
    :param chat_id: Chat id of the user """
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
    """
    This function is used to set the configure value to false.
    :param chat_id : Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET configure = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_announcement_access_false(chat_id):
    """
    This function is used to set the announcement to false and can be used to know whether the manager has access to the announcements or not.
    :param chat_id : Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET announcement = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()


async def set_show_reports_access_false(chat_id):
    """
    This Function is used to set the show requests access as false.
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET show_reports = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_reply_reports_access_false(chat_id):
    """This Function is used to set the reply_reports access as false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET reply_reports = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_clear_reports_access_false(chat_id):
    """This Function is used to set the clear_reports access as false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET clear_reports = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_ban_username_access_false(chat_id):
    """This Function is used to set the ban_username access as false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET ban_username = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_unban_username_access_false(chat_id):
    """This Function is used to set the unban_username access as false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET unban_username = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_manage_maintainers_access_false(chat_id):
    """This Function is used to set the manage_maintainers access as false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET manage_maintainers = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()

async def set_logs_access_false(chat_id):
    """This Function is used to set the logs access as false
    :param chat_id: Chat id of the user
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_managers SET logs = ? WHERE chat_id = ?",(0,chat_id))
        conn.commit()
async def store_bot_managers_data_in_database(chat_id, admin, maintainer,name,control_access,access_users,announcement,
                                              configure,show_reports,reply_reports,clear_reports,ban_username,unban_username,manage_maintainers,logs):
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
    """
    This function is used to clear the bot Managers data from the Managers database
    """
    with sqlite3.connect(MANAGERS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bot_managers")
        conn.commit()

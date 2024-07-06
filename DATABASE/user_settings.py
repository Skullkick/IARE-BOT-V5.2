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
    if attendance_threshold > 95:
        attendance_threshold = 95
    if attendance_threshold < 35:
        attendance_threshold = 35
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_settings SET attendance_threshold = ? WHERE chat_id = ?", (attendance_threshold, chat_id))
        conn.commit()

async def set_biometric_threshold(chat_id,biometric_threshold):
    """This function is used to set the attendance threshold manually
    :param chat_id: Chat Id of the user based on the message
    :param biometric_threshold: Value of the biometric threshold"""
    if biometric_threshold > 95:
        biometric_threshold = 95
    if biometric_threshold < 35:
        biometric_threshold = 35
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
async def set_default_attendance_indexes():
    """
    This function is used to set the default index values for the attendance table
    Updated index values on 15-05-2024
    Make sure to update the index values if there is a change
    """
    name = "ATTENDANCE_INDEX_VALUES"
    course_name_index = 2
    attendance_percentage_index = 7
    conducted_classes_index = 5
    attended_classes_index = 6
    status = 8
    all_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : status
    }
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO index_values (name,index_) VALUES (?,?)", (name,json.dumps(all_attendance_indexes)))
        conn.commit()
async def set_default_biometric_indexes():
    """
    This function is used to set the default index values for the biometric table
    Updated index values on 15-05-2024
    Make sure to update the index values if there is a change
    """
    name = "BIOMETRIC_INDEX_VALUES"
    status_index = 6
    intime_index = 4
    outtime_index = 5
    all_biometric_index = {
        'status' : status_index,
        'intime' : intime_index,
        'outtime' : outtime_index
    }
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO index_values (name,index_) VALUES (?,?)", (name,json.dumps(all_biometric_index)))
        conn.commit()

async def set_default_pat_attendance_indexes():
    """
    This function is used to set the default index values for the biometric table
    Updated index values on 15-05-2024
    Make sure to update the index values if there is a change
    """
    name = "PAT_INDEX_VALUES"
    course_name_index = 2
    conducted_classes_index = 3
    attended_classes_index = 4
    pat_attendance_percentage_index = 5
    pat_status = 6
    pat_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : pat_attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : pat_status
    }
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO index_values (name,index_) VALUES (?,?)", (name,json.dumps(pat_attendance_indexes)))
        conn.commit()

async def set_attendance_indexes(
        course_name_index,
        conducted_classes_index,
        attended_classes_index,
        attendance_percentage_index,
        status_index):
    """This Function is used to set the index values of the attendance table
    :course_name_index: Index value of the course name column
    :conducted_classes: Index value of conducted_classes column
    :attended_classes: Index value of the attended classes column
    :attendance_percentage_index: Index value of the attendance percentage coloumm
    :status_index: Index value of status column """
    name = "ATTENDANCE_INDEX_VALUES"
    all_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status':status_index
    }
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(all_attendance_indexes), name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name, json.dumps(all_attendance_indexes)))
            conn.commit()
    except Exception as e:
        print(f"Error updating the attendance index values : {e}")

async def set_biometric_indexes(intime_index,outtime_index,status_index):
    """This function is used to set the biometric index values manually
    :status_index: Index value of the status column
    :intime_index: Index value of the intime column
    :outtime_index: Index value of the outtime column"""
    name = "BIOMETRIC_INDEX_VALUES"
    all_biometric_index = {
        'status' : status_index,
        'intime' : intime_index,
        'outtime' : outtime_index
    }
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(all_biometric_index),name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name,json.dumps(all_biometric_index)))
            conn.commit()
    except Exception as e:
        print(f"Error updating biometric index values : {e}")

async def set_pat_attendance_indexes(course_name_index,
    conducted_classes_index,
    attended_classes_index,
    pat_attendance_percentage_index,
    pat_status):
    """This Function is used to set the index values of the pat attendance table
    :course_name_index: Index value of the course name column
    :conducted_classes: Index value of conducted_classes column
    :attended_classes: Index value of the attended classes column
    :attendance_percentage_index: Index value of the attendance percentage coloumm
    :status_index: Index value of status column """
    name = "PAT_INDEX_VALUES"
    pat_attendance_indexes  = {
        'course_name' : course_name_index,
        'attendance_percentage' : pat_attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : pat_status
    }
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(pat_attendance_indexes),name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name,json.dumps(pat_attendance_indexes)))
            conn.commit()
    except Exception as e:
        print(f"Error updating pat attendance index values : {e}")

async def get_attendance_index_values():
    """
    This Function extracts the attendance index values from the database
    :return: Returns a dictionary containing all the index values 
    dictionary : {
        'course_name' : course_name_index,
        'attendance_percentage' : attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status':status_index
    }
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT index_ FROM index_values WHERE name = ?", ("ATTENDANCE_INDEX_VALUES",))
        result = cursor.fetchone()
        
        if result:
            attendance_indexes = json.loads(result[0])
            return attendance_indexes
        else:
            return None

async def get_pat_attendance_index_values():
    """
    This Function extracts the pat attendance index values from the database
    :return: Returns a dictionary containing all the index values 
    dictionary : {
        'course_name' : course_name_index,
        'attendance_percentage' : pat_attendance_percentage_index,
        'conducted_classes' : conducted_classes_index,
        'attended_classes' : attended_classes_index,
        'status' : pat_status
    }"""
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT index_ FROM index_values WHERE name = ?", ("PAT_INDEX_VALUES",))
        result = cursor.fetchone()
        
        if result:
            pat_attendance_indexes = json.loads(result[0])
            return pat_attendance_indexes
        else:
            return None
        
async def get_biometric_index_values():
    """
    This Function extracts the pat attendance index values from the database
    :return: Returns a dictionary containing all the index values 
    dictionary : {
        'status' : status_index,
        'intime' : intime_index,
        'outtime' : outtime_index
    }
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT index_ FROM index_values WHERE name = ?", ("BIOMETRIC_INDEX_VALUES",))
        result = cursor.fetchone()
        if result:
            biometric_indexes = json.loads(result[0])
            return biometric_indexes
        else:
            return None

async def store_index_values_to_restore(name,indexes_dictionary):
    """
    This function is used to store the index values in the form of dictionary
    
    Usually used while restoring the index values from the pgdatabase
    
    :param name: Name of the index values
    :param indexes_dicttionary: Dictionary containing all the index values
    """
    try:
        with sqlite3.connect(SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM index_values WHERE name = ?", (name,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE index_values SET index_ = ? WHERE name = ?", (json.dumps(indexes_dictionary),name))
            else:
                cursor.execute("INSERT INTO index_values (name, index_) VALUES (?, ?)", (name,json.dumps(indexes_dictionary)))
            conn.commit()
    except Exception as e:
        print(f"Error restoring index values : {e}")

async def clear_indexes_table():
    """
    This Function is used to clear all the values in index_value table.
    """
    with sqlite3.connect(SETTINGS_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM index_values")
        conn.commit()

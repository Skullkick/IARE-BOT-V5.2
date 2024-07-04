import asyncpg,os,json

#Database Credentials
USER_CRED = os.environ.get("POSTGRES_USER_ID")
PASSWORD_CRED = os.environ.get("POSTGRES_PASSWORD")
DATABASE_CRED = os.environ.get("POSTGRES_DATABASE")
HOST_CRED = os.environ.get("POSTGRES_HOST")
PORT_CRED = os.environ.get("POSTGRES_PORT")

# Data stored in this database is permanent, only if user removes the data will be removed.

async def connect_pg_database():
    """connect_pg_database is used to make a connection to the postgres database"""
    # connecting to the PSQL database
    connection = await asyncpg.connect(
        user=USER_CRED,
        password=PASSWORD_CRED,
        database=DATABASE_CRED,
        host=HOST_CRED,
        port=PORT_CRED
    )
    return connection

# async def create_user_credentials_table():  
#     """This function is used to create a table in postgres database if it dosent exist"""
#     conn = await connect_pg_database() 
#     try:
#         await conn.execute(
#             '''
#             CREATE TABLE IF NOT EXISTS user_credentials (
#                 chat_id BIGINT PRIMARY KEY,
#                 username VARCHAR(25),
#                 password VARCHAR(30),
#                 pat_student BOOLEAN DEFAULT false
#             )
#             '''
#         )
#         return True
#     except Exception as e:
#         print(f"Error creating table: {e}")
#         return False
#     finally:
        
#         await conn.close()

async def create_all_pgdatabase_tables():
    """
    This Function is used to create all the necessary tables in the pgdatabase

    - user credentials table
    - banned users table
    - bot managers table
    - reports table
    - indexes table

    """
    await create_user_credentials_table()
    await create_banned_users_table()
    await create_bot_managers_tables()
    await create_reports_table()
    await create_indexes_table()
    await create_cgpa_tracker_table()
    await create_cie_tracker_table()

async def create_user_credentials_table():

    connection = await connect_pg_database()
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_credentials (
                chat_id BIGINT PRIMARY KEY,
                username  VARCHAR(25),
                password VARCHAR(30),
                pat_student  BOOLEAN DEFAULT FALSE,
                attendance_threshold INTEGER DEFAULT 75,
                biometric_threshold INTEGER DEFAULT 75,
                traditional_ui BOOLEAN DEFAULT TRUE,
                extract_title BOOLEAN DEFAULT TRUE,
                lab_subjects_data TEXT,
                lab_weeks_data TEXT
            )

            """)
        
    except Exception as e:
        print(f"error while creating the user_credentials table {e}")
        return False
    finally:
        await connection.close()


async def create_reports_table():
    connection = await connect_pg_database()
    try:  
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS pending_reports(
            unique_id VARCHAR(75) PRIMARY KEY,
            user_id VARCHAR(25),
            message TEXT,
            chat_id BIGINT,
            replied_message TEXT,
            replied_maintainer TEXT,
            reply_status BOOLEAN
        )
    """)
        return True
    except Exception as e:
        print(f"error creating report table : {e}")
        return False
    finally:
        await connection.close()

async def create_banned_users_table():
    connection = await connect_pg_database()
    
    # Create the banned_users table in the PSQL database.
    try:
        await connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS banned_users (
                username TEXT PRIMARY KEY
                )
            ''')
        return True

    except Exception as e:
        print(f"Error creating banned_users table : {e}")
        return False

    finally:
        await connection.close()

async def create_bot_managers_tables():
    # Connect to PostgreSQL database
    connection = await connect_pg_database()
    try:
        # Create table in database
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS bot_managers (
            chat_id BIGINT PRIMARY KEY,
            admin BOOLEAN DEFAULT FALSE,
            maintainer BOOLEAN DEFAULT FALSE,
            name VARCHAR(60),
            control_access VARCHAR(60),
            access_users BOOLEAN DEFAULT TRUE,
            announcement BOOLEAN DEFAULT FALSE,
            configure BOOLEAN DEFAULT FALSE,
            show_reports BOOLEAN DEFAULT FALSE,
            reply_reports BOOLEAN DEFAULT FALSE,
            clear_reports BOOLEAN DEFAULT FALSE,
            ban_username BOOLEAN DEFAULT FALSE,
            unban_username BOOLEAN DEFAULT FALSE,
            manage_maintainers BOOLEAN DEFAULT FALSE,
            logs BOOLEAN DEFAULT FALSE
            )''')
        return True

    except Exception as e:
        print(f"Error creating table: {e}")
        return False
    finally:
        await connection.close()

async def create_indexes_table():
    """
    Create the necessary table for the index values in sqlite database
    """
    connection = await connect_pg_database()
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS index_values(
            name VARCHAR(40) PRIMARY KEY,
            index_ VARCHAR(350)
            )
            """)
        return True
    except Exception as e:
        print(f"error in creating the indexes_table {e}")
        return False
    finally:
        await connection.close()

async def create_cgpa_tracker_table():
    """
    Create the necessary table for the cgpa tracker in sqlite database
    """
    connection = await connect_pg_database()
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cgpa_tracker(
                chat_id BIGINT PRIMARY KEY,
                status BOOLEAN DEFAULT FALSE,
                current_cgpa VARCHAR(10)
            )
            """)
        return True
    except Exception as e:
        print(f"error in creating the cgpa_tracker {e}")
        return False
    finally:
        await connection.close()

async def create_cie_tracker_table():
    """
    Create the necessary table for the cie tracker in sqlite database
    """
    connection = await connect_pg_database()
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cie_tracker(
                chat_id BIGINT PRIMARY KEY,
                status BOOLEAN DEFAULT FALSE,
                current_cie VARCHAR(10)
            )
            """)
        return True
    except Exception as e:
        print(f"error in creating the cie_tracker {e}")
        return False
    finally:
        await connection.close()


async def check_chat_id_in_pgb(chat_id):
    """
    param : This function checks whether the chat_id of the user is already present in the database or not
    and returns true or false values
    
    """
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchval(
            "SELECT EXISTS (SELECT 1 FROM user_credentials WHERE chat_id = $1)",
            chat_id
        )
        return result
    except Exception as e:
        return False
    finally:
        await connection.close()


async def get_username(chat_id):
    """Retrieve username from the PostgreSQL database"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchval(
            "SELECT username FROM user_credentials WHERE chat_id = $1",
            chat_id
        )
        return result
    except Exception as e:
        print(f"Error retrieving username from database: {e}")
        return None
    finally:
        if connection:
            await connection.close()

async def store_banned_username(username):
    """
    This Function is used to store the banned username in the database
    :param username : Username of the banned user.
    Note : Store the banned username by converting it to lowercase or uppercase
    """
    connection = await connect_pg_database()
    try:
        await connection.execute(
            "INSERT INTO banned_users (username) VALUES (LOWER($1))", username.lower()
        )
        return True
    except Exception as e:
        print("error occured while storing the banned username into pgdatabase")
        return False
    finally:
        await connection.close()

async def set_pat_attendance_indexes(pat_attendance_indexes):
    """This Function is used to set the index values of the pat attendance table
    :param pat_attendance_indexes: Dictionary containing all the pat attendance index values 
    
    :Dictionary: {
        'course_name': course_name_index,
        'attendance_percentage': pat_attendance_percentage_index,
        'conducted_classes': conducted_classes_index,
        'attended_classes': attended_classes_index,
        'status': pat_status
    }"""

    connection = await connect_pg_database()
    name = "PAT_INDEX_VALUES"
    try:
        data = await connection.fetchrow("SELECT * FROM index_values WHERE name = $1", name)
        if data:
            await connection.execute("UPDATE index_values SET index_ = $1 WHERE name = $2", json.dumps(pat_attendance_indexes), name)
        else:
            await connection.execute("INSERT INTO index_values (name, index_) VALUES ($1, $2)", name, json.dumps(pat_attendance_indexes))
    except Exception as e:
        print(f"Error updating pat attendance index values : {e}")

async def store_cgpa_tracker_details(chat_id:int,status:bool,current_cgpa:str):
    """
    This function is used to store the cgpa_tracker details
    :param chat_id: Chat id of the user
    :param status: Boolean value which is used to stop the tracker
    :param current_cgpa: Current cgpa of the user
    table name: cgpa_tracker
    """
    connection = await connect_pg_database()
    chat_id = int(chat_id)
    current_cgpa = str(current_cgpa)
    try:
        data = await connection.fetchrow("SELECT * FROM cgpa_tracker WHERE chat_id = $1", chat_id)
        if data:
            await connection.execute("UPDATE cgpa_tracker SET status = $1,current_cgpa = $2 WHERE chat_id = $3", status,current_cgpa,chat_id)
        else:
            await connection.execute("INSERT INTO cgpa_tracker (chat_id,status,current_cgpa) VALUES ($1, $2, $3)",chat_id,status,current_cgpa)
        return True
    except Exception as e:
        print(f"Error storing cgpa tracker values : {e}")

async def store_cie_tracker_details(chat_id: int, status: bool, current_cie: str):
    """
    This function is used to store the cie_tracker details
    :param chat_id: Chat id of the user
    :param status: Boolean value which is used to stop the tracker
    :param current_cie: Current cie of the user
    table name: cie_tracker
    """
    connection = await connect_pg_database()
    chat_id = int(chat_id)
    current_cie = str(current_cie)
    try:
        data = await connection.fetchrow("SELECT * FROM cie_tracker WHERE chat_id = $1", chat_id)
        if data:
            await connection.execute("UPDATE cie_tracker SET status = $1, current_cie = $2 WHERE chat_id = $3", status, current_cie, chat_id)
        else:
            await connection.execute("INSERT INTO cie_tracker (chat_id, status, current_cie) VALUES ($1, $2, $3)", chat_id, status, current_cie)
        return True
    except Exception as e:
        print(f"Error storing cie tracker values: {e}")


async def remove_cgpa_tracker_details(chat_id):
    """
    This function is used to remove the row in cgpa_tracker table based on the chat_id
    :param chat_id: Chat id of the user

    """

    connection = await connect_pg_database()

    try:
        await connection.execute(
            "DELETE FROM cgpa_tracker WHERE chat_id = $1",(chat_id)
        )
        return True

    except Exception as e:
        print(f"error while removing the cgpa tracker details {e}. ")
        return False
    finally:
        await connection.close()


async def remove_cie_tracker_details(chat_id: int):
    """
    This function is used to remove the row in cie_tracker table based on the chat_id.
    :param chat_id: Chat id of the user
    """
    connection = await connect_pg_database()

    try:
        await connection.execute(
            "DELETE FROM cie_tracker WHERE chat_id = $1", chat_id
        )
        return True

    except Exception as e:
        print(f"Error while removing the cie tracker details: {e}.")
        return False
    finally:
        await connection.close()


async def set_attendance_indexes(all_attendance_indexes):
    """This Function is used to set the index values of the attendance table
    :param all_attendance_indexes: Dictionary containing all attendance table index values
    
    :Dictionary: {
        'course_name': course_name_index,
        'attendance_percentage': attendance_percentage_index,
        'conducted_classes': conducted_classes_index,
        'attended_classes': attended_classes_index,
        'status': status_index
    }"""

    connection = await connect_pg_database()
    name = "ATTENDANCE_INDEX_VALUES"
    try:
        data = await connection.fetchrow("SELECT * FROM index_values WHERE name = $1", name)
        if data:
            await connection.execute("UPDATE index_values SET index_ = $1 WHERE name = $2", json.dumps(all_attendance_indexes), name)
        else:
            await connection.execute("INSERT INTO index_values (name, index_) VALUES ($1, $2)", name, json.dumps(all_attendance_indexes))
    except Exception as e:
        print(f"Error updating the attendance index values : {e}")

async def set_biometric_indexes(all_biometric_index):
    """This function is used to set the biometric index values manually
    :param all_biometric_index: Dictionary containing all the biometric index values
    
    :Dictionary: {
        'status': status_index,
        'intime': intime_index,
        'outtime': outtime_index
    }
"""

    connection = await connect_pg_database()
    name = "BIOMETRIC_INDEX_VALUES"
    try:
        data = await connection.fetchrow("SELECT * FROM index_values WHERE name = $1", name)
        if data:
            await connection.execute("UPDATE index_values SET index_ = $1 WHERE name = $2", json.dumps(all_biometric_index), name)
        else:
            await connection.execute("INSERT INTO index_values (name, index_) VALUES ($1, $2)", name, json.dumps(all_biometric_index))
    except Exception as e:
        print(f"Error updating biometric index values : {e}")


async def get_all_banned_usernames():
    """
    This Function is used to get all the banned usernames
    :return: Returns a tuple containing all the usernames
    """
    connection = await connect_pg_database()
    try:
        banned_usernames = await connection.fetch(
            " SELECT * FROM banned_users "
        )
        if banned_usernames:
            return banned_usernames
        else:
            return None
    except Exception as e:
        print(f"error while retriving the data {e}")
        return False
    finally:
        await connection.close()

async def get_all_user_settings():

    connection = await connect_pg_database()

    try:
        user_setting_values = await connection.fetch(
            """
                SELECT chat_id,attendance_threshold, biometric_threshold,
                traditional_ui, extract_title FROM user_credentials
            """
        )
        if user_setting_values:
            return user_setting_values
        else:
            return None
    except Exception as e:
        print(f"Error while returning the user setting values {e}. ")
        return False
    finally:
        await connection.close()

async def get_all_index_values():
    connection = await connect_pg_database()

    try:
        index_values = await connection.fetch(
            """
                SELECT * FROM index_values
            """
        )
        if index_values:
            return index_values
        else:
            return None
    except Exception as e:
        print(f"Error while returning the index values {e}. ")
        return False
    finally:
        await connection.close()


async def get_all_cgpa_trackers():
    connection = await connect_pg_database()
    try:
        query = "SELECT * FROM cgpa_tracker"
        result = await connection.fetch(query)
        if result:
            return result
        else:
            return None
    except Exception as e:
        print(f"Error retrieving cgpa tracker data from database: {e}")
        return False
    finally:
        await connection.close()

async def get_all_cie_tracker_data():
    connection = await connect_pg_database()
    try:
        query = "SELECT * FROM cie_tracker"
        result = await connection.fetch(query)
        if result:
            return result
        else:
            return None
    except Exception as e:
        print(f"Error retrieving cie tracker data from the database : {e}")
    finally:
        await connection.close()

async def store_as_admin(name,chat_id):
    """
    Perform storing the user as admin.
    :param chat_id: chat id based on the message
    :param name: Name of the user
    """
    connection = await connect_pg_database()
    try:
        async with connection.transaction():
            await connection.execute("""INSERT INTO bot_managers 
            (chat_id,admin,name,control_access) VALUES ($1,$2,$3,$4)""",chat_id,True,name,'Full')
        return True
    except Exception as e:
        print(f"error in store_as_admin function {e}")
        return False
    
    finally:
        await connection.close()

async def store_as_maintainer(name,chat_id):

    """
    Perform storing the user as maintainer
    :param chat_id: Chat id of the maintainer.
    :param name: Name of the user"""

    connection = await connect_pg_database()
    try:
        async with connection.transaction():
            await connection.execute("INSERT INTO bot_managers (chat_id,maintainer,name,control_access) VALUES ($1,$2,$3,$4)",int(chat_id),True,name,'limited')
        return True

    except Exception as e:
        print(f"error in maintainer table{e}")
        return False

    finally:
        await connection.close()

async def update_access_data_pgdatabase(maintainer_chat_id,access_data,announcement,configure,show_reports,reply_reports,clear_reports,ban_username,unban_username,manage_maintainers,logs):
    connection = await connect_pg_database()
    try:
        await connection.execute('''
            UPDATE bot_managers
            SET access_users = $1,
                announcement = $2,
                configure = $3,
                show_reports = $4,
                reply_reports = $5,
                clear_reports = $6,
                ban_username = $7,
                unban_username = $8,
                manage_maintainers = $9,
                logs = $10
            WHERE chat_id = $11
        ''', access_data, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs, int(maintainer_chat_id))
        
    finally:
        await connection.close()

async def store_reports(unique_id: str, user_id: str, message: str, chat_id: str, 
                        replied_message: str, replied_maintainer: str, reply_status: str) -> bool:
    """
    This function is used to store the reports sent by the user.

    :param unique_id: Unique id which is generated for the specific report
    :param user_id: User ID of the user
    :param message: Report sent by the user
    :param chat_id: Chat ID of the user
    :param replied_message: Replied message
    :param replied_maintainer: Replied maintainer
    :param reply_status: Reply status
    """
    connection = await connect_pg_database()
    try:
        existing_report = await connection.fetchrow("SELECT * FROM pending_reports WHERE unique_id = $1", unique_id)
        if existing_report:
            # Update existing report fields if they are provided
            if user_id is not None:
                await connection.execute("UPDATE pending_reports SET user_id = $1 WHERE unique_id = $2", user_id, unique_id)
            if message is not None:
                await connection.execute("UPDATE pending_reports SET message = $1 WHERE unique_id = $2", message, unique_id)
            if chat_id is not None:
                await connection.execute("UPDATE pending_reports SET chat_id = $1 WHERE unique_id = $2", chat_id, unique_id)
            if replied_message is not None:
                await connection.execute("UPDATE pending_reports SET replied_message = $1 WHERE unique_id = $2", replied_message, unique_id)
            if replied_maintainer is not None:
                await connection.execute("UPDATE pending_reports SET replied_maintainer = $1 WHERE unique_id = $2", replied_maintainer, unique_id)
            if reply_status is not None:
                await connection.execute("UPDATE pending_reports SET reply_status = $1 WHERE unique_id = $2", reply_status, unique_id)
        else:
            # Insert new report if it doesn't exist
            await connection.execute(
                "INSERT INTO pending_reports (unique_id, user_id, message, chat_id, replied_message, replied_maintainer, reply_status) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                unique_id, user_id, message, chat_id, replied_message, replied_maintainer, reply_status
            )
        return True

    except Exception as e:
        print(f"Error in maintainer table: {e}")
        return False

    finally:
        await connection.close()
async def clear_banned_users_database():
    connection = await connect_pg_database()
    try:
        # Execute the SQL command to delete banned users data
        await connection.execute("DELETE FROM banned_users")
        print("Index values removed successfully! from the database")
        return True
        # handles the exceptional errors .
    except Exception as e:
        print(f"Error while clearing banned user values from the database: {e}")
        return False
    
    finally:
        # Close the database connection
        await connection.close()

async def total_users_pg_database(bot,chat_id):
    """This Function return the Total Number of users in the database."""
    connection = await connect_pg_database()
    try:
        query = "SELECT COUNT(*) FROM user_credentials"
        result = await connection.fetchval(query)
        return result
    except Exception as e:
        await bot.send_message(chat_id, f"Error retrieving data: {e}")
        return None
    finally:
        await connection.close()
async def get_all_chat_ids():
    """This Function Gets all the Chat_ids Present in the database"""
    conn = await connect_pg_database()
    try:
        query = "SELECT chat_id FROM user_credentials"
        result = await conn.fetch(query)
        # Returns the data in list.
        return [record['chat_id'] for record in result]
    except Exception as e:
        print(f"Error fetching chat IDs: {e}")
        return []
    finally:
        await conn.close()

async def get_all_credentials():
    connection = await connect_pg_database()
    try:
        if connection:
            query = "SELECT * FROM user_credentials"
            result = await connection.fetch(query)
            if result:
                return result
            else:
                return None
        else:
            print("Database connection not established.")
            return None
    except asyncpg.PostgresError as e:
        print(f"Error retrieving data from database: {e}")
        return None
    finally:
        if connection:
            await connection.close()
async def get_pat_student(chat_id):
    """This Function checks whether the pat_student column is True or False, Based on chat_id of the user"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchrow(
            "SELECT pat_student FROM user_credentials WHERE chat_id = $1",
            chat_id
        )
        if result:
            return result['pat_student']
        else:
            return False
    except Exception as e:
        print(f"Error retrieving credentials from database: {e}")
        return False
    finally:
        if connection:
            await connection.close()
async def set_pat_student_true(chat_id):
    """This Function Sets the pat_student Colum to True"""
    connection = await connect_pg_database()
    try:
        # Execute UPDATE query to set pat_student to True for the specified user_id
        await connection.execute('''
            UPDATE user_credentials
            SET pat_student = TRUE
            WHERE chat_id = $1
        ''', chat_id)
        return True
    except asyncpg.PostgresError as e:
        print(f"Error setting pat_student to True: {e}")
        return False
    finally:
        await connection.close()

async def update_all_the_threshold_values(attendance_threshold, biometric_threshold, traditional_ui, extract_title, chat_id):

    connection = await connect_pg_database()

    try:
        await connection.execute("""
            UPDATE user_credentials 
                SET attendance_threshold = $1,
                biometric_threshold = $2,
                traditional_ui = $3,
                extract_title = $4 
            WHERE chat_id = $5 
        """,attendance_threshold, biometric_threshold, traditional_ui, extract_title, chat_id)
        return True 
    except Exception as e:
        print(f"error while upadating the default threshold values {e}")
        return False
    finally:
        await connection.close() 

async def update_user_credentials_table_database():
    """
    This function is used to alter the table present in the credentials table in postgres database
    """
    connection = await connect_pg_database()
    try:
        
            await connection.execute('''

                ALTER TABLE user_credentials
                ADD COLUMN IF NOT EXISTS attendance_threshold INTEGER DEFAULT 75,
                ADD COLUMN IF NOT EXISTS biometric_threshold INTEGER DEFAULT 75,
                ADD COLUMN IF NOT EXISTS traditional_ui BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS extract_title BOOLEAN DEFAULT TRUE
                ''')
            return True
    except Exception as e:
        print(" error as occured during the creation of table. ")
        return False
    
    finally:
        await connection.close()

async def store_lab_info(chat_id,subjects,weeks):
    """Store lab information in the database.
    
    :param chat_id: Chat ID of the user.
    :param subjects: List of subjects.
    :param weeks: List of weeks.
    """
    
    subjects = json.dumps(subjects) # Serializing the data so that it can be stored.
    weeks = json.dumps(weeks)
    connection = await connect_pg_database()
    
    try:
        existing_data = await connection.execute('SELECT * FROM user_credentials WHERE chat_id = $1', chat_id)
        existing_data = connection.fetchone()
        if existing_data:

            if weeks is not None:
                connection.execute('UPDATE user_credentials SET lab_weeks_data = $1 WHERE chat_id = $2', weeks, chat_id)
            if subjects is not None:
                connection.execute('UPDATE user_credentials SET lab_subjects_data = $1 WHERE chat_id = $2', subjects, chat_id)
        else:
            connection.execute('INSERT INTO user_credentials (chat_id, lab_subjects_data, lab_weeks_data) VALUES ($1, $2, $3)',
                        chat_id,subjects,weeks)
            
    except Exception as e:
        print(f"error while executing the store_lab_info function : {e}")
        return False
    finally:
        await connection.close()


async def save_credentials_to_databse(chat_id, username, password):
    """This is used to save the username and password to the pgdatabase"""
    connection = await connect_pg_database() 
    try:
         # Await the coroutine
        await connection.execute(
            "INSERT INTO user_credentials (chat_id, username, password) VALUES ($1, $2, $3)",
            chat_id, username, password
        )
        return True
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False
    finally:
        if connection:
            await connection.close()


async def retrieve_credentials_from_database(chat_id):
    """This Function is used to Retreive the user credentials based on the chat_id
    Returns username and password. Used to login the user automatically during session timeout"""
    connection = await connect_pg_database()
    try:
        
        result = await connection.fetchrow(
            "SELECT username, password FROM user_credentials WHERE chat_id = $1",
            chat_id
        )
        if result:
            return result['username'], result['password']
        else:
            return None, None
    except Exception as e:
        print(f"Error retrieving credentials from database: {e}")
        return None, None
    finally:
        if connection:
            await connection.close()
async def get_all_lab_subjects_and_weeks_data():
    """
    This function returns all the details which are required for the lab selection for all users if the data is previously stored
    
    if data is present then this function returns: 
    - chat_id
    - lab_subjects_data
    - lab_weeks_data\n

    - None if no data

    """
    connection = await connect_pg_database()

    try:
        get_lab_sub_and_weeks_data = await connection.fetch(
            """
                SELECT  chat_id,lab_subjects_data,lab_weeks_data FROM user_credentials
            """
        )
        if get_lab_sub_and_weeks_data:
            return get_lab_sub_and_weeks_data
        else:
            return None
    except Exception as e:
        print(f"Error while returning the lab_subjects_data and lab_week_data values {e}. ")
        return False
    finally:
        await connection.close()
async def delete_labs_data_for_user(chat_id:int)->bool:
    """
    Deletes the lab data stored for a user
    
    :param chat_id: Chat id of the user
    :return: Bool
    
    Labs Data :
    
    - subjects 
    - weeks
    """
    connection = await connect_pg_database()

    try:
        await connection.execute(

            """
                DELETE lab_subjects_data,lab_weeks_data FROM user_credentials WHERE chat_id = $1
            
            """,chat_id)
        return True

    except Exception as e:
        print(f"error while deleting lab_subjects_data,lab_weeks_data from user credentials table of the pg_database {e}")
        return False
    
    finally:
        await connection.close()


async def delete_labs_data_for_all():
    """
    This is used to delete all the labs data for every user in the database
    """
    connection = await connect_pg_database()

    try:
        await connection.execute(

            """
                DELETE lab_subjects_data,lab_weeks_data FROM user_credentials
            
            """)
        return True

    except Exception as e:
        print(f"failed to delete lab_subjects_data and lab_weeks_data from user credentials table by the admin {e}. ")
        return False
    
    finally:
        await connection.close()

async def get_tables_and_columns():
    """
    This function prints all tables and their columns from the PostgreSQL database in a visual format.
    """

    connection = await connect_pg_database()  # Assuming this function connects to the PostgreSQL database

    try:
        # Fetch all tables and their columns
        tables_query = """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """

        async with connection.transaction():
            tables_columns = {}
            async for row in connection.cursor(tables_query):
                table_name = row['table_name']
                column_name = row['column_name']
                
                if table_name in tables_columns:
                    tables_columns[table_name].append(column_name)
                else:
                    tables_columns[table_name] = [column_name]

            # Print tables and their columns in a visual format
            for table, columns in tables_columns.items():
                print(f"+{'=' * (len(table) + 2)}+")
                print(f"| {table} |")
                print(f"+{'=' * (len(table) + 2)}+")
                for column in columns:
                    print(f"| {column} |")
                    print(f"+{'-' * (len(column) + 2)}+")
                print()

    except Exception as e:
        print(f"Error while fetching tables and columns: {e}")

    finally:
        await connection.close()

async def sqlite_bool_to_pg_bool(sqlbool):
    """
    This function is used to convert the boolean values from 1 to True, and 0 to False
    :return: returns boolean values in the form of True and False
    """
    return True if sqlbool else False

async def remove_saved_credentials(bot,chat_id):
    """This Function removes the Column based on chat_id. 
    This is used to remove the saved credentials."""
    connection = await connect_pg_database()
    try:
        
        await connection.execute("DELETE FROM user_credentials WHERE chat_id = $1", chat_id)
        
        await bot.send_message(chat_id,"Data deleted successfully!")
    
    except Exception as e:
        await bot.send_message(chat_id,f"Error deleting data: {e}")
    
    finally:
        await connection.close()

async def remove_saved_credentials_silent(chat_id):
    """
    This Function is mainly used to remove saved credentials of the banned usernames
    :param chat_id: Chat id of the banned username
    """
    connection = await connect_pg_database()
    try:
        await connection.execute("DELETE FROM user_credentials WHERE chat_id = $1", chat_id)
        return True
    except Exception as e:
        print(f"Error deleting data: {e}")
        return False
    finally:
        await connection.close()

async def remove_banned_username_credentials(username):
    """
    THIS FUNCTION DIDN'T PERFORM WELL UNDER MULTIPLE TESTCASES
    RECOMMENDED NOT TO USE THIS FUNCTION.
    
    This function is used to remove the credentials if the username matches with the given username
    :username: Username of the banned user.
    """
    connection = await connect_pg_database()
    try:
        await connection.execute('DELETE FROM banned_users WHERE LOWER($1) LIKE LOWER(username|| \'%\')',f'{username}')
        return True
    except Exception as e:
        print(f"error in removing banned user : {e}")
        return False
    finally:
        await connection.close()

async def remove_banned_username(username):
    """
    This Function is used to remove the banned username,
    Basically this means unban of the user
    :param username : Username of the user
    Note : While deleting send the username in the same letter case when it is stored in the database
    """
    connection = await connect_pg_database()
    try:
        await connection.execute('DELETE FROM banned_users WHERE username = $1',username)
        return True
    except Exception as e:
        print("error in removing banned user")
        return False
    
    finally:
        await connection.close()

async def remove_maintainer(chat_id):
    """
    Remove a maintainer based on the chat_id
    :param chat_id: Chat id of the maintainer
    """
    connection = await connect_pg_database()
    try:
        await connection.execute("DELETE FROM bot_managers WHERE chat_id= $1 AND maintainer = $2",int(chat_id),True)
        return True
    except Exception as e:
        print(f"error raised while relieving the maintainer from his duty {e}")
        return False
    finally:
        await connection.close()

async def remove_admin(chat_id):
    """
    Remove a admin based on the chat_id
    :param chat_id : Chat id of the admin
    """
    connection = await connect_pg_database()
    try:
        async with connection.transaction():
            await connection.execute(
                " DELETE FROM bot_managers WHERE chat_id =$1 AND admin=$1",int(chat_id),True)
            return True
    except Exception as e:
        print(f"error in removing admin from his duty {e} ")
        return False
    finally:
        await connection.close()

async def get_bot_managers_data():
    """
    This function is used to get all the data present in the bot managers table.
    :param chat_id : Chat id of the user 
    :return: Returns a tuple containg boolean access data values.
    :tuple boolean values: access_users,announcement,configure,show_reports,reply_reports,clear_reports,
    ban_username,unban username,manage_maintainers,logs
    """
    connection = await connect_pg_database()
    try:
        
        access_data = await connection.fetch(
                """
                SELECT * FROM bot_managers
                """)

        if access_data:
            return access_data
        else:
            return None           
    except Exception as e:
        print(f"Error getting bot managers data : {e}")
    finally:
        await connection.close()

async def get_all_reports():
    connection = await connect_pg_database()
    try:
    
        all_messages = await connection.fetch("SELECT * FROM pending_reports")
        if all_messages:
            return all_messages
        else:
            return None
    
    except Exception as e:
        print(f"error while running the get_all_reports function {e} ")
        return False
    
    finally:
        await connection.close()

async def delete_report(unique_id):
    """
    This function is used to delete a specific report based on unique id.
    :param unique_id: Unique id is generated specifically for a report instead of chat_id
    """
    connection =  await connect_pg_database()
    try:
        await connection.execute(
                "DELETE FROM pending_reports WHERE unique_id = $1",
                (unique_id))
        return True
    
    except Exception as e:
        print(f"failed to complete the delete_report process {e}")
        return False
    finally:
        await connection.close()


async def clear_pending_reports():
    connection =  await connect_pg_database()

    try:
        await connection.execute(
                "DELETE FROM pending_reports"
                )
        return True
    
    except Exception as e:
        print(f"failed to complete the delete_report process {e}")
        return False
    finally:
        await connection.close()


async def clear_credentials_and_settings_database():
    """This Function Clears the Postgres database."""
    # Connecting to the PSQL database
    connection = await connect_pg_database()
    try:
        async with connection.transaction():
            # Execute the SQL command to delete data
            await connection.execute("DELETE FROM user_credentials")

        print("Data erased successfully!")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False
    finally:
        # Close the database connection
        await connection.close()

async def clear_bot_manager_table():
    connection = await connect_pg_database()
    try:
        # Execute the SQL command to delete banned users data
        await connection.execute("DELETE FROM bot_managers")
        print("bot_manager values have been removed successfully! from the database")
        return True
        # handles the exceptional errors .
    except Exception as e:
        print(f"Error while clearing banned user values from the database: {e}")
        return False
    
    finally:
        # Close the database connection
        await connection.close()
async def clear_index_values_database():
    connection = await connect_pg_database()
    try:
        # Execute the SQL command to delete index values data from database
        await connection.execute("DELETE FROM index_values")
        print("Index values removed successfully! from the database")
        return True
    
    except Exception as e:
        print(f"Error while clearing index values from the database: {e}")
        return False
    
    finally:
        # Close the database connection
        await connection.close()

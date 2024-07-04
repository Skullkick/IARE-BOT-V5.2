import asyncpg,os,json

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

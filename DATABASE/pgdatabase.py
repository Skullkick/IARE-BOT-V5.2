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

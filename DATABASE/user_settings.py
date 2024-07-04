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

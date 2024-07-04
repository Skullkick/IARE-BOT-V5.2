import sqlite3,json


MANAGERS_DATABASE = "managers.db"

async def create_required_bot_manager_tables():
    await create_bot_managers_tables()
    await create_cgpa_tracker_table()
    await create_cie_tracker_table()

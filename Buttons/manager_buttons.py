from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
import asyncio
from DATABASE import managers_handler,tdatabase,pgdatabase,user_settings
from METHODS import operations,manager_operations
from CONFIGURE import extract_index

users_button = InlineKeyboardButton("USERS", callback_data="manager_users")
reports_button = InlineKeyboardButton("REPORTS", callback_data="manager_reports")
logs_button = InlineKeyboardButton("LOGS",callback_data="manager_log_file")
configure_button = InlineKeyboardButton("CONFIGURE",callback_data="manager_configure")
banned_users_button = InlineKeyboardButton("BANNED USERS", callback_data="manager_banned_user_data")
manage_maintainers_button = InlineKeyboardButton("MAINTAINERS",callback_data = "manager_maintainers")
cgpa_tracker_button = InlineKeyboardButton("TRACK CGPA",callback_data="manager_track_cgpa")
cie_tracker_button = InlineKeyboardButton("TRACK CIE",callback_data="manager_track_cie")
server_stats_button = InlineKeyboardButton("SERVER STATS",callback_data="manager_server_stats")

ADMIN_MESSAGE = f"Welcome, Administrator! Your management dashboard awaits."
ADMIN_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("REPORTS", callback_data="manager_reports"), InlineKeyboardButton("USERS", callback_data="manager_users")],
        [InlineKeyboardButton("LOGS",callback_data="manager_log_file"),InlineKeyboardButton("SERVER STATS",callback_data="manager_server_stats")],
        [InlineKeyboardButton("DATABASE", callback_data="manager_database")],
        [InlineKeyboardButton("CONFIGURE", callback_data="manager_configure")],
        [InlineKeyboardButton("MAINTAINERS",callback_data = "manager_maintainers")],
        [InlineKeyboardButton("ADMINS",callback_data="manager_admins")],
        [InlineKeyboardButton("SYNC DATABASE",callback_data="manager_sync_databases")],
        [InlineKeyboardButton("BANNED USERS",callback_data="manager_banned_user_data")],
        [InlineKeyboardButton("TRACK CGPA",callback_data="manager_track_cgpa")],
        [InlineKeyboardButton("TRACK CIE",callback_data="manager_track_cie")]
    ]
)

async def start_admin_buttons(bot,message):
    """
    This function is used to start the admin buttons
    :param bot: Client session
    :param message: Message of the user"""
    await message.reply_text(ADMIN_MESSAGE,reply_markup = ADMIN_BUTTONS)

async def start_add_maintainer_button(maintainer_chat_id,maintainer_name):
    """
    This Funtion is used to generate a yes or no button,
    in Yes button the chat_id and name will be integrated.
    :maintainer_chat_id: Chat id of the maintainer
    :maintainer_name: Name of the maintainer
    :return: Returns Buttons Containing Yes and No
    """
    add_maintainer_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Yes",callback_data=f"manager_add_maintainer_by_admin-{maintainer_name}-{maintainer_chat_id}")],
            [InlineKeyboardButton("No",callback_data="manager_cancel_add_maintainer")]
        ]
    )

    return add_maintainer_button
async def generate_permission_buttons(
        chat_id,access_users,announcement,
        configure,show_reports,reply_reports,
        clear_reports,ban_username,
        unban_username,manage_maintainers,
        logs):
    """
    This Function is used to generate the buttons containing all the permissions
    
    :param chat_id: Chat id of the manager
    :param access_users: Boolean value by which we can decide whether he has access to the users button or not.
    :param announcement: Boolean value by which we can decide whether he has access to announcements or not.
    :param configure: Boolean value by which we can decide whether he has access to the configure or not.
    :param show_reports: Boolean value by which we can decide whether he has access to the reports or not.
    :param reply_reports: Boolean value by which we can decide whether he has access to reply_reports or not.
    :param clear_reports: Boolean value by which we can decide whether he has access to the clear_reports or not.
    :param ban_username: Boolean value by which we can decide whether he has access to ban a user or not.
    :param unban_username:Boolean value by which we can decide whether he has access to unban_a user or not.
    :param manage_maintainers: Boolean value by which we can decide whether he has access to manage the maintainers or not.
    :param logs: Boolean value by which we can decide whether he has access to the logs or not.
    
    :returns: Returns buttons based on above boolean values.
    """
    Button = []
    if access_users is not None:
        if access_users == 1:
            status = "On"
        elif access_users == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Users : {status}",callback_data=f"manager_access_data-{access_users}-{chat_id}")])
    if announcement is not None:
        if announcement == 1:
            status = "On"
        elif announcement == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Announcement : {status}",callback_data=f"manager_announcement_data-{announcement}-{chat_id}")])
    if configure is not None:
        if configure == 1:
            status = "On"
        elif configure == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"configure : {status}",callback_data=f"manager_configure_data-{configure}-{chat_id}")])
    if show_reports is not None:
        if show_reports == 1:
            status = "On"
        elif show_reports == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Show report : {status}",callback_data=f"manager_show_reports_data-{show_reports}-{chat_id}")])
    if reply_reports is not None:
        if reply_reports == 1:
            status = "On"
        elif reply_reports == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Reply report : {status}",callback_data=f"manager_reply_reports_data-{reply_reports}-{chat_id}")])
    if clear_reports is not None:
        if clear_reports == 1:
            status = "On"
        elif clear_reports == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Clear reports : {status}",callback_data=f"manager_clear_report_data-{clear_reports}-{chat_id}")])
    if ban_username is not None:
        if ban_username == 1:
            status = "On"
        elif ban_username == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Ban : {status}",callback_data=f"manager_ban_username_data-{ban_username}-{chat_id}")])
    if unban_username is not None:
        if unban_username == 1:
            status = "On"
        elif unban_username == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Unban : {status}",callback_data=f"manager_unban_username_data-{unban_username}-{chat_id}")])
    if manage_maintainers is not None:
        if manage_maintainers == 1:
            status = "On"
        elif manage_maintainers == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Manager Maintainer : {status}",callback_data=f"manager_manage_maintainers_data-{manage_maintainers}-{chat_id}")])
    if logs is not None:
        if logs == 1:
            status = "On"
        elif logs == 0:
            status = "Off"
        Button.append([InlineKeyboardButton(f"Logs : {status}",callback_data=f"manager_logs_access_data-{logs}-{chat_id}")])
    Button.append([InlineKeyboardButton("Save To Cloud",callback_data=f"manager_save_changes_maintainer-{chat_id}")])
    Button.append([InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")])
    return Button

async def generate_maintainer_buttons(chat_id):
    """
    This Function is used to generate maintainer buttons for specified chat_id
    :param chat_id: Chat id of the user
    :return: returns buttons for the mainainer"""
    access_data_mode = await managers_handler.get_control_access(chat_id) 
    if access_data_mode != "Full":
        access_data = await managers_handler.get_access_data(chat_id)
        access_users = access_data[0]
        announcement = access_data[1]
        configure = access_data[2]
        show_reports = access_data[3]
        reply_reports = access_data[4]
        clear_reports = access_data[5]
        ban_username = access_data[6]
        unban_username = access_data[7]
        manage_maintainers = access_data[8]
        logs = access_data[9]
        maintainer_buttons = []
        if access_users == 1:
            maintainer_buttons.append([users_button])
        if show_reports == 1 or clear_reports == 1:
            maintainer_buttons.append([reports_button])
        if manage_maintainers == 1:
            maintainer_buttons.append([manage_maintainers_button])
        if ban_username == 1:
            maintainer_buttons.append([banned_users_button])
        if configure == 1:
            maintainer_buttons.append([configure_button])
        if logs:
            maintainer_buttons.append([logs_button])
        maintainer_buttons.append([server_stats_button])
        maintainer_buttons.append([cgpa_tracker_button])
        return maintainer_buttons
async def start_maintainer_button(bot,message):
    chat_id = message.chat.id
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    maintainer_name = await managers_handler.fetch_name(chat_id)
    if chat_id not in maintainer_chat_ids:
        return
    maintainer_buttons = await generate_maintainer_buttons(chat_id)
    maintainer_buttons = InlineKeyboardMarkup(
        inline_keyboard=maintainer_buttons
    )
    await message.reply_text(f"Hey {maintainer_name}\n\nThese are your maintainer controls.",reply_markup = maintainer_buttons)
        
async def manager_callback_function(bot,callback_query):
    if callback_query.data == "manager_log_file":
        _message = callback_query.message
        chat_id = _message.chat.id
        await callback_query.answer()
        await operations.get_logs(bot,chat_id)
        
    elif callback_query.data == "manager_reports":
        REPORTS_TEXT = "Here are some operations that you can perform on reports."
        REPORTS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Pending reports",callback_data="manager_show_reports")],
                [InlineKeyboardButton("Replied reports",callback_data="manager_show_replied_reports")],
                [InlineKeyboardButton("Clear All reports",callback_data="manager_clear_reports")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            REPORTS_TEXT,
            reply_markup = REPORTS_BUTTONS
        )
    elif callback_query.data == "manager_show_reports":
        await callback_query.answer()
        _message = callback_query.message
        await operations.show_reports(bot,_message)
    elif callback_query.data == "manager_show_replied_reports":
        _message = callback_query.message
        await operations.show_replied_reports(bot,_message)
        await callback_query.answer()
    elif callback_query.data == "manager_clear_reports":
        await callback_query.answer()
        _message = callback_query.message
        await operations.clean_pending_reports(bot,_message)

    elif callback_query.data == "manager_back_to_admin_operations":
        chat_id = callback_query.message.chat.id
        username = await managers_handler.fetch_name(chat_id)
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
        maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
        if chat_id in admin_chat_ids:
            await callback_query.edit_message_text(
                ADMIN_MESSAGE,
                reply_markup = ADMIN_BUTTONS
            )
        elif chat_id in maintainer_chat_ids:
            maintainer_buttons = await generate_maintainer_buttons(chat_id)
            maintainer_buttons = InlineKeyboardMarkup(
                inline_keyboard=maintainer_buttons
            )
            await callback_query.edit_message_text(
                f"Hey {username}\n\nThese are your maintainer controls.",
                reply_markup = maintainer_buttons
            )
    elif callback_query.data == "manager_users":
        USERS_TEXT = "Here are some operations that you can perform."
        USERS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Total users", callback_data="manager_total_users")],
                [InlineKeyboardButton("List of users(QR)",callback_data="manager_list_of_users")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")],
            ]
        )
        await callback_query.edit_message_text(
            USERS_TEXT,
            reply_markup = USERS_BUTTONS
        )

    elif callback_query.data == "manager_total_users":
        _message = callback_query.message
        chat_id = _message.chat.id
        total_count = await tdatabase.fetch_number_of_total_users_db()
        total_user_in_pgdatabase = await pgdatabase.total_users_pg_database(bot,chat_id)
        TOTAL_USERS_TEXT = f"""
```
TOTAL USERS  : {total_user_in_pgdatabase}

TOTAL USERS (PAST 24 HR'S)  : {total_count}
```
"""
        TOTAL_USERS_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Back",callback_data="manager_users")],
            ]
        )
        await callback_query.edit_message_text(
            TOTAL_USERS_TEXT,
            reply_markup = TOTAL_USERS_BUTTON
        )
    elif callback_query.data == "manager_list_of_users":
        await callback_query.answer()
        _message = callback_query.message
        chat_id = _message.chat.id
        await operations.list_users(bot,chat_id)
    elif callback_query.data == "manager_database":
        DATABASE_TEXT = "Select the database that you want to interact with."
        DATABASE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("SQLite3",callback_data="manager_sqlite3")],
                [InlineKeyboardButton("PostgresSQL",callback_data="manager_postgres_sql")],
                [InlineKeyboardButton("Backup Credentials",callback_data="manager_backup_credentials_settings")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            DATABASE_TEXT,
            reply_markup = DATABASE_BUTTONS
        )
    elif callback_query.data == "manager_backup_credentials_settings":
        _message = callback_query.message
        print("started backup")
        await manager_operations.backup_all_credentials_and_settings(bot,_message)
        await callback_query.answer()
    elif callback_query.data == "manager_sqlite3":
        SQLITE3_TEXT = "Here are few SQLITE3 operations."
        SQLITE3_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("User Sessions",callback_data="manager_select_sqlite3-user_sessions")],
                [InlineKeyboardButton("Credentials",callback_data="manager_select_sqlite3-user_credentials")],
                [InlineKeyboardButton("Banned Users",callback_data="manager_select_sqlite3-banned_users")],
                [InlineKeyboardButton("User Settings",callback_data=f"manager_select_sqlite3-user_settings")],
                [InlineKeyboardButton("Index values",callback_data=f"manager_select_sqlite3-index_values")],
                [InlineKeyboardButton("Subjects and Weeks",callback_data="manager_select_sqlite3-subject_weeks")],
                [InlineKeyboardButton("Bot Manager",callback_data="manager_select_sqlite3-bot_manager")],
                [InlineKeyboardButton("Back",callback_data="manager_database")]
            ]
        )
        await callback_query.edit_message_text(
            SQLITE3_TEXT,
            reply_markup =  SQLITE3_BUTTONS
        )
    elif "manager_select_sqlite3" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        SQLITE3_RESET_TEXT = f"Here are few operations that you can perform.\n\n\ttable - {table_name} table"
        SQLITE3_RESET_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= [
                [InlineKeyboardButton("Reset",callback_data=f"manager_reset_sqlite3-{table_name}")],
                [InlineKeyboardButton("Back", callback_data="manager_sqlite3")]
            ]
        )
        await callback_query.edit_message_text(
            SQLITE3_RESET_TEXT,
            reply_markup =  SQLITE3_RESET_BUTTONS
        )
    elif "manager_reset_sqlite3" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        SQLITE3_FINAL_RESET_DATABASE_TEXT = f"""Are you sure?\n\nWould you like to reset {table_name} table"""
        SQLITE3_FINAL_RESET_DATABASE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Yes",callback_data=f"manager_reset_final_sqlite3-{table_name}")],
                [InlineKeyboardButton("Back",callback_data="manager_sqlite3")]
            ]
        )
        await callback_query.edit_message_text(
            SQLITE3_FINAL_RESET_DATABASE_TEXT,
            reply_markup =  SQLITE3_FINAL_RESET_DATABASE_BUTTON
        )
    elif "manager_reset_final_sqlite3" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        if table_name == "user_sessions":
            await tdatabase.clear_sessions_table()
        elif table_name == "user_credentials":
            await tdatabase.clear_credentials_table()
        elif table_name == "banned_users":
            await tdatabase.clear_banned_usernames_table()
        elif table_name == "user_settings":
            await user_settings.clear_user_settings_table()
        elif table_name == "index_values":
            await user_settings.clear_indexes_table()
        elif table_name == "bot_manager":
            await managers_handler.clear_bot_managers_data()
        elif table_name == "subject_weeks":
            await tdatabase.delete_labs_subjects_weeks_all_users()
        SQLITE3_FINAL_RESET_DATABASE_TEXT = f"""{table_name} has been reset."""
        SQLITE3_FINAL_RESET_DATABASE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Back",callback_data="manager_sqlite3")]
            ]
        )
        await callback_query.edit_message_text(
            SQLITE3_FINAL_RESET_DATABASE_TEXT,
            reply_markup =  SQLITE3_FINAL_RESET_DATABASE_BUTTON
        )

    elif callback_query.data == "manager_postgres_sql":
        POSTGRES_TEXT = "Here are few Postgres operations."
        POSTGRES_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Banned Users",callback_data="manager_select_postgres-banned_users")],
                [InlineKeyboardButton("Index values",callback_data="manager_select_postgres-index_values")],
                [InlineKeyboardButton("Credentials and Settings",callback_data="manager_select_postgres-user_credentials_settings")],
                [InlineKeyboardButton("Bot Managers",callback_data="manager_select_postgres-bot_managers")],
                [InlineKeyboardButton("Subjects and Weeks",callback_data="manager_select_postgres-subject_weeks")],
                [InlineKeyboardButton("Back",callback_data="manager_database")]
            ]
        )
        await callback_query.edit_message_text(
            POSTGRES_TEXT,
            reply_markup = POSTGRES_BUTTONS
        )
    elif "manager_select_postgres" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        POSTGRES_RESET_TEXT = f"Here are few operations that you can perform in Postgres Database.\n\n\ttable - {table_name} table"
        POSTGRES_RESET_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= [
                [InlineKeyboardButton("Reset",callback_data=f"manager_reset_postgres-{table_name}")],
                [InlineKeyboardButton("Back", callback_data="manager_postgres_sql")]
            ]
        )
        await callback_query.edit_message_text(
            POSTGRES_RESET_TEXT,
            reply_markup = POSTGRES_RESET_BUTTONS
        )
    elif "manager_reset_postgres" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        POSTGRES_FINAL_RESET_DATABASE_TEXT = f"""Are you sure?\n\nWould you like to reset {table_name} table in Postgres database."""
        POSTGRES_FINAL_RESET_DATABASE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Yes",callback_data=f"manager_reset_final_postgres-{table_name}")],
                [InlineKeyboardButton("Back",callback_data="manager_postgres_sql")]
            ]
        )
        await callback_query.edit_message_text(
            POSTGRES_FINAL_RESET_DATABASE_TEXT,
            reply_markup =  POSTGRES_FINAL_RESET_DATABASE_BUTTON
        )
    elif "manager_reset_final_postgres" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        if table_name == "user_credentials_settings":
            await pgdatabase.clear_credentials_and_settings_database()
        elif table_name == "index_values":
            await pgdatabase.clear_index_values_database()
        elif table_name == "banned_users":
            await pgdatabase.clear_banned_users_database()
        elif table_name == "bot_managers":
            await pgdatabase.clear_bot_manager_table()
        elif table_name == "subject_weeks":
            await pgdatabase.delete_labs_data_for_all()
        POSTGRES_FINAL_RESET_DATABASE_TEXT = f"""{table_name} has been reset in Postgres database."""
        POSTGRES_FINAL_RESET_DATABASE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Back",callback_data="manager_postgres_sql")]
            ]
        )
        await callback_query.edit_message_text(
            POSTGRES_FINAL_RESET_DATABASE_TEXT,
            reply_markup =  POSTGRES_FINAL_RESET_DATABASE_BUTTON
        )
#     elif callback_query.data == "manager_pgtusers":
#         await callback_query.answer()
#         _message = callback_query.message
#         chat_id = _message.chat.id
#         total_user_in_pgdatabase = await pgdatabase.total_users_pg_database(bot,chat_id)
#         TOTAL_USERS_PGDATABASE_TEXT = f"""
# ```
# TOTAL USERS  : {total_user_in_pgdatabase}
# ```
# """
#         TOTAL_USERS_BUTTON = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton("Back",callback_data="manager_users")],
#             ]
#         )
#         await callback_query.edit_message_text(
#             TOTAL_USERS_PGDATABASE_TEXT,
#             reply_markup = TOTAL_USERS_BUTTON
#         )
    elif callback_query.data == "manager_pg_reset":
        PG_RESET_FINAL_TEXT = "Are you sure?"
        PG_RESET_FINAL_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= [
                [InlineKeyboardButton("YES",callback_data="manager_reset_pg_final")],
                [InlineKeyboardButton("Back", callback_data="manager_database")]
            ]
        )
        await callback_query.edit_message_text(
            PG_RESET_FINAL_TEXT,
            reply_markup =  PG_RESET_FINAL_BUTTONS
        )
    elif callback_query.data == "manager_reset_pg_final":
        _message = callback_query.message
        chat_id = _message.chat.id
        await pgdatabase.clear_database()
        await callback_query.answer()
    elif callback_query.data == "manager_maintainers":
        _message = callback_query.message
        chat_id = _message.chat.id
        # await managers_handler.fetch_name()
        maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
        # Prepare the inline keyboard buttons
        button = []
        for maintainer_chat_id in maintainer_chat_ids:
            # Fetch the username for each maintainer chat ID
            username = await managers_handler.fetch_name(maintainer_chat_id)
            # Create a button with the username and callback data including the chat ID
            button.append([
                InlineKeyboardButton(
                    text=username,
                    callback_data=f"manager_select_maintainer-{maintainer_chat_id}"
                )
            ])
        # Adding Back button
        button.append([InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")])
        # Create an inline keyboard markup
        maintainers_button = InlineKeyboardMarkup(inline_keyboard=button)
        
        # Send the message with inline keyboard (or edit the existing message)
        await callback_query.edit_message_text(
            "Maintainers : ",
            reply_markup = maintainers_button
        )
    elif "manager_select_maintainer" in callback_query.data:
        chat_id = callback_query.data.split("-")[1] # Get the chat id from the callback query
        maintainer_name = await managers_handler.fetch_name(chat_id) # Fetching the name of the manager
        SELECT_MAINTAINER_TEXT = f"Maintainer Name : **{maintainer_name}**"
        SELECT_MAINTAINER_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Permissions",callback_data=f"manager_Permission_view-{chat_id}")],
                [InlineKeyboardButton("Remove",callback_data=f"manager_remove_maintainer-{chat_id}")],
                [InlineKeyboardButton("Back",callback_data="manager_maintainers")]
            ]
        )
        await callback_query.edit_message_text(# Editing the message with the updated text and buttons
            SELECT_MAINTAINER_TEXT,
            reply_markup = SELECT_MAINTAINER_BUTTON
        )
    elif "manager_remove_maintainer" in callback_query.data:
        chat_id = callback_query.data.split("-")[1]# Get the chat id from the callback query
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        await managers_handler.remove_maintainer(chat_id) # Removing the maintainer from the database
        await pgdatabase.remove_maintainer(chat_id) # Remove the maintainer from the postgres database
        if await managers_handler.remove_cgpa_tracker_details(int(chat_id)): # remove if there is any cgpa tracker from local database
            await pgdatabase.remove_cgpa_tracker_details(int(chat_id)) # remove tracker if the tracker is found and removed from the local database
        await bot.send_message(chat_id,"You have been relieved of your Maintainer duties.")
        REMOVED_MAINTAINER_TEXT = f"Removed Maintainer **{maintainer_name}**"
        REMOVED_MAINTAINER_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Back",callback_data="manager_maintainers")]
            ]
        )
        await callback_query.edit_message_text(
            REMOVED_MAINTAINER_TEXT,
            reply_markup = REMOVED_MAINTAINER_BUTTON
        )
    elif "Permission_view" in callback_query.data:
        chat_id = callback_query.data.split("-")[1]# Get the chat id from the callback query
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_VIEW_TEXT = f"Manage access for {maintainer_name}"
        PERMISSION_VIEW_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_VIEW_TEXT,
            reply_markup = PERMISSION_VIEW_BUTTONS
        )
    elif "manager_access_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_data_bool, chat_id = data[0] ,data[1]
        if access_data_bool == '1':
            await managers_handler.set_access_users_false(chat_id) # Set the access users as false
            value = "Removed"
        elif access_data_bool == '0':
            await managers_handler.set_access_users_true(chat_id) # set the access users as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} User Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_announcement_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_announcement_bool, chat_id = data
        if access_announcement_bool == '1':
            await managers_handler.set_announcement_access_false(chat_id) # Set the access to announcement as false
            value = "Removed"
        elif access_announcement_bool == '0':
            await managers_handler.set_announcement_access_true(chat_id)# Set the access to announcement as true
            value = "Added" 
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name} \n\n {value} Announcement Rights ."
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_configure_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_configure_bool, chat_id = data[0] ,data[1]
        if access_configure_bool == '1':
            await managers_handler.set_configure_access_false(chat_id) # Set the access to configure as false
            value = "Removed"
        elif access_configure_bool == '0':
            await managers_handler.set_configure_access_true(chat_id) # Set the access to configure as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Configuration Rights."
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_show_reports_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_show_reports_bool, chat_id = data[0] ,data[1]
        if access_show_reports_bool == '1':
            await managers_handler.set_show_reports_access_false(chat_id) # Set the access to show reports as false
            value = "Removed"
        elif access_show_reports_bool == '0':
            await managers_handler.set_show_reports_access_true(chat_id) # Set the access to show reports as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Show reports Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_reply_reports_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_reply_reports_bool, chat_id = data[0] ,data[1]
        if access_reply_reports_bool == '1':
            await managers_handler.set_reply_reports_access_false(chat_id) # Set the access to reply reports as false
            value = "Removed"
        elif access_reply_reports_bool == '0':
            await managers_handler.set_reply_reports_access_true(chat_id) # Set the access to reply reports as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Reply reports rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_clear_report_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_clear_reports_bool, chat_id = data[0] ,data[1]
        if access_clear_reports_bool == '1':
            await managers_handler.set_clear_reports_access_false(chat_id) # Set the access to clear reports as false
            value = "Removed"
        elif access_clear_reports_bool == '0':
            await managers_handler.set_clear_reports_access_true(chat_id) # Set the access to clear reports as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Clear report Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_ban_username_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_ban_username_bool, chat_id = data[0] ,data[1]
        if access_ban_username_bool == '1':
            await managers_handler.set_ban_username_access_false(chat_id) # Set the access to ban username as false
            value = "Removed"
        elif access_ban_username_bool == '0':
            await managers_handler.set_ban_username_access_true(chat_id) # Set the access to ban username as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Ban Username Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_unban_username_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_unban_username_bool, chat_id = data[0] ,data[1]
        if access_unban_username_bool == '1':
            await managers_handler.set_unban_username_access_false(chat_id) # Set the access to unban username as false
            value = "Removed"
        elif access_unban_username_bool == '0':
            await managers_handler.set_unban_username_access_true(chat_id) # Set the access to unban username as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Unban Username Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_manage_maintainers_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_manage_maintainer_bool, chat_id = data[0] ,data[1]
        if access_manage_maintainer_bool == '1':
            await managers_handler.set_manage_maintainers_access_false(chat_id)# Set the access to manage maintainer as false
            value = "Removed"
        elif access_manage_maintainer_bool == '0':
            await managers_handler.set_manage_maintainers_access_true(chat_id) # Set the access to manage maintainer as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n {value} Manage Maintainer Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_logs_access_data" in callback_query.data:
        data = callback_query.data.split("-")[1:]
        access_logs_access_bool, chat_id = data[0] ,data[1]
        if access_logs_access_bool == '1':
            await managers_handler.set_logs_access_false(chat_id)# Set the access to logs access as false
            value = "Removed"
        elif access_logs_access_bool == '0':
            await managers_handler.set_logs_access_true(chat_id) # Set the access to logs access as true
            value = "Added"
        maintainer_name = await managers_handler.fetch_name(chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n{value} Logs Access Rights"
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif "manager_save_changes_maintainer" in callback_query.data:
        user_chat_id = callback_query.message.chat.id
        maintainer_chat_id = callback_query.data.split("-")[1:][0]
        maintainer_name = await managers_handler.fetch_name(maintainer_chat_id)# Fetching the name of the manager
        access_data = await managers_handler.get_access_data(maintainer_chat_id) # get all the Boolean access data values
        access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs = access_data
        access_users_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(access_users)
        announcement_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(announcement)
        configure_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(configure)
        show_reports_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(show_reports)
        reply_reports_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(reply_reports)
        clear_reports_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(clear_reports)
        ban_username_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(ban_username)
        unban_username_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(unban_username)
        manage_maintainers_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(manage_maintainers)
        logs_pgdatabase = await pgdatabase.sqlite_bool_to_pg_bool(logs)
        await pgdatabase.update_access_data_pgdatabase(maintainer_chat_id, access_users_pgdatabase, announcement_pgdatabase, configure_pgdatabase, show_reports_pgdatabase, reply_reports_pgdatabase, clear_reports_pgdatabase, ban_username_pgdatabase, unban_username_pgdatabase, manage_maintainers_pgdatabase, logs_pgdatabase)
        PERMISSION_CHANGE_TEXT = f"Manage access for {maintainer_name}\n\n Saved Changes To Cloud."
        PERMISSION_CHANGE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard= await generate_permission_buttons(user_chat_id,access_users, announcement, configure, show_reports, reply_reports, clear_reports, ban_username, unban_username, manage_maintainers, logs)
        )
        await callback_query.edit_message_text(
            PERMISSION_CHANGE_TEXT,
            reply_markup = PERMISSION_CHANGE_BUTTONS
        )
    elif callback_query.data == "manager_banned_user_data":
        chat_id = callback_query.message.chat.id
        banned_usernames = await tdatabase.get_all_banned_usernames()
        banned_usernames_buttons = []
        
        if not banned_usernames:
            await callback_query.answer()
            await bot.send_message(chat_id, "No Banned Usernames")
        
        for username in banned_usernames:
            username_for_display = username.upper()
            username_for_operation = username.lower()
            banned_usernames_buttons.append(InlineKeyboardButton(f"{username_for_display}", callback_data=f"manager_specific_banned_user-{username_for_operation}"))
        if len(banned_usernames_buttons) <= 10:
            columns = 1
        elif len(banned_usernames_buttons) >= 10 and len(banned_usernames_buttons) <= 20:
            columns = 2
        elif len(banned_usernames_buttons) >= 20:
            columns = 3
        banned_usernames_buttons = [banned_usernames_buttons[i:i+3] for i in range(0, len(banned_usernames_buttons), 3)]
        banned_usernames_buttons.append([InlineKeyboardButton("Back", callback_data="manager_back_to_admin_operations")])
        
        BANNED_USERNAME_TEXT = "Banned Usernames"
        BANNED_USERNAME_BUTTON = InlineKeyboardMarkup(inline_keyboard=banned_usernames_buttons)
        
        await callback_query.edit_message_text(BANNED_USERNAME_TEXT, reply_markup=BANNED_USERNAME_BUTTON)

    elif "manager_specific_banned_user" in callback_query.data:
        username = callback_query.data.split("-")[1:][0].lower()
        BANNED_USERNAME_TEXT = f"Would You like to Unban **{username.upper()}**"
        BANNED_USERNAME_BUTTON = InlineKeyboardMarkup(

            inline_keyboard=[
                [InlineKeyboardButton("UNBAN",callback_data=f"manager_unban_user-{username}")],
                [InlineKeyboardButton("Back",callback_data="manager_banned_user_data")]
            ]
        )
        await callback_query.edit_message_text(
            BANNED_USERNAME_TEXT,
            reply_markup = BANNED_USERNAME_BUTTON
        )
    elif "manager_unban_user" in callback_query.data:
        chat_id = callback_query.message.chat.id
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
        maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
        if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
            return
        access_data = await managers_handler.get_access_data(chat_id)
        if chat_id in maintainer_chat_ids and access_data[7] != 1:
            await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
            return
        username = callback_query.data.split("-")[1:][0].lower()
        await tdatabase.remove_banned_username(username)
        await pgdatabase.remove_banned_username(username)
        UNBANNED_USERNAME_TEXT = f"Unbanned Username Successfully **{username.upper()}**"
        UNBANNED_USERNAME_BUTTON = InlineKeyboardMarkup(

            inline_keyboard=[
                [InlineKeyboardButton("BAN",callback_data=f"manager_ban_by_username-{username}")],
                [InlineKeyboardButton("Back",callback_data="manager_banned_user_data")]
            ]
        )
        await callback_query.edit_message_text(
            UNBANNED_USERNAME_TEXT,
            reply_markup = UNBANNED_USERNAME_BUTTON
        )

    elif "manager_ban_by_username" in callback_query.data:
        username = callback_query.data.split("-")[1:][0].lower()
        await tdatabase.store_banned_username(username)
        BANNED_USERNAME_TEXT = f"Banned Username Successfully **{username.upper()}**"
        BANNED_USERNAME_BUTTON = InlineKeyboardMarkup(

            inline_keyboard=[
                [InlineKeyboardButton("UNBAN",callback_data=f"manager_unban_by_username-{username}")],
                [InlineKeyboardButton("Back",callback_data="manager_banned_user_data")]
            ]
        )
        await callback_query.edit_message_text(
            BANNED_USERNAME_TEXT,
            reply_markup = BANNED_USERNAME_BUTTON
        )
    elif callback_query.data == "manager_configure":

        CONFIGURE_BUTTON_TEXT = f"""
Click on one of the buttons to continue."""
        CONFIGURE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("AUTO INDEX",callback_data="manager_auto_configure_index")],
                [InlineKeyboardButton("MANUAL INDEX",callback_data="manager_manual_configure_index")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            CONFIGURE_BUTTON_TEXT,
            reply_markup = CONFIGURE_BUTTON
        )
    elif callback_query.data == "manager_auto_configure_index":
        _message = callback_query.message
        chat_id = _message.chat.id
        AUTO_CONFIGURE_BUTTON_TEXT = f"""
Please wait while this configures the indexes. \n\nPressing the Back button does not cancel the auto-indexing process."""
        AUTO_CONFIGURE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("BACK",callback_data="manager_configure")],
            ]
        )
        await callback_query.edit_message_text(
            AUTO_CONFIGURE_BUTTON_TEXT,
            reply_markup = AUTO_CONFIGURE_BUTTON
        )
        try:
            course_name_index,conducted_classes_index,attended_classes_index,attendance_percentage_index,att_status_index = await extract_index.get_attendance_indexes(bot,_message)
            await user_settings.set_attendance_indexes(course_name_index,conducted_classes_index,attended_classes_index,attendance_percentage_index,att_status_index)
            await pgdatabase.set_attendance_indexes(await user_settings.get_attendance_index_values())
        except Exception as e:
            await bot.send_message(chat_id,f"Error Extracting Attendance Index Values : {e}")
            return
        ATTENDANCE_INDEX_TEXT = F"""
```
--ATTENDANCE INDEX VALUES--

● COURSE NAME           : {course_name_index}

● CONDUCTED CLASSES     : {conducted_classes_index}

● ATTENDED CLASSES      : {attended_classes_index}

● ATTENDANCE PERCENTAGE : {attendance_percentage_index}

● STATUS                : {att_status_index}
```
"""
        await bot.send_message(chat_id,ATTENDANCE_INDEX_TEXT)
        try:
            intime_index,outtime_index,bio_status_index= await extract_index.get_biometric_indexes(bot,_message)
            await user_settings.set_biometric_indexes(intime_index,outtime_index,bio_status_index)
            await pgdatabase.set_biometric_indexes(await user_settings.get_biometric_index_values())
        except Exception as e:
            await bot.send_message(chat_id,f"Error Extracting Bio index Values : {e}")
            return
        BIOMETRIC_INDEX_TEXT = f"""
```
--BIOMETRIC INDEX VALUES--

● INTIME        : {intime_index}

● OUTTIME       : {outtime_index}

● STATUS INDEX  : {bio_status_index}

```"""
        await bot.send_message(chat_id,BIOMETRIC_INDEX_TEXT)
        try:
            course_name_index,conducted_classes_index,attended_classes_index,pat_attendance_percentage_index,pat_status_index = await extract_index.get_pat_indexes(bot,_message)
            await user_settings.set_pat_attendance_indexes(course_name_index,conducted_classes_index,attended_classes_index,pat_attendance_percentage_index,pat_status_index)
            await pgdatabase.set_pat_attendance_indexes(await user_settings.get_pat_attendance_index_values())
        except Exception as e:
            await bot.send_message(chat_id,f"Error Extracting PAT Indexes : {e}")
            return
        PAT_ATTENDANCE_INDEX_TEXT = f"""
```
--PAT ATTENDANCE INDEX VALUES--

● COURSE NAME               : {course_name_index}

● CONDUCTED CLASSES         : {conducted_classes_index}

● ATTENDED CLASSES          : {attended_classes_index}

● PAT ATTENDANCE PERCENTAGE : {pat_attendance_percentage_index}

● STATUS                    : {pat_status_index}
```
"""
        await bot.send_message(chat_id,PAT_ATTENDANCE_INDEX_TEXT)
        
        AFTER_AUTO_CONFIGURE_TEXT = f"""
Successfully Configured Index Values.
"""
        await  callback_query.edit_message_text(
            AFTER_AUTO_CONFIGURE_TEXT,
            reply_markup = AUTO_CONFIGURE_BUTTON
        )
    elif callback_query.data == "manager_manual_configure_index":
        MANUAL_CONFIGURE_BUTTON_TEXT = f"""
Select one of the buttons from the choices given."""
        MANUAL_CONFIGURE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("ATTENDANCE",callback_data="manager_index_attendance")],
                [InlineKeyboardButton("PAT ATTENDANCE",callback_data="manager_index_pat_att")],
                [InlineKeyboardButton("BIOMETRIC",callback_data="manager_index_biometric")],
                [InlineKeyboardButton("BACK",callback_data="manager_configure")],
            ]
        )
        await callback_query.edit_message_text(
            MANUAL_CONFIGURE_BUTTON_TEXT,
            reply_markup = MANUAL_CONFIGURE_BUTTON
        )
    elif callback_query.data == "manager_index_attendance":
        current_attendance_index_values = await user_settings.get_attendance_index_values()
        if not current_attendance_index_values:
            await user_settings.set_default_attendance_indexes()
            current_attendance_index_values = await user_settings.get_attendance_index_values()
        course_name_index = current_attendance_index_values['course_name']
        attendance_percentage_index = current_attendance_index_values['attendance_percentage']
        conducted_classes_index = current_attendance_index_values['conducted_classes']
        attended_classes_index = current_attendance_index_values['attended_classes']
        att_status_index = current_attendance_index_values['status']
        MANUAL_ATTENDANCE_INDEX_TEXT = f"""
```ATTENDANCE

COURSE NAME INDEX       : {course_name_index}

CONDUCTED CLASSES INDEX : {conducted_classes_index}

ATTENDED CLASSES INDEX  : {attended_classes_index}

ATTENDANCE % INDEX      : {attendance_percentage_index}

STATUS INDEX            : {att_status_index}

The Changes that you have made are saved temporarily\n\n To save permanently Click on "SAVE CHANGES"
```
"""
        MANUAL_ATTENDANCE_INDEX_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-course_index"), InlineKeyboardButton(course_name_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-course_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-conducted_classes_index"), InlineKeyboardButton(conducted_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-conducted_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-attended_classes_index"), InlineKeyboardButton(attended_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-attended_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-att_%_index"), InlineKeyboardButton(attendance_percentage_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-att_%_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-status_index"), InlineKeyboardButton(att_status_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-status_index")],
                    [InlineKeyboardButton("BACK", callback_data="manager_manual_configure_index")]
            ]
        )
        await callback_query.edit_message_text(
            MANUAL_ATTENDANCE_INDEX_TEXT,
            reply_markup = MANUAL_ATTENDANCE_INDEX_BUTTON
        )
    
    elif callback_query.data == "manager_index_pat_att":
        current_pat_attendance_index_values = await user_settings.get_pat_attendance_index_values()
        if not current_pat_attendance_index_values:
            await user_settings.set_default_pat_attendance_indexes()
            current_pat_attendance_index_values = await user_settings.get_pat_attendance_index_values()
        course_name_index = current_pat_attendance_index_values['course_name']
        attendance_percentage_index = current_pat_attendance_index_values['attendance_percentage']
        conducted_classes_index = current_pat_attendance_index_values['conducted_classes']
        attended_classes_index = current_pat_attendance_index_values['attended_classes']
        att_status_index = current_pat_attendance_index_values['status']
        MANUAL_PAT_ATTENDANCE_INDEX_TEXT = f"""
```PAT ATTENDANCE

COURSE NAME INDEX       : {course_name_index}

CONDUCTED CLASSES INDEX : {conducted_classes_index}

ATTENDED CLASSES INDEX  : {attended_classes_index}

ATTENDANCE % INDEX      : {attendance_percentage_index}

STATUS INDEX            : {att_status_index}

The Changes that you have made are saved temporarily\n\n To save permanently Click on "SAVE CHANGES"
```
"""
        MANUAL_PAT_ATTENDANCE_INDEX_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-course_index"), InlineKeyboardButton(course_name_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-course_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-conducted_classes_index"), InlineKeyboardButton(conducted_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-conducted_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-attended_classes_index"), InlineKeyboardButton(attended_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-attended_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-att_%_index"), InlineKeyboardButton(attendance_percentage_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-att_%_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-status_index"), InlineKeyboardButton(att_status_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-status_index")],
                    [InlineKeyboardButton("BACK", callback_data="manager_manual_configure_index")]
            ]
        )
        await callback_query.edit_message_text(
            MANUAL_PAT_ATTENDANCE_INDEX_TEXT,
            reply_markup = MANUAL_PAT_ATTENDANCE_INDEX_BUTTON
        )
    elif callback_query.data == "manager_index_biometric":
        biometric_index_values = await user_settings.get_biometric_index_values()
        if not biometric_index_values:
            await user_settings.set_default_biometric_indexes()
            biometric_index_values = await user_settings.get_biometric_index_values()
        bio_status_index = biometric_index_values['status']
        bio_intime_index = biometric_index_values['intime']
        bio_outtime_index = biometric_index_values['outtime']
        MANUAL_BIO_ATTENDANCE_INDEX_TEXT = f"""
```BIOMETRIC ATTENDANCE

IN TIME INDEX           : {bio_intime_index}

OUT TIME INDEX          : {bio_outtime_index}

STATUS INDEX            : {bio_status_index}

The Changes that you have made are saved temporarily\n\n To save permanently Click on "SAVE CHANGES"
```
"""
        MANUAL_BIO_ATTENDANCE_INDEX_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("-", callback_data="manager_bio_attendance-decrease-intime_index"), InlineKeyboardButton(bio_intime_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_bio_attendance-increase-intime_index")],
                [InlineKeyboardButton("-", callback_data="manager_bio_attendance-decrease-outtime_index"), InlineKeyboardButton(bio_outtime_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_bio_attendance-increase-outtime_index")],
                [InlineKeyboardButton("-", callback_data="manager_bio_attendance-decrease-status_index"), InlineKeyboardButton(bio_status_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_bio_attendance-increase-status_index")],
                [InlineKeyboardButton("BACK", callback_data="manager_manual_configure_index")]
            ]
        )
        await callback_query.edit_message_text(
            MANUAL_BIO_ATTENDANCE_INDEX_TEXT,
            reply_markup = MANUAL_BIO_ATTENDANCE_INDEX_BUTTON
        )
    elif  "manager_attendance" in callback_query.data:
        vary, column = callback_query.data.split("-")[1:]
        current_attendance_index_values = await user_settings.get_attendance_index_values()
        course_name_index = current_attendance_index_values['course_name']
        attendance_percentage_index = current_attendance_index_values['attendance_percentage']
        conducted_classes_index = current_attendance_index_values['conducted_classes']
        attended_classes_index = current_attendance_index_values['attended_classes']
        att_status_index = current_attendance_index_values['status']
        if vary == "increase":
            if column == "course_index":
                course_name_index += 1
            elif column == "att_%_index":
                attendance_percentage_index += 1
            elif column == "conducted_classes_index":
                conducted_classes_index += 1
            elif column == "attended_classes_index":
                attended_classes_index += 1
            elif column == "status_index":
                att_status_index += 1
        elif vary == "decrease":
            if column == "course_index":
                course_name_index -= 1
            elif column == "att_%_index":
                attendance_percentage_index -= 1
            elif column == "conducted_classes_index":
                conducted_classes_index -= 1
            elif column == "attended_classes_index":
                attended_classes_index -= 1
            elif column == "status_index":
                att_status_index -= 1

        await user_settings.set_attendance_indexes(
            course_name_index,
            conducted_classes_index,
            attended_classes_index,
            attendance_percentage_index,
            att_status_index
        )
        MANUAL_ATTENDANCE_INDEX_TEXT = f"""
```ATTENDANCE

COURSE NAME INDEX       : {course_name_index}

CONDUCTED CLASSES INDEX : {conducted_classes_index}

ATTENDED CLASSES INDEX  : {attended_classes_index}

ATTENDANCE % INDEX      : {attendance_percentage_index}

STATUS INDEX            : {att_status_index}
```
"""
        MANUAL_ATTENDANCE_INDEX_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-course_index"), InlineKeyboardButton(course_name_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-course_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-conducted_classes_index"), InlineKeyboardButton(conducted_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-conducted_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-attended_classes_index"), InlineKeyboardButton(attended_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-attended_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-att_%_index"), InlineKeyboardButton(attendance_percentage_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-att_%_index")],
                    [InlineKeyboardButton("-", callback_data="manager_attendance-decrease-status_index"), InlineKeyboardButton(att_status_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_attendance-increase-status_index")],
                    [InlineKeyboardButton("SAVE CHANGES",callback_data="manager_save_indexes-attendance")],
                    [InlineKeyboardButton("BACK", callback_data="manager_manual_configure_index")]
            ]
        )
        await callback_query.edit_message_text(
            MANUAL_ATTENDANCE_INDEX_TEXT,
            reply_markup = MANUAL_ATTENDANCE_INDEX_BUTTON
        )
    elif "manager_pat_attendance" in callback_query.data:
        vary, column = callback_query.data.split("-")[1:]
        current_attendance_index_values = await user_settings.get_pat_attendance_index_values()
        course_name_index = current_attendance_index_values['course_name']
        attendance_percentage_index = current_attendance_index_values['attendance_percentage']
        conducted_classes_index = current_attendance_index_values['conducted_classes']
        attended_classes_index = current_attendance_index_values['attended_classes']
        att_status_index = current_attendance_index_values['status']
        if vary == "increase":
            if column == "course_index":
                course_name_index += 1
            elif column == "att_%_index":
                attendance_percentage_index += 1
            elif column == "conducted_classes_index":
                conducted_classes_index += 1
            elif column == "attended_classes_index":
                attended_classes_index += 1
            elif column == "status_index":
                att_status_index += 1
        elif vary == "decrease":
            if column == "course_index":
                course_name_index -= 1
            elif column == "att_%_index":
                attendance_percentage_index -= 1
            elif column == "conducted_classes_index":
                conducted_classes_index -= 1
            elif column == "attended_classes_index":
                attended_classes_index -= 1
            elif column == "status_index":
                att_status_index -= 1

        await user_settings.set_pat_attendance_indexes(
            course_name_index,
            conducted_classes_index,
            attended_classes_index,
            attendance_percentage_index,
            att_status_index
        )
        MANUAL_PAT_ATTENDANCE_INDEX_TEXT = f"""
```PAT ATTENDANCE

COURSE NAME INDEX       : {course_name_index}

ATTENDANCE % INDEX      : {attendance_percentage_index}

CONDUCTED CLASSES INDEX : {conducted_classes_index}

ATTENDED CLASSES INDEX  : {attended_classes_index}

STATUS INDEX            : {att_status_index}
```
"""
        MANUAL_PAT_ATTENDANCE_INDEX_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-course_index"), InlineKeyboardButton(course_name_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-course_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-conducted_classes_index"), InlineKeyboardButton(conducted_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-conducted_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-attended_classes_index"), InlineKeyboardButton(attended_classes_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-attended_classes_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-att_%_index"), InlineKeyboardButton(attendance_percentage_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-att_%_index")],
                    [InlineKeyboardButton("-", callback_data="manager_pat_attendance-decrease-status_index"), InlineKeyboardButton(att_status_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_pat_attendance-increase-status_index")],
                    [InlineKeyboardButton("SAVE CHANGES",callback_data="manager_save_indexes-pat_attendance")],
                    [InlineKeyboardButton("BACK", callback_data="manager_manual_configure_index")]
            ]
        )
        await callback_query.edit_message_text(
            MANUAL_PAT_ATTENDANCE_INDEX_TEXT,
            reply_markup = MANUAL_PAT_ATTENDANCE_INDEX_BUTTON
        )
    elif "manager_bio_attendance" in callback_query.data:
        vary, column = callback_query.data.split("-")[1:]
        biometric_index_values = await user_settings.get_biometric_index_values()
        bio_status_index = int(biometric_index_values['status'])
        bio_intime_index = int(biometric_index_values['intime'])
        bio_outtime_index = int(biometric_index_values['outtime'])
        if vary == "increase":
            if column == "status_index":
                bio_status_index = bio_status_index + 1
                print(bio_status_index)
                print(bio_intime_index)
                print(bio_outtime_index)
            elif column == "intime_index":
                bio_intime_index = bio_intime_index + 1
            elif column == "outtime_index":
                bio_outtime_index = bio_outtime_index + 1
        elif vary == "decrease":
            if column == "status_index":
                bio_status_index = bio_status_index-1
            elif column == "intime_index":
                bio_intime_index = bio_intime_index-1
            elif column == "outtime_index":
                bio_outtime_index = bio_outtime_index-1
        await user_settings.set_biometric_indexes(
            bio_intime_index,
            bio_outtime_index,
            bio_status_index
        )
        MANUAL_BIO_ATTENDANCE_INDEX_TEXT = f"""
```BIOMETRIC ATTENDANCE

IN TIME INDEX           : {bio_intime_index}

OUT TIME INDEX          : {bio_outtime_index}

STATUS INDEX            : {bio_status_index}
```
"""
        MANUAL_BIO_ATTENDANCE_INDEX_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("-", callback_data="manager_bio_attendance-decrease-intime_index"), InlineKeyboardButton(bio_intime_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_bio_attendance-increase-intime_index")],
                [InlineKeyboardButton("-", callback_data="manager_bio_attendance-decrease-outtime_index"), InlineKeyboardButton(bio_outtime_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_bio_attendance-increase-outtime_index")],
                [InlineKeyboardButton("-", callback_data="manager_bio_attendance-decrease-status_index"), InlineKeyboardButton(bio_status_index, callback_data="None"), InlineKeyboardButton("+", callback_data="manager_bio_attendance-increase-status_index")],
                [InlineKeyboardButton("SAVE CHANGES", callback_data="manager_save_indexes-bio_attendance")],
                [InlineKeyboardButton("BACK", callback_data="manager_manual_configure_index")]
            ]
        )

        await callback_query.edit_message_text(
            MANUAL_BIO_ATTENDANCE_INDEX_TEXT,
            reply_markup = MANUAL_BIO_ATTENDANCE_INDEX_BUTTON
        )
    elif "manager_save_indexes" in callback_query.data:
        column = callback_query.data.split("-")[1:][0]
        if column == "attendance":
            attendance_index_values_dictionary = await user_settings.get_attendance_index_values()
            await pgdatabase.set_attendance_indexes(attendance_index_values_dictionary)
        elif column == "pat_attendance":
            pat_attendance_index_values = await user_settings.get_pat_attendance_index_values()
            await pgdatabase.set_pat_attendance_indexes(pat_attendance_index_values)
        elif column == "bio_attendance":
            bio_attendance_index_values = await user_settings.get_biometric_index_values()
            await pgdatabase.set_biometric_indexes(bio_attendance_index_values)
        await callback_query.answer()
    elif "manager_add_maintainer_by_admin" in callback_query.data:
        _message = callback_query.message
        data = callback_query.data.split("-")[1:]
        maintainer_name = data[0]
        maintainer_chat_id = data[1]
        await manager_operations.add_maintainer(bot,_message,maintainer_chat_id,maintainer_name)
        await callback_query.message.delete()
    elif "manager_cancel_add_maintainer" in callback_query.data:
       await callback_query.message.delete()
       await bot.send_message(callback_query.message.chat.id,"Cancelled Adding Maintainer")
    elif "manager_admins" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        # await managers_handler.fetch_name()
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
        # Prepare the inline keyboard buttons
        button = []
        for admin_chat_id in admin_chat_ids:
            # Fetch the username for each admin chat ID
            username = await managers_handler.fetch_name(admin_chat_id)
            # Create a button with the username and callback data including the chat ID
            button.append([
                InlineKeyboardButton(
                    text=username,
                    callback_data=f"manager_select_admin-{admin_chat_id}"
                )
            ])
        # Adding Back button
        button.append([InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")])
        # Create an inline keyboard markup
        admin_button = InlineKeyboardMarkup(inline_keyboard=button)
        
        # Send the message with inline keyboard (or edit the existing message)
        await callback_query.edit_message_text(
            "Administrators : ",
            reply_markup = admin_button
        )
    elif "manager_select_admin" in callback_query.data:
        chat_id = callback_query.message.chat.id
        admin_chat_id = callback_query.data.split("-")[1:][0]
        admin_name = await managers_handler.fetch_name(admin_chat_id) # Fetching the name of the manager
        if chat_id == int(admin_chat_id):
            SELECT_ADMIN_TEXT = f"Admin Name : **{admin_name}**"
            SELECT_ADMIN_BUTTON = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("QUIT RESPONSIBILITY",callback_data=f"manager_quit_admin_responsibilities-{admin_chat_id}")],
                    [InlineKeyboardButton("BACK",callback_data="manager_admins")]
                ]
            )
        else:
            SELECT_ADMIN_TEXT = f"Admin Name : **{admin_name}**"
            SELECT_ADMIN_BUTTON = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("REMOVE",callback_data=f"manager_remove_admin_responsibilities-{admin_chat_id}")],
                    [InlineKeyboardButton("BACK",callback_data="manager_admins")]
                ]
            )

        await callback_query.edit_message_text(# Editing the message with the updated text and buttons
            SELECT_ADMIN_TEXT,
            reply_markup = SELECT_ADMIN_BUTTON
        )
    elif "manager_quit_admin_responsibilities" in callback_query.data:
        admin_chat_id = callback_query.data.split("-")[1:][0]
        await managers_handler.remove_admin(admin_chat_id)
        await pgdatabase.remove_admin(admin_chat_id) # Removing admin from the pgdatabase
        if await managers_handler.remove_cgpa_tracker_details(int(chat_id)): # remove if there is any cgpa tracker from local database
            await pgdatabase.remove_cgpa_tracker_details(int(chat_id)) # remove tracker if the tracker is found and removed from the local database
        await callback_query.answer()
        await callback_query.message.delete()
        await bot.send_message(admin_chat_id,"Your resignation as an administrator has been processed. We value your efforts and wish you the best.")
    elif "manager_remove_admin_responsibilities" in callback_query.data :
        user_chat_id = callback_query.message.chat.id
        user_name = await manager_operations.get_username(bot,user_chat_id)
        admin_chat_id = callback_query.data.split("-")[1:][0]
        admin_name = await manager_operations.get_username(bot,admin_chat_id)
        await managers_handler.remove_admin(admin_chat_id)
        await pgdatabase.remove_admin(admin_chat_id) # Removing admin from the pgdatabase
        if await managers_handler.remove_cgpa_tracker_details(int(chat_id)): # remove if there is any cgpa tracker from local database
            await pgdatabase.remove_cgpa_tracker_details(int(chat_id)) # remove tracker if the tracker is found and removed from the local database
        await callback_query.answer()
        await bot.send_message(user_chat_id,f"You have removed {admin_name} as Admin.")
        await bot.send_message(admin_chat_id,f"You are no longer an admin, as per {user_name}'s decision.")
    elif callback_query.data == "None":
            await callback_query.answer()
    elif callback_query.data == "manager_track_cgpa":
        _message = callback_query.message
        chat_id = _message.chat.id
        tracker_details = await managers_handler.get_cgpa_tracker_details(chat_id)
        if tracker_details:
            status,current_cgpa = tracker_details
            if status:
                CGPA_TRACKER_TEXT = F"""
```CGPA TRACKER
Your CGPA tracker is Live.

Your Current CGPA is {current_cgpa}

You will get notified of your result if your results are out.

To stop tracking your CGPA, Click on \"Stop\"
```
"""
                CGPA_TRACKER_BUTTON = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton("Stop",callback_data = "manager_stop_cgpa_tracker")],
                        [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
                    ]
                    )
            else:
                CGPA_TRACKER_TEXT = f"""
```
CGPA Tracker can be used to track the result

This tracks the CGPA every 10 minutes and if there is any change in the CGPA the updated CGPA and SGPA will be sent to your chat

Click on \"Start\" to start the tracker

```
"""
                CGPA_TRACKER_BUTTON = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton("Start",callback_data = "manager_start_cgpa_tracker")],
                        [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
                    ]
                    )
        elif tracker_details is None:
            CGPA_TRACKER_TEXT = f"""
```
CGPA Tracker can be used to track the result

This tracks the CGPA every 10 minutes and if there is any change in the CGPA the updated CGPA and SGPA will be sent to your chat

Click on \"Start\" to start the tracker
```"""
            CGPA_TRACKER_BUTTON = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("Start",callback_data = f"manager_start_cgpa_tracker")],
                    [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
                ]
                )
        await callback_query.edit_message_text(
            CGPA_TRACKER_TEXT,
            reply_markup = CGPA_TRACKER_BUTTON
        )
    elif callback_query.data == "manager_track_cie":
        _message = callback_query.message
        chat_id = _message.chat.id
        tracker_details = await managers_handler.get_cie_tracker_details(chat_id=chat_id)
        if tracker_details:
            status,current_cie = tracker_details
            if status:
                CIE_TRACKER_TEXT = F"""
```CIE TRACKER
Your CIE tracker is Live.

Your Current CIE Marks are {current_cie}

You will get notified of your result if your results are out.

To stop tracking your CIE , Click on \"Stop\"
```
"""
                CIE_TRACKER_BUTTON = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton("Stop",callback_data = "manager_stop_cie_tracker")],
                        [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
                    ]
                    )
            else:
                CIE_TRACKER_TEXT = f"""
```
CIE Tracker can be used to track the result

This tracks the CIE every 10 minutes and if there is any change in the CIE marks, the updated CIE marks will be sent to your chat

Click on \"Start\" to start the tracker

```
"""
                CIE_TRACKER_BUTTON = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton("Start",callback_data = "manager_start_cie_tracker")],
                        [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
                    ]
                    )
        elif tracker_details is None:
            CIE_TRACKER_TEXT = f"""
```
CIE Tracker can be used to track the result

This tracks the CIE every 10 minutes and if there is any change in the CIE, the updated CIE marks will be sent to your chat

Click on \"Start\" to start the tracker
```"""
            CIE_TRACKER_BUTTON = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("Start",callback_data = f"manager_start_cie_tracker")],
                    [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
                ]
                )
        await callback_query.edit_message_text(
            CIE_TRACKER_TEXT,
            reply_markup = CIE_TRACKER_BUTTON
        )
    elif callback_query.data == "manager_start_cie_tracker":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_cie = await manager_operations.total_cie_marks(bot,chat_id)
        await managers_handler.store_cie_tracker_details(chat_id,1,current_cie)
        await pgdatabase.store_cie_tracker_details(chat_id,True,current_cie)
        tracker_details = await managers_handler.get_cie_tracker_details(chat_id)
        status,current_cie = tracker_details
        CIE_START_TRACKER_TEXT = F"""
```CIE TRACKER
Your CIE tracker is Live.

Your Current CIE Marks are {current_cie}

You will get notified of your result if your results are out.

To stop tracking your CIE, Click on \"Stop\"
```
"""
        CIE_START_TRACKER_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Stop",callback_data = f"manager_stop_cie_tracker")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            CIE_START_TRACKER_TEXT,
            reply_markup = CIE_START_TRACKER_BUTTON
        )
    
    elif callback_query.data == "manager_stop_cie_tracker":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_cie = await manager_operations.total_cie_marks(bot,chat_id)
        await managers_handler.store_cie_tracker_details(chat_id,0,current_cie)
        await pgdatabase.store_cie_tracker_details(chat_id,False,current_cie)
        CIE_STOP_TRACKER_TEXT = f"""
```CIE TRACKER
CIE Tracker has been stopped

Hope Tracker helped you to track the latest CIE Marks

```
"""
        CIE_STOPPED_TRACKER_BUTTON =  InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Start",callback_data = f"manager_start_cie_tracker")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            CIE_STOP_TRACKER_TEXT,
            reply_markup = CIE_STOPPED_TRACKER_BUTTON
        )
    elif callback_query.data == "manager_start_cgpa_tracker":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_cgpa = await manager_operations.get_cgpa(bot,chat_id)
        await managers_handler.store_cgpa_tracker_details(chat_id,1,current_cgpa)
        await pgdatabase.store_cgpa_tracker_details(chat_id,True,current_cgpa)
        tracker_details = await managers_handler.get_cgpa_tracker_details(chat_id)
        status,current_cgpa = tracker_details
        CGPA_START_TRACKER_TEXT = F"""
```CGPA TRACKER
Your CGPA tracker is Live.

Your Current CGPA is {current_cgpa}

You will get notified of your result if your results are out.

To stop tracking your CGPA, Click on \"Stop\"
```
"""
        CGPA_START_TRACKER_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Stop",callback_data = f"manager_stop_cgpa_tracker")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            CGPA_START_TRACKER_TEXT,
            reply_markup = CGPA_START_TRACKER_BUTTON
        )
    elif callback_query.data == "manager_stop_cgpa_tracker":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_cgpa = await manager_operations.get_cgpa(bot,chat_id)
        await managers_handler.store_cgpa_tracker_details(chat_id,0,current_cgpa)
        await pgdatabase.store_cgpa_tracker_details(chat_id,False,current_cgpa)
        CGPA_STOP_TRACKER_TEXT = f"""
```CGPA TRACKER
CGPA Tracker has been stopped

Hope Tracker helped you to track the latest GPA

```
"""
        CGPA_STOPPED_TRACKER_BUTTON =  InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Start",callback_data = f"manager_start_cgpa_tracker")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            CGPA_STOP_TRACKER_TEXT,
            reply_markup = CGPA_STOPPED_TRACKER_BUTTON
        )

    elif callback_query.data == "manager_stop_cgpa_tracker":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_cie = await manager_operations.total_cie_marks(bot,chat_id)
        await managers_handler.store_cie_tracker_details(chat_id,0,current_cie)
        await pgdatabase.store_cie_tracker_details(chat_id,False,current_cie)
        CIE_STOP_TRACKER_TEXT = f"""
```CIE TRACKER
CIE Tracker has been stopped

Hope Tracker helped you to track the latest CIE marks

```
"""
        CIE_STOPPED_TRACKER_BUTTON =  InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Start",callback_data = f"manager_start_cie_tracker")],
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            CIE_STOP_TRACKER_TEXT,
            reply_markup = CIE_STOPPED_TRACKER_BUTTON
        )
    elif callback_query.data == "manager_server_stats":
        SERVER_STATS_MESSAGE = f"""
```SERVER STATS
{await manager_operations.get_server_stats()}
```"""
        BACK_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Back",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            SERVER_STATS_MESSAGE,
            reply_markup = BACK_BUTTON
        )
    elif callback_query.data == "manager_sync_databases":
        SYNC_DATABASE_TEXT = "Select the databases that you want to sync."
        SYNC_DATABASE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("CREDENTIALS",callback_data="manager_select_sync_database-credentials")],
                [InlineKeyboardButton("USER SETTINGS",callback_data="manager_select_sync_database-user_settings")],
                [InlineKeyboardButton("REPORTS",callback_data="manager_select_sync_database-reports")],
                [InlineKeyboardButton("BANNED USERS",callback_data="manager_select_sync_database-banned_users")],
                [InlineKeyboardButton("INDEX DATA",callback_data="manager_select_sync_database-index_data")],
                [InlineKeyboardButton("BOT MANAGER DATA",callback_data="manager_select_sync_database-bot_manager_data")],
                [InlineKeyboardButton("BACK",callback_data="manager_back_to_admin_operations")]
            ]
        )
        await callback_query.edit_message_text(
            SYNC_DATABASE_TEXT,
            reply_markup = SYNC_DATABASE_BUTTONS
        )
    elif "manager_select_sync_database" in callback_query.data:
        table_name = callback_query.data.split("-")[1]
        if table_name == "credentials":
            await operations.perform_sync_credentials(bot)
        elif table_name == "user_settings":
            await operations.perform_sync_user_settings(bot)
        elif table_name == "reports":
            await operations.perform_sync_reports(bot)
        elif table_name == "banned_users":
            await operations.perform_sync_banned_users(bot)
        elif table_name == "index_data":
            await operations.perform_sync_index_data(bot)
        elif table_name == "bot_manager_data":
            await operations.perform_sync_bot_manager_data(bot)
        await callback_query.answer()
    

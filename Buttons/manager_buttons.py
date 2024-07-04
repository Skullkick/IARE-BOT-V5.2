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

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

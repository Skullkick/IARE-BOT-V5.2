from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from METHODS import labs_handler, operations,manager_operations,lab_operations,pdf_compressor
from Buttons import buttons,manager_buttons
from pyrogram.errors import FloodWait
import time,logging
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
bot = Client(
        "IARE BOT",
        bot_token = BOT_TOKEN,
        api_id = API_ID,
        api_hash = API_HASH
)
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("bot_errors.log"),
                        logging.StreamHandler()
                    ])

@bot.on_message(filters.command(commands=['start']))
async def _start(bot,message):
    try:
        await operations.get_random_greeting(bot, message)
    except Exception as e:
        logging.error("Error in 'start' command: %s", e)
@bot.on_message(filters.command(commands=['login']))
async def _login(bot,message):
    try:
        await operations.login(bot, message)
    except Exception as e:
        logging.error("Error in 'login' command: %s", e)
@bot.on_message(filters.command(commands=['logout']))
async def _logout(bot,message):
    try:
        await operations.logout(bot, message)
    except Exception as e:
        logging.error("Error in 'logout' command: %s", e)

@bot.on_message(filters.command(commands=['report']))
async def _report(bot,message):
    try:
        await operations.report(bot, message)
    except Exception as e:
        logging.error("Error in 'report' command: %s", e)
@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        await operations.help_command(bot, message)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)
@bot.on_message(filters.command(commands="settings"))
async def settings_buttons(bot,message):
    # Initializes settings for the user
    chat_id = message.chat.id
    try:
        if await user_settings.fetch_user_settings(chat_id) is None:
            await user_settings.set_user_default_settings(chat_id)
        await buttons.start_user_settings(bot, message)
    except Exception as e:
        logging.error("Error in 'settings' command: %s", e)

# @bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    await operations.attendance(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['biometric']))
async def _biometric(bot,message):
    await operations.biometric(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['bunk']))
async def _bunk(bot,message):
    await operations.bunk(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['profile']))
async def _profile_details(bot,message):
    await operations.profile_details(bot,message)
# @bot.on_message(filters.command(commands=['del_save']))
async def delete_login_details_pgdatabase(bot,message):
    chat_id = message.chat.id
    await pgdatabase.remove_saved_credentials(bot,chat_id)
# @bot.on_message(filters.command(commands="deletepdf"))
async def delete_pdf(bot,message):
    chat_id = message.chat.id
    if await labs_handler.remove_pdf_file(chat_id) is True:
        await bot.send_message(chat_id,"Deleted Successfully")
    else:
        await bot.send_message(chat_id,"Failed")
@bot.on_message(filters.command(commands=['reply']))
async def _reply(bot,message):
    try:
        await operations.reply_to_user(bot, message)
    except Exception as e:
        logging.error("Error in 'reply' command: %s", e)
@bot.on_message(filters.command(commands=['rshow']))
async def _show_requests(bot,message):
    try:
        await operations.show_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'rshow' command: %s", e)

@bot.on_message(filters.command(commands=['announce']))
async def _announce(bot,message):
    try:
        await manager_operations.announcement_to_all_users(bot, message)
    except Exception as e:
        logging.error("Error in 'announce' command: %s", e)

@bot.on_message(filters.command(commands=['lusers']))
async def _users_list(bot,message):
    try:
        await operations.list_users(bot, message.chat.id)
    except Exception as e:
        logging.error("Error in 'lusers' command: %s", e)
@bot.on_message(filters.command(commands=['tusers']))
async def _total_users(bot,message):
    try:
        await operations.total_users(bot, message)
    except Exception as e:
        logging.error("Error in 'tusers' command: %s", e)
@bot.on_message(filters.command(commands=['rclear']))
async def _clear_requests(bot,message):
    try:
        await operations.clean_pending_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'rclear' command: %s", e)
@bot.on_message(filters.command(commands=['reset']))
async def _reset_sqlite(bot,message):
    try:
        await operations.reset_user_sessions_database(bot, message)
    except Exception as e:
        logging.error("Error in 'reset' command: %s", e)
# @bot.on_message(filters.command(commands=["pgtusers"]))
async def _total_users_pg_database(bot,message):
    chat_id = message.chat.id
    await pgdatabase.total_users_pg_database(bot,chat_id)
@bot.on_message(filters.command(commands="admin"))
async def admin_buttons(bot,message):
    chat_id = message.chat.id
    try:
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
        if chat_id in admin_chat_ids:
            await manager_buttons.start_admin_buttons(bot, message)
    except Exception as e:
        logging.error("Error in 'admin' command: %s", e)

@bot.on_message(filters.command(commands="maintainer"))
async def maintainer_buttons(bot,message):
    try:
        await manager_buttons.start_maintainer_button(bot, message)
    except Exception as e:
        logging.error("Error in 'maintainer' command: %s", e)
@bot.on_message(filters.command(commands="ban"))
async def ban_username(bot,message):
    try:
        await manager_operations.ban_username(bot, message)
    except Exception as e:
        logging.error("Error in 'ban' command: %s", e)

@bot.on_message(filters.command(commands="unban"))
async def unban_username(bot,message):
    try:
        await manager_operations.unban_username(bot, message)
    except Exception as e:
        logging.error("Error in 'unban' command: %s", e)

@bot.on_message(filters.command(commands="authorize"))
async def authorize_and_add_admin(bot,message):
    try:
        await manager_operations.add_admin_by_authorization(bot, message)
    except Exception as e:
        logging.error("Error in 'authorize' command: %s", e)
@bot.on_message(filters.forwarded | filters.command(commands="add_maintainer"))
async def add_maintainer(bot, message):
    try:
        await labs_handler.download_pdf(bot, message, pdf_compress_scrape=pdf_compressor.use_pdf_compress_scrape)
        await manager_operations.verification_to_add_maintainer(bot, message)
    except Exception as e:
        logging.error("Error in 'add_maintainer' command: %s", e)

@bot.on_message(filters.private & filters.document)
async def _download_pdf(bot,message):
    try:
        await labs_handler.download_pdf(bot, message, pdf_compress_scrape=pdf_compressor.use_pdf_compress_scrape)
    except Exception as e:
        logging.error("Error in '_download_pdf' function: %s", e)


@bot.on_message(filters.private & ~filters.service)
async def _get_title_from_user(bot,message):
    try:
        if message.text:
            await labs_handler.get_title_from_user(bot, message)
    except Exception as e:
        logging.error("Error in '_get_title_from_user' function: %s", e)
            
@bot.on_callback_query()
async def _callback_function(bot,callback_query):
    try:
        if "manager" in callback_query.data:
            await manager_buttons.manager_callback_function(bot, callback_query)
        else:
            await buttons.callback_function(bot, callback_query)
    except Exception as e:
        logging.error("Error in '_callback_function': %s", e)

async def main(bot):
    try:
        await tdatabase.create_all_tdatabase_tables()
        await pgdatabase.create_all_pgdatabase_tables()
        await user_settings.create_user_settings_tables()
        await managers_handler.create_required_bot_manager_tables()
        await operations.sync_databases(bot)
    except Exception as e:
        logging.error("Error in 'main' function: %s", e)

    while True:
        cgpa_tracker_chat_ids = await managers_handler.get_all_cgpa_tracker_chat_ids()
        cie_tracker_chat_ids = await managers_handler.get_all_cie_tracker_chat_ids()
        if cgpa_tracker_chat_ids:
            for chat_id in cgpa_tracker_chat_ids:
                await manager_operations.cgpa_tracker(bot,chat_id)
        if cie_tracker_chat_ids:
            for chat_id in cie_tracker_chat_ids:
                await manager_operations.cie_tracker(bot,chat_id)
        await asyncio.sleep(300)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(bot))
    bot.run()

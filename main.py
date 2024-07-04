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

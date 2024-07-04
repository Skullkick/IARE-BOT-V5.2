from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from Buttons import buttons
from bs4 import BeautifulSoup 
import requests,json,uuid,os,pyqrcode,random,re
from pytz import timezone
from datetime import datetime
import io,shutil


login_message_updated_ui = f"""
```NO USER FOUND
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot
```
"""
    
login_message_traditional_ui = f"""
NO USER FOUND

⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot"""



async def get_indian_time():
    return datetime.now(timezone('Asia/Kolkata'))
async def get_random_greeting(bot,message):
    """
    Get a random greeting based on the time and day.
    """
    chat_id = message.chat.id
    indian_time = await get_indian_time()
    current_hour = indian_time.hour
    current_weekday = indian_time.weekday()
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # List of greetings based on the time of day
    morning_greetings = ["Good morning!", "Hello, early bird!", "Rise and shine!", "Morning!"]
    afternoon_greetings = ["Good afternoon!", "Hello there!", "Afternoon vibes!", "Hey!"]
    evening_greetings = ["Good evening!", "Hello, night owl!", "Evening time!", "Hi there!"]

    # List of greetings based on the day of the week
    weekday_greetings = ["Have a productive day!", "Stay focused and have a great day!", "Wishing you a wonderful day!", "Make the most of your day!"]
    weekend_greetings = ["Enjoy your weekend!", "Relax and have a great weekend!", "Wishing you a fantastic weekend!", "Make the most of your weekend!"]

    # Get a random greeting based on the time of day
    if 5 <= current_hour < 12:  # Morning (5 AM to 11:59 AM)
        greeting = random.choice(morning_greetings)
    elif 12 <= current_hour < 18:  # Afternoon (12 PM to 5:59 PM)
        greeting = random.choice(afternoon_greetings)
    else:  # Evening (6 PM to 4:59 AM)
        greeting = random.choice(evening_greetings)

    # Add a weekday-specific greeting if it's a weekday, otherwise, add a weekend-specific greeting
    if 0 <= current_weekday < 5:  # Monday to Friday
        greeting += " " + random.choice(weekday_greetings)
    else:  # Saturday and Sunday
        greeting += " " + random.choice(weekend_greetings)

    # Send the greeting to the user
    await message.reply(greeting)

    # Check if User Logged-In else,return LOGIN_MESSAGE
    login_message = login_message_updated_ui
    if not await tdatabase.load_user_session(chat_id) and await pgdatabase.check_chat_id_in_pgb(chat_id) is False:
        await bot.send_message(chat_id,login_message)
    else:
        await buttons.start_user_buttons(bot,message)


async def is_user_logged_in(bot,message):
    chat_id = message.chat.id
    if await tdatabase.load_user_session(chat_id):
        return True

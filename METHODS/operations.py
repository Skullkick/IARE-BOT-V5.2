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
async def perform_login( username, password):
    """
    Perform login with the provided username and password.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    # Set up the necessary headers and cookies
    cookies = {'PHPSESSID': ''}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://samvidha.iare.ac.in',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://samvidha.iare.ac.in/index',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    data = {
        'username': username,
        'password': password,
    }

    with requests.Session() as s:
        index_url = "https://samvidha.iare.ac.in/index"
        login_url = "https://samvidha.iare.ac.in/pages/login/checkUser.php"
        home_url = "https://samvidha.iare.ac.in/home"

        response = s.get(index_url)
        cookie_to_extract = 'PHPSESSID'
        cookie_value = response.cookies.get(cookie_to_extract)
        cookies['PHPSESSID'] = cookie_value

        s.post(login_url, cookies=cookies, headers=headers, data=data)

        response = s.get(home_url)
        if '<title>IARE - Dashboard - Student</title>' in response.text:

            session_data = {
                'cookies': s.cookies.get_dict(),
                'headers': headers,
                'username': username  # Save the username in the session data
            }
            return session_data
        else:   
            return None


async def login(bot,message):
    chat_id = message.chat.id
    command_args = message.text.split()[1:]
    # banned_usernames = await tdatabase.get_all_banned_usernames()
    if not command_args:
        username = ""
    else:
        username = command_args[0] # username of the user
    if await tdatabase.get_bool_banned_username(username) is True: # Checks whether the username is in banned users or not.
        return # Returns Nothing
    if await tdatabase.load_user_session(chat_id): # Tries to get the cookies from the database.If found, it displays that you are already logged in.
        await message.reply("You are already logged in.")
        await buttons.start_user_buttons(bot,message)
        await message.delete()
        return

    if len(command_args) != 2:
        invalid_command_message =f"""
```INVALID COMMAND USAGE
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot
```
        """
        await message.reply(invalid_command_message)
        return

    password = command_args[1]
    session_data = await perform_login(username, password)
    # Initializes settings for the user
    await user_settings.set_user_default_settings(chat_id)
    if session_data:
        await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)
        await tdatabase.store_username(username)
        await message.delete()
        await bot.send_message(chat_id,text="Login successful!")
        if await pgdatabase.check_chat_id_in_pgb(chat_id) is False:

            await message.reply_text("If you want to save your credentials Click on \"Yes\".",reply_markup =await buttons.start_save_credentials_buttons(username[:10],password))           
        else:
            await bot.send_message(chat_id,text="Your login information has already been registered.")
        await buttons.start_user_buttons(bot,message)
        
    else:
        await bot.send_message(chat_id,text="Invalid username or password.")

async def auto_login_by_database(bot,message,chat_id):
    # username,password = await pgdatabase.retrieve_credentials_from_database(chat_id) This Can be used if you want to take credentials from cloud database.
    username,password = await tdatabase.fetch_credentials_from_database(chat_id) # This can be used to Fetch credentials from the Local database.
    # Initializes settings for the user if the settings are not present
    await user_settings.set_user_default_settings(chat_id)
    if username != None:
        username = username[:10]
        if await tdatabase.get_bool_banned_username(username) is True: # Checks whether the username is in banned users or not.
            # await tdatabase.delete_banned_username_credentials_data(username)
            banned_username_chat_ids = await tdatabase.get_chat_ids_of_the_banned_username(username)
            for chat_id in banned_username_chat_ids:
                if await tdatabase.delete_user_credentials(chat_id) is True:
                    if await pgdatabase.remove_saved_credentials_silent(chat_id) is True:
                        return False
        session_data = await perform_login(username, password)
        if session_data:
            await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function
            await tdatabase.store_username(username)
            await bot.send_message(chat_id,text="Login successful!")
            return True
        else:
            if await tdatabase.check_chat_id_in_database(chat_id) is True:
                await bot.send_message(chat_id,text="Unable to login using saved credentials, please try updating your password")
            return False
    else:
        return False

async def logout(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        if ui_mode[0] == 0:
            await bot.send_message(chat_id,text=login_message_updated_ui)
        elif ui_mode[0] == 1:
            await bot.send_message(chat_id,text=login_message_traditional_ui)
        return

    logout_url = 'https://samvidha.iare.ac.in/logout'
    session_data = await tdatabase.load_user_session(chat_id)
    cookies,headers = session_data['cookies'], session_data['headers']
    requests.get(logout_url, cookies=cookies, headers=headers)
    await tdatabase.delete_user_session(chat_id)
    await message.reply("Logout successful.")

async def logout_user_and_remove(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)

    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        await bot.send_message(chat_id,text="You are already logged out.")
        return

    logout_url = 'https://samvidha.iare.ac.in/logout'
    session_data = await tdatabase.load_user_session(chat_id)
    cookies,headers = session_data['cookies'], session_data['headers']
    requests.get(logout_url, cookies=cookies, headers=headers)
    await tdatabase.delete_user_session(chat_id)

    await message.reply("Logout successful.")

async def logout_user_if_logged_out(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return

    await tdatabase.delete_user_session(chat_id)

    await bot.send_message(chat_id, text="Your session has been logged out due to inactivity.")

async def silent_logout_user_if_logged_out(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return

    await tdatabase.delete_user_session(chat_id)

async def attendance(bot,message):
    chat_id = message.chat.id
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)

    # Access the attendance page and retrieve the content
    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        attendance_response = s.get(attendance_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await attendance(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:
        req_table = table_all[1]

        table_data = []

        rows = req_table.tbody.find_all('tr')
        
        # ATTENDANCE HEADING
        
        attendance_heading = f"""
```ATTENDANCE
@iare_unofficial_bot
```
"""
        await bot.send_message(chat_id,attendance_heading)

        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            table_data.append(row_data)
        sum_attendance = 0
        count_att = 0
        all_attendance_indexes_dictionary = await user_settings.get_attendance_index_values()
        if all_attendance_indexes_dictionary:
            course_name_index = all_attendance_indexes_dictionary['course_name']
            conducted_classes_index = all_attendance_indexes_dictionary['conducted_classes']
            attended_classes_index = all_attendance_indexes_dictionary['attended_classes']
            attendance_percentage_index = all_attendance_indexes_dictionary['attendance_percentage']
            attendance_status_index = all_attendance_indexes_dictionary['status']
        else:
            course_name_index = 2
            conducted_classes_index = 5
            attended_classes_index = 6
            attendance_percentage_index = 7
            attendance_status_index = 8
        for row in table_data[0:]:
            course_name = row[course_name_index]
            conducted = row[conducted_classes_index]
            attended = row[attended_classes_index]
            attendance_percentage = row[attendance_percentage_index]
            attendance_status = row[attendance_status_index]
            if course_name and attendance_percentage:
                att_msg_updated_ui = f"""
```{course_name}

● Conducted         -  {conducted}
             
● Attended          -  {attended}  
         
● Attendance %      -  {attendance_percentage} 
            
● Status            -  {attendance_status}  
         
```
"""
                
                att_msg_traditional_ui = f"""
\n**{course_name}**

● Conducted         -  {conducted}
             
● Attended            -  {attended}   
         
● Attendance %    -  {attendance_percentage} 
            
● Status                 -  {attendance_status}
 
"""
# ● Conducted         -  {conducted}
             
# ● Attended          -  {attended}  
         
# ● Attendance %      -  {attendance_percentage} 
            
# ● Status            -  {attendance_status}
                # att_msg = f"Course: {course_name}, Attendance: {attendance_percentage}"
                
                sum_attendance += float(attendance_percentage)
                if int(conducted) > 0:
                        count_att += 1
                if ui_mode[0] == 0:
                    await bot.send_message(chat_id,att_msg_updated_ui)
                else:
                    await bot.send_message(chat_id,att_msg_traditional_ui)
        aver_attendance = round(sum_attendance/count_att, 2)
        over_all_attendance = f"**Overall Attendance is {aver_attendance}**"
        await bot.send_message(chat_id,over_all_attendance)

    else:
        await bot.send_message(chat_id,"Attendance data not found.")
    await buttons.start_user_buttons(bot,message)



async def six_hours_biometric(biometric_rows, totaldays, intime_index,outtime_index):
    intimes, outtimes = [], []
    time_gap_more_than_six_hours = 0
    for row in biometric_rows:
        cell = row.find_all('td')
        intime = cell[intime_index].text.strip()
        outtime = cell[outtime_index].text.strip()
        if intime and outtime and ':' in intime and ':' in outtime:
            intimes.append(intime)
            outtimes.append(outtime)
            intime_hour, intime_minute = intime.split(':')
            outtime_hour, outtime_minute = outtime.split(':')
            time_difference = (int(outtime_hour) - int(intime_hour)) * 60 + (int(outtime_minute) - int(intime_minute))
            if time_difference >= 360:
                time_gap_more_than_six_hours += 1
    # Calculate the biometric percentage with six hours gap
    six_percentage = (time_gap_more_than_six_hours / totaldays) * 100 if totaldays != 0 else 0
    six_percentage = round(six_percentage, 3)
    return six_percentage,time_gap_more_than_six_hours

async def biometric_leaves(chat_id,present_days,total_days):
    biometric_threshold = await user_settings.fetch_biometric_threshold(chat_id)
    biometric_percentage = present_days / total_days * 100
    if biometric_percentage > biometric_threshold[0]:
        no_of_leaves = 0
        while (present_days / (total_days + no_of_leaves)) * 100 >= biometric_threshold[0]:
            no_of_leaves += 1
        no_of_leaves -= 1  # Subtract 1 to account for the last iteration
        return no_of_leaves, True
    elif biometric_percentage < biometric_threshold[0]:
        days_need_attend = 0
        while (present_days + days_need_attend) / (total_days + days_need_attend) * 100 < biometric_threshold[0]:
            days_need_attend += 1
        return days_need_attend, False
    

async def bunk(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    if not session_data:
        auto_login_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # LOGIN MESSAGE
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return

    session_data = await tdatabase.load_user_session(chat_id)

    attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
    
    with requests.Session() as s:

        cookies = session_data['cookies']
        s.cookies.update(cookies)

        attendance_response = s.get(attendance_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    data = BeautifulSoup(attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await bunk(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return

    table_all = data.find_all('table', class_='table table-striped table-bordered table-hover table-head-fixed responsive')
    if len(table_all) > 1:

        req_table = table_all[1]
        table_data = []
        rows = req_table.tbody.find_all('tr')
        
        # BUNK HEADING
        attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)
        bunk_heading = f"""
```BUNK
@iare_unofficial_bot

● Attendance Threshold - {attendance_threshold[0]}
```
"""
        await bot.send_message(chat_id,bunk_heading)
        
        for row in rows:
            cells = row.find_all('td')

            row_data = [cell.get_text(strip=True) for cell in cells]

            table_data.append(row_data)
        all_attendance_indexes_dictionary = await user_settings.get_attendance_index_values()
        if all_attendance_indexes_dictionary:
            course_name_index = all_attendance_indexes_dictionary['course_name']
            conducted_classes_index = all_attendance_indexes_dictionary['conducted_classes']
            attended_classes_index = all_attendance_indexes_dictionary['attended_classes']
            attendance_percentage_index = all_attendance_indexes_dictionary['attendance_percentage']
            attendance_status_index = all_attendance_indexes_dictionary['status']
        else:
            course_name_index = 2
            conducted_classes_index = 5
            attended_classes_index = 6
            attendance_percentage_index = 7
            attendance_status_index = 8
        for row in table_data[0:]:
            course_name = row[course_name_index]
            attendance_percentage = row[attendance_percentage_index]
            if course_name and attendance_percentage:
                attendance_present = float(attendance_percentage)
                conducted_classes = int(row[conducted_classes_index])
                attended_classes = int(row[attended_classes_index])
                classes_bunked = 0
                
                if attendance_present >= attendance_threshold[0]:
                    classes_bunked = 0
                    while (attended_classes / (conducted_classes + classes_bunked)) * 100 >= attendance_threshold[0]:
                        classes_bunked += 1
                    classes_bunked -= 1
                    bunk_can_msg_updated = f"""
```{course_name}
⫷

● Attendance  -  {attendance_percentage}

● You can bunk {classes_bunked} classes


⫸

```
"""
                    bunk_can_msg_traditional = f"""
**{course_name}**

⫷

● Current Attendance      -  {attendance_percentage}

● You can bunk {classes_bunked} classes


⫸

"""
                    if ui_mode[0] == 0:
                        await bot.send_message(chat_id,bunk_can_msg_updated)
                    else:
                        await bot.send_message(chat_id,bunk_can_msg_traditional)
                  
                    
                else:
                    classes_needattend = 0
                    if conducted_classes == 0:
                        classes_needattend = 0
                    else:
                        while((attended_classes + classes_needattend) / (conducted_classes + classes_needattend)) * 100 < attendance_threshold[0]:
                            classes_needattend += 1    
                    bunk_recover_msg_updated = f"""
```{course_name}
⫷

● Attendance  -  Below {attendance_threshold[0]}%

● Attend  {classes_needattend} classes for {attendance_threshold[0]}%

● No Bunk Allowed

⫸

```
"""
                    bunk_recover_msg_traditional = f"""
**{course_name}**

⫷

● Attendance  -  Below {attendance_threshold[0]}%

● Attend  {classes_needattend} classes for {attendance_threshold[0]}%

● No Bunk Allowed

⫸"""
                    if ui_mode[0] == 0:
                        await bot.send_message(chat_id,bunk_recover_msg_updated)
                    else:
                        await bot.send_message(chat_id,bunk_recover_msg_traditional)              
    else:
        await message.reply("Data not found.")
    await buttons.start_user_buttons(bot,message)

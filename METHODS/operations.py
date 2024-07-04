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

async def biometric(bot, message):
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
            # LOGIN MESSAGE
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return

    session_data = await tdatabase.load_user_session(chat_id)

    biometric_url = 'https://samvidha.iare.ac.in/home?action=std_bio'
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']
        response = s.get(biometric_url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        Biometric_html = BeautifulSoup(response.text, 'html.parser')
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    # Check if the response contains the expected title
    if '<title>Samvidha - Campus Management Portal - IARE</title>' in response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot, chat_id)
            await biometric(bot, message)
        else:
            await logout_user_if_logged_out(bot, chat_id)
        return

    # Find the table
    biometric_table = Biometric_html.find('table', class_='table')

    if not biometric_table:
        await message.reply("Biometric data not found.")
        return

    # Dictionary to store attendance data for each student
    attendance_data = {
        'Total Days Present': 0,
        'Total Days Absent': 0,
        'Total Days': 0
    }

    # Find all rows in the table body except the last one
    biometric_rows = biometric_table.find('tbody').find_all('tr')[:-1]
    biometric_index_values = await user_settings.get_biometric_index_values()
    if biometric_index_values:
        intime_index = biometric_index_values['intime']
        outtime_index = biometric_index_values['outtime']
        status_index = biometric_index_values['status']
    else:
        intime_index = 4
        outtime_index = 5
        status_index = 6
    for row in biometric_rows:
        # Extract data from each row
        cells = row.find_all('td')
        status = cells[6].text.strip()
        if status.lower() == 'present':
            attendance_data['Total Days Present'] += 1
        else:
            attendance_data['Total Days Absent'] += 1

    attendance_data['Total Days'] = attendance_data['Total Days Present'] + attendance_data['Total Days Absent']
    # Calculate the biometric percentage
    biometric_percentage = (attendance_data['Total Days Present'] / attendance_data['Total Days']) * 100 if attendance_data['Total Days'] != 0 else 0
    biometric_percentage = round(biometric_percentage, 3)

    # Calculate the biometric percentage with six hours gap
    six_percentage,days_six_hours = await six_hours_biometric(biometric_rows, attendance_data['Total Days'],intime_index,outtime_index)
    leaves_biometric,leave_status = await biometric_leaves(chat_id,present_days=attendance_data['Total Days Present'],total_days=attendance_data['Total Days'])
    six_hour_leaves,six_hour_leave_status = await biometric_leaves(chat_id,present_days=days_six_hours,total_days=attendance_data['Total Days'])
    biometric_threshold = await user_settings.fetch_biometric_threshold(chat_id)
    if leave_status is True:
        leaves_biometric_msg = f"● Leaves available       -  {leaves_biometric}"
    elif leave_status is False:
        leaves_biometric_msg = f"Biometric Below {biometric_threshold[0]}\n\n● Days to Attend              -  {leaves_biometric}\n"
    if six_hour_leave_status is True:
        six_hour_leave_msg = f"● Leaves available (6h)  -  {six_hour_leaves}"
    elif six_hour_leave_status is False:
        six_hour_leave_msg = f"Biometric (6h) Below {biometric_threshold[0]}\n\n    ● Days to Attend         -  {six_hour_leaves}\n" 
    biometric_msg_updated = f"""
    ```Biometric
⫷

● Total Days             -  {attendance_data['Total Days']}
                    
● Days Present           -  {attendance_data['Total Days Present']}  
                
● Days Absent            -  {attendance_data['Total Days Absent']}
                    
● Biometric %            -  {biometric_percentage}

● Biometric % (6h gap)   -  {six_percentage}

● Biometric Threshold    -  {biometric_threshold[0]}

{leaves_biometric_msg}

{six_hour_leave_msg}
⫸

@iare_unofficial_bot
    ```
    """
    biometric_msg_traditional = f"""
**Biometric**

⫷

● Total Days                      -  {attendance_data['Total Days']}
                    
● Days Present                 -  {attendance_data['Total Days Present']}  
                
● Days Absent                  -  {attendance_data['Total Days Absent']}
                    
● Biometric %                   -  {biometric_percentage}

● Biometric % (6h gap)   -  {six_percentage}

● Biometric Threshold    -  {biometric_threshold[0]}

{leaves_biometric_msg}

{six_hour_leave_msg}

⫸

@iare_unofficial_bot
"""
    if ui_mode[0] == 0:
        await bot.send_message(chat_id, biometric_msg_updated)
    else:
        await bot.send_message(chat_id, biometric_msg_traditional)
    
    
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
async def generate_unique_id():
    """
    Generate a unique identifier using UUID version 4.

    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())




async def report(bot,message):
    chat_id = message.from_user.id
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    session_data = await tdatabase.load_user_session(chat_id)
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
        else:
            session_data = await tdatabase.load_user_session(chat_id)

    user_report = " ".join(message.text.split()[1:])
    if not user_report:
        no_report_message = f"""
```EMPTY MESSAGE
⫸ ERROR : MESSAGE CANNOT BE EMPTY

⫸ How to use command:

●  /report We are encountering issues with the attendance feature.
It seems that attendance records are not updating correctly after submitting.
```
"""
        await message.reply(no_report_message)
        return
    getuname = await tdatabase.load_username(chat_id)

    username = getuname[2]

    user_unique_id = await generate_unique_id()

    await tdatabase.store_reports(user_unique_id,username,user_report,chat_id,None,None,0)
    await pgdatabase.store_reports(user_unique_id,username,user_report,chat_id,None,None,False)
    forwarded_message = f"New User Report from @{username} (ID: {user_unique_id}):\n\n{user_report}"
    all_admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    all_maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    if all_admin_chat_ids+all_maintainer_chat_ids:
        for chat_id in all_admin_chat_ids+all_maintainer_chat_ids:
            await bot.send_message(chat_id,text=forwarded_message)
        await bot.send_message(chat_id,"Thank you for your report! Your message has been forwarded to the developer.")
    else:
        await bot.send_message(chat_id,"Although an error occurred while sending, your request has been successfully stored in the database.")
async def reply_to_user(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[4] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return

    maintainer_name = await managers_handler.fetch_name(chat_id)
    if not message.reply_to_message:
        await message.reply("Please reply to a user's report to send a reply.")
        return
    
    reply_text = message.reply_to_message.text
    unique_id_keyword = "ID: "
    if unique_id_keyword not in reply_text:
        await message.reply("The replied message does not contain the unique ID.")
        return


    unique_id_start_index = reply_text.find(unique_id_keyword) + len(unique_id_keyword)
    unique_id_end_index = reply_text.find(")", unique_id_start_index)
    report_id = reply_text[unique_id_start_index:unique_id_end_index].strip()
    pending_reports = await tdatabase.load_reports(report_id)

    if report_id not in pending_reports:
        await message.reply("Invalid or unknown unique ID.")
        return

    user_chat_id = pending_reports[3]

    developer_reply = message.text.split("/reply", 1)[1].strip()

    reply_message = f"{developer_reply}\n\nThis is a reply from the bot developer."

    try:

        await bot.send_message(chat_id=user_chat_id, text=reply_message)

        developer_chat_id = message.chat.id
        await bot.send_message(chat_id=developer_chat_id, text="Message sent successfully.")

        await tdatabase.store_reports(report_id,None,None,None,reply_message,maintainer_name,1)
        await pgdatabase.store_reports(report_id,None,None,None,reply_message,maintainer_name,True)
    except Exception as e:
        error_message = f"An error occurred while sending the message to the user: {e}"
        await bot.send_message(chat_id=developer_chat_id, text=error_message)

async def show_reports(bot,message):
    chat_id = message.chat.id
    reports = await tdatabase.load_allreports()
    # if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
    #     return
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[3] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    if len(reports) == 0:
        await bot.send_message(chat_id,text="There are no pending reports.")
        return
    for report in reports:
        unique_id, user_id, message, report_chat_id = report
        report_message = f"User report from @{user_id} (ID: {unique_id}):\n\n{message}"
        await bot.send_message(chat_id, text=report_message)

async def show_replied_reports(bot,message):
    chat_id = message.chat.id
    reports = await tdatabase.load_all_replied_reports()
    # if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
    #     return
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[3] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    if len(reports) == 0:
        await bot.send_message(chat_id,text="There are no Replied reports.")
        return
    for report in reports:
        unique_id, user_id, message, report_chat_id,replied_message,replied_maintainer,reply_status = report
        replied_message = replied_message.split("This is a reply from the bot developer.")[0]
        report_message = f"User report from @{user_id} (ID: {unique_id}):\n\n{message}\n\nReplied By : {replied_maintainer}\n\nReplied Message : {replied_message}"
        await bot.send_message(chat_id, text=report_message)

async def list_users(bot,chat_id):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[0] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    usernames = await tdatabase.fetch_usernames_total_users_db()   
    users_list = ";".join(usernames)
    qr_code = pyqrcode.create(users_list)
    qr_image_path = "list_users_qr.png"
    qr_code.png(qr_image_path, scale=5)
    await bot.send_photo(chat_id, photo=open(qr_image_path, 'rb'))
    os.remove(qr_image_path)


async def get_logs(bot, chat_id):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()  # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()  # Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[9] != 1:
        await bot.send_message(chat_id, "Access denied. You don't have permission to use this command.")
        return
    
    log_file_name = "bot_errors.log"
    temp_log_file_name = "temp_bot_errors.log"
    
    if log_file_name in os.listdir():
        try:
            # Copy the log file to a temporary file
            shutil.copy(log_file_name, temp_log_file_name)
            
            # Send the temporary log file
            await bot.send_document(chat_id, temp_log_file_name)
            
            # Remove the temporary log file after sending
            os.remove(temp_log_file_name)
        except Exception as e:
            await bot.send_message(chat_id, f"Error: {e}")
    else:
        await bot.send_message(chat_id, "No log file found.")

async def total_users(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[0] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    total_count = await tdatabase.fetch_number_of_total_users_db()
    await bot.send_message(message.chat.id,f"Total users: {total_count}")

async def clean_pending_reports(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[5] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    await pgdatabase.clear_pending_reports()
    await tdatabase.clear_reports()
    await bot.send_message(chat_id,"Emptied the reports successfully")


async def perform_sync_credentials(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        credentials = await pgdatabase.get_all_credentials()
        if credentials is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from credentials database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from credentials database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from credentials database")
            return
        if credentials is not None:
            for row in credentials:
                chat_id,username,password = row[0],row[1],row[2]
                await tdatabase.store_credentials_in_database(chat_id,username,password)
        else:
            print("There is no data present in the credential's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing credentials to database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing credentials to database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing credentials to database : {e}")

async def perform_sync_reports(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        reports = await pgdatabase.get_all_reports()
        if reports is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from reports database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from reports database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from reports database")
            return
        if reports is not None:
            for row in reports:
                unique_id,user_id,message,chat_id,replied_message,replied_maintainer,reply_status = row
                await tdatabase.store_reports(unique_id,user_id,message,chat_id,replied_message,replied_maintainer,reply_status)
        else:
            print("There is no data present in the report's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing reports to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing reports to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing reports to local database : {e}")

async def perform_sync_banned_users(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        banned_users = await pgdatabase.get_all_banned_usernames()
        if banned_users is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from banned users database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from banned users database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from banned users database")
            return
        if banned_users is not None:
            print(banned_users)
            for row in banned_users: # Each row contains data like this <Record username='223235464'>
                banned_username = row[0] # Extracting username from the record
                await tdatabase.store_banned_username(banned_username.lower())
        else:
            print("There is no data present in the bannned user's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing banned users to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing banned users to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing banned users to local database : {e}")

async def perform_sync_user_settings(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_user_settings = await pgdatabase.get_all_user_settings()
        if all_user_settings is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from user settings database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from user settings database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from user settings database")
            return
        if all_user_settings is not None:
            for row in all_user_settings:
                chat_id, attendance_threshold,biometric_threshold,traditional_ui,extract_title = row
                traditional_ui_sqlite = await tdatabase.pg_bool_to_sqlite_bool(traditional_ui)
                extract_title_sqlite = await tdatabase.pg_bool_to_sqlite_bool(extract_title)
                await user_settings.store_user_settings(chat_id, attendance_threshold,biometric_threshold,traditional_ui_sqlite,extract_title_sqlite)
        else:
            print("There is no data present in the user setting's database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing user settings to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing user settings to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing user settings to local database : {e}")

async def perform_sync_bot_manager_data(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        bot_managers_data = await pgdatabase.get_bot_managers_data()
        if bot_managers_data is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from bot manager database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from bot manager database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from bot manager database")
            return
        if bot_managers_data is not None and bot_managers_data is not False:
            for row in bot_managers_data:
                chat_id,admin,maintainer,name,control_access,access_users,announcement,configure,show_reports_,reply_reports,clear_reports,ban_username,unban_username,manage_maintainer,logs = row
                admin_sqlite = await tdatabase.pg_bool_to_sqlite_bool(admin)
                maintainer_sqlite = await tdatabase.pg_bool_to_sqlite_bool(maintainer)
                access_users_sqlite = await tdatabase.pg_bool_to_sqlite_bool(access_users)
                announcement_sqlite = await tdatabase.pg_bool_to_sqlite_bool(announcement)
                configure_sqlite = await tdatabase.pg_bool_to_sqlite_bool(configure)
                show_reports_sqlite = await tdatabase.pg_bool_to_sqlite_bool(show_reports_)
                reply_reports_sqlite = await tdatabase.pg_bool_to_sqlite_bool(reply_reports)
                clear_reports_sqlite = await tdatabase.pg_bool_to_sqlite_bool(clear_reports)
                ban_username_sqlite = await tdatabase.pg_bool_to_sqlite_bool(ban_username)
                unban_username_sqlite = await tdatabase.pg_bool_to_sqlite_bool(unban_username)
                manage_maintainer_sqlite = await tdatabase.pg_bool_to_sqlite_bool(manage_maintainer)
                logs_sqlite = await tdatabase.pg_bool_to_sqlite_bool(logs)

                await managers_handler.store_bot_managers_data_in_database(
                                chat_id = chat_id,
                                admin=admin_sqlite,
                                maintainer= maintainer_sqlite,
                                name= name,
                                control_access= control_access,
                                access_users=access_users_sqlite,
                                announcement= announcement_sqlite,
                                configure= configure_sqlite,
                                show_reports= show_reports_sqlite,
                                reply_reports=reply_reports_sqlite,
                                clear_reports=clear_reports_sqlite,
                                ban_username= ban_username_sqlite,
                                unban_username= unban_username_sqlite,
                                manage_maintainers=manage_maintainer_sqlite,
                                logs= logs_sqlite
                            )
        else:
            print("There is no data present in the bot manager's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing bot managers data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing bot managers data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing bot managers data to local database : {e}")

async def perform_sync_index_data(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_indexes = await pgdatabase.get_all_index_values()
        if all_indexes is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from index database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from index database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from index database")
            return
        if all_indexes is not None:
            for row in all_indexes:
                name,indexes_dictionary = row
                await user_settings.store_index_values_to_restore(name,json.loads(indexes_dictionary))
        else:
            print("There is no data present in the index's database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing index to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing index to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing index to local database : {e}")

async def perform_sync_cgpa_tracker(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_tracker_details = await pgdatabase.get_all_cgpa_trackers()
        if all_tracker_details is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cgpa_tracker database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cgpa_trackers database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from cgpa_tracker database")
            return
        if all_tracker_details is not None:
            for row in all_tracker_details:
                chat_id,status,current_cgpa = row
                status_sqlite = await tdatabase.pg_bool_to_sqlite_bool(status)
                await managers_handler.store_cgpa_tracker_details(chat_id,status_sqlite,current_cgpa)
        else:
            print("There is no data present in the cgpa_tracker database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing cgpa_tracker data to local database : {e}")

async def perform_sync_cie_tracker(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_tracker_details = await pgdatabase.get_all_cie_tracker_data()
        if all_tracker_details is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cie_tracker database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cie_trackers database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from cie_tracker database")
            return
        if all_tracker_details is not None:
            for row in all_tracker_details:
                chat_id,status,current_cie_marks = row
                status_sqlite = await tdatabase.pg_bool_to_sqlite_bool(status)
                await managers_handler.store_cie_tracker_details(chat_id,status_sqlite,current_cie_marks)
        else:
            print("There is no data present in the cie_tracker database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing cie_tracker data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing cie_tracker data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing cie_tracker data to local database : {e}")

async def perform_sync_labs_data(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        labs_data = await pgdatabase.get_all_lab_subjects_and_weeks_data()
        if labs_data is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from labs_data database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from labs_data database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from cie_tracker database")
            return
        if labs_data is not None:
            for row in labs_data:
                chat_id,subject,weeks = row
                await tdatabase.store_lab_info(chat_id,subject_index= None,week_index=None,subjects=subject,weeks=weeks)
        else:
            print("There is no data present in the cgpa_tracker database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing cgpa_tracker data to local database : {e}")

async def sync_databases(bot):
    """
    This Function is used to execute all the functions which sync the local database with the Postgres database.
    
    :param bot: Pyrogram client
    """
    await perform_sync_index_data(bot)
    await perform_sync_bot_manager_data(bot)
    await perform_sync_credentials(bot)
    await perform_sync_user_settings(bot)
    # await perform_sync_labs_data(bot)
    await perform_sync_banned_users(bot)
    await perform_sync_cgpa_tracker(bot)
    await perform_sync_cie_tracker(bot)
    await perform_sync_reports(bot)

async def help_command(bot,message):
    """
    Handler function for the /help command.
    Provides information about the available commands.
    """
    chat_id = message.chat.id
    help_msg = """Available commands:

    /login username password - Log in with your credentials.

    /logout - Log out from the current session.

    /report {your report} - Send a report to the bot developer.

    /settings - Access user settings and preferences.

    Note: Replace {username}, {password}, and {your report} with actual values.
    """
    help_admin_msg = """
    Available commands:

    /login {username} {password} - Log in with your credentials.
    
    /logout - Log out from the current session.    
    
    /report {your report} - Send a report to the bot developer.

    /settings - Access user settings and preferences.

    Note: Replace {username}, {password}, {your report} and {your reply} with actual values.

    As an Admin :

    /admin - Access authorized operations.

    /reset - Reset the User Sessions Sqlite3 Database

    /reply {your reply} - Send a reply to the report by replying to it.

    /ban {username} - Ban a user or users from the system.

    /unban {username} - Unban a user from the system.

    /announce {your announcement} - Send an announcement.

    /add_maintainer {chat_id} - Add a maintainer.

    /rshow - View reports.  

    /lusers - Generate a QR code of active users in a day.

    /tusers - Display total active users in a day.

    /rclear - Clear reports.
    """
    help_maintainer_msg = """
    Available commands:

    /login {username} {password} - Log in with your credentials.
    
    /logout - Log out from the current session.    
    
    /report {your report} - Send a report to the bot developer.

    Note: Replace {username}, {password}, {your report} and {your reply} with actual values.

    As a Maintainer :
    
    /maintainer -  Access authorized operations.

    /ban {username} - Ban a user or users from the system.  

    /unban {username} - Unban a user from the system.  

    /announce {your announcement} - Send an announcement.  

    /rshow - View reports.  

    /lusers - Generate a QR code of active users in a day.

    /tusers - Display total active users in a day.

    /rclear - Clear reports.

    Note : \n\nMaintainers require authorization from the admin to ensure that the commands function properly.
"""
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    if chat_id in admin_chat_ids:
        await bot.send_message(chat_id,text=help_admin_msg)
        await buttons.start_user_buttons(bot,message)
    elif chat_id in maintainer_chat_ids:
        await bot.send_message(chat_id,text=help_maintainer_msg)
        await buttons.start_user_buttons(bot,message)
    else:
        await bot.send_message(chat_id,text=help_msg)
        if await is_user_logged_in(chat_id,message) is True or await pgdatabase.check_chat_id_in_pgb(chat_id):
            await buttons.start_user_buttons(bot,message)

async def reset_user_sessions_database(bot,message):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    chat_id = message.chat.id
    if chat_id in admin_chat_ids:
        await tdatabase.clear_sessions_table()
        await message.reply("Reset done")

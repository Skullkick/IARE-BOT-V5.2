# This file containg all the code regarding manager operations on database, testing,etc..

from DATABASE import tdatabase,pgdatabase,managers_handler,user_settings
from Buttons import buttons,manager_buttons
import re,requests,json,psutil
from METHODS import operations
from bs4 import BeautifulSoup
import sqlite3,os
from pyrogram.errors import FloodWait
import asyncio

# access_users = access_data[0]
# announcement = access_data[1]
# configure = access_data[2]
# show_reports = access_data[3]
# reply_reports = access_data[4]
# clear_reports = access_data[5]
# ban_username = access_data[6]
# unban_username = access_data[7]
# manage_maintainers = access_data[8]
# logs = access_data[9]


ADMIN_AUTHORIZATION_CODE = os.environ.get("ADMIN_AUTHORIZATION_PASS")

async def get_username(bot,chat_id):
    user = await bot.get_users(chat_id)
    user_name = f"{user.first_name} {user.last_name}" 
    return user_name
async def get_all_details(bot,chat_id):
    user = await bot.get_users(5877699254)
    phone_number = user.phone_number if user.phone_number else "Phone number not available"
    name = user.first_name + (" " + user.last_name if user.last_name else "")
    return f"Name: {name} \n\n Phone number : {phone_number}"
async def ban_username(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[6] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    usernames = re.split(r'[ ,]+', message.text)[1:]
    if len(usernames) == 0:
        await bot.send_message(chat_id,"No username found.")
        return
    if len(usernames[0]) < 10:
        await bot.send_message(chat_id, "Not a valid username")
        return
    if len(usernames) > 1:
        if len(usernames[0]) > len(usernames[1]):
            if await tdatabase.get_bool_banned_username(usernames[0].lower()) is False:
                    await tdatabase.store_banned_username(usernames[0].lower())
                    await pgdatabase.store_banned_username(usernames[0].lower())
            else:
                await bot.send_message(chat_id,f"Username : {usernames[0]},\n\nis already banned.")
            for index in range(1,len(usernames)):
                complete_username = usernames[0][:8] + usernames[index]
                if await tdatabase.get_bool_banned_username(complete_username.lower()) is True:
                    await bot.send_message(chat_id,f"Username : {complete_username},\n\nis already banned.")
                    continue
                await tdatabase.store_banned_username(complete_username.lower())
                await pgdatabase.store_banned_username(complete_username.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames banned successfully")
            else:
                await bot.send_message(chat_id,"Username banned successfully")
        else:
            for username_0 in usernames:
                for username_1 in usernames:
                    if len(username_0) != len(username_1):
                        await bot.send_message(chat_id,"Invalid Ban username format.")
                        return
                if await tdatabase.get_bool_banned_username(username_0.lower()) is True:
                    await bot.send_message(chat_id,f"Username : {username_0},\n\nis already banned.")
                    continue
                await tdatabase.store_banned_username(username_0.lower())
                await pgdatabase.store_banned_username(username_0.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames banned successfully")
            else:
                await bot.send_message(chat_id,"Username banned successfully")
    elif len(usernames) == 1:
        if await tdatabase.get_bool_banned_username(usernames[0]) is True:
            await bot.send_message(chat_id,"Username is already banned")
            return
        await tdatabase.store_banned_username(usernames[0].lower())
        await pgdatabase.store_banned_username(usernames[0].lower())
        await bot.send_message(chat_id,"Username banned successfully")

async def unban_username(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[7] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    usernames = re.split(r'[ ,]+', message.text)[1:]
    if len(usernames) == 0:
        await bot.send_message(chat_id,"No username found.")
        return
    if len(usernames[0]) < 10:
        await bot.send_message(chat_id, "Not a valid username")
        return
    if len(usernames) > 1:
        if len(usernames[0]) > len(usernames[1]):
            if await tdatabase.get_bool_banned_username(usernames[0].lower()) is True:
                await tdatabase.remove_banned_username(usernames[0])
                await pgdatabase.remove_banned_username(usernames[0])
                await bot.send_message(chat_id, f"Username {usernames[0]} has been unbanned successfully.")
            else:
                await bot.send_message(chat_id,f"Username : {usernames[0]},\n\nis not in banned list.")
            for index in range(1,len(usernames)):
                complete_username = usernames[0][:8] + usernames[index]
                if await tdatabase.get_bool_banned_username(complete_username.lower()) is False:
                    await bot.send_message(chat_id,f"Username : {complete_username},\n\nis not in banned list")
                    continue
                await tdatabase.remove_banned_username(complete_username.lower())
                await pgdatabase.remove_banned_username(complete_username.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames unbanned successfully")
            else:
                await bot.send_message(chat_id,"Username unbanned successfully")
        else:
            for username_0 in usernames:
                for username_1 in usernames:
                    if len(username_0) != len(username_1):
                        await bot.send_message(chat_id,"Invalid Ban username format.")
                        return
                if await tdatabase.get_bool_banned_username(username_0.lower()) is False:
                    await bot.send_message(chat_id,f"Username : {username_0},\n\nis not in banned list.")
                    continue
                await tdatabase.remove_banned_username(username_0.lower())
                await pgdatabase.remove_banned_username(username_0.lower())
            if len(usernames) > 1:
                await bot.send_message(chat_id,"Usernames unbanned successfully")
            else:
                await bot.send_message(chat_id,"Username unbanned successfully")
    elif len(usernames) == 1:
        if await tdatabase.get_bool_banned_username(usernames[0]) is False:
            await bot.send_message(chat_id,"Username is not in banned username list.")
            return
        await tdatabase.remove_banned_username(usernames[0].lower())
        await pgdatabase.remove_banned_username(usernames[0].lower())
        await bot.send_message(chat_id,"Username unbanned successfully")

async def add_maintainer(bot,message,maintainer_chat_id,maintainer_name):
    """
    This function is used to add a maintainer. It notifies both the admin and the maintainer about the relevant details.
    :maintainer_chat_id: chat id of the maintainer
    :maintainer_name: Name of the maintainer
    :return: None
    """
    user_chat_id = message.chat.id
    user_full_name = await get_username(bot,user_chat_id)
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    all_maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    if maintainer_chat_id in admin_chat_ids:
        await bot.send_message(user_chat_id,"You are already an admin and cannot be a maintainer.")
        return
    if maintainer_chat_id in all_maintainer_chat_ids:
        await bot.send_message(user_chat_id,f"{maintainer_name} is already a maintainer.")
        return
    await managers_handler.store_as_maintainer(maintainer_name,maintainer_chat_id)
    await pgdatabase.store_as_maintainer(maintainer_name,maintainer_chat_id)
    await bot.send_message(user_chat_id,f"Successfully added {maintainer_name} as maintainer")
    await bot.send_message(maintainer_chat_id,f"You've been added as maintainer by {user_full_name}, Use \"/maintainer\" To Access The Buttons")
async def verification_to_add_maintainer(bot,message):
    """
    This Function is used to get all the maintainer details and ask admin whether he needs to be added or not.
    :param bot: Pyrogram client
    :param message: Message sent by the user.
    """
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    chat_id = message.chat.id
    if message.chat.id not in admin_chat_ids:
        return
    if message.forward_from and message.text:
        maintainer_chat_id = message.forward_from.id
        maintainer_name = await get_username(bot,maintainer_chat_id)
        await bot.send_message(chat_id,f"Would you like to add {maintainer_name} as Maintainer.",reply_markup = await manager_buttons.start_add_maintainer_button(maintainer_chat_id,maintainer_name))
    if message.forward_from_chat and message.text:
        maintainer_chat_id = message.forward_from_chat.id # Chat id of the message that user forwarded
        maintainer_name = await get_username(bot,maintainer_chat_id) # Name of the maintainer based on the chat_id

    elif message.from_user and message.text and not message.forward_from and not message.forward_from_chat:
        # print(message.text)
        maintainer_chat_id = message.text.split()[1:][0]
        maintainer_name = await get_username(bot,maintainer_chat_id)
        await bot.send_message(chat_id,f"Would you like to add {maintainer_name} as Maintainer.",reply_markup = await manager_buttons.start_add_maintainer_button(maintainer_chat_id,maintainer_name))

async def add_admin_by_authorization(bot,message):
    """
    This Function is used to add Admin access to the user by authorizing the message sent.
    :param bot: Pyrogram client
    :param message: Message sent by the user"""
    chat_id = message.chat.id
    authorization_code = message.text.split()[1:][0]
    if authorization_code == ADMIN_AUTHORIZATION_CODE:
        admin_name = await get_username(bot,chat_id)
        await managers_handler.store_as_admin(admin_name,chat_id)
        await pgdatabase.store_as_admin(admin_name,chat_id)
        await bot.send_message(chat_id,"Authorized Successfully for Admin access, use \"/admin\" to start admin panel.")
        await message.delete()

async def announcement_to_all_users(bot, message):
    """
    This function is used to announce a message to all the users that are present in the 
    Postgres database, this can only be used by BOT_DEVELOPER or BOT_MAINTAINER
    """
    admin_or_maintainer_chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_id = await managers_handler.fetch_maintainer_chat_ids()
    if admin_or_maintainer_chat_id not in admin_chat_ids and admin_or_maintainer_chat_id not in maintainer_chat_id:
        return
    access_data = await managers_handler.get_access_data(admin_or_maintainer_chat_id)
    maintainer_announcement_status = access_data[1]
    if admin_or_maintainer_chat_id in maintainer_chat_id and maintainer_announcement_status != 1:
        await bot.send_message(admin_or_maintainer_chat_id,"Permission denied. You cannot use this command.")
        return
    # Retrieve all chat IDs from database
    chat_ids = await pgdatabase.get_all_chat_ids()
    # Get the announcement message from the input message
    developer_announcement = message.text.split("/announce", 1)[1].strip()
    
    # Validate announcement message
    if not developer_announcement:
        await bot.send_message(admin_or_maintainer_chat_id, "Announcement cannot be empty.")
        return
    announcement_message_updated_ui = f"""
```ANNOUNCEMENT
{developer_announcement}
```
"""
    announcement_message_traditional_ui = f"""
**ANNOUNCEMENT**

{developer_announcement}
"""
    # Track successful sends
    successful_sends = 0
    announcement_status_dev = f"""
```ANNOUNCEMENT
● STATUS : Started sending.
```
""" 
    message_to_developer = await bot.send_message(admin_or_maintainer_chat_id,announcement_status_dev)
    # Iterate over each chat ID and send the announcement message and documents
    for chat_id in chat_ids:
        total_users = len(chat_ids)
        try:
            ui_mode = await user_settings.fetch_ui_bool(chat_id)
            if ui_mode[0] == 0:
                await bot.send_message(chat_id, announcement_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id, announcement_message_traditional_ui)
            else:
                await bot.send_message(chat_id, announcement_message_updated_ui)
            successful_sends += 1
            announcement_status_dev = f"""
```ANNOUNCEMENT
● STATUS     : Started sending.

● TOTAL USERS  : {total_users}

● SUCCESSFULL SENDS : {successful_sends}
```
""" 
            await bot.edit_message_text(admin_or_maintainer_chat_id,message_to_developer.id, announcement_status_dev)
        except FloodWait as e:
            # Handle FloodWait: Pause and retry
            await bot.send_message(admin_or_maintainer_chat_id, f"FloodWait triggered. Pausing for {e.value} seconds.")
            await asyncio.sleep(e.value)  # Pause for the duration of the FloodWait
            try:
                ui_mode = await user_settings.fetch_ui_bool(chat_id)
                if ui_mode[0] == 0:
                    await bot.send_message(chat_id, announcement_message_updated_ui)
                elif ui_mode[0] == 1:
                    await bot.send_message(chat_id, announcement_message_traditional_ui)
                else:
                    await bot.send_message(chat_id, announcement_message_updated_ui)
                
                successful_sends += 1
            except Exception as retry_error:
                await bot.send_message(admin_or_maintainer_chat_id, f"Retry failed for chat ID {chat_id}: {retry_error}")
        except Exception as e:
            await bot.send_message(admin_or_maintainer_chat_id, f"Error sending message to chat ID {chat_id}: {e}")
    
    # Calculate success percentage
    total_attempts = len(chat_ids)
    success_percentage = (successful_sends / total_attempts) * 100 if total_attempts > 0 else 0.0
    announcement_status_dev = f"""
```ANNOUNCEMENT
● STATUS : SENT

● TOTAL USERS  : {total_attempts}

● SUCCESSFULL SENDS : {successful_sends}

● SUCCESS % : {success_percentage}

```
""" 
    # Send success percentage message
    await bot.edit_message_text(admin_or_maintainer_chat_id,message_to_developer.id, announcement_status_dev)

async def get_cgpa(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        return
    gpa_url = "https://samvidha.iare.ac.in/home?action=credit_register"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        gpa_response = s.get(gpa_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in gpa_response.text:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            await get_cgpa(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    pattern = r'Semester Grade Point Average \(SGPA\) : (\d(?:\.\d\d)?)'
    sgpa_values = re.findall(pattern,gpa_response.text)
    sgpa_values = [float(x) for x in sgpa_values]
    if not sgpa_values:
        return False,"0.00"
    cgpa = round(sum(sgpa_values) / len(sgpa_values) , 3)
    await silent_logout(chat_id)
    return True,str(cgpa)

async def total_cie_marks(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        return
    cie_marks_url = "https://samvidha.iare.ac.in/home?action=cie_marks_ug"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        cie_response = s.get(cie_marks_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in cie_response.text:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            return await total_cie_marks(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(cie_response.text, 'html.parser')
        # Find all tables 
        tables = soup.find_all('table')
        # Select the latest semester table 
        cie_table = tables[1].find_all('tr')
        # Initialize a list to store the relevant data
        subject_marks_data = []
        # Iterate over each row in the selected semester table
        for row in cie_table:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Break if 'Laboratory Marks (Practical)' is found -> to get only subject marks
            if any(item.startswith('Laboratory Marks (Practical)') for item in row_data):
                break
            # Append row data if it's not empty -> to get only subject marks
            if row_data:
                subject_marks_data.append(row_data)
        # Initialize dictionaries and total mark variables
        cie1_marks_dict = {}
        cie2_marks_dict = {}
        total_cie1_marks = 0
        total_cie2_marks = 0

        # Process each row data
        for marks_row in subject_marks_data:
            subject_name = marks_row[2]
            cie1_marks = marks_row[3]
            cie2_marks = marks_row[5]

            cie1_marks_dict[subject_name] = cie1_marks
            cie2_marks_dict[subject_name] = cie2_marks
            excluded_marks = ['','-', '0', '0.0'] 

            if cie1_marks not in excluded_marks:
                total_cie1_marks += float(int(cie1_marks))

            if cie2_marks not in excluded_marks:
                total_cie2_marks += float(int(cie2_marks))

        total_cie_marks = total_cie1_marks + total_cie2_marks

        return str(total_cie_marks)
    except Exception as e:
        return e

async def gpa(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    gpa_url = "https://samvidha.iare.ac.in/home?action=credit_register"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        gpa_response = s.get(gpa_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in gpa_response.text:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            await gpa(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:
        pattern = r'Semester Grade Point Average \(SGPA\) : (\d(?:\.\d\d)?)'
        sgpa_values = re.findall(pattern,gpa_response.text)
        sgpa_values = [float(x) for x in sgpa_values]
        cgpa = round(sum(sgpa_values) / len(sgpa_values) , 3)
        gpa_message = """
```GPA
⫸ SGPA 

"""

        for i,sgpa in enumerate(sgpa_values,start = 1):
            sgpa_message = f'Semester-{i} : {sgpa} \n \n'
            gpa_message += sgpa_message 
            


        gpa_message += f"""⫸ CGPA : {cgpa}  
```
"""
        await bot.send_message(chat_id,gpa_message)
    except Exception as e:
        await bot.send_message(chat_id,f"Error Retrieving GPA : {e}")
async def cie_marks(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database_silent(bot,"",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    cie_marks_url = "https://samvidha.iare.ac.in/home?action=cie_marks_ug"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        cie_marks_response = s.get(cie_marks_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in cie_marks_response.text:
        if chat_id_in_local_database:
            await silent_logout(bot,chat_id)
            await cie_marks(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(cie_marks_response.text, 'html.parser')
        # Find all tables and reverse the list to get the semesters in ascending order i.e semester 1 to 8 
        tables = soup.find_all('table')
        reversed_tables = tables[::-1] 
        semester_count = len(tables) - 2
        # Select the required semester table 
        cie_table = reversed_tables[semester_count].find_all('tr')
        # Initialize a list to store the relevant data
        subject_marks_data = []
        # Iterate over each row in the selected semester table
        for row in cie_table:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Break if 'Laboratory Marks (Practical)' is found -> to get only subject marks
            if 'Laboratory Marks (Practical)' in row_data:
                break
            # Append row data if it's not empty -> to get only subject marks
            if row_data:
                subject_marks_data.append(row_data)
        # Initialize dictionaries and total mark variables
        cie1_marks_dict = {}
        cie2_marks_dict = {}
        total_cie1_marks = 0
        total_cie2_marks = 0
        # Process each row data
        for marks_row in subject_marks_data:
            subject_name = marks_row[2]
            cie1_marks = marks_row[3]
            cie2_marks = marks_row[5]
            cie1_marks_dict[subject_name] = cie1_marks
            cie2_marks_dict[subject_name] = cie2_marks
            excluded_marks = ['-', '0', '0.0'] 
            if cie1_marks not in excluded_marks:
                total_cie1_marks += float(cie1_marks)
            if cie2_marks not in excluded_marks:
                total_cie2_marks += float(cie2_marks)
        # Default total marks as each subject has a maximum of 10 marks
        default_total_marks = float(len(cie1_marks_dict) * 10)
        # print(f"Default Total Marks: {default_total_marks}")
        # Print CIE-1 marks message as markdown
        cie1_marks_message_updated = f"""
```CIE  Marks
""" 
        cie1_marks_message_traditional = f"""
**CIE Marks**
"""
        if ui_mode[0] == 0:
            cie1_marks_message = cie1_marks_message_updated
        elif ui_mode[0] == 1:
            cie1_marks_message = cie1_marks_message_traditional
        for subject_name, marks in cie1_marks_dict.items():
            # print(f"{subject_name}: {marks}")
            cie1_marks_message += f"{subject_name}\n⫸ {marks}\n\n"
            1
        cie1_marks_message += "----\n"
        cie1_marks_message += f"Total Marks - {total_cie1_marks} / {default_total_marks} \n"
        if ui_mode[0] == 0:
            cie1_marks_message += "\n```"
        elif ui_mode[0] == 1:
            cie1_marks_message +="\n"
        # print(cie1_marks_message)
        await bot.send_message(chat_id,cie1_marks_message)
    except Exception as e:
        await bot.send_message(chat_id,f"Error retrieving cie marks : {e}")


async def cgpa_tracker(bot,chat_id):
    iscurrent_cgpa,current_cgpa = await get_cgpa(bot,chat_id)
    if not iscurrent_cgpa: # Check whether current CGPA is returned or not.
        return
    all_tracker_data = await managers_handler.get_cgpa_tracker_details(chat_id) # retrieve previously stored cgpa
    if all_tracker_data:
        status,previous_cgpa = all_tracker_data
    if status:
        if str(previous_cgpa) != current_cgpa:
            UPDATED_CGPA_TEXT = f"""
```UPDATED CGPA
SEE Results are out!!

PREVIOUS CGPA : {previous_cgpa}

CURRENT CGPA  : {current_cgpa}
```
"""
            await bot.send_message(chat_id,UPDATED_CGPA_TEXT)
            await gpa(bot,chat_id)
            await managers_handler.remove_cgpa_tracker_details(chat_id) # Turning off Tracker on local database
            await pgdatabase.remove_cgpa_tracker_details(chat_id) # Turning off otrracker on pgdatabase
            await bot.send_message(chat_id,"""
```
The CGPA tracker has been reset. We hope you are happy with your semester results. 
                                   
🎉📋
```
""")


async def cie_tracker(bot,chat_id):
    current_cie_marks = await total_cie_marks(bot,chat_id)
    if not current_cie_marks:
        return
    all_tracker_data = await managers_handler.get_cie_tracker_details(chat_id)
    if all_tracker_data:
        status,previous_cie_marks = all_tracker_data
    if status:
        if str(previous_cie_marks) != current_cie_marks:
            UPDATED_CIE_TEXT = f"""
```UPDATED CIE
CIE Results are out!!

PREVIOUS CIE : {previous_cie_marks}

CURRENT CIE  : {current_cie_marks}
```
"""
            await bot.send_message(chat_id,UPDATED_CIE_TEXT)
            await cie_marks(bot,chat_id)
            await managers_handler.remove_cie_tracker_details(chat_id) # Turning off Tracker on local database
            await pgdatabase.remove_cie_tracker_details(chat_id) # Turning off otrracker on pgdatabase
            await bot.send_message(chat_id,"""
```
The CIA tracker has been reset. We hope you are happy with your CIA results. 
                                   
🎉📋
```
""")


async def auto_login_by_database_silent(bot,chat_id):
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
        session_data = await operations.perform_login(username, password)
        if session_data:
            await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function
            await tdatabase.store_username(username)
            return True
        else:
            return False
    else:
        return False

async def silent_logout(chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    logout_url = 'https://samvidha.iare.ac.in/logout'
    cookies,headers = session_data['cookies'], session_data['headers']
    requests.get(logout_url, cookies=cookies, headers=headers)
    await tdatabase.delete_user_session(chat_id)

async def get_server_stats():
    try:# CPU stats
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq().current

        # Memory stats
        mem = psutil.virtual_memory()
        mem_used = mem.used / (1024 * 1024)  # Convert bytes to MB
        mem_total = mem.total / (1024 * 1024)  # Convert bytes to MB

        # Disk stats
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        # Network stats
        net = psutil.net_io_counters()
        bytes_sent = net.bytes_sent / (1024 * 1024)  # Convert bytes to MB
        bytes_recv = net.bytes_recv / (1024 * 1024)  # Convert bytes to MB

        # Construct message
        message = f"CPU: {cpu_percent}% ({cpu_freq} MHz)\n\n"
        message += f"Memory: {mem_used:.2f} MB / {mem_total:.2f} MB\n\n"
        message += f"Disk: {disk_percent}%\n\n"
        message += f"Network: Sent {bytes_sent:.2f} MB, Received {bytes_recv:.2f} MB"

        return message
    except Exception as e:
        return f"Error : {e}"

async def backup_all_credentials_and_settings(bot,message):
    user_chat_id = message.chat.id
    # admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    # if chat_id not in admin_chat_ids:
    #     print("chat id not in admin chat_ids")
    #     await bot.send_message(user_chat_id,"You are not authorized to perform this operation")
    #     return
    user_credentials_and_settings_sqlite = "user_credentials_settings_backup.db"
    print("User credentials database name is assigned")
    with sqlite3.connect(user_credentials_and_settings_sqlite) as conn:
        print("Connection with the sqlite3 database is successfully done")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_credentials (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                pat_student BOOLEAN,
                attendance_threshold INTEGER,
                biometric_threshold INTEGER,
                traditional_ui BOOLEAN,
                title_extract BOOLEAN
            )
        """)
        credentials_settings = await pgdatabase.get_all_credentials()
        for row in credentials_settings:
            chat_id,username,password,pat_student,attendance_threshold,biometric_threshold,traditional_ui,extract_title = row
            cursor.execute("INSERT INTO user_credentials (chat_id,username,password,pat_student,attendance_threshold,biometric_threshold,traditional_ui,title_extract) VALUES (?,?,?,?,?,?,?,?)",(chat_id,username,password,pat_student,attendance_threshold,biometric_threshold,traditional_ui,extract_title))
        conn.commit()

    try:
            # Ensure the file exists before sending
            # chat_id = message.chat.id
            if os.path.exists(user_credentials_and_settings_sqlite):
                await bot.send_document(user_chat_id, document=user_credentials_and_settings_sqlite, caption="Backup of user credentials and settings")
            else:
                await bot.send_message(user_chat_id, "Error: Backup file not found.")
    except Exception as e:
            await bot.send_message(user_chat_id, f"Error sending backup file: {e}")
            # print(e)


# This Function can be used to send the Announcement file in future.
# async def download_announcement_file(bot,message):
#     if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
#         return
#     download_document_directory = "Announcements"
#     chat_id  = message.chat.id
#     if message.document or message.video:
#         try:
#             if not os.path.exists(download_document_directory):
#                 os.makedirs(download_document_directory)
#             started_receiving_document_text = f"""
#     ```DOC STATUS
#     ● Status : Receiving
#     ```
#     """
#             message_before_recieving = await bot.send_message(chat_id,started_receiving_document_text)
#             file_name_ = message.document.file_name
#             await message.download(
#                         file_name=os.path.join(download_document_directory, file_name_),
#                     )
#             received_document_text = f"""
#     ```DOC STATUS
#     ● Status : Received

#     ● Filename : {file_name_}
#     ```
#     """
#             await bot.edit_message_text(chat_id,message_before_recieving.id,received_document_text)
#         except Exception as e:
#             await bot.send_message(chat_id,f"Error receiving file : {e}")

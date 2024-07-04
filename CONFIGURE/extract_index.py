from bs4 import BeautifulSoup
import re,requests
from DATABASE import tdatabase
from METHODS import operations

async def get_attendance_indexes(bot,message):
    """
    Extracts the indices of specific headers from the attendance HTML table.
    Raises a KeyError if any specified header is not found.

    Returns:
        tuple: A tuple containing the indices of 'Course Name', 'Conducted',
               'Attended', 'Attendance %', 'Status'.
    """
    try:
        chat_id = message.chat.id
        # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id) #check Chat id in the database
        session_data = await tdatabase.load_user_session(chat_id)
        if not session_data:
            if await operations.auto_login_by_database(bot,message,chat_id) is False and chat_id_in_local_database is False:
                # Login message if no user found in database based on chat_id
                await bot.send_message(chat_id,text="You are not logged in.")
                return
        session_data = await tdatabase.load_user_session(chat_id)
        # Access the attendance page and retrieve the content
        attendance_url = 'https://samvidha.iare.ac.in/home?action=stud_att_STD'
        
        with requests.Session() as s:
            cookies = session_data['cookies']
            s.cookies.update(cookies)

            attendance_response = s.get(attendance_url)
        data = BeautifulSoup(attendance_response.text, 'html.parser')
        if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in attendance_response.text:
                if chat_id_in_local_database:
                    await operations.silent_logout_user_if_logged_out(bot,chat_id)
                    await get_attendance_indexes(bot,message)
                else:
                    await operations.logout_user_if_logged_out(bot,chat_id)
                return
        table = data.thead.tr
        # print(table)
        # Find all th elements excluding "JNTUH - AEBAS"
        headers = [header for header in table.find_all('th')]

        indexes_dict = {}
        
        for index, header in enumerate(headers,start=0):
            indexes_dict[header.text] = index
        
        keys = ['Course Name','Conducted','Attended','Attendance %','Status']

        # index_list = [indexes_dict.get(key) for key in keys] 

        # Gets the indexes of specified keys, raise KeyError if any key not found 
        index_list = []
        for key in keys:
            if key not in indexes_dict:
                raise KeyError(f"Header {key} not found in the table.")
            
            index_list.append(indexes_dict.get(key))

        index_tuple = tuple(index_list)

        return index_tuple
    except Exception as e:
        await bot.send_message(chat_id,f"Error : {e}")

async def get_pat_indexes(bot,message):

    """
    Extracts the indices of specific headers from the PAT HTML table.
    Raises a KeyError if any specified header is not found.

    Returns:
        tuple: A tuple containing the indices of 'Course Name', 'Conducted',
               'Attended', 'Attendance %', 'Status'.
    """
    chat_id = message.chat.id
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id) #check Chat id in the database
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        if await operations.auto_login_by_database(bot,message,chat_id) is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            await bot.send_message(chat_id,text="You are not logged in.")
            return
    session_data = await tdatabase.load_user_session(chat_id)

    # Access the attendance page and retrieve the content
    attendance_url = "https://samvidha.iare.ac.in/home?action=Attendance_std"
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        pat_attendance_response = s.get(attendance_url)
    data = BeautifulSoup(pat_attendance_response.text, 'html.parser')
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in pat_attendance_response.text:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            await get_pat_indexes(bot,message)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    tables_list = data.find_all('table')
    attendance_table = tables_list[2]

    headers = [header for header in attendance_table.find_all('th')]

    indexes_dict = {}

    for index, header in enumerate(headers,start=0):
        indexes_dict[header.text] = index

    keys = ['Course Name','Conducted','Attended','Attendance %','Status']

    # index_list = [indexes_dict.get(key) for key in keys] 

    # Gets the indexes of specified keys, raise KeyError if any key not found 
    index_list = []
    for key in keys:
        if key not in indexes_dict:
            raise KeyError(f"Header {key} not found in the table.")
        
        index_list.append(indexes_dict.get(key))

    index_tuple = tuple(index_list)

    return index_tuple

async def get_biometric_indexes(bot,message):

    """
    Extracts the indices of specific headers from the biometric HTML table.
    Excludes the 'JNTUH - AEBAS' header.
    Raises a KeyError if any specified header is not found.

    Returns:
        tuple: A tuple containing the indices of 'In Time', 'Out Time', 'Status'.
    """
    try:
        chat_id = message.chat.id
        # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id) #check Chat id in the database
        session_data = await tdatabase.load_user_session(chat_id)
        if not session_data:
            if await operations.auto_login_by_database(bot,message,chat_id) is False and chat_id_in_local_database is False:
                # Login message if no user found in database based on chat_id
                await bot.send_message(chat_id,text="You are not logged in.")
                return
        session_data = await tdatabase.load_user_session(chat_id)
        # Access the attendance page and retrieve the content
        attendance_url = 'https://samvidha.iare.ac.in/home?action=std_bio'
        
        with requests.Session() as s:
            cookies = session_data['cookies']
            s.cookies.update(cookies)

            biometric_response = s.get(attendance_url)
        data = BeautifulSoup(biometric_response.text, 'html.parser')
        if '<title>Samvidha - Campus Management Portal - IARE</title>' in biometric_response.text:
                if chat_id_in_local_database:
                    await operations.silent_logout_user_if_logged_out(bot, chat_id)
                    await get_biometric_indexes(bot, message)
                else:
                    await operations.logout_user_if_logged_out(bot, chat_id)
                return
        # Find all th elements excluding "JNTUH - AEBAS"
        headers = [header for header in data.find_all('th') if header.text.strip() != "JNTUH - AEBAS"]

        indexes_dict = {}

        for index, header in enumerate(headers,start=-1):
            indexes_dict[header.text] = index
        keys = ['In Time','Out Time','Status']

        # index_list = [indexes_dict.get(key) for key in keys] 

        # Gets the indexes of specified keys, raise KeyError if any key not found 
        index_list = []
        for key in keys:
            if key not in indexes_dict:
                raise KeyError(f"Header {key} not found in the table.")
            
            index_list.append(indexes_dict.get(key))

        index_tuple = tuple(index_list)

        return index_tuple
    except Exception as e:
        await bot.send_message(chat_id,f"Error in biometric index : {e}")
        

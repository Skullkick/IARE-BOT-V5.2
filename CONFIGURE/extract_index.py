"""
HTML index extractors for attendance, PAT, and biometric tables.

These helpers authenticate using the user's saved session (from
``DATABASE.tdatabase``), fetch the relevant Samvidha pages, and compute
the zero-based column indices for specific headers by inspecting the
rendered HTML tables. The resulting tuples are typically persisted to the
database by higher-level configuration flows and then reused by scraping
logic elsewhere in the bot.

Behavior
- If the user session is missing/expired, a notification is sent via the
    ``bot`` and the function returns early.
- If the remote page indicates a logged-out state, these functions trigger
    a logout flow and may recall themselves after a silent re-login attempt.
- A KeyError is raised if any expected header is not present in the page.

Note: Only docstrings have been added here; function logic is unchanged.
"""
from bs4 import BeautifulSoup
import re,requests
from DATABASE import tdatabase
from METHODS import operations

async def get_attendance_indexes(bot,message):
    """Compute column indices for the Attendance table headers.

    Fetches the student's Attendance page and builds a header-to-index
    mapping from the first table header row. The returned tuple follows
    this order: ``('Course Name', 'Conducted', 'Attended',
    'Attendance %', 'Status')``.

    Parameters
    - bot: Telegram client used to send messages (async context).
    - message: Incoming message object supplying ``chat.id``.

    Returns
    - tuple[int, int, int, int, int]: Indices for the above headers.
    - None: When the user is not logged in and auto-login fails.

    Raises
    - KeyError: If any expected header is missing from the page/table.
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
    """Compute column indices for the PAT Attendance table headers.

    Loads the PAT view and selects the relevant table (third in the page)
    to build a header-to-index mapping. The returned tuple follows this
    order: ``('Course Name', 'Conducted', 'Attended', 'Attendance %', 'Status')``.

    Parameters
    - bot: Telegram client used to send messages (async context).
    - message: Incoming message object supplying ``chat.id``.

    Returns
    - tuple[int, int, int, int, int]: Indices for the above headers.
    - None: When the user is not logged in and auto-login fails.

    Raises
    - KeyError: If any expected header is missing from the page/table.
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
    """Compute column indices for the Biometric table headers.

    Fetches the biometric page and builds a header-to-index mapping while
    ignoring the banner header ``"JNTUH - AEBAS"``. The returned tuple
    follows this order: ``('In Time', 'Out Time', 'Status')``.

    Parameters
    - bot: Telegram client used to send messages (async context).
    - message: Incoming message object supplying ``chat.id``.

    Returns
    - tuple[int, int, int]: Indices for the above headers.
    - None: When the user is not logged in and auto-login fails.

    Raises
    - KeyError: If any expected header is missing from the page/table.
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
        

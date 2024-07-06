from bs4 import BeautifulSoup
import requests
from DATABASE import user_settings,tdatabase
from METHODS import operations,labs_handler,pdf_compressor
from Buttons import buttons
import os,re

async def fetch_available_labs(bot,message):
    """
    Fetches available labs and returns them as a dictionary
    
    :return: Dictionary Containing the lab details
    :Dictionary: {sub_name:sub_code}"""
    chat_id = message.chat.id
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await operations.auto_login_by_database(bot,"message",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)

    # Access the Lab record page and retrieve the content
    lab_record_url = 'https://samvidha.iare.ac.in/home?action=labrecord_std'
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        lab_record_response = s.get(lab_record_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    # data = BeautifulSoup(attendance_response.text, 'html.parser')
    if lab_record_response.status_code == 200:
            html_content = lab_record_response.text
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in html_content:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            return await fetch_available_labs(bot,message)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return
    try:           
# Step 2: Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Step 3: Locate the <select> element
        select_element = soup.find('select', id='ddlsub_code')
        
        if not select_element:
            await bot.send_message(chat_id, "Error retrieving the available lab data.")
            print("Failed to find the <select> element with id 'ddlsub_code'")
            raise Exception("Failed to find the <select> element with id 'ddlsub_code'.")
        
        # Step 4: Extract lab details from <option> elements
        lab_details = {}
        for option in select_element.find_all('option'):
            lab_text = option.text.strip()
            if lab_text and lab_text != "Select Lab":  # Exclude the placeholder "Select Lab"
                lab_text = lab_text.split(" - ")
                sub_code = lab_text[0]
                sub_name = lab_text[1]
                lab_details[sub_name] = sub_code

        return lab_details
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
async def get_week_details(experiment_names,submitted_lab_records,all_weeks_numbers_bool:bool,submitted_weeks_bool:bool,not_submitted_weeks_bool:bool,can_delete_weeks_bool:bool):

    soup = BeautifulSoup(experiment_names, 'html.parser')
    rows = soup.find_all('tr')[1:]
    all_week_numbers = []

    for row in rows:
        week_text = row.find_all('td')[0].get_text(strip=True)
        week_number = re.findall(r'\d+', week_text)
        if week_number:
            all_week_numbers.append(int(week_number[0]))

# Extract the list of submitted weeks
    submitted_data = submitted_lab_records[0] 
    # print(submitted_data)
    submitted_weeks = []

    for week_no, entries in submitted_data.items():
        for entry in entries:
            # if entry['delete'] == 0:  # Check if the 'delete' flag is 0
            submitted_weeks.append(int(week_no))  # Add the week number to the list as an integer
    # Sort the weeks for better readability
    submitted_weeks = sorted(submitted_weeks)
    can_upload_list = [week for week in all_week_numbers if week not in submitted_weeks]
    can_upload_list_updated = [week for week in can_upload_list if week not in submitted_lab_records[1]]
    if all_weeks_numbers_bool is True:
        return all_week_numbers
    if submitted_weeks_bool is True:
        return submitted_weeks
    if not_submitted_weeks_bool is True:
        return can_upload_list_updated
    if can_delete_weeks_bool is True:
        return submitted_lab_records[1]
    
async def get_marks_by_week(submitted_lab_records, week_no):
    records, exempted_weeks = submitted_lab_records
    week_key = str(week_no)
    if week_key in records and week_no not in exempted_weeks:
        week_records = records[week_key]
        # Assuming there's only one record per week
        if week_records:
            return week_records[0]['mark']
    return None

async def fetch_submitted_lab_records(bot,chat_id,user_details,sub_code):
    url = 'https://samvidha.iare.ac.in/pages/student/lab_records/ajax/day2day.php'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://samvidha.iare.ac.in',
        'referer': 'https://samvidha.iare.ac.in/home?action=labrecord_std',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'rollno':user_details['roll_no'],
        'ay': user_details['ay'],
        'sub_code': sub_code,
        'action': 'day2day_lab',
    }
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await operations.auto_login_by_database(bot,"message",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

   # Make the POST request
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    
    # Check if the response is successful
    if response.status_code != 200:
        await bot.send_message(chat_id,f"Failed to fetch lab records: {response.status_code}")
        return
    
    # Parse the JSON data
    json_data = response.json()
    
    # Initialize a dictionary to store records grouped by week number
    data_by_week = {}

    # Process the data to group by week_no
    for record in json_data['data']:
        week_no = record['week_no']
        if week_no not in data_by_week:
            data_by_week[week_no] = []
        data_by_week[week_no].append(record)
    
    weeks_with_delete = [int(entry['week_no']) for key in data_by_week for entry in data_by_week[key] if entry['delete'] == 1]

    # return weeks_with_delete
    return data_by_week,weeks_with_delete

async def get_view_pdf_url(sub_code,user_details,week_no):
    roll_no = user_details['roll_no'].upper()
    current_sem = user_details['current_sem'].upper()
    url = f'https://iare-data.s3.ap-south-1.amazonaws.com/uploads/STUDENTS/{roll_no}/LAB/SEM{current_sem}/{sub_code}/{roll_no}_week{week_no}.pdf'
    return url

async def delete_lab_record(bot,chat_id,sub_code, user_details, week_number):
    url = 'https://samvidha.iare.ac.in/pages/student/lab_records/ajax/day2day'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://samvidha.iare.ac.in',
        'referer': 'https://samvidha.iare.ac.in/home?action=labrecord_std',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'rollno': user_details['roll_no'],
        'ay': user_details['ay'],
        'sub_code': sub_code,
        'week_no': week_number,
        'sem': user_details['current_sem'],
        'action': 'day2day_lab_delete',
    }
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await operations.auto_login_by_database(bot,"message",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
    response = requests.post(url, headers=headers, data=data, cookies=cookies)
    return response.json()

async def get_subject_name(subject_code,lab_details):
    """
    This function is used to get the subject name based on the subject code provided
    :subject_code: Subject code of the required subject
    :lab_details: Details of all the lab_record containing subject_name and subject code as a dictionary

    """
    subject_name = (subject_name for subject_name, value in lab_details.items() if value == subject_code)
    return list(subject_name)[0]

async def user_lab_data(bot,chat_id):
    """
    This function is used to extract the data required while uploading the lab record
    
    :return: Dictionary
    
    :Dictionary:
    - ay: academic_year
    - roll_no : roll_no
    - current_sem : semester
    - lab_batch_no: lab_batch_no
    """
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await operations.auto_login_by_database(bot,"message",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    url = 'https://samvidha.iare.ac.in/home?action=labrecord_std'
    with requests.session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        lab_record_user_data_response = s.get(url)
    if lab_record_user_data_response.status_code == 200:
        html_content = lab_record_user_data_response.text
        soup = BeautifulSoup(html_content, 'html.parser') 
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in html_content:
        if chat_id_in_local_database:
            await operations.silent_logout_user_if_logged_out(bot,chat_id)
            await user_lab_data(bot,chat_id)
        else:
            await operations.logout_user_if_logged_out(bot,chat_id)
        return 
    try:
        academic_year = soup.find('input', id='ay')['value'].strip()
    except TypeError:
        academic_year = 'Not Found'

    try:
        roll_no = soup.find('input', id='rollno')['value'].strip()
    except TypeError:
        roll_no = 'Not Found'

    try:
        semester = soup.find('input', id='current_sem')['value'].strip()
    except TypeError:
        semester = 'Not Found'

    try:
        lab_batch_no = soup.find('input', id='lab_batch_no')['value'].strip()
    except TypeError:
        lab_batch_no = 'Not Found'
    
    user_details = {
        'ay': academic_year,
        'roll_no': roll_no,
        'current_sem': semester,
        'lab_batch_no': lab_batch_no,
    }
    return user_details

async def fetch_experiment_names_html(bot,chat_id,user_details, sub_code)->str:
    """
    Can be used to fetch the html response which contains all the experiment names based on the subject code
    :return: html code to extract the experiment names
    """
    url = 'https://samvidha.iare.ac.in/pages/student/lab_records/ajax/day2day.php'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://samvidha.iare.ac.in',
        'referer': 'https://samvidha.iare.ac.in/home?action=labrecord_std',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'ay': user_details['ay'],
        'sub_code': sub_code,
        'action': 'get_exp_list',
    }
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await operations.auto_login_by_database(bot,"message",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    with requests.session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
    response = requests.post(url, headers=headers, data=data, cookies=cookies)
    return response.text

async def get_experiment_title(experiment_names_html, week_no):
    soup = BeautifulSoup(experiment_names_html, 'html.parser')
    table = soup.find('table', class_='table')

    if not table:
        return None
    try:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Start from index 1 to skip header row
            cells = row.find_all('td')
            week_number = cells[0].get_text().strip()
            if week_number == f"Week-{week_no}":
                experiment_title = cells[2].get_text().strip() 

        return experiment_title
    except:
        return None

async def get_upload_details(week_no, exp_title, file_name, file_path):
    upload_details = {
        'week_no': week_no,
        'exp_title': exp_title,
        'file_name': file_name,
        'file_path': file_path
    }
    return upload_details

async def upload_pdf(bot,message,sub_code,user_details,upload_details):
    url = 'https://samvidha.iare.ac.in/pages/student/lab_records/ajax/day2day'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.5',
        'origin': 'https://samvidha.iare.ac.in',
        'referer': 'https://samvidha.iare.ac.in/home?action=labrecord_std',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    files = {
        'ay': (None, user_details['ay']),
        'rollno': (None, user_details['roll_no']),
        'current_sem': (None, user_details['current_sem']),
        'sub_code': (None, sub_code),
        'lab_batch_no': (None, user_details['lab_batch_no']),
        'week_no': (None, upload_details['week_no']),
        'exp_title': (None, upload_details['exp_title']),
        # 'prog_doc': (upload_details['file_name'], open(upload_details['file_name'], 'rb'), fr"{upload_details['file_path']}"),
        'prog_doc': (upload_details['file_name'], open(upload_details['file_path'], 'rb'), 'application/pdf'),
        'action': (None, 'upload_lab_record_student'),
    }
    chat_id = message.chat.id
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id) 
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await operations.auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # Login message if no user found in database based on chat_id
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=operations.login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=operations.login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
    response = requests.post(url, headers=headers, files=files, cookies=cookies)
    return response.json()


async def upload_lab_record(bot,message,title,subject_code,week_no):
    """
    This Function is used to upload the the pdf to the samvidha by retreiving the required data from the database.

    :param bot: Pyrogram Client.
    :param message: message sent by the user.
    :param subject_code: Code of the subject
    :param week_no: Week number of the selected subject
    :return: None
    """
    # chat_id of the user based on the message sent by the user
    chat_id = message.chat.id
    message_sent_when_started = await bot.send_message(chat_id,"Initiated retrieval of necessary data for uploading.")
    pdf_folder = "pdfs"
    if await labs_handler.check_pdf_size_above_1mb(chat_id) is True:
        message_of_pdf_operation_start = await bot.edit_message_text(chat_id,message_sent_when_started.id,"PDF Above 1 MB Trying to Compress")
        if pdf_compressor.use_pdf_compress_scrape is True:
            pdf_compression = await pdf_compressor.compress_pdf_scrape(bot,message)
            compress_pdf_status,status_message = pdf_compression
            if compress_pdf_status is False:
                await bot.send_message(chat_id,status_message)
            else:
                message_of_pdf_operation = await bot.edit_message_text(chat_id,message_of_pdf_operation_start.id,"Compressed PDF Successfully.")

        else:
            if await pdf_compressor.compress_pdf(bot,chat_id) is True:
                message_of_pdf_operation = await bot.edit_message_text(chat_id,message_of_pdf_operation_start.id,"Compressed Pdf Successfully.")
                check,size = await labs_handler.check_pdf_size_after_compression(chat_id)
                if check is True:
                    failed_message = f"""
● ERROR : Unable to reduce the PDF file size to less than 1MB.

● PDF Size : {size}"""
                    await bot.send_message(chat_id,failed_message)
                    return
    else:
        message_of_pdf_operation = message_sent_when_started
    extracted_user_details = await user_lab_data(bot,chat_id)
    labs_data = await fetch_available_labs(bot,message)
    selected_subject_name = await get_subject_name(subject_code,labs_data)
    # Folder name containg pdfs
    pdf_folder = "pdfs"
    # Check Whether the pdf is present or not, If the pdf is present gets the compression status
    check_present , check_compress = await labs_handler.check_recieved_pdf_file(bot,chat_id)
    if check_present:
        # According to the compression status the pdf file is selected to uplaod
        if check_compress is True:
            pdf_folder = os.path.join(pdf_folder,f"C-{chat_id}-comp.pdf")
        else:
            pdf_folder = os.path.join(pdf_folder,f"C-{chat_id}.pdf")
        if check_compress is True:
            pdf_name = f"C-{chat_id}-comp.pdf"
        else:
            pdf_name = f"C-{chat_id}.pdf"
    pdf_file_path = os.path.abspath(pdf_folder)
    pdf_size = await labs_handler.get_pdf_size(bot,chat_id)
    renamed_pdf_name,updated_pdf_file_path = await labs_handler.rename_to_upload_pdf(pdf_file_path,chat_id,week_no)
    message_text_before_uploading = f"""
```UPLOAD INITIATED
⫸ STATUS : UPLOADING

⫸ UPLOAD DETAILS :

TITLE : {title} 

SUBJECT : {selected_subject_name}

WEEK : {f"Week - {week_no}"}

PDF SIZE : {pdf_size}MB
```
"""
    message_before_start_upload = await bot.edit_message_text(chat_id,message_of_pdf_operation.id,message_text_before_uploading)
    try:
        upload_details = await get_upload_details(week_no,title,file_name=renamed_pdf_name,file_path=updated_pdf_file_path)
        lab_record_upload_json = await upload_pdf(bot,message,subject_code,extracted_user_details,upload_details=upload_details)
    except Exception as e:
        print(e)    
    if lab_record_upload_json['status'] == "error":# Checks if received status code is error or not.
        UNSUCCESSFULL_UPLOAD_MESSAGE = f"""
    ```UPLOAD FAILED
⫸ STATUS : FAILED

⫸ ERROR : {lab_record_upload_json['msg']}

⫸ UPLOAD DETAILS :

● TITLE : {title} 

● SUBJECT : {selected_subject_name}

● WEEK : {f"Week - {week_no}"}

    ```
    """
        await labs_handler.remove_pdf_file(bot,chat_id) # Removes the Pdf from the pdf folder
        await tdatabase.delete_indexes_and_title_info(chat_id) # Delete the selected index values
        await bot.edit_message_text(chat_id,message_before_start_upload.id,UNSUCCESSFULL_UPLOAD_MESSAGE)
    else:
        SUCCESSFULL_UPLOAD_MESSAGE = F"""
    ```UPLOAD SUCCESS
⫸ STATUS : {lab_record_upload_json['status'].upper()}

⫸ STATUS MESSAGE : {lab_record_upload_json['msg']}

⫸ Upload details :

● TITLE : {title}

● SUBJECT : {selected_subject_name}

● WEEK : {f"Week - {week_no}"}

● PDF SIZE : {pdf_size}MB
    ``` 
    """
        await labs_handler.remove_pdf_file(bot,chat_id)# Removes the Pdf from the pdf folder
        await tdatabase.delete_indexes_and_title_info(chat_id)# Delete the selected index values
        await bot.edit_message_text(chat_id,message_before_start_upload.id,SUCCESSFULL_UPLOAD_MESSAGE)
    await buttons.start_user_buttons(bot,message) # Starts the user buttons.


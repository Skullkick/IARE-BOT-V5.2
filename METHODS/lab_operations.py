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
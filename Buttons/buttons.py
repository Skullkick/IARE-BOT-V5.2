from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from DATABASE import pgdatabase,tdatabase,user_settings
from METHODS import operations,labs_driver,labs_handler,lab_operations
import main
import json,asyncio


USER_MESSAGE = "Here are some actions you can perform."
USER_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Attendance", callback_data="attendance"),InlineKeyboardButton("Bunk", callback_data="bunk")],
        [InlineKeyboardButton("Biometric", callback_data="biometric"),InlineKeyboardButton("Logout", callback_data="logout")],
        # [InlineKeyboardButton("Lab Upload",callback_data="lab_upload_start")],
        [InlineKeyboardButton("Labs Records",callback_data="lab_record_subject")],
        [InlineKeyboardButton("Student Info",callback_data="student_info")],
        [InlineKeyboardButton("Saved Username", callback_data="saved_username")]

    ]
)

SETTINGS_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Attendance Threshold", callback_data="attendance_threshold")],
        [InlineKeyboardButton("Biometric Threshold",callback_data="biometric_threshold")],
        [InlineKeyboardButton("Title Extract",callback_data="title_extract")],
        [InlineKeyboardButton("User Interface", callback_data="ui")],
        [InlineKeyboardButton("Labs Data",callback_data="labs_data")]
    ]
)
SETTINGS_TEXT = "Welcome to the settings menu.\n\n Here, you can customize various aspects of your experience to suit your preferences."

remove_cred_keyboard = InlineKeyboardMarkup(
inline_keyboard=[
    [InlineKeyboardButton("Remove",callback_data="remove_saved_cred")]
])

ADMIN_OPERATIONS_TEXT = "Menu (ADMIN)"
ADMIN_MESSAGE = f"welcome back!, You have access to additional commands. Here are some actions you can perform."
ADMIN_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("REQUESTS", callback_data="requests"), InlineKeyboardButton("USERS", callback_data="users")],
        [InlineKeyboardButton("LOGS",callback_data="log_file")],
        [InlineKeyboardButton("DATABASE", callback_data="database")],
        [InlineKeyboardButton("BANNED USERS",callback_data="banned_user_data")]
    ]
)

CERTIFICATES_TEXT  = f"""
Select one from the available ones."""
CERTIFICATES_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton("Profile Pic",callback_data="get_profile_pic"),InlineKeyboardButton("Aadhar Card",callback_data="get_aadhar_pic")],
        [InlineKeyboardButton("SSC Memo",callback_data="get_ssc_memo"),InlineKeyboardButton("Inter Memo",callback_data="get_inter_memo")],
        [InlineKeyboardButton("DOB Certificate",callback_data="get_dob_certificate"),InlineKeyboardButton("Income Certificate",callback_data="get_income_certificate")],
        [InlineKeyboardButton("Back",callback_data="student_info")]
    ]
)

START_LAB_UPLOAD_MESSAGE_TITLE_MANUAL_UPDATED = f"""
**STEP - 1**
```How to Submit Your Experiment Title
● Title: Title of Experiment.

● Example:
 
Title: Intro to Python.```


**STEP - 2**
```How to Send the PDF file
● You Can Either Forward or Send Your PDF File

● Wait until The Whole Process of Receiving the PDF File completes.```

**STEP - 3**
```Upload Lab PDF
After completing Step 1 and 2,
Click the upload lab record button to upload the PDF.```
"""

START_LAB_UPLOAD_MESSAGE_TITLE_MANUAL_TRADITIONAL = f"""
**STEP - 1**

How to Submit Your Experiment Title

● Title: Title of Experiment.

● Example:
 
Title: Intro to Python. 


**STEP - 2**

How to Send the PDF file

● You Can Either Forward or Send Your PDF File

● Wait until The Whole Process of Receiving the PDF File completes. 

**STEP - 3**

Upload Lab PDF

After completing Step 1 and 2,

Click the upload lab record button to upload the PDF. 
"""

START_LAB_UPLOAD_MESSAGE_TITLE_AUTOMATIC_UPDATED = f"""
**STEP - 1**
```How to Send the PDF file
● You Can Either Forward or Send Your PDF File

● Wait until The Whole Process of Receiving the PDF File completes.```

**STEP - 2**
```Upload Lab PDF
After completing Step 1 ,
Click the upload lab record button to upload the PDF.```

"""

START_LAB_UPLOAD_MESSAGE_TITLE_AUTOMATIC_TRADITIONAL = f"""
**STEP - 1**

How to Send the PDF file

● You Can Either Forward or Send Your PDF File

● Wait until The Whole Process of Receiving the PDF File completes.

**STEP - 2**

Upload Lab PDF

After completing Step 1 ,

Click the upload lab record button to upload the PDF.

"""

# Buttons for the LAB UPLOADS
START_LAB_UPLOAD_BUTTONS = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Upload Lab Record", callback_data="lab_upload")],
        [InlineKeyboardButton("Back",callback_data="user_back")]
    ]
)

# Back Button
BACK_TO_USER_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Back",callback_data="user_back")]
    ]
)

# text for user not logged in
NO_SAVED_LOGIN_TEXT = f"""
```NO SAVED LOGIN
This can be used only by Saved login users.

⫸ How To Save the Login Credentials:

● Click on Logout

● Login Again Using /login username password

● Example : /login 22951A0000 password
```
"""
# PDF Uploading text.
UPLOAD_PDF_TEXT = "Please send me the PDF file you'd like to upload."
# Text for title sending instructions.
SEND_TITLE_TEXT = f"""
```Send Title
⫸ How To Send Title:

Title : Title of Experiment

⫸ Example:

Title : Introduction to Python

``` 
"""


# Message that needs to be sent if title is not Stored
NO_TITLE_MESSAGE = f"""
```NO TITLE FOUND
⫸ How To Send Title:

Title : Title of Experiment

⫸ Example:

Title : Introduction to Python

``` 
"""

# Function to start the user buttons.
async def start_user_buttons(bot,message):
    """
    This Function is used to start the user buttons with the text.
    :param bot: Client session
    :param message: Message of the user"""
    await message.reply_text(USER_MESSAGE,reply_markup = USER_BUTTONS)

async def start_certificates_buttons(message):
    """This Function is used to start the Certificates buttons
    :param message: Message of the user
    """
    await message.reply_text(CERTIFICATES_TEXT,reply_markup = CERTIFICATES_BUTTONS)

async def start_user_settings(bot,message):
    """This Function is used to start the settings buttons of a user
    :param bot: Client session
    :param message: Message of the user
    """
    await message.reply_text(SETTINGS_TEXT,reply_markup = SETTINGS_BUTTONS)


async def start_save_credentials_buttons(username,password):
    SAVE_USER_BUTTON = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Yes",callback_data=f"save_credentials-{username}-{password}")],
            [InlineKeyboardButton("No",callback_data="no_save")]
        ]
    )
    return SAVE_USER_BUTTON

async def start_student_profile_buttons(message):
    STUDENT_PROFILE_BUTTON = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("GPA",callback_data="user_gpa")],
                [InlineKeyboardButton("CIE",callback_data="user_cie")],
                [InlineKeyboardButton("Certificates",callback_data="certificates_start")],
                [InlineKeyboardButton("Payment Details",callback_data="payment_details")],
                [InlineKeyboardButton("Profile",callback_data="student_profile")],
                [InlineKeyboardButton("Back",callback_data="user_back")]
            ]
        )
    await message.reply_text("Select one from the available ones.",reply_markup = STUDENT_PROFILE_BUTTON)

async def callback_function(bot,callback_query):
    """
    This Function performs operations based on the callback data from the user
    :param bot: Client session.
    :param callback_query: callback data of the user.

    :return: This returns nothing, But performs operations.
    
    """
    if callback_query.data == "attendance":# If callback_query data is attendance
        message = callback_query.message
        chat_id = message.chat.id
        
        # Check if the user is a PAT student
        if await operations.check_pat_student(bot, message) is True:
            # Display PAT options
            PAT_BUTTONS = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("PAT Attendance", callback_data="pat_attendance")],
                    [InlineKeyboardButton("Attendance", callback_data="attendance_in_pat_button")],
                    [InlineKeyboardButton("Back", callback_data="user_back")]
                ]
            )
            # Edit the previous buttons with the added pat attendance button.
            await callback_query.edit_message_text(USER_MESSAGE, reply_markup=PAT_BUTTONS)
        else:
            # proceed with regular attendance
            await operations.attendance(bot, message)
            await callback_query.answer()
            await callback_query.message.delete() # delete the older buttons message
            
    elif callback_query.data == "attendance_in_pat_button":
        _message = callback_query.message
        await operations.attendance(bot,_message)  
        await callback_query.answer()  
        await callback_query.message.delete()
    elif callback_query.data == "pat_attendance":
        _message = callback_query.message
        await operations.pat_attendance(bot,_message)
        await callback_query.answer()
        await callback_query.message.delete()
    elif callback_query.data == "bunk":
        _message = callback_query.message
        await operations.bunk(bot,_message)
        await callback_query.answer()
        await callback_query.message.delete()
    elif callback_query.data == "biometric":
        _message = callback_query.message
        await operations.biometric(bot,_message)
        await callback_query.answer()
        await callback_query.message.delete()
    elif callback_query.data == "logout":
        _message = callback_query.message
        await operations.logout(bot,_message)
        await callback_query.answer()
    elif callback_query.data == "saved_username":
        _message = callback_query.message
        chat_id = _message.chat.id
        USERNAME = await tdatabase.fetch_username_from_credentials(chat_id)
        # USERNAME = await pgdatabase.get_username(chat_id=_message.chat.id)
        if USERNAME is not None:
            SAVED_USERNAME_TEXT = "Here are your saved credentials."
            USERNAME = USERNAME.upper()
            SAVED_USERNAME_BUTTONS = InlineKeyboardMarkup(
                inline_keyboard= [
                    [InlineKeyboardButton(f"{USERNAME}",callback_data="username_saved_options")],
                    [InlineKeyboardButton("Back",callback_data="user_back")]
                ]
            )
            await callback_query.edit_message_text(
                SAVED_USERNAME_TEXT,
                reply_markup = SAVED_USERNAME_BUTTONS
            )
        else:
            await callback_query.answer()
            await callback_query.edit_message_text(NO_SAVED_LOGIN_TEXT,reply_markup = BACK_TO_USER_BUTTON)

    elif callback_query.data == "lab_upload_start":
        _message = callback_query.message
        chat_id = _message.chat.id
        chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
        ui_mode = await user_settings.fetch_ui_bool(chat_id)
        if chat_id_in_pgdatabase is False:
            await bot.send_message(chat_id,"This feature is currently available to Saved Credential users")
            await callback_query.answer()
            return
        await tdatabase.store_pdf_status(chat_id,"Recieve")
        title_mode = await user_settings.fetch_extract_title_bool(chat_id)
        if title_mode[0] == 0:
            await tdatabase.store_title_status(chat_id,"Recieve")
            if ui_mode[0] == 0:
                await callback_query.edit_message_text(START_LAB_UPLOAD_MESSAGE_TITLE_MANUAL_UPDATED,reply_markup = START_LAB_UPLOAD_BUTTONS)
            elif ui_mode[0] == 1:
                await callback_query.edit_message_text(START_LAB_UPLOAD_MESSAGE_TITLE_MANUAL_TRADITIONAL,reply_markup = START_LAB_UPLOAD_BUTTONS)
        elif title_mode[0] == 1:
            if ui_mode[0] == 0:
                await callback_query.edit_message_text(START_LAB_UPLOAD_MESSAGE_TITLE_AUTOMATIC_UPDATED,reply_markup = START_LAB_UPLOAD_BUTTONS)
            elif ui_mode[0] == 1:
                await callback_query.edit_message_text(START_LAB_UPLOAD_MESSAGE_TITLE_AUTOMATIC_TRADITIONAL,reply_markup = START_LAB_UPLOAD_BUTTONS)
    elif callback_query.data == "lab_upload":
        _message = callback_query.message
        chat_id = _message.chat.id
        await callback_query.message.delete()
        
        # The amount of time it should check whether the pdf is downloaded or not
        timeout,count = 10,0
        CHECK_FILE = await labs_handler.check_recieved_pdf_file(bot,chat_id)
        while not CHECK_FILE[0]:
        # Sleep briefly before checking again
            if timeout != count:
                count += 2
                await asyncio.sleep(1)
            else:
                await bot.send_message(chat_id,"Unable to find the pdf file. Please try sending the pdf file again.")
                await start_user_buttons(bot,_message)
                return
        # Checks it the title is present or not.
        current_title = await tdatabase.fetch_title_lab_info(chat_id)
        title_mode = await user_settings.fetch_extract_title_bool(chat_id) # Whether the title retrieval is automatic or not.
        if title_mode[0] == 0:
            if current_title[0] is None:
                await bot.send_message(chat_id,NO_TITLE_MESSAGE)
                await start_user_buttons(bot,_message)
                return
        # Fetch the subjects from the sqlite3 database
        lab_details = await lab_operations.fetch_available_labs(bot,_message)
        # Deserialize the lab_details data
        # lab_details = json.loads(lab_details[0])
        LAB_SUBJECT_TEXT = "Select the subject that you want to upload"
        # Generate InlineKeyboardButtons for lab subjects selection
        LAB_SUBJECT_BUTTONS = [
            [InlineKeyboardButton(subject_name, callback_data=f"subject_{subject_code}")]
            for subject_name, subject_code in lab_details
        ]
        LAB_SUBJECT_BUTTONS.append([InlineKeyboardButton("Back", callback_data="user_back")])

        LAB_SUBJECT_BUTTONS_MARKUP = InlineKeyboardMarkup(LAB_SUBJECT_BUTTONS)

        await bot.send_message(
            chat_id,
            text=LAB_SUBJECT_TEXT,
            reply_markup=LAB_SUBJECT_BUTTONS_MARKUP
        )
    elif "subject_" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        selected_subject = callback_query.data.split("subject_")[1]
        # # Store selected Subject index in the labuploads database
        await tdatabase.store_subject_code(chat_id,selected_subject)
        user_details = await lab_operations.user_data(bot,chat_id)
        experiment_names = await lab_operations.fetch_experiment_names(user_details,selected_subject)
        all_submitted_lab_records = await lab_operations.fetch_submitted_lab_records(bot,chat_id,user_details,selected_subject)
        week_details = await lab_operations.get_week_details(experiment_names,all_submitted_lab_records,False,False,True,False)
        LAB_WEEK_TEXT = "Select the week"
        LAB_WEEK_BUTTONS = [
            [InlineKeyboardButton(f"Week-{week_no}",callback_data=f"Week-{week_no}")]
            for week_no in week_details
        ]

        LAB_WEEK_BUTTONS.append([InlineKeyboardButton("Back",callback_data="lab_upload")])
        LAB_WEEK_BUTTONS_MARKUP = InlineKeyboardMarkup(LAB_WEEK_BUTTONS)
        await callback_query.message.edit_text(
                    LAB_WEEK_TEXT,
                    reply_markup=LAB_WEEK_BUTTONS_MARKUP
                )
    elif "Week-" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        selected_week = callback_query.data.split("Week-")[1]
        # Store the index of selected week in database
        await tdatabase.store_week_index(chat_id,selected_week)
        await callback_query.message.delete()
        # if await tdatabase.fetch_title_lab_info(chat_id):
        #     await labs_driver.upload_lab_pdf(bot,_message)
        await lab_operations.upload_lab_record(bot,_message)

    elif "save_credentials" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        # Splitting the username and password from the callback_query
        user_credentials = callback_query.data.split("-")
        username = user_credentials[1].lower()
        password = user_credentials[2]
        try:
            # Saving the credentials to the database
            await pgdatabase.save_credentials_to_databse(chat_id,username,password) # saving credentials in postgres database
            await tdatabase.store_credentials_in_database(chat_id,username,password) # saving credentials in temporary database
            await callback_query.message.edit_text("Your credentails have been saved successfully.")
        except Exception as e:
            await bot.send_message(chat_id,f"Error saving credentils : {e}")

    elif callback_query.data == "user_back":
        await callback_query.edit_message_text(USER_MESSAGE,reply_markup = USER_BUTTONS)
    elif callback_query.data == "username_saved_options":
        USERNAME_SAVED_OPTIONS_TEXT = "Here are some operations that you can perform."
        USERNAME_SAVED_OPTIONS_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Remove",callback_data="remove_saved_cred")],
                [InlineKeyboardButton("Remove and Logout", callback_data="remove_logout_saved_cred")],
                [InlineKeyboardButton("Back",callback_data="user_back")]
            ]
        )
        await callback_query.edit_message_text(
            USERNAME_SAVED_OPTIONS_TEXT,
            reply_markup = USERNAME_SAVED_OPTIONS_BUTTONS
        )
    elif callback_query.data == "remove_saved_cred":
        await callback_query.answer()
        _message = callback_query.message
        chat_id = _message.chat.id
        # await tdatabase.delete_lab_upload_data(chat_id) # Deletes the saved Subjects and weeks from database
        await pgdatabase.remove_saved_credentials(bot,chat_id)
        await tdatabase.delete_user_credentials(chat_id)
        await callback_query.answer()

    elif callback_query.data == "remove_logout_saved_cred":        
        _message = callback_query.message
        chat_id = _message.chat.id
        # if await tdatabase.fetch_lab_subjects_from_lab_info(chat_id):
        #     await tdatabase.delete_lab_upload_data(chat_id)# Deletes the saved Subjects and weeks from database
        await pgdatabase.remove_saved_credentials(bot,chat_id)
        await operations.logout_user_and_remove(bot,_message)
        await tdatabase.delete_user_credentials(chat_id)
        await callback_query.answer()

    elif callback_query.data == "attendance_threshold":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_threshold = await user_settings.fetch_attendance_threshold(chat_id)
        ATTENDANCE_THRESHOLD_TEXT = f"Current Attendance Threshold : {current_threshold[0]}\n\nClick on \n ●\t \"+\" to increase threshold \n\n ●\t \"-\" to decrease threshold"
        ATTENDANCE_THRESHOLD_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("-",callback_data="decrease_att_threshold"),InlineKeyboardButton(current_threshold[0],callback_data="None"),InlineKeyboardButton("+",callback_data="increase_att_threshold")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await callback_query.edit_message_text(
            ATTENDANCE_THRESHOLD_TEXT,
            reply_markup = ATTENDANCE_THRESHOLD_BUTTONS
        )
    elif callback_query.data == "None":
        await callback_query.answer()
    elif "att_threshold" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        query = callback_query.data.split("_")[0]
        if query == "increase":
            current_threshold = await user_settings.fetch_attendance_threshold(chat_id)
            await user_settings.set_attendance_threshold(chat_id,current_threshold[0]+5)
        elif query == "decrease":
            current_threshold = await user_settings.fetch_attendance_threshold(chat_id)
            await user_settings.set_attendance_threshold(chat_id,current_threshold[0]-5)
        current_threshold = await user_settings.fetch_attendance_threshold(chat_id)
        ATTENDANCE_THRESHOLD_TEXT = f"Current Attendance Threshold : {current_threshold[0]}\n\nClick on \n ●\t \"+\" to increase threshold \n\n ●\t \"-\" to decrease threshold"
        ATTENDANCE_THRESHOLD_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("-",callback_data="decrease_att_threshold"),InlineKeyboardButton(current_threshold[0],callback_data="None"),InlineKeyboardButton("+",callback_data="increase_att_threshold")],
                [InlineKeyboardButton("Save Changes",callback_data="save_changes_settings")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await callback_query.edit_message_text(
            ATTENDANCE_THRESHOLD_TEXT,
            reply_markup = ATTENDANCE_THRESHOLD_BUTTONS
        )
    elif callback_query.data == "biometric_threshold":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_threshold = await user_settings.fetch_biometric_threshold(chat_id)
        # current_threshold = current_threshold[0]
        BIOMETRIC_THRESHOLD_TEXT = f"Current Biometric Threshold : {current_threshold[0]}\n\nClick on \n ●\t \"+\" to increase threshold \n\n ●\t \"-\" to decrease threshold"
        BIOMETRIC_THRESHOLD_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("-",callback_data="decrease_bio_threshold"),InlineKeyboardButton(current_threshold[0],callback_data="None"),InlineKeyboardButton("+",callback_data="increase_bio_threshold")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await callback_query.edit_message_text(
            BIOMETRIC_THRESHOLD_TEXT,
            reply_markup = BIOMETRIC_THRESHOLD_BUTTONS
        )
    elif "bio_threshold" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id    
        query = callback_query.data.split("_")[0]
        if query == "increase":
            current_threshold = await user_settings.fetch_biometric_threshold(chat_id)
            await user_settings.set_biometric_threshold(chat_id,current_threshold[0]+5)
        elif query == "decrease":
            current_threshold = await user_settings.fetch_biometric_threshold(chat_id)
            await user_settings.set_biometric_threshold(chat_id,current_threshold[0]-5)
        current_threshold = await user_settings.fetch_biometric_threshold(chat_id)
        BIOMETRIC_THRESHOLD_TEXT = f"Current Biometric Threshold : {current_threshold[0]}\n\nClick on \n ●\t + to increase threshold \n\n ●\t - to decrease threshold"
        BIOMETRIC_THRESHOLD_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("-",callback_data="decrease_bio_threshold"),InlineKeyboardButton(current_threshold[0],callback_data="None"),InlineKeyboardButton("+",callback_data="increase_bio_threshold")],
                [InlineKeyboardButton("Save Changes",callback_data="save_changes_settings")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await callback_query.edit_message_text(
            BIOMETRIC_THRESHOLD_TEXT,
            reply_markup = BIOMETRIC_THRESHOLD_BUTTONS
        )
    elif callback_query.data == "title_extract":
        _message = callback_query.message
        chat_id = _message.chat.id
        TITLE_BOOL = await user_settings.fetch_extract_title_bool(chat_id)
        TITLE_EXTRACT_TEXT = "Title Modes:\n\n\tAutomatic : Title is taken from the Experiment Details \n\n\tMANUAL : Title needs to be given by the user to the bot\n\n"
        if TITLE_BOOL[0] == 1:
            TITLE_EXTRACT_BUTTONS = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("● AUTOMATIC",callback_data="set_auto_title")],
                    [InlineKeyboardButton("MANUAL",callback_data="set_man_title")],
                    [InlineKeyboardButton("Back",callback_data="back_settings")]
                ]
            )
        else:
            TITLE_EXTRACT_BUTTONS = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("AUTOMATIC",callback_data="set_auto_title")],
                    [InlineKeyboardButton("● MANUAL",callback_data="set_man_title")],
                    [InlineKeyboardButton("Back",callback_data="back_settings")]
                ]
            )
        await callback_query.edit_message_text(
            TITLE_EXTRACT_TEXT,
            reply_markup = TITLE_EXTRACT_BUTTONS
        )
    elif callback_query.data == "back_settings":
        await callback_query.edit_message_text(
            SETTINGS_TEXT,
            reply_markup = SETTINGS_BUTTONS
        )
    elif callback_query.data == "set_auto_title":
        _message = callback_query.message
        chat_id = _message.chat.id
        TITLE_EXTRACT_TEXT = "Title Modes:\n\n\tAutomatic : Title is taken from the Experiment Details \n\n\tMANUAL : Title needs to be given by the user to the bot\n\n\tYou Have Selected Automatic Mode."
        TITLE_EXTRACT_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("● AUTOMATIC",callback_data="set_auto_title")],
                [InlineKeyboardButton("MANUAL",callback_data="set_man_title")],
                [InlineKeyboardButton("Save Changes",callback_data="save_changes_settings")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await user_settings.set_extract_title_as_true(chat_id)
        await callback_query.edit_message_text(
                TITLE_EXTRACT_TEXT,
                reply_markup = TITLE_EXTRACT_BUTTONS
        )
    elif callback_query.data == "set_man_title":
        _message = callback_query.message
        chat_id = _message.chat.id
        TITLE_EXTRACT_TEXT = "Title Modes:\n\n\tAutomatic : Title is taken from the Experiment Details \n\n\tMANUAL : Title needs to be given by the user to the bot\n\n\tYou Have Selected Manual Mode."
        TITLE_EXTRACT_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("AUTOMATIC",callback_data="set_auto_title")],
                [InlineKeyboardButton("● MANUAL",callback_data="set_man_title")],
                [InlineKeyboardButton("Save Changes",callback_data="save_changes_settings")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await user_settings.set_extract_title_as_false(chat_id)
        await callback_query.edit_message_text(
                TITLE_EXTRACT_TEXT,
                reply_markup = TITLE_EXTRACT_BUTTONS
        )
    elif callback_query.data == "ui":
        _message = callback_query.message
        chat_id = _message.chat.id
        current_ui = await user_settings.fetch_ui_bool(chat_id)
        USERINTERFACE_TEXT = "Switch effortlessly between traditional and updated UI for a refreshed experience.\n\n Customize your view with just a click!"    
        # "Switch effortlessly between traditional and updated UI for a refreshed experience. Customize your view with just a click!" 
        if current_ui[0] == 0:
            traditional_ui = "Traditional"
            updated_ui = "● Updated"
        elif current_ui[0] == 1:
            traditional_ui = "● Traditional"
            updated_ui = "Updated"
        USERINTERFACE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(traditional_ui,callback_data="traditional_set_ui")],
                [InlineKeyboardButton(updated_ui,callback_data="updated_set_ui")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await callback_query.edit_message_text(
            USERINTERFACE_TEXT,
            reply_markup = USERINTERFACE_BUTTONS
        )
    elif "set_ui" in callback_query.data:
        _message = callback_query.message
        chat_id = _message.chat.id
        query = callback_query.data.split("_")[0]
        if query == "traditional":
            await user_settings.set_traditional_ui_true(chat_id)
        if query == "updated":
            await user_settings.set_traditional_ui_as_false(chat_id)
        current_ui = await user_settings.fetch_ui_bool(chat_id)
        if current_ui[0] == 0:
            traditional_ui = "Traditional"
            updated_ui = "● Updated"
            USERINTERFACE_TEXT = f"""
UPDATED UI : 

```biometric
⫷

● Total Days             -  50
                    
● Days Present           -  41  
                
● Days Absent            -  9
                    
● Biometric %            -  82.0

● Biometric % (6h gap)   -  70.0

⫸

@iare_unofficial_bot

```"""
        elif current_ui[0] == 1:
            traditional_ui = "● Traditional"
            updated_ui = "Updated"
            USERINTERFACE_TEXT = f"""
TRADITIONAL UI :

BIOMETRIC

⫷
● Total Days                     -  50
                                        
● Days Present                -  41  

● Days Absent                  -  9

● Biometric %                   -  82.0

● Biometric % (6h gap)   -  70.0

⫸"""
        USERINTERFACE_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(traditional_ui,callback_data="traditional_set_ui")],
                [InlineKeyboardButton(updated_ui,callback_data="updated_set_ui")],
                [InlineKeyboardButton("Save Changes",callback_data="save_changes_settings")],
                [InlineKeyboardButton("Back",callback_data="back_settings")]
            ]
        )
        await callback_query.edit_message_text(
            USERINTERFACE_TEXT,
            reply_markup = USERINTERFACE_BUTTONS
        )

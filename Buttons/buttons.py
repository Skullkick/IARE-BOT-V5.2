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

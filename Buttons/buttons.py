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

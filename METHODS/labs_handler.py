from pyrogram import filters
import os
from time import sleep
# from DATABASE import tdatabase,pgdatabase
import os
from DATABASE import tdatabase
from Buttons import buttons
from METHODS import lab_operations


PDF_MESSAGE = f"""
```PDF STATUS
STATUS : Receiving
```
"""


async def download_pdf(bot, message,pdf_compress_scrape):
    chat_id = message.chat.id
    download_folder = "pdfs"
    if pdf_compress_scrape is True:
        allowable_size = 125
    else:
        allowable_size = 10
    # Checks the Status
    status = await tdatabase.fetch_pdf_status(chat_id)
    # If the status is recieve then only it recieves the pdf.
    if status is None:
        return
    if int(status) == 1:
        # Checks if the message is document or not.
        if message.document:
            mime_type = message.document.mime_type
            if mime_type == "application/pdf":
                # If download_folder does not exist then it creates a directory
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)
                # Message Receiving the PDF.
                message_in_receive = await bot.send_message(chat_id,PDF_MESSAGE)
                # Download the PDF file with progress callback
                await message.download(
                    file_name=os.path.join(download_folder, f"C-{chat_id}.pdf"),
                )
                # Send a completion message
                RECEIVED_PDF_MSG = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : Checking.
```
"""
                # Message After Receiving the PDF.
                message_after_recieve = await bot.edit_message_text(chat_id,message_in_receive.id, RECEIVED_PDF_MSG)
                # check_pdf_size returns 2 values whether the pdf is above 10mb or not and size of pdf
                check ,size = await check_pdf_size(chat_id,allowable_size)
                if check is True:
                    PDF_ABOVE_ALLOWED_SIZE_DELETED = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : {size} MB.

The PDF file exceeds the allowable size limit of {allowable_size}MB and has been deleted.

Please resend a PDF file that is under {allowable_size}MB.

```
"""
                    PDF_ABOVE_ALLOWED_SIZE_ERROR_DELETE = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : {size} MB.

The PDF file exceeds the allowable size limit of {allowable_size}MB.

Error Deleting the PDF.

Please resend a PDF file that is under{allowable_size}MB.

```
"""
                    if await remove_pdf_file(bot,chat_id) is True:
                        await bot.edit_message_text(
                            chat_id,
                            message_after_recieve.id,
                            PDF_ABOVE_ALLOWED_SIZE_DELETED)
                    else:
                        await bot.edit_message_text(
                            chat_id,
                            message_after_recieve.id,
                            PDF_ABOVE_ALLOWED_SIZE_ERROR_DELETE)
                    
                else:
                    LESS_THAN_ALLOWED_SIZE = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : {size} MB.

```                    
"""
                    # Remove the Status of pdf.
                    await tdatabase.delete_pdf_status_info(chat_id)   
                    await bot.edit_message_text(chat_id,message_after_recieve.id,LESS_THAN_ALLOWED_SIZE)
                    await initialize_lab_upload(bot,message)
            else:
                await bot.send_message(chat_id, "This File type is not supported.")

async def initialize_lab_upload(bot,message):
    """
    This function is used to know the status of pdf and the title
    
    :param chat_id: Chat id of the user
    """
    chat_id = message.chat.id
    pdf_present,pdf_comp = await check_recieved_pdf_file(bot,chat_id)
    title = await tdatabase.fetch_title_lab_info(chat_id)
    if title is None:
        await bot.send_message(chat_id,"Send the title in the appropriate format.")
        return
    if pdf_present is False:
        await bot.send_message(chat_id,"● Send the PDF File")
        return
    if title and pdf_present is True:
        title,subject_code,week_no = await tdatabase.fetch_required_lab_info(chat_id)
        await lab_operations.upload_lab_record(bot,message,title=title,subject_code=subject_code,week_no=week_no)

async def rename_to_upload_pdf(pdf_path,chat_id,week_no):
    session_data = await tdatabase.load_user_session(chat_id)
    username = session_data['username'][:10].upper()
    pdf_folder = "pdfs"
    pdf_file_name = f"{username}_week{week_no}.pdf"
    updated_path_to_rename = os.path.join(pdf_folder,pdf_file_name)
    os.rename(pdf_path,updated_path_to_rename)
    updated_pdf_path = os.path.abspath(updated_path_to_rename)
    return pdf_file_name,updated_pdf_path

async def check_pdf_size(chat_id,allowed_size):
        """This Function checks whether the pdf file is above allowed pdf size or not,
        If the file is above 1mb then it returns true and the file size ."""
        file_size= os.path.getsize(os.path.abspath(f"pdfs/C-{chat_id}.pdf"))
        file_size_mb = round((file_size/(1024*1024)),3)
        if file_size_mb > allowed_size:
            return True, file_size_mb
        else:
            return False, file_size_mb

async def check_pdf_size_above_1mb(chat_id):
        """This Function checks whether the pdf file is above 1 mb or not,
        If the file is above 1mb then it returns true and the file size ."""
        print("started checking pdf size")
        file_size= os.path.getsize(os.path.abspath(f"pdfs/C-{chat_id}.pdf"))
        file_size_mb = round((file_size/(1024*1024)),3)
        if file_size_mb > 1:
            print("check done")
            return True
        else:
            print("Check done")
            return False


async def check_pdf_size_after_compression(chat_id):
        """This Function checks whether the compressed pdf file is above 1mb or not,
        If the file is above 1mb then it returns true and the file size .
        :return: If the file size is above 1 mb then it returns True, Else it returns false"""
        file_size = os.path.getsize(os.path.abspath(f"pdfs/C-{chat_id}-comp.pdf"))
        file_size_mb = round((file_size/(1024*1024)),3)
        if file_size_mb > 1:
            return True, file_size_mb
        else:
            return False, file_size_mb

async def get_pdf_size(bot,chat_id):
    """
    This Function is used to get the PDF size in mb.
    
    :param chat_id: Chat id of the user
    """
    pdf_folder = "pdfs"
    check_present , check_compress = await check_recieved_pdf_file(bot,chat_id)
    if check_present and check_compress:
        pdf_location = os.path.join(pdf_folder, f"C-{chat_id}-comp.pdf")
    elif check_present and not check_compress:
        pdf_location = os.path.join(pdf_folder, f"C-{chat_id}.pdf")
    pdf_size = os.path.getsize(os.path.abspath(pdf_location))
    pdf_size_in_mb = round(pdf_size/(1024*1024),2)
    return pdf_size_in_mb


async def get_title_from_user(bot, message):
    """This Function Gets the title from the message that user has sent."""
    print("recieved message")
    chat_id = message.chat.id
    # Checks the status
    status = await tdatabase.fetch_title_status(chat_id)
    # if the status is recieve then only it receives the text.
    if status is None:
        return
    if int(status) == 1:
        messages = message.text
        chat_id = message.chat.id
        if "TITLE" in messages.upper() and ":" in messages.upper():
            parts = messages.split(":")
            # Extract the title part (excluding "TITLE" if present)
            title = parts[-1].strip()
            if title:
                await bot.send_message(chat_id,f"The title you provided is :\n{title}")
                # Stores the title in temporary labupload database.
                await tdatabase.store_title(chat_id,title=title)
                # Deletes the Status so that next title cannot be sent again directly.
                await tdatabase.delete_title_status_info(chat_id)
            await initialize_lab_upload(bot,message)

async def remove_pdf_file(bot,chat_id):
    """This function retreive the file is present or not and compressed or not from the check_recieved_pdf_file function,
    Based on that result it deletes the pdf file"""
    pdf_folder = "pdfs"
    check_present , check_compress = await check_recieved_pdf_file(bot,chat_id)
    if check_present and check_compress:
        pdf_location = os.path.join(pdf_folder, f"C-{chat_id}-comp.pdf")
    elif check_present and not check_compress:
        pdf_location = os.path.join(pdf_folder, f"C-{chat_id}.pdf")
    else:
        # If neither present nor compress, no action needed
        return False

    pdf_location_path = os.path.abspath(pdf_location)
    
    try:
        os.remove(pdf_location_path)
        return True
    except OSError as e:
        await bot.send_message(chat_id,f"Error deleting pdf : {e}")
        return False

async def check_recieved_pdf_file(bot,chat_id):
    """This Function Can be used to check whether the file is present or not,
    and Whether the current pdf file is compressed or not.
    
    :return: Boolean_1,Boolean_2 
    :Boolean_1: File is present or not.
    :Boolean_2: File is compressed or not."""
    pdf_folder = "pdfs"
    pdf_folder = os.path.abspath(pdf_folder)
    file_name = f"C-{chat_id}.pdf"
    file_name_compressed = f"C-{chat_id}-comp.pdf"
    # Checks if the directory is present or not
    try:
        all_pdf_files = os.listdir(pdf_folder)
    except:
        return False,None
    try:
        # Checks if the Normal pdf is present in the directory and returns
        # indicating it as uncompressed file
        if file_name in all_pdf_files:
            return True, False
        elif file_name_compressed in all_pdf_files:
            return True, True
        else:
            return False, None
    except Exception as e:
        await bot.send_message(chat_id,f"There is an error finding pdf : {e}")





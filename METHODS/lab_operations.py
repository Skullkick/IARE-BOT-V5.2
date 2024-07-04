import os
import tempfile
import logging
from PIL import Image
from pdf2image import convert_from_path
from METHODS import labs_handler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


use_pdf_compress_scrape = True


async def compress_pdf_scrape(bot,message):

    download_wait_time = 120  # Maximum time to wait for the download to complete
    extension_folder = "EXTENSION"
    ublock_file = "ublock.crx"
    ublock_path = os.path.join(extension_folder,ublock_file)
    ublock_complete_path = os.path.abspath(ublock_path)
    ublock_crx_path = ublock_complete_path#r"D:\BOT -Adding Compression\EXTENSION\ublock.crx"  # Update this to the path of your uBlock Origin .crx file
    chat_id = message.chat.id
    check_file = await labs_handler.check_recieved_pdf_file(bot, chat_id)
    pdf_folder = "pdfs"
    pdf_file_folder = os.path.join(pdf_folder, f"C-{chat_id}.pdf")
    if check_file[0] is True and check_file[1] is False:
        input_path = os.path.abspath(pdf_file_folder)
    elif check_file[0] is False:
        await bot.send_message(chat_id, "PDF file is not present.")
        return
    elif check_file[0] is True and check_file[1] is True:
        await bot.send_message(chat_id, "PDF file is already compressed.")
        return
    output_path = os.path.abspath(pdf_folder)
    download_dir = output_path

    # Chrome options
    options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.notifications": 2  # Disable notifications
    }
    options.add_experimental_option("prefs", prefs)

    # Run in headless mode and disable GPU
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    options.add_extension(ublock_crx_path)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
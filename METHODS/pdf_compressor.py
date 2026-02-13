"""
PDF compression utilities for lab report workflows.

This module provides two approaches for compressing user-submitted PDF files:

- A headless browser scraping workflow that uploads the PDF to an online
    compressor (disabled by default via `use_pdf_compress_scrape`).
- A fully local fallback that rasterizes PDF pages to images, compresses them,
    and reassembles a compact PDF.

Integrations and side effects:
- Reads and writes files in the `pdfs` folder using the pattern `C-<chat_id>.pdf`
    for original files and `C-<chat_id>-comp.pdf` for compressed output.
- Communicates status to users through the provided bot instance.
- Uses Selenium with a bundled uBlock extension to reduce page noise in the
    scraping pathway.

All public functions aim to be non-intrusive to the rest of the bot codebase and
report clear success/failure with actionable messages.
"""

import os,sys,stat,uuid
import tempfile
import logging
import time
from METHODS import labs_handler
from PIL import Image
from pdf2image import convert_from_path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

use_pdf_compress_scrape = False

async def compress_pdf_scrape(bot, message):
    """Compress a PDF via a headless browser using an online service.
    This async routine automates a Chromium instance to upload the user's PDF
    to BigPDF (11zon) and iteratively tries multiple compression levels until
    the resulting size drops below 1 MB, then downloads the compressed file.
    Behavior and side effects:
    - Checks for the expected input file `pdfs/C-<chat_id>.pdf` and whether a
        compressed variant already exists.
    - Sends status updates to the user via `bot.send_message`.
    - Writes the compressed file to `pdfs/C-<chat_id>-comp.pdf` and removes the
        original file when successful.
    - Runs Chrome in headless mode and installs a local uBlock extension to
        minimize popups and ads.
    Args:
            bot: A bot/client instance capable of `send_message(chat_id, text)`.
            message: An incoming message object providing `chat.id`.
    Returns:
            tuple[bool, str]:
                    - True, success_message when a compressed file is produced and
                        saved.
                    - False, error_message when the input is missing, already compressed,
                        or compression fails to reach the target size.
    Raises:
            No exception is intentionally propagated; unexpected errors are caught
            and returned in the message while yielding `(False, <details>)`.
    """
    try:
        download_wait_time = 120  # Maximum time to wait for the download to complete
        extension_folder = "EXTENSION"
        ublock_file = "ublock.crx"
        ublock_path = os.path.join(extension_folder, ublock_file)
        ublock_crx_path = os.path.abspath(ublock_path)

        chat_id = message.chat.id
        check_file = await labs_handler.check_recieved_pdf_file(bot, chat_id)
        pdf_folder = "pdfs"
        pdf_file_folder = os.path.join(pdf_folder, f"C-{chat_id}.pdf")

        if check_file[0] is True and check_file[1] is False:
            input_path = os.path.abspath(pdf_file_folder)
        elif check_file[0] is False:
            await bot.send_message(chat_id, "PDF file is not present.")
            return False, "PDF file is not present."
        elif check_file[0] is True and check_file[1] is True:
            await bot.send_message(chat_id, "PDF file is already compressed.")
            return True, f"PDF file for chat_id {chat_id} is already compressed."

        output_path = os.path.join(pdf_folder, f"C-{chat_id}-comp.pdf")
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
        options.add_argument("--no-sandbox")
        options.add_extension(ublock_crx_path)

        # Initialize WebDriver
        driver_path = ChromeDriverManager().install()
        if not os.path.basename(driver_path).startswith("chromedriver"):
            driver_dir = os.path.dirname(driver_path)
            exe_name = "chromedriver.exe" if sys.platform.startswith("win") else "chromedriver"
            driver_path = os.path.join(driver_dir, exe_name)
        if sys.platform.startswith("linux"):
            os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IEXEC)
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        def rename_downloaded_file(download_directory, chat_id):
            """Rename the downloaded PDF to the expected compressed filename.

            This helper looks for the file pattern created by the 11zon site
            ("C-<chat_id>_11zon.pdf"), removes any pre-existing compressed file,
            and renames the fresh download to "C-<chat_id>-comp.pdf". It also
            removes the original uncompressed file once the rename completes.

            Args:
                download_directory (str): Absolute path where the file was
                    downloaded.
                chat_id (int | str): The user's chat identifier used in the
                    naming convention.

            Returns:
                None

            Notes:
                All filesystem errors are caught and logged to stdout to avoid
                interrupting the outer compression flow.
            """
            try:
                pdf_folder = "pdfs"
                pdf_folder = os.path.abspath(pdf_folder)
                file_name_compressed = f"C-{chat_id}-comp.pdf"
                all_pdf_files = os.listdir(pdf_folder)
                
                if file_name_compressed in all_pdf_files:
                    pdf_path = os.path.join(pdf_folder, file_name_compressed)
                    os.remove(os.path.abspath(pdf_path))
                
                compressed_file_downloaded_path = os.path.join(download_directory, f"C-{chat_id}_11zon.pdf")
                rename_compressed_file_path = os.path.join(download_directory, f"C-{chat_id}-comp.pdf")
                os.rename(compressed_file_downloaded_path, rename_compressed_file_path)
                
                normal_filename = f"C-{chat_id}.pdf"
                old_pdf_location = os.path.join(pdf_folder, normal_filename)
                os.remove(os.path.abspath(old_pdf_location))
                print(f"File {compressed_file_downloaded_path} renamed to {rename_compressed_file_path}")
            except Exception as e:
                print(f"Error renaming downloaded file: {str(e)}")

        try:
            # Navigate to the website
            driver.get("https://bigpdf.11zon.com/en/compress-pdf")

            # Close the popup (if any)
            try:
                close_popup_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.ID, "zon-donation-popup-close"))
                )
                close_popup_button.click()
            except Exception as e:
                print(f"No popup found or failed to close popup: {str(e)}")

            # Upload the PDF file
            driver.execute_script(f"document.querySelector('input[type=file]').setAttribute('style', 'display: block');")
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type=file]")
            file_input.send_keys(input_path)
            time.sleep(2)  # Wait for file to be uploaded

            # Iterate over compression levels
            compression_levels_to_try = [60, 70, 80, 90, 100]
            successful_compression = False
            new_filename = f"C-{chat_id}-comp.pdf"

            for compression_level in compression_levels_to_try:
                try:
                    # Set the compression level using the slider
                    driver.execute_script(f"document.getElementById('compress-range').value = {compression_level};")
                    time.sleep(1)  # Wait for the slider to update

                    # Click the "Compress" button
                    compress_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "apply-button"))
                    )
                    compress_button.click()

                    # Wait for compression to complete
                    time.sleep(8)

                    # Check the new size after compression
                    new_size_element = WebDriverWait(driver, 1).until(
                        EC.visibility_of_element_located((By.ID, "zon-bottom-txt-cl0"))
                    )
                    new_size_text = new_size_element.text
                    if "KB" in new_size_text:
                        new_size_kb = float(new_size_text.split()[2])
                        new_size_mb = new_size_kb / 1024
                    elif "MB" in new_size_text:
                        new_size_mb = float(new_size_text.split()[2])

                    print(f"Compression at {compression_level}% resulted in file size: {new_size_mb:.2f} MB")

                    # Check if size is below 1 MB
                    if new_size_mb < 1:
                        print(f"Compression successful. Final file size: {new_size_mb:.2f} MB")

                        download_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "zon-download-cbtn0"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                        try:
                            download_button.click()
                        except Exception as e:
                            print(f"Direct click failed, using JavaScript click due to: {str(e)}")
                            driver.execute_script("arguments[0].click();", download_button)
                        time.sleep(1)  # Wait for download to start

                        # Rename the downloaded file
                        rename_downloaded_file(download_dir, chat_id)
                        return True, f"Compressed file {new_filename} is available in the directory: {download_dir}"

                except Exception as ex:
                    print(f"Error during compression at {compression_level}%")

            print("Unable to compress PDF below 1 MB even at maximum compression.")
            return False, "Unable to compress PDF below 1 MB even at maximum compression."

        finally:
            # Close the browser
            driver.quit()

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False, f"An unexpected error occurred: {str(e)}"

def pdf_image_generator(input_path):
    """Yield PIL images converted from a PDF file path.

    This generator streams each page of the PDF as a `PIL.Image.Image` using
    `pdf2image.convert_from_path`, which helps keep memory usage bounded for
    large documents.

    Args:
        input_path (str): Absolute path to the input PDF.

    Yields:
        PIL.Image.Image: The next page converted to an RGB image.

    Raises:
        Exceptions from `convert_from_path` are caught and logged, and the
        generator terminates early.
    """
    try:
        for img in convert_from_path(input_path):
            yield img
    except Exception as e:
        print(f"Error in pdf image generator : {e}")

async def compress_pdf(bot, chat_id, batch_size: int = 1) -> bool:
    """Compress a PDF locally by rasterizing pages and recombining.

    The local fallback workflow converts each page of the user's PDF into a
    JPEG image with reduced dimensions and quality, then assembles the images
    back into a single PDF. This approach does not rely on any external web
    service and works offline.

    Behavior and side effects:
    - Validates the presence of `pdfs/C-<chat_id>.pdf` and whether a compressed
      file already exists.
    - Sends status messages to the user via `bot.send_message` in early exit
      cases.
    - On success, writes `pdfs/C-<chat_id>-comp.pdf` and removes the original
      input PDF.

    Args:
        bot: A bot/client instance used for user notifications.
        chat_id (int | str): Identifier used to resolve file locations and send
            messages.
        batch_size (int, optional): Reserved for future batching improvements;
            currently unused. Default is 1.

    Returns:
        bool: True if compression succeeded and the compressed file was saved;
        False otherwise.

    Raises:
        No exceptions are propagated; unexpected errors are caught and logged,
        and the function returns False.
    """
    
    try:
        # Check whether the PDF is present or not
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
        output_path = os.path.join(pdf_folder, f"C-{chat_id}-comp.pdf")
        
        # Create a temporary directory to store compressed images
        with tempfile.TemporaryDirectory() as temp_dir:
            compressed_image_paths = []

            for i, img in enumerate(pdf_image_generator(input_path)):
                # Process images sequentially
                compressed_img_path = os.path.join(temp_dir, f"page_{i}.jpg")
                img = img.convert("RGB")
                img.thumbnail((img.width / 2, img.height / 2))
                img.save(compressed_img_path, "JPEG", quality=50)
                compressed_image_paths.append(compressed_img_path)
                
            # Compile all compressed images into a single PDF
            await compile_and_save_pdf_batch(compressed_image_paths, output_path)
                
        print(f"compressed successfully to: {output_path}")
        await labs_handler.remove_pdf_file(bot,chat_id)
        return True

    except Exception as error:
        print(f"Error: {error}")
        return False

async def compile_and_save_pdf_batch(image_paths: list, output_path: str):
    """Compile a batch of images into a single PDF file.

    Opens the provided image paths with Pillow and saves them into a single PDF
    at the requested `output_path`.

    Args:
        image_paths (list[str]): File paths to images ordered by page index.
        output_path (str): Target path for the resulting PDF.

    Returns:
        None

    Raises:
        Any unexpected Pillow-related errors are caught and logged; the
        function does not raise.
    """
    try:
        images = [Image.open(img_path) for img_path in image_paths]
        images[0].save(output_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
    except Exception as error:
        print(f"Error compiling PDF batch: {error}")



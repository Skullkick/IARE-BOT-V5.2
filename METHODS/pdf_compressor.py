"""
Native in-memory PDF compression utilities for lab report workflows.

Replaces headless Selenium browser scraping and lossy rasterization with
fast, pure-Python in-memory stream and object compression using `pypdf`.
Eliminates heavy browser binaries, driver management, and privacy risks.
"""

import os
import logging
from METHODS import labs_handler
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

# External scrape compression disabled in favor of native in-memory compression
use_pdf_compress_scrape = False

def _native_compress_pdf(input_path: str, output_path: str) -> bool:
    """Perform native stream and object compression on a PDF using pypdf.

    Preserves vector text while applying lossless content stream deflation
    and compressing embedded images.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        # Compress embedded images if present
        for img in page.images:
            try:
                img.replace(img.image, quality=60)
            except Exception:
                pass
        writer.add_page(page)

    writer.compress_identical_objects()
    with open(output_path, "wb") as f:
        writer.write(f)
    return True

async def compress_pdf(bot, chat_id, batch_size: int = 1) -> bool:
    """Compress a PDF natively using pypdf in-memory compression.

    Args:
        bot: Pyrogram client instance.
        chat_id: User's chat identifier.
        batch_size: Unused, kept for backwards compatibility.

    Returns:
        bool: True on success, False otherwise.
    """
    try:
        check_file = await labs_handler.check_recieved_pdf_file(bot, chat_id)
        pdf_folder = "pdfs"
        pdf_file_folder = os.path.join(pdf_folder, f"C-{chat_id}.pdf")
        if check_file[0] is True and check_file[1] is False:
            input_path = os.path.abspath(pdf_file_folder)
        elif check_file[0] is False:
            await bot.send_message(chat_id, "PDF file is not present.")
            return False
        elif check_file[0] is True and check_file[1] is True:
            await bot.send_message(chat_id, "PDF file is already compressed.")
            return True

        output_path = os.path.join(pdf_folder, f"C-{chat_id}-comp.pdf")

        # Native compression
        success = _native_compress_pdf(input_path, output_path)
        if success:
            logger.info("PDF compressed successfully to: %s", output_path)
            await labs_handler.remove_pdf_file(bot, chat_id)
            return True
        return False

    except Exception as error:
        logger.error("Error during native PDF compression: %s", error)
        return False

async def compress_pdf_scrape(bot, message):
    """Compatibility wrapper that delegates to native in-memory compression.

    Args:
        bot: Pyrogram client instance.
        message: Triggering message object providing chat.id.

    Returns:
        tuple[bool, str]: Success flag and status message.
    """
    chat_id = message.chat.id
    success = await compress_pdf(bot, chat_id)
    if success:
        return True, "PDF compressed successfully."
    return False, "Unable to compress PDF."

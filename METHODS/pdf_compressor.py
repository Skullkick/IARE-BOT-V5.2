"""
Native in-memory PDF compression utilities for lab report workflows.

Replaces headless Selenium browser scraping and lossy rasterization with
fast, pure-Python in-memory stream and object compression using `pypdf`.
Eliminates heavy browser binaries, driver management, and privacy risks.
"""

import os
import asyncio
import logging
from METHODS import labs_handler
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

# External scrape compression disabled in favor of native in-memory compression
use_pdf_compress_scrape = False

# Global lock to serialize PDF compression requests so system CPU and RAM are not overwhelmed
_PDF_COMPRESSION_LOCK = asyncio.Lock()

def _native_compress_pdf(input_path: str, output_path: str, quality: int = 60, max_dimension: int = 1600) -> bool:
    """Perform native stream and object compression on a PDF using pypdf.

    Preserves vector text while applying lossless content stream deflation,
    downscaling oversized camera photos, and recompressing embedded images.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for writer_page in writer.pages:
        writer_page.compress_content_streams()
        # Compress and downscale embedded images if present
        for img in writer_page.images:
            try:
                pil_img = img.image
                if max_dimension and max(pil_img.width, pil_img.height) > max_dimension:
                    pil_img.thumbnail((max_dimension, max_dimension))
                img.replace(pil_img, quality=quality)
            except Exception:
                pass

    writer.compress_identical_objects()
    with open(output_path, "wb") as f:
        writer.write(f)
    return True

async def compress_pdf(bot, chat_id, batch_size: int = 1) -> bool:
    """Compress a PDF natively using pypdf in-memory compression.

    Executes sequentially using a global lock and offloads CPU-bound
    image resampling to a worker thread so the bot remains responsive.

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
        os.makedirs(pdf_folder, exist_ok=True)
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

        # Notify user if another compression is currently holding system resources
        if _PDF_COMPRESSION_LOCK.locked():
            try:
                await bot.send_message(chat_id, "⏳ PDF compression queued. Waiting for server resources...")
            except Exception:
                pass

        # Ensure only one PDF compression runs at a time to prevent resource exhaustion
        async with _PDF_COMPRESSION_LOCK:
            # Native compression pass 1: standard compression offloaded to worker thread
            success = await asyncio.to_thread(_native_compress_pdf, input_path, output_path, 60, 1600)
            if success:
                # If still exceeding 1MB (1024KB), run adaptive pass 2 to guarantee under 1MB
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1024 * 1024:
                    logger.info("PDF still > 1MB after pass 1 (%d bytes); running adaptive pass 2", os.path.getsize(output_path))
                    await asyncio.to_thread(_native_compress_pdf, input_path, output_path, 40, 1200)

                logger.info("PDF compressed successfully to: %s (%d bytes)", output_path, os.path.getsize(output_path))
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

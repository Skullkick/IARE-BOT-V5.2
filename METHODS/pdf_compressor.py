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

# Metrics registry for last compression executed per chat_id
_COMPRESSION_METRICS: dict[str, dict] = {}

def get_compression_metrics(chat_id: int | str) -> dict:
    """Retrieve compression metrics for the given chat_id."""
    return _COMPRESSION_METRICS.get(str(chat_id), {})

def clear_compression_metrics(chat_id: int | str) -> None:
    """Clear compression metrics for the given chat_id."""
    _COMPRESSION_METRICS.pop(str(chat_id), None)

# Progressive compression tiers ordered from highest quality (lightest) to highest compression
COMPRESSION_TIERS = [
    # Tier 0: High visual fidelity (for files <= 2.5 MB)
    {"quality": 75, "max_dimension": 1600, "grayscale": False},
    # Tier 1: Balanced compression (for files 2.5 MB - 6 MB)
    {"quality": 60, "max_dimension": 1300, "grayscale": False},
    # Tier 2: Strong compression (for files 6 MB - 12 MB)
    {"quality": 45, "max_dimension": 1000, "grayscale": False},
    # Tier 3: Aggressive compression (for files > 12 MB)
    {"quality": 35, "max_dimension": 800, "grayscale": False},
    # Tier 4: Maximum emergency compression with grayscale (for massive scanned files)
    {"quality": 25, "max_dimension": 650, "grayscale": True},
]

def select_initial_tier_index(file_size_bytes: int) -> int:
    """Select the initial compression tier based on input PDF file size.

    Args:
        file_size_bytes: Size of the input PDF in bytes.

    Returns:
        int: Index of the starting tier in COMPRESSION_TIERS.
    """
    mb = file_size_bytes / (1024 * 1024)
    if mb <= 2.5:
        return 0
    elif mb <= 6.0:
        return 1
    elif mb <= 12.0:
        return 2
    else:
        return 3

def _native_compress_pdf(
    input_path: str,
    output_path: str,
    quality: int = 60,
    max_dimension: int = 1600,
    grayscale: bool = False,
) -> bool:
    """Perform native stream and object compression on a PDF using pypdf.

    Preserves vector text while applying lossless content stream deflation,
    downscaling oversized camera photos, and recompressing embedded images.

    Args:
        input_path: Path to source PDF file.
        output_path: Target path for the compressed PDF.
        quality: JPEG recompression quality factor (1-100).
        max_dimension: Maximum pixel width or height for embedded images.
        grayscale: Whether to convert color images to grayscale for maximum compression.

    Returns:
        bool: True on success, False otherwise.
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
                if grayscale and pil_img.mode != "L":
                    pil_img = pil_img.convert("L")
                elif not grayscale and pil_img.mode in ("RGBA", "P"):
                    pil_img = pil_img.convert("RGB")

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
    """Compress a PDF natively using dynamic multi-tier pypdf compression.

    Executes sequentially using a global lock, selects initial compression
    parameters based on the input PDF size, and dynamically retries with
    progressively higher compression if the output exceeds 1 MB.

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
            input_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
            start_tier_idx = select_initial_tier_index(input_size)
            logger.info(
                "Starting dynamic PDF compression for chat_id %s (size: %d bytes, initial tier: %d)",
                chat_id,
                input_size,
                start_tier_idx + 1,
            )

            produced_output = False

            # Dynamic progressive retry loop: escalate compression until under 1MB (1,048,576 bytes)
            for tier_idx in range(start_tier_idx, len(COMPRESSION_TIERS)):
                tier = COMPRESSION_TIERS[tier_idx]
                logger.info(
                    "Executing compression tier %d/%d (quality=%d, max_dim=%s, grayscale=%s)",
                    tier_idx + 1,
                    len(COMPRESSION_TIERS),
                    tier["quality"],
                    tier["max_dimension"],
                    tier["grayscale"],
                )

                pass_ok = await asyncio.to_thread(
                    _native_compress_pdf,
                    input_path,
                    output_path,
                    quality=tier["quality"],
                    max_dimension=tier["max_dimension"],
                    grayscale=tier["grayscale"],
                )

                if not pass_ok or not os.path.exists(output_path):
                    continue

                produced_output = True
                current_size = os.path.getsize(output_path)

                if current_size <= 1024 * 1024:
                    logger.info(
                        "PDF successfully compressed under 1MB at tier %d: %d bytes (%.2f KB)",
                        tier_idx + 1,
                        current_size,
                        current_size / 1024,
                    )
                    break
                else:
                    logger.info(
                        "PDF size %d bytes (%.2f KB) still exceeds 1MB threshold after tier %d. Retrying with higher compression...",
                        current_size,
                        current_size / 1024,
                        tier_idx + 1,
                    )

            if produced_output and os.path.exists(output_path):
                final_size = os.path.getsize(output_path)
                tier_used = COMPRESSION_TIERS[tier_idx]
                is_high = tier_idx >= 3 or bool(tier_used.get("grayscale")) or (input_size > 0 and (1 - final_size / input_size) >= 0.75)
                _COMPRESSION_METRICS[str(chat_id)] = {
                    "chat_id": chat_id,
                    "tier_index": tier_idx,
                    "quality": tier_used["quality"],
                    "max_dimension": tier_used["max_dimension"],
                    "grayscale": tier_used["grayscale"],
                    "initial_size": input_size,
                    "final_size": final_size,
                    "is_high_compression": is_high,
                }
                logger.info("PDF compressed successfully to: %s (%d bytes, is_high=%s)", output_path, final_size, is_high)
                # Remove uncompressed source PDF so only the compressed version remains for upload
                if os.path.exists(input_path):
                    try:
                        os.remove(input_path)
                    except Exception:
                        pass
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

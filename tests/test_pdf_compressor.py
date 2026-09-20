import os
import pytest
from pypdf import PdfWriter
from pypdf.errors import EmptyFileError, PdfReadError
from METHODS import pdf_compressor

@pytest.fixture
def sample_valid_pdf(tmp_path):
    """Generate a minimal valid PDF file for testing."""
    pdf_path = tmp_path / "valid.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

def test_native_compress_valid_pdf(sample_valid_pdf, tmp_path):
    """Verify valid PDF compression produces a readable compressed output."""
    out_path = str(tmp_path / "compressed.pdf")
    res = pdf_compressor._native_compress_pdf(sample_valid_pdf, out_path)
    assert res is True
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 0

def test_native_compress_zero_byte_file(tmp_path):
    """Verify zero-byte file handling in native compressor."""
    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(b"")
    out_path = str(tmp_path / "out.pdf")
    with pytest.raises((EmptyFileError, PdfReadError, Exception)):
        pdf_compressor._native_compress_pdf(str(empty_pdf), out_path)

def test_native_compress_corrupt_file(tmp_path):
    """Verify corrupted non-PDF file handling in native compressor."""
    corrupt_pdf = tmp_path / "corrupt.pdf"
    corrupt_pdf.write_bytes(b"NOT_A_REAL_PDF_HEADER_OR_CONTENT")
    out_path = str(tmp_path / "out.pdf")
    with pytest.raises((PdfReadError, Exception)):
        pdf_compressor._native_compress_pdf(str(corrupt_pdf), out_path)

def test_native_compress_nonexistent_file(tmp_path):
    """Verify non-existent input file raises FileNotFoundError."""
    non_existent = str(tmp_path / "non_existent.pdf")
    out_path = str(tmp_path / "out.pdf")
    with pytest.raises(FileNotFoundError):
        pdf_compressor._native_compress_pdf(non_existent, out_path)

async def test_compress_pdf_file_not_present(mock_bot, monkeypatch):
    """Verify compress_pdf gracefully reports when file is not present."""
    from METHODS import labs_handler
    async def mock_check(bot, chat_id):
        return False, None
    monkeypatch.setattr(labs_handler, "check_recieved_pdf_file", mock_check)
    
    success = await pdf_compressor.compress_pdf(mock_bot, chat_id=123)
    assert success is False
    mock_bot.send_message.assert_called_once_with(123, "PDF file is not present.")

async def test_compress_pdf_already_compressed(mock_bot, monkeypatch):
    """Verify compress_pdf acknowledges already compressed files."""
    from METHODS import labs_handler
    async def mock_check(bot, chat_id):
        return True, True
    monkeypatch.setattr(labs_handler, "check_recieved_pdf_file", mock_check)
    
    success = await pdf_compressor.compress_pdf(mock_bot, chat_id=123)
    assert success is True
    mock_bot.send_message.assert_called_once_with(123, "PDF file is already compressed.")

def test_native_compress_pdf_with_image_under_1mb(tmp_path):
    """Verify that a PDF containing a high-resolution image is compressed and remains under 1MB."""
    import io
    from PIL import Image

    # Create a 2000x2000 image and save as PDF
    img = Image.new("RGB", (2000, 2000), color=(120, 160, 220))
    for x in range(0, 2000, 40):
        for y in range(0, 2000, 40):
            img.putpixel((x, y), (255, 50, 50))

    in_pdf = tmp_path / "large_image.pdf"
    img.save(str(in_pdf), format="PDF", quality=100)
    original_size = os.path.getsize(str(in_pdf))

    out_pdf = tmp_path / "compressed_image.pdf"
    res = pdf_compressor._native_compress_pdf(str(in_pdf), str(out_pdf))

    assert res is True
    assert os.path.exists(str(out_pdf))
    compressed_size = os.path.getsize(str(out_pdf))

    # Must be significantly reduced and strictly under 1MB (1,048,576 bytes)
    assert compressed_size < original_size
    assert compressed_size < 1024 * 1024, f"Output PDF ({compressed_size} bytes) exceeds 1MB threshold!"

@pytest.mark.asyncio
async def test_compress_pdf_sequential_locking(mock_bot, monkeypatch):
    """Verify that multiple concurrent PDF compression requests run strictly in sequence."""
    import asyncio
    from METHODS import labs_handler

    active_compressions = 0
    max_concurrent = 0
    completed = []

    async def mock_check(bot, chat_id):
        return True, False

    async def mock_remove(bot, chat_id):
        return True

    def mock_native_compress(in_p, out_p, *args, **kwargs):
        nonlocal active_compressions, max_concurrent
        active_compressions += 1
        if active_compressions > max_concurrent:
            max_concurrent = active_compressions
        import time
        time.sleep(0.05)
        # Write dummy output
        with open(out_p, "wb") as f:
            f.write(b"%PDF-dummy")
        active_compressions -= 1
        return True

    monkeypatch.setattr(labs_handler, "check_recieved_pdf_file", mock_check)
    monkeypatch.setattr(labs_handler, "remove_pdf_file", mock_remove)
    monkeypatch.setattr(pdf_compressor, "_native_compress_pdf", mock_native_compress)

    async def run_compress(user_id):
        res = await pdf_compressor.compress_pdf(mock_bot, chat_id=user_id)
        completed.append(user_id)
        return res

    results = await asyncio.gather(run_compress(101), run_compress(102), run_compress(103))

    assert all(results)
    assert len(completed) == 3
    # Critical assertion: Concurrency must NEVER exceed 1 at any moment
    assert max_concurrent == 1, f"Expected strictly sequential execution, but max concurrency was {max_concurrent}"

def test_select_initial_tier_index():
    """Verify initial tier selection logic based on file size boundaries."""
    # <= 2.5 MB -> Tier 0
    assert pdf_compressor.select_initial_tier_index(int(1.5 * 1024 * 1024)) == 0
    assert pdf_compressor.select_initial_tier_index(int(2.5 * 1024 * 1024)) == 0
    # 2.5 MB - 6 MB -> Tier 1
    assert pdf_compressor.select_initial_tier_index(int(4.0 * 1024 * 1024)) == 1
    assert pdf_compressor.select_initial_tier_index(int(6.0 * 1024 * 1024)) == 1
    # 6 MB - 12 MB -> Tier 2
    assert pdf_compressor.select_initial_tier_index(int(8.0 * 1024 * 1024)) == 2
    assert pdf_compressor.select_initial_tier_index(int(12.0 * 1024 * 1024)) == 2
    # > 12 MB -> Tier 3
    assert pdf_compressor.select_initial_tier_index(int(15.0 * 1024 * 1024)) == 3

@pytest.mark.asyncio
async def test_compress_pdf_dynamic_retry_under_1mb(mock_bot, monkeypatch, tmp_path):
    """Verify that compress_pdf dynamically retries with higher compression when pass 1 exceeds 1MB."""
    from METHODS import labs_handler

    attempted_tiers = []

    async def mock_check(bot, chat_id):
        return True, False

    async def mock_remove(bot, chat_id):
        return True

    def mock_escalating_compress(in_p, out_p, quality=60, max_dimension=1600, grayscale=False):
        attempted_tiers.append({"quality": quality, "max_dimension": max_dimension, "grayscale": grayscale})
        # If first attempt, write a file that exceeds 1MB (e.g. 1.2 MB)
        # If second attempt, write a file under 1MB (e.g. 500 KB)
        with open(out_p, "wb") as f:
            if len(attempted_tiers) == 1:
                f.write(b"X" * (1200 * 1024))  # 1.2 MB (exceeds 1MB)
            else:
                f.write(b"X" * (500 * 1024))   # 500 KB (under 1MB)
        return True

    monkeypatch.setattr(labs_handler, "check_recieved_pdf_file", mock_check)
    monkeypatch.setattr(labs_handler, "remove_pdf_file", mock_remove)
    monkeypatch.setattr(pdf_compressor, "_native_compress_pdf", mock_escalating_compress)

    res = await pdf_compressor.compress_pdf(mock_bot, chat_id=999)

    assert res is True
    # Verify that it retried: exactly 2 attempts were executed
    assert len(attempted_tiers) == 2
    # Verify that attempt 2 used stronger compression (lower quality) than attempt 1
    assert attempted_tiers[1]["quality"] < attempted_tiers[0]["quality"]

def test_native_compress_pdf_grayscale(tmp_path):
    """Verify that _native_compress_pdf with grayscale=True produces a readable, compact PDF."""
    from PIL import Image

    img = Image.new("RGB", (600, 600), color=(200, 50, 50))
    in_pdf = tmp_path / "color_input.pdf"
    img.save(str(in_pdf), format="PDF")

    out_pdf = tmp_path / "grayscale_output.pdf"
    res = pdf_compressor._native_compress_pdf(
        str(in_pdf),
        str(out_pdf),
        quality=30,
        max_dimension=500,
        grayscale=True,
    )

    assert res is True
    assert os.path.exists(str(out_pdf))
    assert os.path.getsize(str(out_pdf)) > 0

@pytest.mark.asyncio
async def test_compression_metrics_tracking(mock_bot, monkeypatch):
    """Verify that get_compression_metrics records metrics and clear_compression_metrics purges them."""
    from METHODS import labs_handler

    async def mock_check(bot, chat_id):
        return True, False

    async def mock_remove(bot, chat_id):
        return True

    def mock_compress(in_p, out_p, *args, **kwargs):
        with open(out_p, "wb") as f:
            f.write(b"X" * (800 * 1024))
        return True

    monkeypatch.setattr(labs_handler, "check_recieved_pdf_file", mock_check)
    monkeypatch.setattr(labs_handler, "remove_pdf_file", mock_remove)
    monkeypatch.setattr(pdf_compressor, "_native_compress_pdf", mock_compress)

    pdf_compressor.clear_compression_metrics(888)
    res = await pdf_compressor.compress_pdf(mock_bot, chat_id=888)
    assert res is True

    metrics = pdf_compressor.get_compression_metrics(888)
    assert metrics != {}
    assert metrics["chat_id"] == 888
    assert "tier_index" in metrics
    assert "final_size" in metrics
    assert "is_high_compression" in metrics

    pdf_compressor.clear_compression_metrics(888)
    assert pdf_compressor.get_compression_metrics(888) == {}


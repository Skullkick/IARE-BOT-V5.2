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

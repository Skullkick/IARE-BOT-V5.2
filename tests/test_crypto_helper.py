import os
import pytest
from METHODS import crypto_helper

def test_crypto_encrypt_decrypt_roundtrip():
    """Verify plaintext passwords encrypt and decrypt back deterministically."""
    plain = "MySecretPassword123!@#"
    encrypted = crypto_helper.encrypt_password(plain)
    assert encrypted != plain
    assert crypto_helper.is_encrypted(encrypted)
    
    decrypted = crypto_helper.decrypt_password(encrypted)
    assert decrypted == plain

def test_crypto_empty_and_none_inputs():
    """Verify empty or None inputs return empty string gracefully."""
    assert crypto_helper.encrypt_password("") == ""
    assert crypto_helper.encrypt_password(None) == ""
    assert crypto_helper.decrypt_password("") == ""
    assert crypto_helper.decrypt_password(None) == ""

def test_crypto_no_double_encryption():
    """Verify an already encrypted token is not double-encrypted."""
    plain = "ValidPassword456"
    encrypted1 = crypto_helper.encrypt_password(plain)
    encrypted2 = crypto_helper.encrypt_password(encrypted1)
    assert encrypted1 == encrypted2

def test_crypto_legacy_plaintext_handling():
    """Verify legacy unencrypted passwords return as-is without raising errors."""
    legacy_plain = "legacy_plain_pass"
    decrypted = crypto_helper.decrypt_password(legacy_plain)
    assert decrypted == legacy_plain

def test_crypto_corrupted_token_handling():
    """Verify corrupted or invalid Fernet tokens fall back to raw string."""
    corrupted_token = "gAAAAAB" + "x" * 60  # Has prefix and length, but invalid base64/HMAC
    result = crypto_helper.decrypt_password(corrupted_token)
    assert result == corrupted_token

def test_crypto_unicode_and_special_characters():
    """Verify unicode, emoji, and boundary strings encrypt and decrypt properly."""
    special_text = "🔑P@sswørd!_1234_漢字_ñ"
    encrypted = crypto_helper.encrypt_password(special_text)
    assert crypto_helper.decrypt_password(encrypted) == special_text

def test_crypto_long_password():
    """Verify very long password strings are handled without truncation."""
    long_pass = "A" * 10000
    encrypted = crypto_helper.encrypt_password(long_pass)
    assert crypto_helper.decrypt_password(encrypted) == long_pass

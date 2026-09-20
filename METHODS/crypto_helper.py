"""
Cryptographic utilities for securing user credentials at rest.

This module provides symmetric encryption and decryption using Fernet (AES-128-CBC
with HMAC-SHA256). Passwords stored in PostgreSQL or SQLite are encrypted before
persisting and decrypted in memory only when performing an automated portal login.

Features:
- Encrypts plaintext passwords into authenticated Fernet tokens.
- Gracefully handles backward compatibility: if a legacy unencrypted password is
  encountered, it returns the plaintext without throwing an InvalidToken error.
- Fallback key derivation: if ENCRYPTION_KEY is not set in environment variables,
  derives a consistent fallback key from API_HASH/BOT_TOKEN to prevent runtime crashes.
"""

import os
import base64
import hashlib
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

def _get_fernet_instance() -> Fernet:
    """Initialize and return a Fernet cipher instance."""
    raw_key = os.environ.get("ENCRYPTION_KEY")
    if raw_key:
        try:
            return Fernet(raw_key.strip().encode())
        except Exception as e:
            logger.error("Invalid ENCRYPTION_KEY provided: %s. Using fallback key.", e)

    # Derive deterministic fallback key from available bot secrets if ENCRYPTION_KEY is unset
    seed = os.environ.get("API_HASH", "") + os.environ.get("BOT_TOKEN", "iare_bot_default_secret_seed")
    derived_key = base64.urlsafe_b64encode(hashlib.sha256(seed.encode()).digest())
    logger.warning("ENCRYPTION_KEY not set. Using derived fallback encryption key. "
                   "Set ENCRYPTION_KEY in environment variables for maximum security.")
    return Fernet(derived_key)

_fernet = _get_fernet_instance()

def encrypt_password(plain_password: str) -> str:
    """Encrypt a plaintext password into an authenticated Fernet token string.

    Args:
        plain_password: User password in cleartext.

    Returns:
        Fernet encrypted token as a string.
    """
    if not plain_password:
        return ""
    # If already encrypted (Fernet tokens start with gAAAAA), don't re-encrypt
    if plain_password.startswith("gAAAAA") and len(plain_password) > 50:
        return plain_password
    try:
        token = _fernet.encrypt(plain_password.encode("utf-8"))
        return token.decode("utf-8")
    except Exception as e:
        logger.error("Failed to encrypt password: %s", e)
        return plain_password

def is_encrypted(token: str) -> bool:
    """Return True if the provided string appears to be a Fernet encrypted token."""
    return bool(token and token.startswith("gAAAAA") and len(token) > 50)

def decrypt_password(cipher_or_plain: str) -> str:
    """Decrypt a Fernet token string back into the original plaintext password.

    Handles legacy plaintext gracefully: if the token is not a valid Fernet token,
    it returns the string as-is.

    Args:
        cipher_or_plain: The encrypted token or legacy plaintext string.

    Returns:
        The decrypted plaintext password.
    """
    if not cipher_or_plain:
        return ""
    # If not a Fernet token format, it's a legacy plaintext password
    if not (cipher_or_plain.startswith("gAAAAA") and len(cipher_or_plain) > 50):
        return cipher_or_plain
    try:
        decrypted_bytes = _fernet.decrypt(cipher_or_plain.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except (InvalidToken, Exception) as e:
        logger.warning("Fernet decryption failed (possible legacy plaintext or key change): %s", e)
        return cipher_or_plain

def generate_new_key() -> str:
    """Helper utility to generate a fresh base64 Fernet key."""
    return Fernet.generate_key().decode("utf-8")

"""
security.py
Password hashing (using Python's built-in hashlib with a salt - simple
enough to explain in a viva without external native-extension dependencies
like bcrypt) and JWT creation/verification using PyJWT.
"""
import hashlib
import hmac
import os
import datetime
from typing import Optional

import jwt

from config import settings


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random salt.
    Stored format: <salt_hex>$<hash_hex>"""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"{salt.hex()}${pwd_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return hmac.compare_digest(computed, expected)
    except Exception:
        return False


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

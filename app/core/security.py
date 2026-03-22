"""
Security helpers: password hashing and verification.
"""

from typing import Final

from passlib.context import CryptContext

# Recommended scheme: argon2. Requires argon2-cffi installed.
pwd_context: Final = CryptContext(schemes=["argon2"], deprecated="auto")

# Compute a dummy hash once to mitigate timing attacks when a user is not found
# or when a stored hash is malformed. Computing it at import time avoids
# repeated expensive allocations on each failed auth attempt.
DUMMY_HASH: Final[str] = pwd_context.hash("dummypassword")


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password.

    :param password: The plaintext password to hash.
    :return: The hashed password as a string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored hash.

    If verification raises (e.g. malformed hash), we perform a dummy verify to
    keep timing similar and return False.

    :param plain_password: The plaintext password to verify.
    :param hashed_password: The stored hashed password to compare against.
    :return: True if the password matches the hash, False otherwise.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Run verity against a dummy hash to make timing of failed attempts more uniform.
        try:
            pwd_context.verify(plain_password, DUMMY_HASH)
        except Exception:
            # ignore
            pass
        return False

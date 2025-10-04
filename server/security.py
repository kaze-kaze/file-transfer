import base64
import hashlib
import os
import secrets
from typing import Optional, Tuple

DEFAULT_ITERATIONS = 200_000


def generate_random_string(length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str, salt: Optional[bytes] = None, iterations: int = DEFAULT_ITERATIONS) -> Tuple[str, str, int]:
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt_bytes = base64.b64decode(salt)
    else:
        salt_bytes = salt
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    return base64.b64encode(salt_bytes).decode("ascii"), base64.b64encode(dk).decode("ascii"), iterations


def verify_password(password: str, salt: str, stored_hash: str, iterations: int = DEFAULT_ITERATIONS) -> bool:
    _, new_hash, _ = hash_password(password, salt, iterations)
    return secrets.compare_digest(new_hash, stored_hash)

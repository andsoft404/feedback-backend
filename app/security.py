import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
HASH_ITERATIONS = 210_000


def hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS,
    )
    encoded = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt}${encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        actual = base64.urlsafe_b64encode(digest).decode("ascii")
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(subject: int, role: str) -> str:
    payload = {
        "sub": subject,
        "role": role,
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    payload_part = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload_part.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_part}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload_part, signature_part = token.split(".", 1)
        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(
            _base64url_encode(expected_signature),
            signature_part,
        ):
            return None

        payload = json.loads(_base64url_decode(payload_part))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except (ValueError, TypeError, json.JSONDecodeError):
        return None

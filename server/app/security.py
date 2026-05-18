from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Any, Dict

import jwt

from .errors import ApiError


JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
ACCESS_EXPIRES_SECONDS = int(os.getenv("JWT_ACCESS_EXPIRES_SECONDS", "900"))  # 15 min
REFRESH_EXPIRES_SECONDS = int(os.getenv("JWT_REFRESH_EXPIRES_SECONDS", str(60 * 60 * 24 * 7)))  # 7 days
PBKDF2_ALG = os.getenv("PWD_ALG", "sha256")
PBKDF2_ITERS = int(os.getenv("PWD_ITERS", "210000"))


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")


def _b64d(s: str) -> bytes:
    s = str(s or "")
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("utf-8"))


def hash_password(password: str) -> str:
    pwd = str(password or "").encode("utf-8")
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac(PBKDF2_ALG, pwd, salt, PBKDF2_ITERS)
    return f"pbkdf2_{PBKDF2_ALG}${PBKDF2_ITERS}${_b64e(salt)}${_b64e(dk)}"


def verify_password(password: str, password_hash: str) -> bool:
    ph = str(password_hash or "")
    if ph.startswith("pbkdf2_"):
        try:
            scheme, iters, salt_b64, dk_b64 = ph.split("$", 3)
            alg = scheme.replace("pbkdf2_", "", 1) or "sha256"
            rounds = int(iters)
            salt = _b64d(salt_b64)
            expected = _b64d(dk_b64)
            got = hashlib.pbkdf2_hmac(alg, str(password or "").encode("utf-8"), salt, rounds)
            return hmac.compare_digest(got, expected)
        except Exception:
            return False
    return False


def sign_access_token(user_id: str) -> str:
    now = int(time.time())
    payload = {"sub": user_id, "iat": now, "exp": now + ACCESS_EXPIRES_SECONDS, "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as e:
        raise ApiError(401, "BAD_TOKEN", "Invalid or expired access token") from e
    except jwt.InvalidTokenError as e:
        raise ApiError(401, "BAD_TOKEN", "Invalid or expired access token") from e

    if payload.get("type") != "access":
        raise ApiError(401, "BAD_TOKEN", "Invalid token type")
    return payload


def make_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()

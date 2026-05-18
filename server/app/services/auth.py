from __future__ import annotations

import sqlite3
from typing import Dict

from ..errors import ApiError
from ..repositories import auth as auth_repo
from ..security import (
    ACCESS_EXPIRES_SECONDS,
    REFRESH_EXPIRES_SECONDS,
    hash_refresh_token,
    make_refresh_token,
    sign_access_token,
)
from ..services.users import create_user, get_user_by_id, verify_user_password
from ..util import make_id, now_ms


def _mint_session(db: sqlite3.Connection, user: Dict[str, str]) -> Dict[str, object]:
    refresh_token = make_refresh_token()
    refresh_id = make_id("rft")
    created_at = now_ms()
    expires_at = created_at + (REFRESH_EXPIRES_SECONDS * 1000)
    auth_repo.insert_refresh_token(
        db,
        token_id=refresh_id,
        user_id=user["id"],
        token_hash=hash_refresh_token(refresh_token),
        expires_at=expires_at,
        created_at=created_at,
    )
    return {
        "user": user,
        "accessToken": sign_access_token(user["id"]),
        "refreshToken": refresh_token,
        "accessTokenExpiresIn": ACCESS_EXPIRES_SECONDS,
    }


def register_user(db: sqlite3.Connection, *, email: str, name: str, password: str):
    user = create_user(db, email=email, name=name, password=password)
    return _mint_session(db, user)


def login_user(db: sqlite3.Connection, *, email: str, password: str):
    user = verify_user_password(db, email=email, password=password)
    if not user:
        raise ApiError(401, "INVALID_CREDENTIALS", "invalid email or password")
    return _mint_session(db, user)


def refresh_session(db: sqlite3.Connection, *, refresh_token: str):
    token_hash = hash_refresh_token(refresh_token)
    row = auth_repo.get_refresh_token_by_hash(db, token_hash)
    if not row:
        raise ApiError(401, "BAD_REFRESH", "refresh token is invalid")
    if row["revokedAt"] is not None:
        raise ApiError(401, "BAD_REFRESH", "refresh token has been revoked")
    if int(row["expiresAt"]) <= now_ms():
        raise ApiError(401, "BAD_REFRESH", "refresh token has expired")

    user = get_user_by_id(db, row["userId"])
    if not user:
        raise ApiError(401, "BAD_REFRESH", "user not found")

    next_refresh_token = make_refresh_token()
    next_refresh_id = make_id("rft")
    created_at = now_ms()
    expires_at = created_at + (REFRESH_EXPIRES_SECONDS * 1000)
    auth_repo.insert_refresh_token(
        db,
        token_id=next_refresh_id,
        user_id=user["id"],
        token_hash=hash_refresh_token(next_refresh_token),
        expires_at=expires_at,
        created_at=created_at,
    )
    auth_repo.revoke_refresh_token(db, row["id"], revoked_at=created_at, replaced_by_token_id=next_refresh_id)

    return {
        "user": user,
        "accessToken": sign_access_token(user["id"]),
        "refreshToken": next_refresh_token,
        "accessTokenExpiresIn": ACCESS_EXPIRES_SECONDS,
    }


def logout_session(db: sqlite3.Connection, *, refresh_token: str):
    token_hash = hash_refresh_token(refresh_token)
    row = auth_repo.get_refresh_token_by_hash(db, token_hash)
    if row and row["revokedAt"] is None:
        auth_repo.revoke_refresh_token(db, row["id"], revoked_at=now_ms())
    return {"ok": True}

from __future__ import annotations

import sqlite3
from typing import Optional


def insert_refresh_token(
    db: sqlite3.Connection,
    *,
    token_id: str,
    user_id: str,
    token_hash: str,
    expires_at: int,
    created_at: int,
) -> None:
    db.execute(
        "INSERT INTO refresh_tokens (id, userId, tokenHash, expiresAt, createdAt) VALUES (?, ?, ?, ?, ?)",
        (token_id, user_id, token_hash, expires_at, created_at),
    )
    db.commit()


def get_refresh_token_by_hash(db: sqlite3.Connection, token_hash: str):
    return db.execute("SELECT * FROM refresh_tokens WHERE tokenHash = ?", (token_hash,)).fetchone()


def revoke_refresh_token(db: sqlite3.Connection, token_id: str, revoked_at: int, replaced_by_token_id: Optional[str] = None) -> None:
    db.execute(
        "UPDATE refresh_tokens SET revokedAt = ?, replacedByTokenId = COALESCE(?, replacedByTokenId) WHERE id = ?",
        (revoked_at, replaced_by_token_id, token_id),
    )
    db.commit()


def revoke_all_user_refresh_tokens(db: sqlite3.Connection, user_id: str, revoked_at: int) -> None:
    db.execute(
        "UPDATE refresh_tokens SET revokedAt = COALESCE(revokedAt, ?) WHERE userId = ?",
        (revoked_at, user_id),
    )
    db.commit()

from __future__ import annotations

import sqlite3
from typing import Any, Dict, Optional

from ..errors import ApiError
from ..rbac import ROLES, normalize_role
from ..repositories import users as users_repo
from ..security import hash_password, verify_password
from ..util import make_id, now_ms


def _normalize_email(email: str | None) -> str:
    return str(email or "").strip().lower()


def _public_user(row) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    role = row["role"] if not isinstance(row, dict) else row.get("role")
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "role": normalize_role(role),
    }


def create_user(db: sqlite3.Connection, *, email: str, name: str, password: str) -> Dict[str, Any]:
    e = _normalize_email(email)
    n = str(name or "").strip()
    p = str(password or "")

    if not e or "@" not in e:
        raise ApiError(400, "VALIDATION_ERROR", "email is invalid")
    if not n or len(n) < 2:
        raise ApiError(400, "VALIDATION_ERROR", "name is required (min 2 chars)")
    if not p or len(p) < 6:
        raise ApiError(400, "VALIDATION_ERROR", "password must be at least 6 chars")
    if len(p.encode("utf-8")) > 256:
        raise ApiError(400, "VALIDATION_ERROR", "password is too long")

    if users_repo.get_by_email(db, e):
        raise ApiError(409, "ALREADY_EXISTS", "user already exists")

    user = {
        "id": make_id("usr"),
        "email": e,
        "name": n,
        "role": ROLES.USER,
        "passwordHash": hash_password(p),
        "createdAt": now_ms(),
    }
    users_repo.insert_user(db, user)
    return _public_user(user)  # type: ignore[arg-type]


def verify_user_password(db: sqlite3.Connection, *, email: str, password: str) -> Optional[Dict[str, Any]]:
    row = users_repo.get_by_email(db, _normalize_email(email))
    if not row:
        return None
    if not verify_password(str(password or ""), row["passwordHash"]):
        return None
    return _public_user(row)


def get_user_by_id(db: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    return _public_user(users_repo.get_by_id(db, str(user_id or "")))


def list_users(db: sqlite3.Connection):
    return [_public_user(r) for r in users_repo.list_public_rows(db)]


def set_role(db: sqlite3.Connection, *, user_id: str, next_role: str):
    role = normalize_role(next_role)
    if role == ROLES.GUEST:
        raise ApiError(400, "VALIDATION_ERROR", "invalid role")
    row = users_repo.get_by_id(db, str(user_id or ""))
    if not row:
        raise ApiError(404, "NOT_FOUND", "user not found")
    users_repo.update_role(db, row["id"], role)
    return {"id": row["id"], "email": row["email"], "name": row["name"], "role": role}

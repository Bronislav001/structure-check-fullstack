from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional


def get_by_email(db: sqlite3.Connection, email: str):
    return db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_by_id(db: sqlite3.Connection, user_id: str):
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def insert_user(db: sqlite3.Connection, user: Dict[str, Any]) -> None:
    db.execute(
        "INSERT INTO users (id, email, name, role, passwordHash, createdAt) VALUES (?, ?, ?, ?, ?, ?)",
        (user["id"], user["email"], user["name"], user["role"], user["passwordHash"], user["createdAt"]),
    )
    db.commit()


def update_role(db: sqlite3.Connection, user_id: str, role: str) -> None:
    db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    db.commit()


def list_public_rows(db: sqlite3.Connection):
    return db.execute("SELECT id, email, name, role, createdAt FROM users ORDER BY createdAt DESC").fetchall()

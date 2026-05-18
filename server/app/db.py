from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Generator


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = (BASE_DIR.parent / 'storage').resolve()
DB_PATH = STORAGE_DIR / 'app.db'


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    _ensure_dir(STORAGE_DIR)
    con = sqlite3.connect(DB_PATH)
    try:
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys = ON')
        con.executescript(
            '''
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              email TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'user',
              passwordHash TEXT NOT NULL,
              createdAt INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS checks (
              id TEXT PRIMARY KEY,
              userId TEXT NOT NULL,
              label TEXT NOT NULL,
              text TEXT NOT NULL,
              notes TEXT NOT NULL DEFAULT '',
              createdAt INTEGER NOT NULL,
              updatedAt INTEGER NOT NULL,
              inputLength INTEGER NOT NULL,
              ok INTEGER NOT NULL,
              templateJson TEXT NOT NULL,
              foundJson TEXT NOT NULL,
              missingJson TEXT NOT NULL,
              orderIssuesJson TEXT NOT NULL,
              FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
              id TEXT PRIMARY KEY,
              userId TEXT NOT NULL,
              tokenHash TEXT NOT NULL UNIQUE,
              expiresAt INTEGER NOT NULL,
              revokedAt INTEGER,
              createdAt INTEGER NOT NULL,
              replacedByTokenId TEXT,
              FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
              FOREIGN KEY (replacedByTokenId) REFERENCES refresh_tokens(id)
            );

            CREATE TABLE IF NOT EXISTS attachments (
              id TEXT PRIMARY KEY,
              checkId TEXT NOT NULL,
              userId TEXT NOT NULL,
              originalName TEXT NOT NULL,
              storageKey TEXT NOT NULL,
              contentType TEXT NOT NULL,
              size INTEGER NOT NULL,
              createdAt INTEGER NOT NULL,
              FOREIGN KEY (checkId) REFERENCES checks(id) ON DELETE CASCADE,
              FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_userId ON refresh_tokens(userId);
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash ON refresh_tokens(tokenHash);
            CREATE INDEX IF NOT EXISTS idx_checks_userId_createdAt ON checks(userId, createdAt DESC);
            CREATE INDEX IF NOT EXISTS idx_checks_ok_createdAt ON checks(ok, createdAt DESC);
            CREATE INDEX IF NOT EXISTS idx_attachments_checkId ON attachments(checkId, createdAt DESC);
            '''
        )

        cols = [r['name'] for r in con.execute("PRAGMA table_info('users')").fetchall()]
        if 'role' not in cols:
            con.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
            con.commit()
    finally:
        con.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    try:
        yield con
    finally:
        con.close()

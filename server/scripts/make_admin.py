from __future__ import annotations

import sys
import sqlite3

from app.db import DB_PATH, init_db
from app.rbac import ROLES


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.make_admin you@example.com")
        return 2

    email = sys.argv[1].strip().lower()

    init_db()
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute("SELECT id, email, role FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            print("User not found. Register first in UI, then run this script.")
            return 1

        con.execute("UPDATE users SET role = ? WHERE id = ?", (ROLES.ADMIN, row["id"]))
        con.commit()
        print(f"OK: {row['email']} is now '{ROLES.ADMIN}'")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())

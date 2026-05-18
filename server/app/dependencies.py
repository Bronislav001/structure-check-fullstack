from __future__ import annotations

from typing import Callable, Dict

from fastapi import Depends, Header
from sqlite3 import Connection

from .db import get_db
from .errors import ApiError
from .rbac import has_permission
from .security import verify_access_token
from .services.users import get_user_by_id


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Connection = Depends(get_db),
) -> Dict:
    h = str(authorization or "")
    if not h.startswith("Bearer "):
        raise ApiError(401, "NO_TOKEN", "Authorization Bearer token required")

    token = h[len("Bearer "):].strip()
    payload = verify_access_token(token)
    user = get_user_by_id(db, payload.get("sub"))
    if not user:
        raise ApiError(401, "BAD_TOKEN", "User not found")
    return user


def require_permission(perm: str) -> Callable:
    def dep(user: Dict = Depends(get_current_user)) -> Dict:
        if not has_permission(user.get("role"), perm):
            raise ApiError(403, "FORBIDDEN", "insufficient permissions")
        return user

    return dep

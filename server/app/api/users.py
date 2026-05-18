from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlite3 import Connection

from ..db import get_db
from ..models import RolePatchIn, RolePatchOut, UsersListOut
from ..rbac import PERMS
from ..dependencies import require_permission
from ..services.users import list_users, set_role


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=UsersListOut)
def list_(
    _user=Depends(require_permission(PERMS.USERS_READ_ANY)),
    db: Connection = Depends(get_db),
):
    items = list_users(db)
    return {"items": items}


@router.patch("/{user_id}/role", response_model=RolePatchOut)
def patch_role(
    user_id: str,
    payload: RolePatchIn,
    _user=Depends(require_permission(PERMS.USERS_UPDATE_ROLE)),
    db: Connection = Depends(get_db),
):
    user = set_role(db, user_id=user_id, next_role=payload.role)
    return {"user": user}

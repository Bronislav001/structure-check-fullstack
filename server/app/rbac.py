from __future__ import annotations

from typing import Dict, List


class ROLES:
    GUEST = "guest"
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class PERMS:
    CHECKS_CREATE = "checks:create"
    CHECKS_READ_OWN = "checks:read_own"
    CHECKS_UPDATE_OWN = "checks:update_own"
    CHECKS_DELETE_OWN = "checks:delete_own"

    CHECKS_READ_ANY = "checks:read_any"
    CHECKS_UPDATE_ANY = "checks:update_any"
    CHECKS_DELETE_ANY = "checks:delete_any"

    USERS_READ_ANY = "users:read_any"
    USERS_UPDATE_ROLE = "users:update_role"


ROLE_PERMISSIONS: Dict[str, List[str]] = {
    ROLES.GUEST: [],
    ROLES.USER: [
        PERMS.CHECKS_CREATE,
        PERMS.CHECKS_READ_OWN,
        PERMS.CHECKS_UPDATE_OWN,
        PERMS.CHECKS_DELETE_OWN,
    ],
    ROLES.MANAGER: [
        PERMS.CHECKS_CREATE,
        PERMS.CHECKS_READ_OWN,
        PERMS.CHECKS_UPDATE_OWN,
        PERMS.CHECKS_DELETE_OWN,
        PERMS.CHECKS_READ_ANY,
        PERMS.CHECKS_UPDATE_ANY,
    ],
    ROLES.ADMIN: [
        PERMS.CHECKS_CREATE,
        PERMS.CHECKS_READ_OWN,
        PERMS.CHECKS_UPDATE_OWN,
        PERMS.CHECKS_DELETE_OWN,
        PERMS.CHECKS_READ_ANY,
        PERMS.CHECKS_UPDATE_ANY,
        PERMS.CHECKS_DELETE_ANY,
        PERMS.USERS_READ_ANY,
        PERMS.USERS_UPDATE_ROLE,
    ],
}


def normalize_role(role: str | None) -> str:
    r = str(role or "").strip().lower()
    return r if r in ROLE_PERMISSIONS else ROLES.GUEST


def permissions_for_role(role: str | None) -> List[str]:
    return ROLE_PERMISSIONS.get(normalize_role(role), [])


def has_permission(role: str | None, perm: str) -> bool:
    return perm in permissions_for_role(role)

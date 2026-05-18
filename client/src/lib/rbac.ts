export const ROLES = {
  GUEST: 'guest',
  USER: 'user',
  MANAGER: 'manager',
  ADMIN: 'admin'
}

export const PERMS = {
  CHECKS_CREATE: 'checks:create',
  CHECKS_READ_OWN: 'checks:read_own',
  CHECKS_UPDATE_OWN: 'checks:update_own',
  CHECKS_DELETE_OWN: 'checks:delete_own',
  CHECKS_READ_ANY: 'checks:read_any',
  CHECKS_UPDATE_ANY: 'checks:update_any',
  CHECKS_DELETE_ANY: 'checks:delete_any',
  USERS_READ_ANY: 'users:read_any',
  USERS_UPDATE_ROLE: 'users:update_role'
}

const ROLE_PERMISSIONS = {
  [ROLES.GUEST]: [],
  [ROLES.USER]: [
    PERMS.CHECKS_CREATE,
    PERMS.CHECKS_READ_OWN,
    PERMS.CHECKS_UPDATE_OWN,
    PERMS.CHECKS_DELETE_OWN
  ],
  [ROLES.MANAGER]: [
    PERMS.CHECKS_CREATE,
    PERMS.CHECKS_READ_OWN,
    PERMS.CHECKS_UPDATE_OWN,
    PERMS.CHECKS_DELETE_OWN,
    PERMS.CHECKS_READ_ANY,
    PERMS.CHECKS_UPDATE_ANY
  ],
  [ROLES.ADMIN]: [
    PERMS.CHECKS_CREATE,
    PERMS.CHECKS_READ_OWN,
    PERMS.CHECKS_UPDATE_OWN,
    PERMS.CHECKS_DELETE_OWN,
    PERMS.CHECKS_READ_ANY,
    PERMS.CHECKS_UPDATE_ANY,
    PERMS.CHECKS_DELETE_ANY,
    PERMS.USERS_READ_ANY,
    PERMS.USERS_UPDATE_ROLE
  ]
}

export function normalizeRole(role) {
  const r = String(role || '').toLowerCase().trim()
  return ROLE_PERMISSIONS[r] ? r : ROLES.GUEST
}

export function permissionsForRole(role) {
  const r = normalizeRole(role)
  return ROLE_PERMISSIONS[r] || []
}

export function hasPermission(role, perm) {
  return permissionsForRole(role).includes(perm)
}

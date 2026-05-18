import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../state/auth'
import { hasPermission } from '../lib/rbac'

export default function RequirePerm({ perm, children }: { perm: string; children: React.ReactNode }) {
  const { isAuthed, user } = useAuth()
  const loc = useLocation()

  if (!isAuthed) {
    return <Navigate to="/login" replace state={{ from: loc.pathname }} />
  }

  const role = user?.role || 'guest'
  if (!hasPermission(role, perm)) {
    return (
      <div className="card">
        <h3>Нет доступа</h3>
        <p>
          Для этой страницы нужны права: <b>{perm}</b>
        </p>
      </div>
    )
  }

  return <>{children}</>
}

import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api, authStorage, SessionData, UserPublic } from '../lib/api'

type AuthCtxValue = {
  accessToken: string | null
  refreshToken: string | null
  user: UserPublic | null
  isAuthed: boolean
  saveSession: (session: SessionData) => void
  logout: () => Promise<void>
}

const AuthCtx = createContext<AuthCtxValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [user, setUser] = useState<UserPublic | null>(null)

  useEffect(() => {
    const s = authStorage.readSession()
    setAccessToken(s?.accessToken || null)
    setRefreshToken(s?.refreshToken || null)
    setUser(s?.user || null)
  }, [])

  useEffect(() => {
    if (!accessToken) return
    api.me().then((data: any) => {
      if (data?.user) {
        const current = authStorage.readSession()
        const next = current ? { ...current, user: data.user } : null
        if (next) authStorage.writeSession(next)
        setUser(data.user)
        setAccessToken(next?.accessToken || accessToken)
        setRefreshToken(next?.refreshToken || refreshToken)
      }
    }).catch(() => {
      authStorage.clear()
      setAccessToken(null)
      setRefreshToken(null)
      setUser(null)
    })
  }, [accessToken])

  function saveSession(session: SessionData) {
    authStorage.writeSession(session)
    setAccessToken(session.accessToken)
    setRefreshToken(session.refreshToken)
    setUser(session.user)
  }

  async function logout() {
    const current = authStorage.readSession()
    try {
      if (current?.refreshToken) await api.logout(current.refreshToken)
    } catch {}
    authStorage.clear()
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
  }

  const value = useMemo(() => ({ accessToken, refreshToken, user, isAuthed: !!accessToken, saveSession, logout }), [accessToken, refreshToken, user])
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthCtx)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}

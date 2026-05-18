import React, { useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../state/auth'
import { Navigate, useNavigate } from 'react-router-dom'
import Seo from '../components/Seo'

export default function Login() {
  const { saveSession, user } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (user) return <Navigate to="/" replace />

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await api.login({ email, password })
      saveSession(data)
      nav('/validate')
    } catch (e2: any) {
      setError(`${e2.code || 'ERROR'}: ${e2.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ maxWidth: 520, margin: '0 auto' }}>
      <Seo title="Вход" description="Вход в личный кабинет Struct Check." canonicalPath="/login" robots="noindex,nofollow" />
      <h1>Вход</h1>
      <form onSubmit={onSubmit}>
        <div style={{ marginTop: 10 }}>
          <div className="muted" style={{ marginBottom: 6 }}>Email</div>
          <input value={email} onChange={e => setEmail(e.target.value)} />
        </div>

        <div style={{ marginTop: 10 }}>
          <div className="muted" style={{ marginBottom: 6 }}>Пароль</div>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
        </div>

        <div style={{ marginTop: 12 }}>
          <button className="btn primary" disabled={loading} type="submit">
            {loading ? 'Входим…' : 'Войти'}
          </button>
        </div>

        {error && <div style={{ marginTop: 10 }} className="badge">{error}</div>}
      </form>
    </div>
  )
}

import React, { useEffect, useState } from 'react'
import { api } from '../lib/api'
import Seo from '../components/Seo'

const ROLES = ['user', 'manager', 'admin']

export default function AdminUsers() {
  const [items, setItems] = useState<any[]>([])
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setErr('')
    try {
      const data = await api.listUsers()
      setItems(data.items || [])
    } catch (e: any) {
      setErr(e.message || 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function changeRole(id: string, role: string) {
    setErr('')
    try {
      await api.setUserRole(id, role)
      await load()
    } catch (e: any) {
      setErr(e.message || 'Ошибка')
    }
  }

  return (
    <div className="card">
      <Seo title="Пользователи" description="Административный раздел управления пользователями Struct Check." canonicalPath="/admin/users" robots="noindex,nofollow" />
      <h1>Пользователи</h1>
      <p className="muted">Административный раздел управления ролями пользователей.</p>
      {err && <div className="error">{err}</div>}
      {loading ? <p>Загрузка...</p> : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr><th>Email</th><th>Имя</th><th>Роль</th><th></th></tr>
            </thead>
            <tbody>
              {items.map((u) => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>{u.name}</td>
                  <td>
                    <select value={u.role} onChange={(e) => changeRole(u.id, e.target.value)}>
                      {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </td>
                  <td className="muted">{u.id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import RequirePerm from '../components/RequirePerm'
import { PERMS } from '../lib/rbac'

const authState = { isAuthed: false, user: null }

vi.mock('../state/auth', () => ({
  useAuth: () => authState,
}))

describe('RequirePerm', () => {
  it('redirects guest to login', () => {
    authState.isAuthed = false
    authState.user = null
    render(
      <MemoryRouter initialEntries={['/history']}>
        <Routes>
          <Route path="/login" element={<div>Страница входа</div>} />
          <Route path="/history" element={<RequirePerm perm={PERMS.CHECKS_READ_OWN}><div>История</div></RequirePerm>} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText('Страница входа')).toBeInTheDocument()
  })

  it('shows no access for insufficient permissions', () => {
    authState.isAuthed = true
    authState.user = { id: 'u1', email: 'u@example.com', name: 'User', role: 'user' }
    render(
      <MemoryRouter>
        <RequirePerm perm={PERMS.USERS_READ_ANY}><div>Скрыто</div></RequirePerm>
      </MemoryRouter>
    )
    expect(screen.getByText('Нет доступа')).toBeInTheDocument()
  })
})

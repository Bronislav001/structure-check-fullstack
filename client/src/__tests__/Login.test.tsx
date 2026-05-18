import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import Login from '../pages/Login'

const mocks = vi.hoisted(() => ({
  login: vi.fn(),
  saveSession: vi.fn(),
}))

vi.mock('../lib/api', () => ({ api: { login: mocks.login } }))
vi.mock('../state/auth', () => ({
  useAuth: () => ({ saveSession: mocks.saveSession, user: null }),
}))

describe('Login page', () => {
  beforeEach(() => {
    mocks.login.mockReset()
    mocks.saveSession.mockReset()
  })

  it('submits credentials and stores session', async () => {
    mocks.login.mockResolvedValueOnce({
      accessToken: 'a',
      refreshToken: 'r',
      accessTokenExpiresIn: 900,
      user: { id: 'u1', email: 'user@example.com', name: 'User', role: 'user' }
    })

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/validate" element={<div>Проверка</div>} />
        </Routes>
      </MemoryRouter>
    )

    const inputs = screen.getAllByRole('textbox')
    await userEvent.type(inputs[0], 'user@example.com')
    const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement
    await userEvent.type(passwordInput, 'secret123')
    await userEvent.click(screen.getByRole('button', { name: /войти/i }))

    expect(mocks.login).toHaveBeenCalledWith({ email: 'user@example.com', password: 'secret123' })
    expect(mocks.saveSession).toHaveBeenCalledWith(expect.objectContaining({ accessToken: 'a', refreshToken: 'r' }))
    expect(await screen.findByText('Проверка')).toBeInTheDocument()
  })

  it('shows backend error on invalid credentials', async () => {
    mocks.login.mockRejectedValueOnce({ code: 'INVALID_CREDENTIALS', message: 'bad login' })
    render(
      <MemoryRouter initialEntries={['/login']}>
        <Login />
      </MemoryRouter>
    )

    const emailInput = screen.getAllByRole('textbox')[0]
    await userEvent.type(emailInput, 'wrong@example.com')
    const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement
    await userEvent.type(passwordInput, 'bad')
    await userEvent.click(screen.getByRole('button', { name: /войти/i }))

    expect(await screen.findByText(/INVALID_CREDENTIALS/)).toBeInTheDocument()
  })
})

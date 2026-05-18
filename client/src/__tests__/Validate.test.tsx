import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Validate from '../pages/Validate'

const mocks = vi.hoisted(() => ({
  createCheck: vi.fn(),
  createCheckFromFile: vi.fn(),
  isAuthed: false,
}))

vi.mock('../lib/api', () => ({ api: { createCheck: mocks.createCheck, createCheckFromFile: mocks.createCheckFromFile } }))
vi.mock('../state/auth', () => ({
  useAuth: () => ({ isAuthed: mocks.isAuthed }),
}))

describe('Validate', () => {
  beforeEach(() => {
    mocks.createCheck.mockReset()
    mocks.createCheckFromFile.mockReset()
    mocks.isAuthed = false
  })

  it('shows auth error when guest submits', async () => {
    render(<Validate />)
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    expect(await screen.findByText(/Нужно войти/i)).toBeInTheDocument()
  })

  it('sends report text when user is authenticated', async () => {
    mocks.isAuthed = true
    mocks.createCheck.mockResolvedValueOnce({
      label: 'Проверка',
      inputLength: 100,
      found: ['Введение'],
      missing: ['Выводы'],
      ok: false,
      attachment: null
    })

    render(<Validate />)
    const titleInput = screen.getByDisplayValue('Мой отчёт')
    const textareas = screen.getAllByRole('textbox').filter((el) => el.tagName.toLowerCase() === 'textarea')
    await userEvent.clear(titleInput)
    await userEvent.type(titleInput, 'Мой отчёт')
    await userEvent.type(textareas[1], 'Введение. Теоретическая часть.')
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))

    expect(mocks.createCheck).toHaveBeenCalled()
    expect(await screen.findByText(/Выводы/)).toBeInTheDocument()
  })
})

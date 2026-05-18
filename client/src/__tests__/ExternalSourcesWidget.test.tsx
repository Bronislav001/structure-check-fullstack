import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ExternalSourcesWidget from '../components/ExternalSourcesWidget'

const mocks = vi.hoisted(() => ({
  searchSources: vi.fn(),
}))

vi.mock('../lib/api', () => ({
  api: { searchSources: mocks.searchSources },
}))

describe('ExternalSourcesWidget', () => {
  beforeEach(() => {
    mocks.searchSources.mockReset()
  })

  it('renders external sources on success', async () => {
    mocks.searchSources.mockResolvedValueOnce({
      items: [
        { id: '1', title: 'Python 101', authors: ['A'], publisher: 'Pub', publishedYear: '2024', description: 'desc', thumbnail: '', infoUrl: 'https://example.com' }
      ]
    })
    render(<ExternalSourcesWidget />)
    await userEvent.clear(screen.getByPlaceholderText(/базы данных/i))
    await userEvent.type(screen.getByPlaceholderText(/базы данных/i), 'python')
    await userEvent.click(screen.getByRole('button', { name: /подобрать источники/i }))

    expect(await screen.findByText('Python 101')).toBeInTheDocument()
    expect(mocks.searchSources).toHaveBeenCalledWith('python')
  })

  it('shows server error gracefully', async () => {
    mocks.searchSources.mockRejectedValueOnce({ code: 'EXTERNAL_API_ERROR', message: 'failed' })
    render(<ExternalSourcesWidget />)
    await userEvent.clear(screen.getByPlaceholderText(/базы данных/i))
    await userEvent.type(screen.getByPlaceholderText(/базы данных/i), 'python')
    await userEvent.click(screen.getByRole('button', { name: /подобрать источники/i }))

    expect(await screen.findByText(/EXTERNAL_API_ERROR/i)).toBeInTheDocument()
  })
})

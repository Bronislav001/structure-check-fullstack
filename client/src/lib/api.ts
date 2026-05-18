const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8080'
const LS_KEY = 'struct_check_auth_v2'

export type UserPublic = {
  id: string
  email: string
  name: string
  role: string
}

export type SessionData = {
  accessToken: string
  refreshToken: string
  accessTokenExpiresIn: number
  user: UserPublic
}

export type Attachment = {
  id: string
  checkId: string
  originalName: string
  contentType: string
  size: number
  createdAt: number
  downloadUrl: string
}

export type CheckItem = {
  id: string
  userId: string
  authorName?: string
  authorEmail?: string
  label: string
  text?: string
  notes: string
  createdAt: number
  updatedAt: number
  inputLength: number
  ok: boolean
  template: string[]
  found: string[]
  missing: string[]
  orderIssues: Array<{ type: string; message: string; section: string }>
  attachments: Attachment[]
}

export type CheckFilters = {
  scope?: 'own' | 'all'
  q?: string
  status?: 'all' | 'ok' | 'issues'
  sortBy?: 'createdAt' | 'updatedAt' | 'label'
  sortDir?: 'asc' | 'desc'
  page?: number
  pageSize?: number
  ownerId?: string
}

export type ApiErr = Error & { code?: string; status?: number }

function readSession(): SessionData | null {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function writeSession(session: SessionData | null) {
  if (!session) {
    localStorage.removeItem(LS_KEY)
    return
  }
  localStorage.setItem(LS_KEY, JSON.stringify(session))
}

let refreshPromise: Promise<SessionData> | null = null

async function parseResponse<T>(res: Response): Promise<T> {
  const data: any = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.message || `HTTP ${res.status}`) as ApiErr
    err.code = data.code || 'HTTP_ERROR'
    err.status = res.status
    throw err
  }
  return data as T
}

async function rawRequest<T = any>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init)
  return parseResponse<T>(res)
}

async function refreshTokens(): Promise<SessionData> {
  if (refreshPromise) return refreshPromise
  const current = readSession()
  if (!current?.refreshToken) {
    const e = new Error('No refresh token') as ApiErr
    e.code = 'NO_REFRESH'
    e.status = 401
    throw e
  }

  refreshPromise = rawRequest<SessionData>('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken: current.refreshToken })
  }).then((next) => {
    writeSession(next)
    return next
  }).finally(() => {
    refreshPromise = null
  })

  return refreshPromise
}

async function request<T = any>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const current = readSession()
  const headers = new Headers(init.headers || {})
  if (!headers.has('Content-Type') && init.body != null && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (current?.accessToken) headers.set('Authorization', `Bearer ${current.accessToken}`)

  try {
    const res = await fetch(`${API_URL}${path}`, { ...init, headers })
    return await parseResponse<T>(res)
  } catch (e: any) {
    if (retry && e?.status === 401 && current?.refreshToken && path !== '/api/auth/refresh' && path !== '/api/auth/login' && path !== '/api/auth/register') {
      try {
        const next = await refreshTokens()
        const retryHeaders = new Headers(init.headers || {})
        if (!retryHeaders.has('Content-Type') && init.body != null && !(init.body instanceof FormData)) {
          retryHeaders.set('Content-Type', 'application/json')
        }
        retryHeaders.set('Authorization', `Bearer ${next.accessToken}`)
        const res = await fetch(`${API_URL}${path}`, { ...init, headers: retryHeaders })
        return await parseResponse<T>(res)
      } catch (refreshErr) {
        writeSession(null)
        throw refreshErr
      }
    }
    throw e
  }
}

function buildChecksQuery(filters: CheckFilters = {}) {
  const params = new URLSearchParams()
  if (filters.scope === 'all') params.set('scope', 'all')
  if (filters.q) params.set('q', filters.q)
  if (filters.status && filters.status !== 'all') params.set('status', filters.status)
  if (filters.sortBy) params.set('sortBy', filters.sortBy)
  if (filters.sortDir) params.set('sortDir', filters.sortDir)
  if (filters.page) params.set('page', String(filters.page))
  if (filters.pageSize) params.set('pageSize', String(filters.pageSize))
  if (filters.ownerId) params.set('ownerId', filters.ownerId)
  const qs = params.toString()
  return qs ? `/api/checks/?${qs}` : '/api/checks/'
}

export const authStorage = { readSession, writeSession, clear: () => writeSession(null) }

export const api = {
  register: (payload: { email: string; name: string; password: string }) =>
    rawRequest<SessionData>('/api/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  login: (payload: { email: string; password: string }) =>
    rawRequest<SessionData>('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  refresh: (refreshToken: string) =>
    rawRequest<SessionData>('/api/auth/refresh', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refreshToken }) }),
  logout: (refreshToken: string) =>
    rawRequest('/api/auth/logout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refreshToken }) }),
  me: () => request('/api/auth/me'),

  createCheck: (payload: { label: string; text: string; notes?: string }) => request('/api/checks/', { method: 'POST', body: JSON.stringify(payload) }),
  createCheckFromFile: (payload: { label: string; notes?: string; file: File }) => {
    const form = new FormData()
    form.append('label', payload.label)
    form.append('notes', payload.notes || '')
    form.append('upload', payload.file)
    return request<CheckItem>('/api/checks/from-upload', { method: 'POST', body: form })
  },
  listChecks: (filters: CheckFilters = {}) => request<{ items: CheckItem[]; total: number; page: number; pageSize: number }>(buildChecksQuery(filters)),
  getCheck: (id: string) => request<CheckItem>(`/api/checks/${id}`),
  patchCheck: (id: string, payload: { label?: string; notes?: string }) => request<CheckItem>(`/api/checks/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deleteCheck: (id: string) => request(`/api/checks/${id}`, { method: 'DELETE' }),
  uploadAttachment: (checkId: string, file: File) => {
    const form = new FormData()
    form.append('upload', file)
    return request<Attachment>(`/api/checks/${checkId}/attachments`, { method: 'POST', body: form })
  },
  deleteAttachment: (checkId: string, attachmentId: string) => request(`/api/checks/${checkId}/attachments/${attachmentId}`, { method: 'DELETE' }),

  searchSources: (q: string) => rawRequest(`/api/external/sources?q=${encodeURIComponent(q)}`),

  listUsers: () => request('/api/users/'),
  setUserRole: (id: string, role: string) => request(`/api/users/${id}/role`, { method: 'PATCH', body: JSON.stringify({ role }) })
}

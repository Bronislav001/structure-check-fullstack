import React, { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api, CheckFilters, CheckItem } from '../lib/api'
import { useAuth } from '../state/auth'
import { hasPermission, PERMS } from '../lib/rbac'
import Seo from '../components/Seo'

function fmt(ts: number) {
  try { return new Date(ts).toLocaleString() } catch { return String(ts) }
}

function bytes(n: number) {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

const PAGE_SIZES = [5, 10, 20]

export default function History() {
  const { isAuthed, user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const [items, setItems] = useState<CheckItem[]>([])
  const [selected, setSelected] = useState<CheckItem | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [total, setTotal] = useState(0)

  const canSeeAll = hasPermission(user?.role, PERMS.CHECKS_READ_ANY)
  const canEditAny = hasPermission(user?.role, PERMS.CHECKS_UPDATE_ANY)
  const canDeleteAny = hasPermission(user?.role, PERMS.CHECKS_DELETE_ANY)

  const filters = useMemo<CheckFilters>(() => ({
    scope: searchParams.get('scope') === 'all' ? 'all' : 'own',
    q: searchParams.get('q') || '',
    status: (searchParams.get('status') as any) || 'all',
    sortBy: (searchParams.get('sortBy') as any) || 'createdAt',
    sortDir: (searchParams.get('sortDir') as any) || 'desc',
    page: Number(searchParams.get('page') || '1'),
    pageSize: Number(searchParams.get('pageSize') || '5'),
    ownerId: searchParams.get('ownerId') || ''
  }), [searchParams])

  function updateFilters(next: Partial<CheckFilters>) {
    const merged = { ...filters, ...next }
    const params = new URLSearchParams()
    if (merged.scope === 'all') params.set('scope', 'all')
    if (merged.q) params.set('q', merged.q)
    if (merged.status && merged.status !== 'all') params.set('status', merged.status)
    if (merged.sortBy && merged.sortBy !== 'createdAt') params.set('sortBy', merged.sortBy)
    if (merged.sortDir && merged.sortDir !== 'desc') params.set('sortDir', merged.sortDir)
    if (merged.page && merged.page !== 1) params.set('page', String(merged.page))
    if (merged.pageSize && merged.pageSize !== 5) params.set('pageSize', String(merged.pageSize))
    if (merged.ownerId) params.set('ownerId', merged.ownerId)
    setSearchParams(params)
  }

  async function load(preferredId?: string) {
    if (!isAuthed) return
    setLoading(true)
    setError('')
    try {
      const data = await api.listChecks(filters)
      setItems(data.items || [])
      setTotal(data.total || 0)
      const nextId = preferredId || selected?.id
      if (nextId) {
        const target = (data.items || []).find((x: CheckItem) => x.id === nextId)
        if (target) {
          const full = await api.getCheck(target.id)
          setSelected(full)
        } else if ((data.items || [])[0]) {
          const full = await api.getCheck(data.items[0].id)
          setSelected(full)
        } else {
          setSelected(null)
        }
      }
    } catch (e: any) {
      setError(`${e.code || 'ERROR'}: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [isAuthed, searchParams.toString()])

  async function openItem(id: string) {
    setError('')
    try {
      const full = await api.getCheck(id)
      setSelected(full)
    } catch (e: any) {
      setError(`${e.code || 'ERROR'}: ${e.message}`)
    }
  }

  async function saveSelected() {
    if (!selected) return
    setSaving(true)
    setError('')
    try {
      const updated = await api.patchCheck(selected.id, { label: selected.label, notes: selected.notes })
      setSelected(updated)
      await load(updated.id)
    } catch (e: any) {
      setError(`${e.code || 'ERROR'}: ${e.message}`)
    } finally {
      setSaving(false)
    }
  }

  async function removeSelected() {
    if (!selected) return
    if (!window.confirm(`Удалить проверку «${selected.label}»?`)) return
    setSaving(true)
    setError('')
    try {
      await api.deleteCheck(selected.id)
      setSelected(null)
      await load()
    } catch (e: any) {
      setError(`${e.code || 'ERROR'}: ${e.message}`)
    } finally {
      setSaving(false)
    }
  }

  async function removeAttachment(attId: string) {
    if (!selected) return
    if (!window.confirm('Удалить файл?')) return
    setUploading(true)
    setError('')
    try {
      await api.deleteAttachment(selected.id, attId)
      const full = await api.getCheck(selected.id)
      setSelected(full)
      await load(selected.id)
    } catch (err: any) {
      setError(`${err.code || 'ERROR'}: ${err.message}`)
    } finally {
      setUploading(false)
    }
  }

  if (!isAuthed) {
    return <div className="card"><h2>История проверок</h2><div className="muted">Войди, чтобы увидеть историю.</div></div>
  }

  const maxPage = Math.max(1, Math.ceil(total / (filters.pageSize || 5)))
  const canEditSelected = !!selected && (selected.userId === user?.id || canEditAny)
  const canDeleteSelected = !!selected && (selected.userId === user?.id || canDeleteAny)

  return (
    <>
      <Seo title="История проверок" description="Закрытый раздел с поиском, фильтрами, сортировкой и файлами по результатам проверок." canonicalPath="/history" robots="noindex,nofollow" />
      <div className="grid" style={{ gridTemplateColumns: '1.2fr 1fr' }}>
        <div className="card">
          <div className="row">
            <h1>История проверок</h1>
            <button className="btn" onClick={() => load()} disabled={loading}>{loading ? 'Обновляем…' : 'Обновить'}</button>
          </div>

          <div className="grid" style={{ gridTemplateColumns: '2fr 1fr', marginTop: 8 }}>
            <div>
              <div className="muted" style={{ marginBottom: 6 }}>Поиск</div>
              <input
                value={filters.q || ''}
                onChange={(e) => updateFilters({ q: e.target.value, page: 1 })}
                placeholder="По названию, тексту, заметкам, email или имени"
              />
            </div>
            <div>
              <div className="muted" style={{ marginBottom: 6 }}>Статус</div>
              <select value={filters.status} onChange={(e) => updateFilters({ status: e.target.value as any, page: 1 })}>
                <option value="all">Все</option>
                <option value="ok">Только OK</option>
                <option value="issues">Только с пропусками</option>
              </select>
            </div>
            <div>
              <div className="muted" style={{ marginBottom: 6 }}>Сортировка</div>
              <div className="row" style={{ justifyContent: 'stretch' }}>
                <select value={filters.sortBy} onChange={(e) => updateFilters({ sortBy: e.target.value as any, page: 1 })}>
                  <option value="createdAt">По дате создания</option>
                  <option value="updatedAt">По дате обновления</option>
                  <option value="label">По названию</option>
                </select>
                <select value={filters.sortDir} onChange={(e) => updateFilters({ sortDir: e.target.value as any, page: 1 })}>
                  <option value="desc">По убыванию</option>
                  <option value="asc">По возрастанию</option>
                </select>
              </div>
            </div>
            <div>
              <div className="muted" style={{ marginBottom: 6 }}>На странице</div>
              <select value={filters.pageSize} onChange={(e) => updateFilters({ pageSize: Number(e.target.value), page: 1 })}>
                {PAGE_SIZES.map((x) => <option key={x} value={x}>{x}</option>)}
              </select>
            </div>
          </div>

          {canSeeAll && (
            <div className="row" style={{ marginTop: 12, justifyContent: 'flex-start' }}>
              <label className="muted" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="checkbox"
                  checked={filters.scope === 'all'}
                  onChange={(e) => updateFilters({ scope: e.target.checked ? 'all' : 'own', ownerId: '', page: 1 })}
                />
                видеть все проверки
              </label>
              {filters.scope === 'all' && (
                <input
                  style={{ maxWidth: 220 }}
                  value={filters.ownerId || ''}
                  onChange={(e) => updateFilters({ ownerId: e.target.value.trim(), page: 1 })}
                  placeholder="Фильтр по ownerId"
                />
              )}
            </div>
          )}

          {error && <div style={{ marginTop: 10 }} className="badge">{error}</div>}
          <div className="hr" />

          {items.length === 0 ? (
            <div className="muted">Ничего не найдено. Измени фильтры или создай новую проверку.</div>
          ) : (
            <div style={{ display: 'grid', gap: 10 }}>
              {items.map((it) => (
                <button
                  key={it.id}
                  className="card"
                  style={{ padding: 12, textAlign: 'left', borderColor: selected?.id === it.id ? '#94a3b8' : undefined }}
                  onClick={() => openItem(it.id)}
                >
                  <div className="row">
                    <div style={{ fontWeight: 700 }}>{it.label}</div>
                    <span className="badge">{it.ok ? 'OK' : 'Есть пропуски'}</span>
                  </div>
                  {(filters.scope === 'all' || canSeeAll) && (
                    <div className="muted" style={{ marginTop: 6 }}>
                      Автор: {it.authorName || '—'} {it.authorEmail ? `(${it.authorEmail})` : ''}
                    </div>
                  )}
                  <div className="muted" style={{ marginTop: 6 }}>{fmt(it.createdAt)}</div>
                  <div className="muted" style={{ marginTop: 6 }}>
                    missing: {(it.missing || []).length}, found: {(it.found || []).length}, вложений: {(it.attachments || []).length}
                  </div>
                </button>
              ))}
            </div>
          )}

          <div className="hr" />
          <div className="row">
            <span className="muted">Всего: {total}</span>
            <div className="row">
              <button className="btn" disabled={(filters.page || 1) <= 1} onClick={() => updateFilters({ page: Math.max(1, (filters.page || 1) - 1) })}>← Назад</button>
              <span className="badge">Страница {filters.page} / {maxPage}</span>
              <button className="btn" disabled={(filters.page || 1) >= maxPage} onClick={() => updateFilters({ page: Math.min(maxPage, (filters.page || 1) + 1) })}>Вперёд →</button>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Просмотр и редактирование</h2>
          {!selected ? (
            <div className="muted">Выбери проверку слева, чтобы посмотреть детали, отредактировать запись или управлять вложениями.</div>
          ) : (
            <>
              <div className="muted">Автор: {selected.authorName || '—'} {selected.authorEmail ? `(${selected.authorEmail})` : ''}</div>
              <div className="muted" style={{ marginTop: 6 }}>Создано: {fmt(selected.createdAt)}</div>
              <div className="muted" style={{ marginTop: 6 }}>Обновлено: {fmt(selected.updatedAt)}</div>

              <div style={{ marginTop: 12 }}>
                <div className="muted" style={{ marginBottom: 6 }}>Название</div>
                <input value={selected.label} disabled={!canEditSelected} onChange={(e) => setSelected({ ...selected, label: e.target.value })} />
              </div>

              <div style={{ marginTop: 12 }}>
                <div className="muted" style={{ marginBottom: 6 }}>Заметки</div>
                <textarea value={selected.notes || ''} disabled={!canEditSelected} onChange={(e) => setSelected({ ...selected, notes: e.target.value })} style={{ minHeight: 110 }} />
              </div>

              <div className="row" style={{ marginTop: 12 }}>
                <button className="btn primary" disabled={!canEditSelected || saving} onClick={saveSelected}>{saving ? 'Сохраняем…' : 'Сохранить'}</button>
                <button className="btn" disabled={!canDeleteSelected || saving} onClick={removeSelected}>Удалить</button>
              </div>

              <div className="hr" />
              <div className="muted">Вложения к записи</div>
              <div className="muted" style={{ marginTop: 8 }}>
                Здесь отображаются файлы, уже прикреплённые к выбранной записи. Скачивание выполняется через защищённую signed URL ссылку объекта.
              </div>

              <div style={{ display: 'grid', gap: 8, marginTop: 12 }}>
                {(selected.attachments || []).length === 0 ? (
                  <div className="muted">Вложений пока нет.</div>
                ) : (
                  selected.attachments.map((att) => (
                    <div key={att.id} className="row" style={{ justifyContent: 'space-between', gap: 8 }}>
                      <div>
                        <div style={{ fontWeight: 600 }}>{att.originalName}</div>
                        <div className="muted">{bytes(att.size)} · {fmt(att.createdAt)}</div>
                      </div>
                      <div className="row">
                        <a className="btn" href={att.downloadUrl} target="_blank" rel="noreferrer">Скачать</a>
                        <button className="btn" disabled={!canEditSelected || uploading} onClick={() => removeAttachment(att.id)}>Удалить файл</button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="hr" />
              <div className="muted">Результат анализа</div>
              <div style={{ marginTop: 8 }}><b>Найдено:</b> {(selected.found || []).join(', ') || '—'}</div>
              <div style={{ marginTop: 8 }}><b>Не хватает:</b> {(selected.missing || []).join(', ') || '—'}</div>
              {Array.isArray(selected.orderIssues) && selected.orderIssues.length > 0 && (
                <ul className="list" style={{ marginTop: 8 }}>
                  {selected.orderIssues.map((x, i) => <li key={i}>{x.message}</li>)}
                </ul>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}

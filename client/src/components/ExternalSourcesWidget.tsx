import React, { useState } from 'react'
import { api } from '../lib/api'

export default function ExternalSourcesWidget() {
  const [query, setQuery] = useState('машинное обучение')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [items, setItems] = useState<any[]>([])

  async function search() {
    const q = query.trim()
    if (!q) return
    setLoading(true)
    setError('')
    try {
      const data = await api.searchSources(q)
      setItems(data.items || [])
    } catch (e: any) {
      setError(`${e.code || 'ERROR'}: ${e.message || 'Не удалось загрузить внешние данные'}`)
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card" aria-labelledby="external-sources-title">
      <h2 id="external-sources-title">Подбор источников через внешний API</h2>
      <p className="muted">
        Этот блок использует внешний сервис Google Books через backend-адаптер: сервер нормализует ответ,
        ограничивает частоту запросов и обрабатывает ошибки.
      </p>

      <div className="row" style={{ marginTop: 12, alignItems: 'end' }}>
        <div style={{ flex: 1 }}>
          <div className="muted" style={{ marginBottom: 6 }}>Тема или ключевое слово</div>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Например: базы данных" />
        </div>
        <button className="btn primary" onClick={search} disabled={loading}>
          {loading ? 'Ищем…' : 'Подобрать источники'}
        </button>
      </div>

      {error && <div style={{ marginTop: 10 }} className="badge">{error}</div>}

      {items.length > 0 && (
        <div style={{ display: 'grid', gap: 10, marginTop: 14 }}>
          {items.map((item) => (
            <article key={item.id} className="card" style={{ padding: 12 }}>
              <div className="row" style={{ alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0, fontSize: '1rem' }}>{item.title}</h3>
                  <div className="muted" style={{ marginTop: 6 }}>
                    {(item.authors || []).join(', ') || 'Автор не указан'}
                    {item.publishedYear ? ` · ${item.publishedYear}` : ''}
                    {item.publisher ? ` · ${item.publisher}` : ''}
                  </div>
                  {item.description && <p style={{ marginTop: 8 }}>{item.description}</p>}
                </div>
                {item.thumbnail ? (
                  <img
                    src={item.thumbnail}
                    alt={`Обложка книги ${item.title}`}
                    loading="lazy"
                    style={{ width: 80, height: 110, objectFit: 'cover', borderRadius: 12 }}
                  />
                ) : null}
              </div>
              {item.infoUrl && (
                <div style={{ marginTop: 10 }}>
                  <a className="btn" href={item.infoUrl} target="_blank" rel="noreferrer">Открыть источник</a>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

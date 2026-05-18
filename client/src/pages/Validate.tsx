import React, { useMemo, useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../state/auth'
import Seo from '../components/Seo'

const SAMPLE = [
  'Введение',
  'Теоретическая часть',
  'Практическая часть',
  'Методология',
  'Результаты',
  'Выводы',
  'Список литературы',
  'Приложения'
].join('\n')

export default function Validate() {
  const { isAuthed } = useAuth()
  const [label, setLabel] = useState('Мой отчёт')
  const [notes, setNotes] = useState('')
  const [text, setText] = useState('')
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const missingText = useMemo(() => (result?.missing || []).join(', '), [result])
  const foundText = useMemo(() => (result?.found || []).join(', '), [result])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setResult(null)

    if (!isAuthed) {
      setError('Нужно войти, чтобы отправить проверку на сервер и сохранить в историю.')
      return
    }

    if (!text.trim() && !uploadFile) {
      setError('Вставь текст отчёта или выбери файл.')
      return
    }

    setLoading(true)
    try {
      const finalLabel = label.trim() || uploadFile?.name || 'Мой отчёт'
      const data = uploadFile
        ? await api.createCheckFromFile({ label: finalLabel, notes, file: uploadFile })
        : await api.createCheck({ label: finalLabel, text, notes })
      setResult(data)
    } catch (e2: any) {
      setError(`${e2.code || 'ERROR'}: ${e2.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Seo
        title="Проверка структуры отчёта"
        description="Загрузка текста или файла для анализа структуры отчёта. Закрытый пользовательский раздел сервиса Struct Check."
        canonicalPath="/validate"
        robots="noindex,nofollow"
      />
      <div className="grid">
        <div className="card">
          <div className="row">
            <h1>Проверка структуры</h1>
            <button className="btn" type="button" onClick={() => { setText(SAMPLE); setUploadFile(null) }}>Вставить пример</button>
          </div>
          <p className="muted">Можно проверить текст вручную или загрузить TXT / MD / PDF / DOCX — сервер извлечёт текст, выполнит анализ и сохранит запись в историю. Исходный файл сохраняется в объектном хранилище.</p>

          <form onSubmit={onSubmit}>
            <div style={{ marginTop: 10 }}>
              <div className="muted" style={{ marginBottom: 6 }}>Название проверки</div>
              <input value={label} onChange={e => setLabel(e.target.value)} maxLength={120} />
            </div>

            <div style={{ marginTop: 10 }}>
              <div className="muted" style={{ marginBottom: 6 }}>Заметки</div>
              <textarea value={notes} onChange={e => setNotes(e.target.value)} style={{ minHeight: 90 }} />
            </div>

            <div style={{ marginTop: 10 }}>
              <div className="muted" style={{ marginBottom: 6 }}>Текст отчёта</div>
              <textarea value={text} onChange={e => { setText(e.target.value); if (e.target.value.trim()) setUploadFile(null) }} />
            </div>

            <div style={{ marginTop: 10 }}>
              <div className="muted" style={{ marginBottom: 6 }}>Или загрузить файл</div>
              <input
                type="file"
                accept=".txt,.md,.pdf,.docx,text/plain,text/markdown,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={(e) => {
                  const next = e.target.files?.[0] || null
                  setUploadFile(next)
                  if (next && (!label.trim() || label === 'Мой отчёт')) {
                    const clean = next.name.replace(/\.[^.]+$/, '')
                    if (clean.trim()) setLabel(clean)
                  }
                  if (next) setText('')
                }}
              />
              <div className="muted" style={{ marginTop: 6 }}>Поддерживаются TXT, MD, PDF и DOCX до 5 MB.</div>
              {uploadFile && <div style={{ marginTop: 6 }} className="badge">Файл: {uploadFile.name}</div>}
            </div>

            <div className="row" style={{ marginTop: 12 }}>
              <button className="btn primary" disabled={loading} type="submit">
                {loading ? 'Проверяем…' : (uploadFile ? 'Загрузить и проверить' : 'Проверить')}
              </button>
              <span className="muted">После загрузки исходный файл прикрепляется к записи автоматически.</span>
            </div>

            {error && <div style={{ marginTop: 10 }} className="badge">{error}</div>}
          </form>
        </div>

        <div className="card">
          <h2>Результат</h2>
          {!result ? (
            <div className="muted">Пока нет результата. Нажми «Проверить» или «Загрузить и проверить».</div>
          ) : (
            <>
              <div className="row">
                <span className="badge">{result.ok ? 'OK' : 'Есть пропуски'}</span>
                <span className="muted">символов: {result.inputLength}</span>
              </div>
              {Array.isArray(result.attachments) && result.attachments.length > 0 && (
                <div style={{ marginTop: 10 }} className="muted">Прикреплён файл: {result.attachments[0].originalName}</div>
              )}
              <div className="hr" />
              <div className="muted">Найдено</div>
              <div style={{ marginTop: 6 }}>{foundText || '—'}</div>
              <div className="hr" />
              <div className="muted">Не хватает</div>
              <div style={{ marginTop: 6 }}>{missingText || '—'}</div>
              {Array.isArray(result.orderIssues) && result.orderIssues.length > 0 && (
                <>
                  <div className="hr" />
                  <div className="muted">Проблемы порядка</div>
                  <ul className="list">
                    {result.orderIssues.map((x: any, i: number) => <li key={i}>{x.message}</li>)}
                  </ul>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}

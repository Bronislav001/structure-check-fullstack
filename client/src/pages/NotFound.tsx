import React from 'react'
import { Link } from 'react-router-dom'
import Seo from '../components/Seo'

export default function NotFound() {
  return (
    <div className="card">
      <Seo
        title="Страница не найдена"
        description="Запрошенная страница сервиса Struct Check не найдена."
        canonicalPath="/404"
        robots="noindex,nofollow"
      />
      <h1>404 — страница не найдена</h1>
      <p className="muted">Проверь адрес или вернись на главную страницу.</p>
      <div style={{ marginTop: 12 }}>
        <Link className="btn primary" to="/">На главную</Link>
      </div>
    </div>
  )
}

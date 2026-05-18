import React from 'react'
import Seo from '../components/Seo'

const TEMPLATE = [
  'Введение',
  'Теоретическая часть',
  'Практическая часть',
  'Методология',
  'Результаты',
  'Выводы',
  'Список литературы',
  'Приложения'
]

export default function Template() {
  return (
    <>
      <Seo
        title="Эталонная структура отчёта"
        description="Эталонный шаблон отчёта: обязательные разделы, которые используются в сервисе Struct Check для анализа структуры документа."
        canonicalPath="/template"
        jsonLd={{
          '@context': 'https://schema.org',
          '@type': 'TechArticle',
          headline: 'Эталонная структура отчёта',
          description: 'Шаблон обязательных разделов учебного отчёта для проверки структуры.',
        }}
      />
      <div className="grid">
        <div className="card">
          <h1>Эталонный шаблон</h1>
          <ul className="list">
            {TEMPLATE.map(s => <li key={s}>{s}</li>)}
          </ul>
        </div>

        <div className="card">
          <h2>Как проходит проверка</h2>
          <ul className="list">
            <li>Пользователь вводит текст отчёта или загружает файл.</li>
            <li>Сервер извлекает текст и ищет заголовки разделов из эталона.</li>
            <li>Система возвращает найденные и отсутствующие разделы.</li>
            <li>Результат сохраняется в историю и может быть отредактирован.</li>
          </ul>
        </div>
      </div>
    </>
  )
}

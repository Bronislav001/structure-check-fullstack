import React, { Suspense, lazy } from 'react'
import Seo from '../components/Seo'

const ExternalSourcesWidget = lazy(() => import('../components/ExternalSourcesWidget'))

export default function Home() {
  return (
    <>
      <Seo
        title="Проверка структуры учебных отчётов"
        description="Struct Check помогает проверить структуру учебного отчёта, сверить разделы с эталоном и подобрать внешние источники по теме."
        canonicalPath="/"
        jsonLd={{
          '@context': 'https://schema.org',
          '@type': 'WebSite',
          name: 'Struct Check',
          url: `${window.location.origin}/`,
          description: 'Сервис для проверки структуры учебных отчётов и подбора источников по теме.',
        }}
      />

      <div className="grid">
        <section className="card">
          <h1>Проверка структуры учебных отчётов</h1>
          <p>
            Сервис помогает быстро проверить, какие разделы уже есть в отчёте, каких разделов не хватает,
            и сохранить результат анализа в историю пользователя.
          </p>
          <h2>Как пользоваться сайтом</h2>
          <ul className="list">
            <li>Откройте раздел <b>«Эталон»</b> и ознакомьтесь со структурой отчёта.</li>
            <li>Перейдите в раздел проверки после входа в аккаунт.</li>
            <li>Вставьте текст отчёта или загрузите файл для анализа.</li>
            <li>Система покажет найденные и отсутствующие разделы.</li>
          </ul>
        </section>

        <section className="card">
          <h2>Что умеет сервис</h2>
          <ul className="list">
            <li>Проверяет структуру отчёта по эталонному шаблону.</li>
            <li>Сохраняет результаты в историю с поиском, фильтрами и сортировкой.</li>
            <li>Работает с файлами через объектное хранилище MinIO (S3-compatible).</li>
            <li>Подбирает полезные источники по теме через внешний API Google Books.</li>
          </ul>
        </section>
      </div>

      <Suspense fallback={<div className="card"><div className="muted">Загружаем рекомендации по источникам…</div></div>}>
        <ExternalSourcesWidget />
      </Suspense>
    </>
  )
}

import React from 'react'

export default function Hero() {
  return (
    <section style={styles.wrap} aria-label="Описание сервиса Struct Check">
      <div style={styles.inner}>
        <div style={styles.h1}>Проверка учебных отчётов по структуре</div>
        <p style={styles.p}>
          Сервис сравнивает текст отчёта с эталонным шаблоном, сохраняет историю проверок,
          работает с объектным хранилищем и помогает подобрать внешние источники по теме.
        </p>
      </div>
    </section>
  )
}

const styles = {
  wrap: {
    background: 'linear-gradient(135deg, #0b1b3a 0%, #1f4dff 100%)',
    padding: '28px 16px',
  },
  inner: {
    maxWidth: 1100,
    margin: '0 auto',
    borderRadius: 18,
    padding: '28px 24px',
    color: 'white',
    boxShadow: '0 12px 30px rgba(0,0,0,0.18)',
    background: 'rgba(255,255,255,0.08)',
    backdropFilter: 'blur(6px)',
  },
  h1: { margin: 0, fontSize: 36, lineHeight: 1.15, fontWeight: 800 },
  p: { margin: '10px 0 0', opacity: 0.9, fontSize: 16 },
}

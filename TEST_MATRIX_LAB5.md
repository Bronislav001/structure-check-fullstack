# Матрица тестов ЛР-5

| Область | Что проверяется | Где смотреть |
|---|---|---|
| Unit backend | Нормализация и анализ структуры отчёта | `server/tests/test_analyze.py` |
| Auth backend | Register, login, me, refresh, logout | `server/tests/test_auth_api.py` |
| RBAC backend | Запрет чужих данных, admin scope, смена ролей | `server/tests/test_checks_api.py`, `server/tests/test_lab5_extra_api.py` |
| CRUD backend | Создание, просмотр, редактирование, удаление проверок | `server/tests/test_checks_api.py` |
| Фильтры backend | Поиск, статус, сортировка, пагинация | `server/tests/test_lab5_extra_api.py` |
| Файлы backend | Upload, download, delete, signed URL | `server/tests/test_checks_api.py`, `server/tests/test_lab5_extra_api.py` |
| SEO backend | `robots.txt`, `sitemap.xml` | `server/tests/test_seo_and_external_api.py` |
| External API backend | Успех, отказ, валидация query | `server/tests/test_seo_and_external_api.py`, `server/tests/test_lab5_extra_api.py` |
| Frontend SEO | Dynamic meta, canonical, OG, JSON-LD | `client/src/__tests__/Seo.test.tsx` |
| Frontend auth | Login success/error | `client/src/__tests__/Login.test.tsx` |
| Frontend RBAC | Protected routes and permission deny | `client/src/__tests__/RequirePerm.test.tsx` |
| Frontend forms | Submit validation text, guest block | `client/src/__tests__/Validate.test.tsx` |
| Frontend external API | Success and graceful error | `client/src/__tests__/ExternalSourcesWidget.test.tsx` |
| E2E | User navigation and external API отказ | `client/e2e/app.spec.ts` |

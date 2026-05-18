# Лабораторная работа №5 — комплексное тестирование

Тема проекта: **Struct Check — проверка учебных отчётов по структуре**.

В лабораторной работе добавлено полноценное тестирование backend, frontend и E2E-сценариев. Тесты проверяют не отдельную кнопку, а основные рисковые места проекта: авторизацию, роли, CRUD, фильтры, загрузку файлов, signed URL, SEO endpoint'ы и внешний API.

## 1. Что реализовано

### Backend: pytest
Добавлены unit и integration tests:

- unit-тесты сервисной логики анализа отчёта;
- auth flow: register/login/me/refresh/logout;
- проверка 401 без токена;
- проверка плохого пароля;
- CRUD проверок;
- запрет чтения чужих записей;
- admin scope `all`;
- серверные фильтры, поиск, сортировка и пагинация;
- загрузка файла, скачивание по signed URL и удаление вложения;
- запрет неподдерживаемого типа файла;
- проверка некорректного signed URL;
- `robots.txt` и `sitemap.xml`;
- внешний API: успешный ответ, ошибка и валидация короткого запроса;
- проверка role endpoint: обычный user не может смотреть пользователей, admin может менять роль.

Итоговая проверка backend:

```text
18 passed
```

### Frontend: Vitest + Testing Library
Добавлены тесты компонентов и пользовательских сценариев:

- SEO-компонент записывает `title`, `description`, `canonical`, `robots`, `og:*`, JSON-LD;
- `RequirePerm` редиректит гостя на вход;
- `RequirePerm` показывает отказ при недостатке прав;
- `Login` отправляет email/password и сохраняет сессию;
- `Login` показывает ошибку backend;
- `Validate` блокирует гостя;
- `Validate` отправляет текст отчёта авторизованным пользователем;
- `ExternalSourcesWidget` показывает внешний источник при успехе;
- `ExternalSourcesWidget` показывает ошибку при отказе внешнего API.

Итоговая проверка frontend:

```text
5 test files passed, 9 tests passed
```

### E2E: Playwright
Добавлены сквозные тесты:

- гость при открытии `/history` перенаправляется на страницу входа;
- при отказе внешнего API приложение не ломается и показывает понятную ошибку.

## 2. Тестовая инфраструктура

- Для backend используется отдельная временная SQLite-БД через `tmp_path`.
- Между тестами состояние изолируется.
- Объектное хранилище мокируется локальным provider'ом, чтобы тесты не зависели от MinIO.
- Внешний API мокируется через `monkeypatch` на backend и через `vi.mock` на frontend.
- E2E запускается через Playwright с отдельным dev-сервером.

## 3. Команды запуска

### Backend

```powershell
cd C:\Users\Asus\Desktop\lab5proj\server
.\.venv\Scripts\Activate.ps1
pytest -q
```

Ожидаемый результат:

```text
18 passed
```

### Frontend

```powershell
cd C:\Users\Asus\Desktop\lab5proj\client
npm install
npm run test
```

Ожидаемый результат:

```text
Test Files  5 passed
Tests       9 passed
```

### E2E

```powershell
cd C:\Users\Asus\Desktop\lab5proj\client
npx playwright install
npm run test:e2e
```

## 4. Что показывать преподавателю

1. Открыть папку `server/tests` и показать backend-тесты.
2. Запустить `pytest -q` и показать `18 passed`.
3. Открыть папку `client/src/__tests__` и показать frontend-тесты.
4. Запустить `npm run test` и показать `5 passed`, `9 passed`.
5. Открыть папку `client/e2e` и показать Playwright-сценарии.
6. При наличии времени запустить `npm run test:e2e`.
7. Объяснить, что внешние зависимости мокируются: Google Books и объектное хранилище.

## 5. Короткая речь для сдачи

> В пятой лабораторной я реализовал комплексное тестирование проекта. На backend добавлены unit и integration тесты на pytest: проверяется авторизация, refresh/logout, роли, CRUD, фильтрация, файлы, signed URL, SEO endpoints и внешний API. На frontend добавлены тесты компонентов и пользовательских сценариев на Vitest и Testing Library: проверяется форма входа, защита маршрутов, проверка отчёта, SEO и обработка ошибок внешнего API. Также добавлены E2E-сценарии на Playwright. Для тестов используется отдельное тестовое окружение: временная БД, фикстуры, мок внешнего API и мок объектного хранилища.

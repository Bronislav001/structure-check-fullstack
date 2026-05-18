# Лабораторная работа №6

## Тема
Контейнеризация и автоматизация развертывания веб-приложения Struct Check.

## Что сделано

### 1. Архитектура контейнеризации
Выделены сервисы:

| Сервис | Назначение | Порт |
|---|---|---|
| `frontend` | React-приложение, собранное в static и отданное через Nginx | `80` |
| `backend` | FastAPI API | `8080` |
| `minio` | S3-compatible объектное хранилище | `9000`, `9001` |
| `minio-init` | автоматическое создание bucket | внутренний сервис |
| `backend-storage` | volume для SQLite-БД и служебных данных | volume |
| `minio-data` | volume для объектов MinIO | volume |

Сеть сервисов: `app-net`.

### 2. Dockerfile
Добавлены:

- `server/Dockerfile` для FastAPI;
- `client/Dockerfile` для сборки React и запуска через Nginx;
- `client/nginx.conf` для раздачи SPA и reverse proxy на backend;
- `.dockerignore` для backend и frontend.

### 3. Docker Compose
Добавлен `docker-compose.yml`, который запускает:

- frontend;
- backend;
- MinIO;
- minio-init;
- volumes;
- network;
- healthchecks.

### 4. Reverse proxy
Nginx внутри `frontend`:

- отдаёт React SPA;
- проксирует `/api/*` на FastAPI;
- проксирует `/robots.txt` и `/sitemap.xml` на backend;
- обрабатывает fallback на `index.html` для React Router.

### 5. Конфигурация и безопасность
Добавлены:

- `.env.example`;
- `.gitignore`;
- переменные окружения для MinIO, signed URL и внешнего API;
- исключение `.env`, `storage`, `minio-data`, `.venv`, `node_modules` из репозитория.

### 6. Healthcheck
Настроены healthcheck:

- backend: `GET /api/health`;
- frontend: HTTP-проверка корня Nginx;
- MinIO: health endpoint MinIO.

### 7. CI/CD
Добавлен `.github/workflows/ci.yml` с тремя тестовыми этапами:

1. `Backend tests (pytest)` — серверные unit/integration тесты;
2. `Frontend tests (Vitest)` — тесты React-компонентов и сценариев;
3. `E2E tests (Playwright)` — сквозные проверки через браузер.

Docker-сборка запускается только после успешного прохождения всех трёх тестовых этапов.

## Как запустить

```powershell
docker compose up --build -d
```

После запуска:

- сайт: http://localhost
- backend docs: http://localhost:8080/docs
- MinIO console: http://localhost:9001

Логин MinIO по умолчанию:

- `minioadmin`
- `minioadmin`

## Как проверить

```powershell
docker compose ps
```

Должны быть запущены сервисы:

- `struct-check-frontend`;
- `struct-check-backend`;
- `struct-check-minio`.

Проверка backend:

```powershell
curl http://localhost:8080/api/health
```

Проверка frontend:

```powershell
curl http://localhost
```

Проверка MinIO:

```text
http://localhost:9001
```

## Что показывать на сдаче

1. Открыть `docker-compose.yml` и показать сервисы.
2. Открыть `server/Dockerfile` и показать контейнеризацию FastAPI.
3. Открыть `client/Dockerfile` и `client/nginx.conf`.
4. Запустить `docker compose up --build -d`.
5. Показать `docker compose ps`.
6. Открыть сайт на `http://localhost`.
7. Открыть Swagger на `http://localhost:8080/docs`.
8. Открыть MinIO Console на `http://localhost:9001`.
9. Загрузить файл в приложении и показать объект в MinIO.
10. Открыть `.github/workflows/ci.yml` и показать 3 тестовых блока: backend, frontend, E2E.
11. Показать, что `Docker build after 3 tests` зависит от всех трёх тестов.

## Короткая речь

В шестой лабораторной я контейнеризировал клиентскую и серверную части приложения. Frontend собирается как React static build и раздаётся через Nginx, который также проксирует API-запросы на FastAPI. Backend запускается в отдельном контейнере. Для файлов используется S3-compatible хранилище MinIO. Все сервисы запускаются через docker-compose одной командой, настроены сети, volumes, переменные окружения и healthcheck. Также добавлен CI/CD workflow: сначала запускаются три группы тестов — backend, frontend и E2E, а Docker-сборка выполняется только после их успешного прохождения.

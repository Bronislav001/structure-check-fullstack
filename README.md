# Struct Check


## Быстрый запуск

```powershell
docker compose up --build -d
```

Открыть:

- Frontend: http://localhost
- Swagger: http://localhost:8080/docs
- MinIO: http://localhost:9001

MinIO login/password:

```text
minioadmin
minioadmin
```

## Остановка

```powershell
docker compose down
```

Полная очистка с volumes:

```powershell
docker compose down -v
```

## Что добавлено в ЛР-6

- `server/Dockerfile` — образ FastAPI.
- `client/Dockerfile` — сборка React и запуск через Nginx.
- `client/nginx.conf` — reverse proxy и SPA fallback.
- `docker-compose.yml` — запуск frontend, backend, MinIO, volumes и network.
- `.env.example` — пример переменных окружения.
- `.dockerignore` — исключение лишних файлов из образов.
- `.github/workflows/ci.yml` — CI/CD: 3 тестовых блока и docker build после них.
- `REPORT_LAB6.md` — что показывать на сдаче.
- `RUN_LAB6_WINDOWS.md` — команды запуска на Windows.
- `DOCKER_ARCHITECTURE.md` — схема контейнеризации.
- `CI_CD_3_TESTS.md` — описание 3 тестовых блоков в CI/CD.

## Команды для проверки

```powershell
docker compose ps
curl http://localhost:8080/api/health
```

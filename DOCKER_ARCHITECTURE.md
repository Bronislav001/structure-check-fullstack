# Архитектура Docker-развертывания

```text
Browser
  |
  | http://localhost
  v
frontend container / Nginx
  |-- serves React SPA
  |-- /api/* ------------> backend container / FastAPI
  |-- /robots.txt -------> backend container
  |-- /sitemap.xml ------> backend container
                            |
                            | S3 API
                            v
                         minio container
```

## Почему так

- Frontend и backend отделены в разные контейнеры.
- Nginx выполняет роль reverse proxy.
- MinIO вынесен отдельным сервисом как S3-compatible object storage.
- SQLite-БД хранится в volume `backend-storage`.
- Файлы хранятся в volume `minio-data` через MinIO.
- Сервисы общаются внутри Docker-сети `app-net`.

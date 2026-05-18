# Запуск ЛР-6 на Windows

## 1. Проверить Docker

```powershell
docker version
docker compose version
```

Docker Desktop должен быть запущен.

## 2. Перейти в папку проекта

```powershell
cd C:\Users\Asus\Desktop\lab6proj
```

## 3. Запустить всё одной командой

```powershell
docker compose up --build -d
```

## 4. Проверить контейнеры

```powershell
docker compose ps
```

## 5. Открыть в браузере

- Frontend: http://localhost
- Backend Swagger: http://localhost:8080/docs
- MinIO Console: http://localhost:9001

MinIO:

- login: `minioadmin`
- password: `minioadmin`

## 6. Логи

```powershell
docker compose logs -f backend
```

или:

```powershell
docker compose logs -f frontend
```

## 7. Остановить

```powershell
docker compose down
```

## 8. Полностью очистить volumes

Только если нужно удалить БД и файлы:

```powershell
docker compose down -v
```

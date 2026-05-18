# ЛР-1 — Ролевая модель доступа (RBAC) + FastAPI + React TS

Проект: «Проверка учебных отчётов по структуре» (тема №14).

## Используемые технологии
- Backend: Python + FastAPI
- Frontend: TypeScript + React (Vite)
- Git: репозиторий с осмысленными коммитами

## Роли и права
Роли: `guest`, `user`, `manager`, `admin`.

| Действие | Permission | user | manager | admin |
|---|---|---:|---:|---:|
| Создать проверку | `checks:create` | ✅ | ✅ | ✅ |
| Смотреть свои проверки | `checks:read_own` | ✅ | ✅ | ✅ |
| Редактировать свои проверки | `checks:update_own` | ✅ | ✅ | ✅ |
| Удалять свои проверки | `checks:delete_own` | ✅ | ✅ | ✅ |
| Смотреть все проверки | `checks:read_any` | ❌ | ✅ | ✅ |
| Редактировать любые проверки | `checks:update_any` | ❌ | ✅ | ✅ |
| Удалять любые проверки | `checks:delete_any` | ❌ | ❌ | ✅ |
| Смотреть пользователей | `users:read_any` | ❌ | ❌ | ✅ |
| Менять роли пользователей | `users:update_role` | ❌ | ❌ | ✅ |

## Реализация (Backend)
- Права описаны в `server/app/rbac.py`.
- На эндпоинтах используется проверка прав и владельца.
- При недостатке прав возвращается **403 Forbidden**.

Админские эндпоинты:
- `GET /api/users` — список пользователей (только admin)
- `PATCH /api/users/{id}/role` — смена роли (только admin)

## Реализация (Frontend)
- RBAC клиентский: `client/src/lib/rbac.ts`.
- Скрытие/блокировка элементов UI, если нет прав.
- Защита маршрутов компонентом `RequirePerm`.

## Сценарий демонстрации на защите
1) **guest**: без входа нет доступа к истории/проверке.
2) **user**: создать проверку, увидеть в истории (только свои).
3) **manager**: включить «Все проверки» и увидеть чужие; удалить чужую нельзя (403).
4) **admin**: открыть `/admin/users`, поменять роль; удалить любую проверку.

## Запуск
### Один раз (Python зависимости)
```bash
cd server
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### Далее (как раньше одной командой)
```bash
cd ..
npm i
npm run dev
```

## Назначить первого admin
1) Зарегистрироваться.
2) Выполнить:
```bash
cd server
python -m scripts.make_admin you@example.com
```

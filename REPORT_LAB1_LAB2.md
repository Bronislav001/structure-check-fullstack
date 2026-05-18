# Краткая защита ЛР-1 и ЛР-2

## ЛР-1
- Роли: guest, user, manager, admin.
- Запрет по умолчанию и принцип минимальных привилегий.
- 403 при недостатке прав.
- Admin-only endpoint: `PATCH /api/users/{id}/role`.
- На клиенте скрытие вкладок и защита маршрутов.

## ЛР-2
- Access token: короткоживущий JWT.
- Refresh token: отдельный случайный токен, хранится на сервере в виде хеша.
- Маршруты: `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET /api/auth/me`.
- Архитектура backend: API → service → repository.
- На клиенте централизованное состояние аутентификации и автообновление access token.

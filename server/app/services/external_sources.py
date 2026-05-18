from __future__ import annotations

import os
import time
from typing import Any

import httpx

from ..errors import ApiError

GOOGLE_BOOKS_API_URL = os.getenv('GOOGLE_BOOKS_API_URL', 'https://www.googleapis.com/books/v1/volumes')
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY', '').strip()
GOOGLE_BOOKS_TIMEOUT_SECONDS = float(os.getenv('GOOGLE_BOOKS_TIMEOUT_SECONDS', '8'))
GOOGLE_BOOKS_MAX_RESULTS = min(10, max(1, int(os.getenv('GOOGLE_BOOKS_MAX_RESULTS', '5'))))
GOOGLE_BOOKS_RATE_LIMIT_SECONDS = float(os.getenv('GOOGLE_BOOKS_RATE_LIMIT_SECONDS', '1.0'))
GOOGLE_BOOKS_RETRIES = min(3, max(1, int(os.getenv('GOOGLE_BOOKS_RETRIES', '2'))))

_LAST_REQUEST_TS = 0.0


def _throttle() -> None:
    global _LAST_REQUEST_TS
    now = time.monotonic()
    delta = now - _LAST_REQUEST_TS
    if delta < GOOGLE_BOOKS_RATE_LIMIT_SECONDS:
        time.sleep(GOOGLE_BOOKS_RATE_LIMIT_SECONDS - delta)
    _LAST_REQUEST_TS = time.monotonic()


async def search_sources(query: str) -> dict[str, Any]:
    q = str(query or '').strip()
    if len(q) < 2:
        raise ApiError(400, 'VALIDATION_ERROR', 'query is too short')

    params = {
        'q': q,
        'maxResults': GOOGLE_BOOKS_MAX_RESULTS,
        'printType': 'books',
        'projection': 'lite',
        'langRestrict': 'ru',
    }
    if GOOGLE_BOOKS_API_KEY:
        params['key'] = GOOGLE_BOOKS_API_KEY

    last_error: Exception | None = None
    for attempt in range(GOOGLE_BOOKS_RETRIES):
        try:
            _throttle()
            async with httpx.AsyncClient(timeout=GOOGLE_BOOKS_TIMEOUT_SECONDS) as client:
                response = await client.get(GOOGLE_BOOKS_API_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            return _normalize_google_books(payload, q)
        except httpx.TimeoutException as exc:
            last_error = exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response else 502
            if status == 429:
                last_error = exc
                time.sleep(1 + attempt)
                continue
            raise ApiError(502, 'EXTERNAL_API_ERROR', f'google books responded with HTTP {status}') from exc
        except Exception as exc:
            last_error = exc
        if attempt + 1 < GOOGLE_BOOKS_RETRIES:
            time.sleep(0.5 * (attempt + 1))

    raise ApiError(502, 'EXTERNAL_API_ERROR', 'failed to load external sources') from last_error


def _normalize_google_books(payload: dict[str, Any], query: str) -> dict[str, Any]:
    items = payload.get('items') or []
    normalized = []
    for item in items:
        info = item.get('volumeInfo') or {}
        normalized.append(
            {
                'id': item.get('id') or '',
                'title': info.get('title') or 'Без названия',
                'authors': info.get('authors') or [],
                'publisher': info.get('publisher') or '',
                'publishedYear': str(info.get('publishedDate') or '')[:4],
                'description': (info.get('description') or '')[:400],
                'thumbnail': ((info.get('imageLinks') or {}).get('thumbnail') or '').replace('http://', 'https://'),
                'infoUrl': info.get('infoLink') or '',
            }
        )
    return {'query': query, 'provider': 'google-books', 'items': normalized}

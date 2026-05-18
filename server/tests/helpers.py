from __future__ import annotations

from urllib.parse import urlparse

from fastapi.testclient import TestClient


def register_and_login(client: TestClient, *, email: str, name: str = "User", password: str = "secret123") -> dict:
    response = client.post('/api/auth/register', json={'email': email, 'name': name, 'password': password})
    assert response.status_code == 201
    return response.json()


def auth_header(session: dict) -> dict[str, str]:
    return {'Authorization': f"Bearer {session['accessToken']}"}


def signed_download_path(download_url: str) -> str:
    parsed = urlparse(download_url)
    path = parsed.path
    if parsed.query:
        path += '?' + parsed.query
    return path

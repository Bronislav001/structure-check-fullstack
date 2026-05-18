from __future__ import annotations

import sqlite3
from tests.helpers import auth_header, register_and_login, signed_download_path
from tests.test_checks_api import FULL_TEXT


def promote_user(email: str, role: str = 'admin') -> None:
    from app import db as db_module
    con = sqlite3.connect(db_module.DB_PATH)
    try:
        con.execute("UPDATE users SET role = ? WHERE email = ?", (role, email))
        con.commit()
    finally:
        con.close()


def test_filters_sorting_and_pagination_are_server_side(client):
    session = register_and_login(client, email='filter@example.com', name='Filter')
    headers = auth_header(session)

    client.post('/api/checks/', json={'label': 'alpha ok', 'text': FULL_TEXT}, headers=headers)
    client.post('/api/checks/', json={'label': 'beta issues', 'text': 'Введение\nЭто достаточно длинный отчёт без остальных обязательных разделов.'}, headers=headers)
    client.post('/api/checks/', json={'label': 'gamma ok', 'text': FULL_TEXT}, headers=headers)

    only_issues = client.get('/api/checks/?status=issues', headers=headers)
    assert only_issues.status_code == 200
    assert only_issues.json()['total'] == 1
    assert only_issues.json()['items'][0]['label'] == 'beta issues'

    search = client.get('/api/checks/?q=gamma', headers=headers)
    assert search.status_code == 200
    assert search.json()['total'] == 1

    sorted_page = client.get('/api/checks/?sortBy=label&sortDir=asc&page=1&pageSize=2', headers=headers)
    assert sorted_page.status_code == 200
    body = sorted_page.json()
    assert body['page'] == 1
    assert body['pageSize'] == 2
    assert [x['label'] for x in body['items']] == ['alpha ok', 'beta issues']


def test_admin_can_change_role_and_regular_user_cannot(client):
    admin = register_and_login(client, email='role-admin@example.com', name='Admin')
    target = register_and_login(client, email='target@example.com', name='Target')
    promote_user('role-admin@example.com', 'admin')
    admin = client.post('/api/auth/login', json={'email': 'role-admin@example.com', 'password': 'secret123'}).json()

    forbidden = client.get('/api/users/', headers=auth_header(target))
    assert forbidden.status_code == 403

    users = client.get('/api/users/', headers=auth_header(admin))
    assert users.status_code == 200
    target_id = next(u['id'] for u in users.json()['items'] if u['email'] == 'target@example.com')

    changed = client.patch(f'/api/users/{target_id}/role', json={'role': 'manager'}, headers=auth_header(admin))
    assert changed.status_code == 200
    assert changed.json()['user']['role'] == 'manager'


def test_upload_rejects_unsupported_content_type(client):
    session = register_and_login(client, email='bad-file@example.com', name='Bad File')
    files = {'upload': ('script.exe', b'not allowed', 'application/x-msdownload')}
    created = client.post('/api/checks/from-upload', files=files, data={'label': 'bad'}, headers=auth_header(session))
    assert created.status_code == 400
    assert created.json()['code'] == 'VALIDATION_ERROR'


def test_signed_download_url_rejects_bad_token(client):
    session = register_and_login(client, email='signed@example.com', name='Signed')
    files = {'upload': ('report.txt', FULL_TEXT.encode('utf-8'), 'text/plain')}
    created = client.post('/api/checks/from-upload', files=files, data={'label': 'signed'}, headers=auth_header(session))
    attachment = created.json()['attachments'][0]

    url = signed_download_path(attachment['downloadUrl'])
    bad_url = url.split('token=')[0] + 'token=1.bad'
    response = client.get(bad_url)
    assert response.status_code == 403
    assert response.json()['code'] == 'BAD_SIGNED_URL'


def test_external_api_validates_short_query(client):
    response = client.get('/api/external/sources?q=a')
    assert response.status_code in (400, 422)

from urllib.parse import urlparse

from tests.helpers import auth_header, register_and_login, signed_download_path

FULL_TEXT = "\n".join([
    'Введение',
    'Теоретическая часть',
    'Практическая часть',
    'Методология',
    'Результаты',
    'Выводы',
    'Список литературы',
    'Приложения',
])


def test_user_can_crud_own_checks(client):
    session = register_and_login(client, email='user1@example.com', name='User 1')
    created = client.post('/api/checks/', json={'label': 'Мой отчёт', 'text': FULL_TEXT, 'notes': 'черновик'}, headers=auth_header(session))
    assert created.status_code == 201
    check = created.json()
    assert check['ok'] is True
    assert check['missing'] == []

    listed = client.get('/api/checks/', headers=auth_header(session))
    assert listed.status_code == 200
    assert listed.json()['total'] == 1

    patched = client.patch(f"/api/checks/{check['id']}", json={'notes': 'обновлено'}, headers=auth_header(session))
    assert patched.status_code == 200
    assert patched.json()['notes'] == 'обновлено'

    deleted = client.delete(f"/api/checks/{check['id']}", headers=auth_header(session))
    assert deleted.status_code == 200
    assert deleted.json()['deleted'] == check['id']


def test_user_cannot_read_foreign_check_but_admin_can_scope_all(client):
    user_a = register_and_login(client, email='a@example.com', name='User A')
    user_b = register_and_login(client, email='b@example.com', name='User B')

    created = client.post('/api/checks/', json={'label': 'Чужой отчёт', 'text': FULL_TEXT}, headers=auth_header(user_a))
    check_id = created.json()['id']

    forbidden = client.get(f'/api/checks/{check_id}', headers=auth_header(user_b))
    assert forbidden.status_code == 403

    # promote B to admin
    users = client.get('/api/users/', headers=auth_header(user_b))
    assert users.status_code == 403

    admin = register_and_login(client, email='admin@example.com', name='Admin')
    # make admin directly in DB through endpoint chain
    from app.db import DB_PATH
    import sqlite3
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("UPDATE users SET role = 'admin' WHERE email = ?", ('admin@example.com',))
        con.commit()
    finally:
        con.close()
    relogin = client.post('/api/auth/login', json={'email': 'admin@example.com', 'password': 'secret123'}).json()

    listed = client.get('/api/checks/?scope=all', headers=auth_header(relogin))
    assert listed.status_code == 200
    assert listed.json()['total'] >= 1


def test_create_from_upload_and_attachment_download_delete(client):
    session = register_and_login(client, email='file@example.com', name='Files')
    files = {'upload': ('report.txt', FULL_TEXT.encode('utf-8'), 'text/plain')}
    data = {'label': 'Файл', 'notes': 'из файла'}
    created = client.post('/api/checks/from-upload', files=files, data=data, headers=auth_header(session))
    assert created.status_code == 201
    payload = created.json()
    assert payload['attachments']
    attachment = payload['attachments'][0]

    dl = client.get(signed_download_path(attachment['downloadUrl']))
    assert dl.status_code == 200
    assert dl.content.decode('utf-8').startswith('Введение')

    removed = client.delete(f"/api/checks/{payload['id']}/attachments/{attachment['id']}", headers=auth_header(session))
    assert removed.status_code == 200

    updated = client.get(f"/api/checks/{payload['id']}", headers=auth_header(session))
    assert updated.status_code == 200
    assert updated.json()['attachments'] == []


def test_create_check_validation_error(client):
    session = register_and_login(client, email='validation@example.com', name='Validation')
    response = client.post('/api/checks/', json={'label': 'x', 'text': 'коротко'}, headers=auth_header(session))
    assert response.status_code == 400
    assert response.json()['code'] == 'VALIDATION_ERROR'

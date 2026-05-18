from app.security import hash_refresh_token

from tests.helpers import auth_header, register_and_login


def test_register_login_me_refresh_logout_flow(client):
    session = register_and_login(client, email='tester@example.com', name='Tester')

    me = client.get('/api/auth/me', headers=auth_header(session))
    assert me.status_code == 200
    assert me.json()['user']['email'] == 'tester@example.com'

    refreshed = client.post('/api/auth/refresh', json={'refreshToken': session['refreshToken']})
    assert refreshed.status_code == 200
    refreshed_json = refreshed.json()
    assert refreshed_json['refreshToken'] != session['refreshToken']

    logout = client.post('/api/auth/logout', json={'refreshToken': refreshed_json['refreshToken']})
    assert logout.status_code == 200
    assert logout.json() == {'ok': True}

    after_logout = client.post('/api/auth/refresh', json={'refreshToken': refreshed_json['refreshToken']})
    assert after_logout.status_code == 401
    assert after_logout.json()['code'] == 'BAD_REFRESH'


def test_me_requires_bearer_token(client):
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    assert response.json()['code'] == 'NO_TOKEN'


def test_login_with_bad_password_returns_401(client):
    register_and_login(client, email='login@example.com', name='Login')
    response = client.post('/api/auth/login', json={'email': 'login@example.com', 'password': 'wrong'})
    assert response.status_code == 401
    assert response.json()['code'] == 'INVALID_CREDENTIALS'

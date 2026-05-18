import httpx


def test_robots_and_sitemap_are_available(client):
    robots = client.get('/robots.txt')
    assert robots.status_code == 200
    assert 'Disallow: /history' in robots.text

    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    assert '<loc>http://localhost:5173/</loc>' in sitemap.text


def test_external_api_success_is_normalized(client, monkeypatch):
    async def fake_search(q: str):
        return {'query': q, 'provider': 'google-books', 'items': [{'id': '1', 'title': 'Python', 'authors': ['A'], 'publisher': 'Pub', 'publishedYear': '2024', 'description': 'desc', 'thumbnail': '', 'infoUrl': 'https://example.com'}]}

    monkeypatch.setattr('app.api.external.search_sources', fake_search)
    response = client.get('/api/external/sources?q=python')
    assert response.status_code == 200
    body = response.json()
    assert body['provider'] == 'google-books'
    assert body['items'][0]['title'] == 'Python'


def test_external_api_error_is_returned(client, monkeypatch):
    from app.errors import ApiError

    async def broken(_q: str):
        raise ApiError(502, 'EXTERNAL_API_ERROR', 'failed to load external sources')

    monkeypatch.setattr('app.api.external.search_sources', broken)
    response = client.get('/api/external/sources?q=python')
    assert response.status_code == 502
    assert response.json()['code'] == 'EXTERNAL_API_ERROR'

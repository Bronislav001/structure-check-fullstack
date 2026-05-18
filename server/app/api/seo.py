from __future__ import annotations

import os
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

PUBLIC_FRONTEND_URL = os.getenv('PUBLIC_FRONTEND_URL', 'http://localhost:5173').rstrip('/')

router = APIRouter(tags=['seo'])


@router.get('/robots.txt', response_class=PlainTextResponse, include_in_schema=False)
def robots_txt():
    body = f"""User-agent: *
Allow: /
Disallow: /login
Disallow: /register
Disallow: /validate
Disallow: /history
Disallow: /admin
Disallow: /api/

Sitemap: {PUBLIC_FRONTEND_URL}/sitemap.xml
"""
    return body


@router.get('/sitemap.xml', include_in_schema=False)
def sitemap_xml():
    urls = [
        {'loc': f'{PUBLIC_FRONTEND_URL}/', 'changefreq': 'weekly', 'priority': '1.0'},
        {'loc': f'{PUBLIC_FRONTEND_URL}/template', 'changefreq': 'monthly', 'priority': '0.8'},
    ]
    items = ''.join(
        f'<url><loc>{u["loc"]}</loc><changefreq>{u["changefreq"]}</changefreq><priority>{u["priority"]}</priority></url>'
        for u in urls
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    return Response(content=xml, media_type='application/xml')

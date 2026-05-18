from __future__ import annotations

from fastapi import APIRouter, Query

from ..services.external_sources import search_sources

router = APIRouter(prefix='/api/external', tags=['external'])


@router.get('/sources')
async def sources_search(q: str = Query(..., min_length=2, max_length=100)):
    return await search_sources(q)

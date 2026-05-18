from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.auth import router as auth_router
from .api.checks import router as checks_router, files_router
from .api.health import router as health_router
from .api.seo import router as seo_router
from .api.external import router as external_router
from .api.users import router as users_router
from .db import init_db
from .errors import (
    ApiError,
    api_error_handler,
    http_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost,http://127.0.0.1,http://localhost:5173,http://127.0.0.1:5173",
    )
    return [x.strip() for x in raw.split(",") if x.strip()]


def create_app() -> FastAPI:
    app = FastAPI(title="Structure Check API", version="6.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(health_router)
    app.include_router(seo_router)
    app.include_router(auth_router)
    app.include_router(checks_router)
    app.include_router(files_router)
    app.include_router(users_router)
    app.include_router(external_router)

    @app.on_event("startup")
    def _startup():
        init_db()

    return app


app = create_app()

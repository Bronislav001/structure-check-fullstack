from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@dataclass
class ApiError(Exception):
    status: int
    code: str
    message: str


def json_error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return json_error(exc.status, exc.code, exc.message)


async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Normalize FastAPI/Starlette errors to our format
    status = int(getattr(exc, "status_code", 500) or 500)
    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        return json_error(status, str(detail["code"]), str(detail["message"]))
    return json_error(status, "HTTP_ERROR", str(detail or "http error"))


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Keep it simple: match Node version (400 + VALIDATION_ERROR)
    # We don't expose full pydantic error details on purpose.
    return json_error(400, "VALIDATION_ERROR", "invalid request")


async def unhandled_error_handler(_: Request, __: Exception) -> JSONResponse:
    return json_error(500, "INTERNAL_ERROR", "internal error")

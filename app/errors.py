"""Map usage-billing domain errors to HTTP responses."""

from __future__ import annotations

from typing import TypeVar

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from usage_billing import LimitExceededError, NotFoundError

T = TypeVar("T")


def require(resource: T | None, message: str) -> T:
    if resource is None:
        raise NotFoundError(message)
    return resource


def _is_conflict(exc: Exception) -> bool:
    name = type(exc).__name__
    if name in {"IntegrityError", "UniqueViolation", "ForeignKeyViolation"}:
        return True
    message = str(exc).lower()
    return "unique" in message or "duplicate" in message or "foreign key" in message


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(LimitExceededError)
    async def limit_exceeded_handler(
        _request: Request, exc: LimitExceededError
    ) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
            raise exc
        if _is_conflict(exc):
            return JSONResponse(status_code=409, content={"detail": str(exc)})
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

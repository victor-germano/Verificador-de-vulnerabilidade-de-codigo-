"""Domain-level exceptions and their translation into HTTP responses.

Services and repositories raise these instead of HTTPException so that the
domain layer stays framework-agnostic (Clean Architecture: inner layers must
not depend on FastAPI). The mapping to HTTP status codes lives in
`register_exception_handlers`, wired once in app.main.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


class AppError(Exception):
    """Base class for all domain/application errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message: str = "Unexpected error."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found."


class ValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "Invalid input."


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Resource already exists."


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid credentials."


class AuthorizationError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Not allowed to perform this action."


class UnsupportedFileError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Unsupported file type."


class FeatureNotConfiguredError(AppError):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_message = "This feature is not configured."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.info(
            "app_error",
            path=request.url.path,
            error_type=type(exc).__name__,
            message=exc.message,
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def handle_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_error",
            path=request.url.path,
            error_type=type(exc).__name__,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error."},
        )

# src/app/exceptions.py
"""
Domain exception hierarchy and global FastAPI exception handlers.

All custom errors inherit from ``AppException``. This allows a single
global exception handler to catch them and format a consistent JSON response.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class AppException(Exception):
    """Base class for all domain-specific application errors.

    Parameters
    ----------
    status_code:
        HTTP status code to return (e.g., 400, 404).
    detail:
        Human-readable error message.
    error_code:
        Constant string code for the frontend to match against (e.g., "USER_NOT_FOUND").
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "BAD_REQUEST",
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
        )


class ConflictError(AppException):
    """Raised when a resource already exists or state conflicts."""

    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


class UnauthorizedError(AppException):
    """Raised when authentication fails or is absent."""

    def __init__(self, detail: str = "Not authenticated", error_code: str = "UNAUTHORIZED") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
        )


class ForbiddenError(AppException):
    """Raised when the user lacks permission to perform an action."""

    def __init__(self, detail: str = "Permission denied", error_code: str = "FORBIDDEN") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
        )


# ---------------------------------------------------------------------------
# Global Handlers (registered in main.py)
# ---------------------------------------------------------------------------


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Handle our custom AppException and return a consistent JSON shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with a consistent 422 shape."""
    # exc.errors() returns a list of dicts like:
    # [{"loc": ("body", "email"), "msg": "value is not a valid email", "type": "value_error.email"}]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "detail": "Input validation failed",
            "errors": exc.errors(),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected 500 errors.

    Logs the stack trace server-side but never leaks it to the client.
    """
    logger.exception("Unhandled exception", url=str(request.url), method=request.method)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all global handlers on the FastAPI app instance."""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore

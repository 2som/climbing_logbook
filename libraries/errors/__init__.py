from enum import StrEnum


__all__ = [
    "DomainError",
    "ErrorCode",
    "ErrorResponse",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitedError",
    "UnauthenticatedError",
    "ValidationError",
]


class ErrorCode(StrEnum):
    """Values of ``detail.code`` in error responses."""

    UNAUTHENTICATED = "unauthenticated"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    INVALID_CREDENTIALS = "invalid_credentials"
    INVALID_REFRESH_TOKEN = "invalid_refresh_token"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMITED = "rate_limited"
    INTERNAL_SERVER_ERROR = "server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class DomainError(Exception):
    status_code: int = 422
    code: ErrorCode = ErrorCode.VALIDATION_ERROR

    def __init__(
        self, message: str, *, errors: dict[str, list[str]] | None = None
    ) -> None:
        super().__init__(message)
        self.errors = errors or {}


class ValidationError(DomainError):
    """Input breaks a business rule"""


class ForbiddenError(DomainError):
    """The caller may not perform this action"""

    status_code = 403
    code = ErrorCode.FORBIDDEN


class NotFoundError(DomainError):
    """The resource does not exist for this caller"""

    status_code = 404
    code = ErrorCode.NOT_FOUND


class UnauthenticatedError(DomainError):
    """The caller's identity was rejected"""

    status_code = 401
    code = ErrorCode.UNAUTHENTICATED


class RateLimitedError(DomainError):
    """Too many attempts"""

    status_code = 429
    code = ErrorCode.RATE_LIMITED

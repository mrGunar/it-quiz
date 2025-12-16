"""Base exceptions for the application."""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class BusinessException(AppException):
    """Exceptions related to business logic."""


class InfrastructureException(AppException):
    """Exceptions related to infrastructure (DB, external services)."""

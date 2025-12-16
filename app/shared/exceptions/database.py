from app.shared.exceptions.base import AppException


class DatabaseException(AppException):
    def __init__(
        self,
        message: str,
        error_code: str = "database_error",
        status_code=500,
        details=None,
    ):
        super().__init__(message, error_code, status_code, details)


def parse_error_message(error_msg: str) -> DatabaseException:
    error_msg = str(error_msg.orig) if error_msg.orig else str(error_msg)

    if "duplicate key" in error_msg or "already exists" in error_msg:
        return DatabaseException(
            message="Category already exists.",
            error_code="database error",
            status_code=409,
        )
    elif "violates foreign key constraint" in error_msg:
        return DatabaseException(
            error_code="database error",
            status_code=400,
            message="Referenced entity does not exist",
        )
    elif "violates not-null constraint" in error_msg:
        return DatabaseException(
            error_code="database error",
            status_code=400,
            message="Required field is missing",
        )
    else:
        return DatabaseException(
            error_code="database error",
            status_code=400,
            message="Database constraint violation",
        )

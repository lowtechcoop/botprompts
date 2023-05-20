from app.core.errors import AppException


class DatabaseModelError(AppException):
    """
    Base class for database model errors
    """

class DatabaseAdapterError(DatabaseModelError):
    """
    Base class for database adapters errors
    """

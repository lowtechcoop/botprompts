from fastapi import HTTPException


class AppHTTPError(HTTPException):
    """
    Base class for application HTTP errors that will be communicated externally (e.g. via API)
    """


class AppException(Exception):
    """
    Base class for any QDS application-level exception that does not need to go out externally
    """

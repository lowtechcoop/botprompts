from typing import List

from fastapi import HTTPException


class AppHTTPError(HTTPException):
    """
    Base class for application HTTP errors that will be communicated externally (e.g. via API)
    """


class AppException(Exception):
    """
    Base class for any application-level exceptions that does not need to go out externally.
    Use AppHTTPError for errors that need to be communicated to clients.
    """

    reason: str | List[str]

    def __init__(self, reason: str | List[str] | None = None, *args: object) -> None:
        super().__init__(*args)

        if reason is not None:
            self.reason = reason

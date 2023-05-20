from typing import TYPE_CHECKING, Callable, Dict, List, Type

from app.core.errors import AppHTTPError
from app.utils.limiter import rate_limit_exceeded_handler
from dpn_pyutils.common import get_logger
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from starlette import status

log = get_logger(__name__)

if TYPE_CHECKING:
    from pydantic.error_wrappers import ErrorDict


class ErrorModel(BaseModel):
    """
    Common model for errors, specifying the detail
    """

    detail: str | Dict[str, str]


class ErrorCodeReasonModel(BaseModel):
    """
    Common model for error codes, specifying a code and a reason
    """

    code: str
    reason: str


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Provides better error reporting for data validation errors
    """

    source_errors: List[ErrorDict] = exc.errors()
    modified_response: List[Dict[str, str]] = []

    for error in source_errors:
        error_locations: List[str] = [str(x) for x in error["loc"]]
        if "body" in error_locations:
            error_locations.remove("body")
            # error_locations.append("request body")

        location: str = ".".join(error_locations)
        message: str = error["msg"]
        if "value_error.missing" == error["type"]:
            message: str = "A required field was not provided. The field is: {}".format(
                location
            )

        modified_response.append(
            {
                "loc": location,
                "message": message,
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"error": True, "detail": modified_response}),
    )


async def application_http_error_handler(request: Request, exc: AppHTTPError):
    """
    Provides standardized error reporting for AppHTTPError errors
    """

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"error": True, "detail": exc.detail}),
    )


ERROR_HANDLERS: Dict[Type[Exception], Callable] = {
    RequestValidationError: validation_error_handler,
    AppHTTPError: application_http_error_handler,
    RateLimitExceeded: rate_limit_exceeded_handler,
}

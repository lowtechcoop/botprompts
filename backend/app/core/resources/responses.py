"""
This module contains a list of standard API route responses used by the resources routes.
These should be used by other routes as well, where appropriate
"""
from typing import Any, Dict

from app.core.error_handling import ErrorModel
from app.core.resources import constants
from fastapi import status

HTTP_400_BAD_REQUEST_RESPONSE: Dict[str, Dict[str, Any]] = {
    "model": ErrorModel,  # type: ignore
    "content": {
        "application/json": {
            "examples": {
                constants.INVALID_INPUT: {
                    "summary": (
                        "Invalid input supplied to the request. Check that the correct entities "
                        "are being referenced and that the information is appropriately matched."
                    ),
                    "value": {"detail": constants.INVALID_INPUT},
                },
                constants.RECORD_ALREADY_EXISTS: {
                    "summary": (
                        "Attempts to create a resource or record failed because an entity with "
                        "the primary key or secondary unique characteristics already exists."
                    ),
                    "value": {"detail": constants.RECORD_ALREADY_EXISTS},
                },
            }
        }
    },
}

HTTP_401_UNAUTHORIZED_RESPONSE: Dict[str, Dict[str, Any]] = {
    "model": ErrorModel,  # type: ignore
    "content": {
        "application/json": {
            "examples": {
                constants.UNAUTHENTICATED_REQUEST: {
                    "summary": (
                        "Unauthenticated request to a protected resource. Un-authenticated access "
                        "is being attempted to an endpoint or resource that requires "
                        "authenticated user access. "
                    ),
                    "value": {"detail": constants.UNAUTHENTICATED_REQUEST},
                },
                constants.INVALID_CREDENTIALS: {
                    "summary": ("Supplied credentials could not be authenticated."),
                    "value": {"detail": constants.INVALID_CREDENTIALS},
                },
            }
        }
    },
}

HTTP_403_FORBIDDEN_RESPONSE: Dict[str, Dict[str, Any]] = {
    "model": ErrorModel,  # type: ignore
    "content": {
        "application/json": {
            "examples": {
                constants.INSUFFICIENT_CREDENTIALS: {
                    "summary": (
                        "Insufficient credentials. The user is authenticated but lacks the "
                        "required credentials to access this endpoint or resource. Please "
                        "check the permissions, roles, client information, or scopes."
                    ),
                    "value": {"detail": constants.INSUFFICIENT_CREDENTIALS},
                },
            }
        }
    },
}

HTTP_404_NOT_FOUND_RESPONSE: Dict[str, Dict[str, Any]] = {
    "model": ErrorModel,  # type: ignore
    "content": {
        "application/json": {
            "examples": {
                constants.RECORD_DOES_NOT_EXIST: {
                    "summary": (
                        "Requested record does not exist."
                    ),
                    "value": {"detail": constants.RECORD_DOES_NOT_EXIST},
                },
            }
        }
    },
}

HTTP_422_UNPROCESSABLE_ENTITY_RESPONSE: Dict[str, Dict[str, Any]] = {
    "model": ErrorModel,  # type: ignore
    "content": {
        "application/json": {
            "examples": {
                constants.INVALID_DATA: {
                    "summary": ("Invalid data types supplied to the field requests."),
                    "value": {"detail": "Array of fields and field validation errors"},
                },
            }
        }
    },
}


API_RESOURCE_ROUTE_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: HTTP_400_BAD_REQUEST_RESPONSE,
    status.HTTP_401_UNAUTHORIZED: HTTP_401_UNAUTHORIZED_RESPONSE,
    status.HTTP_403_FORBIDDEN: HTTP_403_FORBIDDEN_RESPONSE,
    status.HTTP_404_NOT_FOUND: HTTP_404_NOT_FOUND_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_ENTITY: HTTP_422_UNPROCESSABLE_ENTITY_RESPONSE,
}

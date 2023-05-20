from datetime import datetime
from typing import Annotated, Any, Dict, List, Mapping

import jwt
import pytz
from app.config import get_config
from app.core.auth.errors import UserDoesNotExist, UserLacksRequiredScopes
from app.core.auth.oauth2 import oauth2_scheme
from app.core.errors import AppHTTPError
from app.core.resources import constants
from app.core.sys.users import constants as user_constants
from app.core.sys.users import models
from dpn_pyutils.common import get_logger
from fastapi import Security, status
from fastapi.security import SecurityScopes
from slugify import slugify

log = get_logger(__name__)


async def check_user_token_valid(
    token: models.SysUserToken,
) -> bool:
    """
    Checks if the supplied registration token is valid
    """

    if token is None or not token.is_active:
        raise AppHTTPError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=user_constants.TOKEN_INVALID,
        )

    # Check expired time
    if (
        token.expires_at is not None
        and pytz.UTC.localize(datetime.utcnow()) >= token.expires_at
    ):
        raise AppHTTPError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=user_constants.TOKEN_EXPIRED,
        )

    # Since time has not expired, check that token can still be used
    # If the num_uses_remaining is none, assume a permissive approach and allow
    token_can_be_used = True
    if token.num_uses_remaining is not None and token.num_uses_remaining <= 0:
        token_can_be_used = False

    if not token_can_be_used:
        raise AppHTTPError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=user_constants.TOKEN_INVALID,
        )

    return True


def decode_jwt_token_payload(
    token: str, audience: str = user_constants.ACCESS_TOKEN_AUDIENCE
) -> Mapping[Any, Any]:
    """
    Checks the JWT string and returns the decoded content
    """

    config = get_config()
    payload = jwt.decode(
        token,
        key=config.JWT_SECURITY_TOKEN,
        algorithms=[config.JWT_ALGORITHM],
        audience=audience,
    )

    return payload


def check_user_scopes(
    user: models.SysUser, payload: Dict[str, Any], security_scopes: SecurityScopes
) -> models.SysUser:
    """
    Checks decoded JWT scopes against a user scope
    """

    if user is None or payload is None:
        raise UserDoesNotExist("User or Payload is null")

    user_scope_str = str(payload.get("scope"))
    if user_scope_str is None:
        raise UserLacksRequiredScopes("No scopes found in credential")

    if user.is_superuser:
        log.debug(
            "[superuser] User %s (%s) is in superuser mode, overriding security scopes",
            user.id,
            user.email,
        )
        return user

    # Blend role names and permission names into one list of valid user scopes
    user_scopes = user_scope_str.split(" ")
    user_scopes.extend([p.name for p in get_user_permissions(user)])

    log.debug("User scopes are: %s", user_scopes)

    found_matching_scope = False
    for requested_scope in security_scopes.scopes:
        log.debug("Looking for permission '%s'", requested_scope)
        if requested_scope in user_scopes:
            found_matching_scope = True
            break

    if not found_matching_scope:
        raise UserLacksRequiredScopes("Cannot find at least one matching scope")

    return user


def get_auth_header_from_scopes(security_scopes: SecurityScopes) -> Dict[str, str]:
    """
    Gets the correct WWW-Authenticate header from the supplied security scopes
    """

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    return {"WWW-Authenticate": authenticate_value}


def get_payload_from_token(
    security_scopes: SecurityScopes,
    token: Annotated[str, Security(oauth2_scheme)],
) -> Mapping[Any, Any]:
    """
    Extracts the payload from the supplied token
    """

    credentials_error = AppHTTPError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=constants.INVALID_CREDENTIALS,
        headers=get_auth_header_from_scopes(security_scopes),
    )

    try:
        if token is None:
            raise jwt.DecodeError("Invalid or empty token provided")

        return decode_jwt_token_payload(token)

    except jwt.DecodeError as e:
        credentials_error.detail = f"{credentials_error.detail}: {e}"
        raise credentials_error
    except jwt.ExpiredSignatureError:
        credentials_error.detail = f"{credentials_error.detail}: Token has expired"
        raise credentials_error


def format_role_name(display_name: str) -> str:
    """
    Formats a display name for a role into a machine facing role name
    """

    if display_name is None or len(display_name) == 0:
        raise ValueError("Role name is empty or blank")

    return slugify(display_name)


def user_has_permissions(user: models.SysUser, required_permissions: List[str]) -> bool:
    """
    Checks if the user has at least one of the required permissions
    """

    if user.is_superuser:
        return True

    for p in get_user_permissions(user):
        if p.name in required_permissions:
            return True

    return False


def get_user_permissions(user: models.SysUser) -> List[models.SysPermission]:
    """
    Gets the list of permissions from a user
    """

    permissions = []
    for r in user.roles:
        for p in r.permissions:
            if p not in permissions:
                permissions.append(p)

    return permissions


def get_user_roles_as_string(user: models.SysUser) -> List[str]:
    """
    Gets the list of role names that a user has in string array format
    """

    return [r.name for r in user.roles]


def get_user_permissions_as_string(user: models.SysUser) -> List[str]:
    """
    Gets the list of permissions a user has in string array format
    """

    return [p.permission_name for p in get_user_permissions(user)]

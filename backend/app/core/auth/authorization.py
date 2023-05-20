from typing import Annotated

from app.core.auth import constants as auth_constants
from app.core.auth.errors import UserDoesNotExist, UserLacksRequiredScopes
from app.core.auth.oauth2 import oauth2_scheme
from app.core.auth.utils import (
    check_user_scopes,
    get_auth_header_from_scopes,
    get_payload_from_token,
)
from app.core.errors import AppHTTPError
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from app.core.sys.users.models import SysUser
from dpn_pyutils.common import get_logger
from fastapi import Depends, Request, Security, status
from fastapi.security import SecurityScopes

log = get_logger(__name__)


async def get_auth(
    request: Request,
    security_scopes: SecurityScopes,
    token: Annotated[str, Security(oauth2_scheme)],
    user_manager: UserLogicManager = Depends(get_user_manager),
) -> SysUser | None:
    """
    Callable that compares the authorization required (permissions) with the permissions that
    a user has
    """

    if token is None:
        if request.app.state.guest["role"] is None:
            guest_role = await user_manager.sys_roles.get_by_name(
                request.app.state.guest["role_name"]
            )
            if guest_role is None:
                raise AppHTTPError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        f"Guest Role with name '{request.app.state.guest['role_name']}' cannot be "
                        "found or loaded from the database. Ensure the application is configured "
                        "correctly and the correct guest role is specified in the ENV config."
                    ),
                )

            request.app.state.guest["role"] = guest_role
            request.app.state.guest["permissions"] = [
                p.name for p in guest_role.permissions
            ]


        guest_has_permission = False
        for requested_scope in security_scopes.scopes:
            if requested_scope in request.app.state.guest["permissions"]:
                guest_has_permission = True
                break

        if guest_has_permission:
            return None
        else:
            log.debug(
                "Guest access denied. Endpoint required scopes are %s and guest role scopes are %s",
                security_scopes.scopes,
                request.app.state.guest["permissions"],
            )
            raise AppHTTPError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=auth_constants.AUTH_NOT_ENOUGH_PERMISSIONS,
                headers=get_auth_header_from_scopes(security_scopes),
            )

    try:
        payload = get_payload_from_token(security_scopes=security_scopes, token=token)
    except AppHTTPError as e:
        raise e

    try:
        user = check_user_scopes(
            user=await user_manager.sys_users.get(payload["sub"]),
            payload=payload,  # type: ignore
            security_scopes=security_scopes,
        )

        if user.is_active and user.is_verified:
            return user
        else:
            raise UserLacksRequiredScopes(auth_constants.USER_ACCOUNT_DISABLED)

    except (UserDoesNotExist, UserLacksRequiredScopes):
        raise AppHTTPError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=auth_constants.AUTH_NOT_ENOUGH_PERMISSIONS,
            headers=get_auth_header_from_scopes(security_scopes),
        )

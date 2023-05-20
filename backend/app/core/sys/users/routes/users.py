from app.config import get_config
from app.core.auth.authorization import get_auth
from app.core.errors import AppHTTPError
from app.core.resources.routers import generate_resource_router
from app.core.resources.schemas import UUID_ID
from app.core.sys.users import constants as user_constants
from app.core.sys.users import models, schemas
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, Depends, Security, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__users() -> APIRouter:
    """
    Get the APIRouter for the users endpoints
    """

    route_name_prefix = "sys:users"

    router = generate_resource_router(
        **{
            "resource_name": "sys_users",
            "url_prefix": "/sys/users",
            "route_name_prefix": route_name_prefix,
            "record": models.SysUser,
            "list_schema": schemas.UserListSchema,
            "record_schema": schemas.UserSchema,
            "create_schema": schemas.UserCreateSchema,
            "update_schema": schemas.UserUpdateSchema,
        }
    )

    @router.post(
        "/{user_id}/roles/add",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name=f"{route_name_prefix}:roles:add",
    )
    async def sys__users__users__roles_add(
        user_id: UUID_ID,
        user_roles: schemas.UserAddRolesRequest,
        auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Adds roles to an existing user
        """

        user = await user_manager.sys_users.get(user_id)
        if user is None:
            raise AppHTTPError(
                detail=user_constants.USER_DOES_NOT_EXIST,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        roles = await user_manager.sys_roles.get_by_ids(user_roles.role_ids)

        user = await user_manager.add_roles_to_user(user, roles)

        return schemas.UserSchema.from_orm(user)


    @router.post(
        "/{user_id}/roles/remove",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name=f"{route_name_prefix}:roles:add",
    )
    async def sys__users__users__roles_remove(
        user_id: UUID_ID,
        user_roles: schemas.UserAddRolesRequest,
        auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Remove roles from a user
        """

        user = await user_manager.sys_users.get(user_id)
        if user is None:
            raise AppHTTPError(
                detail=user_constants.USER_DOES_NOT_EXIST,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        roles = await user_manager.sys_roles.get_by_ids(user_roles.role_ids)

        user = await user_manager.remove_roles_from_user(user, roles)

        return schemas.UserSchema.from_orm(user)


    @router.post(
        "/{user_id}/roles",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name=f"{route_name_prefix}:roles:set",
    )
    async def sys__users__users__roles_set(
        user_id: UUID_ID,
        user_roles: schemas.UserAddRolesRequest,
        auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Remove roles from a user
        """

        user = await user_manager.sys_users.get(user_id)
        if user is None:
            raise AppHTTPError(
                detail=user_constants.USER_DOES_NOT_EXIST,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        roles = await user_manager.sys_roles.get_by_ids(user_roles.role_ids)

        roles_to_add = []
        roles_to_remove = []

        # Match the roles to add
        for r in roles:
            if r not in user.roles:
                roles_to_add.append(r)

        # Match the existing roles that are not in our update set to remove
        for er in user.roles:
            if er not in roles:
                roles_to_remove.append(er)

        user = await user_manager.add_roles_to_user(user, roles_to_add)
        user = await user_manager.remove_roles_from_user(user, roles_to_remove)

        return schemas.UserSchema.from_orm(user)

    return router

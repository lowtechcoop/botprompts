from app.config import get_config
from app.core.auth.authorization import get_auth
from app.core.errors import AppHTTPError
from app.core.resources.routers import generate_resource_router
from app.core.sys.users import constants as user_constants
from app.core.sys.users import models, schemas
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, Depends, Security, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__roles() -> APIRouter:
    """
    Get the APIRouter for the roles endpoints
    """

    route_name_prefix = "sys:roles"

    router = generate_resource_router(
        **{
            "resource_name": "sys_roles",
            "url_prefix": "/sys/roles",
            "route_name_prefix": route_name_prefix,
            "record": models.SysRole,
            "list_schema": schemas.RoleListSchema,
            "record_schema": schemas.RoleSchema,
            "create_schema": schemas.RoleCreateSchema,
            "update_schema": schemas.RoleUpdateSchema,
        }
    )

    @router.post(
        "/{name_or_id}/perms",
        response_model=schemas.RoleSchema,
        status_code=status.HTTP_200_OK,
        name=f"{route_name_prefix}:permissions:set",
    )
    async def sys__users__roles__perms__set(
        role_id: int,
        role_perms: schemas.RolePermsAddRequest,
        auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Set the set of permissions that a role should encompass
        """

        existing_role = await user_manager.sys_roles.get_by_name_or_id(role_id)
        if existing_role is None:
            raise AppHTTPError(
                detail=user_constants.ROLE_DOES_NOT_EXIST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        permissions = await user_manager.sys_permissions.get_by_ids(
            role_perms.permission_ids
        )

        perms_to_add = []
        perms_to_remove = []

        # Match the permissions to add
        for p in permissions:
            if p not in existing_role.permissions:
                perms_to_add.append(p)

        # Match the existing permissions that are not in our update set -- remove
        for ep in existing_role.permissions:
            if ep not in permissions:
                perms_to_remove.append(ep)

        updated_role = await user_manager.add_permissions_to_role(
            existing_role, perms_to_add
        )
        updated_role = await user_manager.remove_permissions_from_role(
            updated_role, perms_to_remove
        )

        return schemas.RoleSchema.from_orm(updated_role)

    @router.post(
        "/{name_or_id}/perms/add",
        response_model=schemas.RoleSchema,
        status_code=status.HTTP_200_OK,
        name=f"{route_name_prefix}:permissions:add",
    )
    async def sys__users__roles__perms__add(
        role_id: int,
        role_perms: schemas.RolePermsAddRequest,
        auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Update permissions to a role
        """

        existing_role = await user_manager.sys_roles.get_by_name_or_id(role_id)
        if existing_role is None:
            raise AppHTTPError(
                detail=user_constants.ROLE_DOES_NOT_EXIST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        existing_permissions = await user_manager.sys_permissions.get_by_ids(
            role_perms.permission_ids
        )

        updated_role = await user_manager.add_permissions_to_role(
            existing_role, existing_permissions
        )

        return schemas.RoleSchema.from_orm(updated_role)

    @router.post(
        "/{name_or_id}/perms/remove",
        response_model=schemas.RoleSchema,
        status_code=status.HTTP_200_OK,
        name=f"{route_name_prefix}:permissions:remove",
    )
    async def sys__users__roles__perms__remove(
        role_id: int,
        role_perms: schemas.RolePermsAddRequest,
        auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Remove permissions from a role
        """

        existing_role = await user_manager.sys_roles.get_by_name_or_id(role_id)
        if existing_role is None:
            raise AppHTTPError(
                detail=user_constants.ROLE_DOES_NOT_EXIST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        existing_permissions = await user_manager.sys_permissions.get_by_ids(
            role_perms.permission_ids
        )

        updated_role = await user_manager.remove_permissions_from_role(
            existing_role, existing_permissions
        )

        return schemas.RoleSchema.from_orm(updated_role)

    return router

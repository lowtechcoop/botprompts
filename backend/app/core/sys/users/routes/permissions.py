from app.config import get_config
from app.core.resources.routers import generate_resource_router
from app.core.sys.users import models, schemas
from dpn_pyutils.common import get_logger
from fastapi import APIRouter

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__permissions() -> APIRouter:
    """
    Get the APIRouter for the permissions endpoints
    """

    router = generate_resource_router(
        **{
            "resource_name": "sys_permissions",
            "url_prefix": "/sys/permissions",
            "route_name_prefix": "sys:permissions",
            "record": models.SysPermission,
            "list_schema": schemas.PermissionListSchema,
            "record_schema": schemas.PermissionSchema,
            "create_schema": schemas.PermissionCreateSchema,
            "update_schema": schemas.PermissionUpdateSchema,
        }
    )

    return router

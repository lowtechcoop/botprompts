from app.core.resources.routers import generate_resource_router
from app.core.sys.users import models, schemas
from app.core.sys.users.routes.authenticate import get_router__sys__users__auth
from app.core.sys.users.routes.permissions import get_router__sys__users__permissions
from app.core.sys.users.routes.profile import get_router__sys__users__profile
from app.core.sys.users.routes.register import get_router__sys__users__register
from app.core.sys.users.routes.reset import get_router__sys__users__reset
from app.core.sys.users.routes.roles import get_router__sys__users__roles
from app.core.sys.users.routes.users import get_router__sys__users__users
from app.core.sys.users.routes.verify import get_router__sys__users__verify
from fastapi import APIRouter

users_router: APIRouter = APIRouter(include_in_schema=True)


sys_tokens_router = generate_resource_router(
    **{
        "resource_name": "sys_tokens",
        "url_prefix": "/sys/tokens",
        "route_name_prefix": "sys:tokens",
        "record": models.SysUserToken,
        "list_schema": schemas.UserTokenListSchema,
        "record_schema": schemas.UserTokenSchema,
        "has_create": False,
        "has_update": False,
        "has_delete": True,
    }
)


users_router.include_router(sys_tokens_router, tags=["sys_tokens"])


users_router.include_router(get_router__sys__users__roles(), tags=["sys_roles"])
users_router.include_router(
    get_router__sys__users__permissions(), tags=["sys_permissions"]
)
users_router.include_router(get_router__sys__users__users(), tags=["sys_users"])
users_router.include_router(get_router__sys__users__auth(), include_in_schema=False)
users_router.include_router(get_router__sys__users__register(), include_in_schema=False)
users_router.include_router(get_router__sys__users__reset(), include_in_schema=False)
users_router.include_router(get_router__sys__users__verify(), include_in_schema=False)
users_router.include_router(get_router__sys__users__profile(), include_in_schema=False)

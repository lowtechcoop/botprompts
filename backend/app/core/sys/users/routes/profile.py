from app.config import get_config
from app.core.auth.authorization import get_auth
from app.core.errors import AppHTTPError
from app.core.sys.users import constants as user_constants
from app.core.sys.users import schemas
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, Depends, Security, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__profile() -> APIRouter:
    """
    Get the APIRouter for the profile endpoints
    """

    router = APIRouter(prefix="/profile")

    @router.get(
        "",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name="sys:users:profile",
    )
    async def sys__users__profile(
        current_user=Security(get_auth, scopes=["profile:view"]),
    ):
        """
        Gets the current user's profile
        """
        return schemas.UserSchema.from_orm(current_user)

    @router.patch(
        "",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name="sys:users:profile:edit",
    )
    async def sys__users__profile__edit(
        user_update: schemas.UserUpdateRequest,
        current_user=Security(get_auth, scopes=["profile:edit"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Updates the current user's profile
        """

        if current_user is None:
            raise AppHTTPError(
                detail=user_constants.USER_DOES_NOT_EXIST,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # All people with "profile:edit" permissions can change these fields for their own profile
        permitted_fields = ["name", "display_name", "email", "password"]

        # Only permit changes to is_superuser to super users
        if current_user.is_superuser:
            permitted_fields.append("is_superuser")

        # Only update the permitted fields so that users cannot elevate their own
        # privileges or set themselves as superuser
        current_user = await user_manager.update_user(
            current_user,
            user_update.dict(
                include=set(permitted_fields), exclude_none=True, exclude_unset=True
            ),
        )

        return schemas.UserSchema.from_orm(current_user)

    @router.post(
        "/sudo/add",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name="sys:users:profile:sudo:add",
    )
    async def sys__users__profile__sudo_add(
        auth=Security(get_auth, scopes=["fresh", "admin:sudo"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Adds super user mode to an admin user and requires a freshly logged in token
        """

        admin_access_user = await user_manager.update_user_superuser_add(auth)

        return schemas.UserSchema.from_orm(admin_access_user)

    @router.post(
        "/sudo/remove",
        response_model=schemas.UserSchema,
        status_code=status.HTTP_200_OK,
        name="sys:users:profile:sudo:remove",
    )
    async def sys__users__profile__sudo_remove(
        auth=Security(get_auth, scopes=["admin:sudo"]),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Removes super user mode from an admin user
        """

        admin_access_user = await user_manager.update_user_superuser_remove(auth)

        return schemas.UserSchema.from_orm(admin_access_user)

    return router

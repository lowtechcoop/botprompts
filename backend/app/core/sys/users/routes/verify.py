from app.config import get_config
from app.core.auth.utils import check_user_token_valid
from app.core.errors import AppHTTPError
from app.core.sys.users import constants as user_constants
from app.core.sys.users import schemas
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from app.core.sys.users.notifications.email import UserEmailNotifier
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, BackgroundTasks, Depends, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__verify() -> APIRouter:
    """
    Get the APIRouter for the verify endpoints
    """

    router = APIRouter(prefix="/verify")

    @router.post(
        "",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:verify",
    )
    async def sys__users__verify(
        verify_token: schemas.UsersVerifyToken,
        background_tasks: BackgroundTasks,
        user_manager: UserLogicManager = Depends(get_user_manager),
        notifier: UserEmailNotifier = Depends(UserEmailNotifier),
    ):
        """
        Verifies a user by claiming a verification token
        """

        try:
            token = await user_manager.sys_users_tokens.get_by_token(
                token=verify_token.token,
                token_type=user_constants.TOKEN_TYPE_VERIFICATION,
            )
            await check_user_token_valid(token)

        except AppHTTPError as e:
            # Resend a new email verification token if the one they have used is expired
            if e.detail == user_constants.TOKEN_EXPIRED:
                # Re: type:ignore in next statement, check_register_token_valid checks
                # if token is None
                # This regeneration only applies to email verification tokens
                new_token = await user_manager.create_token_verification(token.user)  # type: ignore
                background_tasks.add_task(
                    notifier.notify_email_verification,
                    user=new_token.user,  # type: ignore
                    token=new_token.token,
                )

            raise e

        user = await user_manager.sys_users.update(
            token.user, {"is_verified": True, "is_active": True}  # type: ignore
        )

        await user_manager.sys_users_tokens.delete(token, hard_delete=True)

        # Add the Authenticated user role to the user
        auth_user_role = await user_manager.sys_roles.get_by_name(
            user_constants.ROLE_AUTHENTICATED_USER
        )
        user.roles.append(auth_user_role)
        await user_manager.sys_users.apply_and_commit(user)

        # HTTP Status 200 and no body means success
        return None

    @router.post(
        "/validate",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:verify:validate",
    )
    async def sys__users__verify__validate(
        verify_token: schemas.UsersVerifyToken,
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Validate a verification token.
        """

        try:
            token = await user_manager.sys_users_tokens.get_by_token(
                token=verify_token.token,
                token_type=user_constants.TOKEN_TYPE_VERIFICATION,
            )
            await check_user_token_valid(token)

        except AppHTTPError:
            raise AppHTTPError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=user_constants.TOKEN_INVALID,
            )

        # HTTP Status 200 and no body means success
        return None

    return router

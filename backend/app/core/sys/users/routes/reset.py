from app.config import get_config
from app.core.auth.errors import PW_LACKS_MIN_LENGTH, UsersException
from app.core.auth.utils import check_user_token_valid
from app.core.errors import AppHTTPError
from app.core.sys.users import constants as user_constants
from app.core.sys.users import schemas
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from app.core.sys.users.notifications.email import UserEmailNotifier
from app.utils.limiter import limiter
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__reset() -> APIRouter:
    """
    Get the APIRouter for the users reset endpoints
    """

    router = APIRouter(prefix="/reset")

    @router.post(
        "",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:reset",
    )
    @limiter.limit(config.RATE_LIMIT_ACCOUNT_RESET)  # Must be below @router decorator
    async def sys__users__reset(
        request: Request,  # Required for rate limiter
        reset_request: schemas.UsersResetTokenRequest,
        background_tasks: BackgroundTasks,
        notifier: UserEmailNotifier = Depends(UserEmailNotifier),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Resets a user account by changing their password after validating the reset token
        """

        token = await user_manager.sys_users_tokens.get_by_token(
            reset_request.token, token_type=user_constants.TOKEN_TYPE_PASSWORD_RESET
        )
        if token is None:
            raise AppHTTPError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=user_constants.TOKEN_INVALID,
            )

        if token.user is None or not await check_user_token_valid(token):
            raise AppHTTPError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=user_constants.TOKEN_INVALID,
            )

        try:
            if reset_request.password is None:
                raise UsersException(PW_LACKS_MIN_LENGTH)

            user_manager.password_helper.validate_password(reset_request.password)
        except UsersException as ue:
            raise AppHTTPError(
                detail=ue.reason, status_code=status.HTTP_400_BAD_REQUEST
            )

        await user_manager.sys_users.update(
            token.user,
            {"password": user_manager.password_helper.hash(reset_request.password)},
        )

        background_tasks.add_task(
            notifier.notify_users_account_recently_updated, user=token.user
        )
        token_to_delete = await user_manager.sys_users_tokens.get(token.id)
        await user_manager.sys_users_tokens.delete(token_to_delete, hard_delete=True)

        # HTTP Status 200 and no body means success
        return None

    @router.post(
        "/validate",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:reset:validate",
    )
    @limiter.limit(config.RATE_LIMIT_ACCOUNT_RESET)  # Must be below @router decorator
    async def sys__users__reset__validate(
        request: Request,  # Required for rate limiter
        reset_request: schemas.UsersResetTokenRequest,
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Validate if a user reset token request will succeeed
        """

        try:
            token = await user_manager.sys_users_tokens.get_by_token(
                token=reset_request.token,
                token_type=user_constants.TOKEN_TYPE_PASSWORD_RESET,
            )
            await check_user_token_valid(token)

        except AppHTTPError:
            raise AppHTTPError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=user_constants.TOKEN_INVALID,
            )

        # HTTP Status 200 and no body means success
        return None

    @router.post(
        "/request",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:reset:request",
    )
    @limiter.limit(config.RATE_LIMIT_ACCOUNT_RESET)  # Must be below @router decorator
    async def users__reset__request(
        request: Request,  # Required for rate limiter
        reset_request: schemas.UsersResetRequest,
        background_tasks: BackgroundTasks,
        user_manager: UserLogicManager = Depends(get_user_manager),
        notifier: UserEmailNotifier = Depends(UserEmailNotifier),
    ):
        """
        Request a password reset token
        """

        user = await user_manager.sys_users.get_by_email(reset_request.email)

        if user is not None:
            recovery_token = await user_manager.create_token_password_reset(user)
            if recovery_token is not None:
                background_tasks.add_task(
                    notifier.notify_users_account_recovery_token,
                    user=user,
                    token=recovery_token.token,
                )

        else:
            # Run the password hash anyway to defeat timing attacks and mitigate against CWE-208
            # https://cwe.mitre.org/data/definitions/208.html
            await user_manager.create_token_password_reset(
                user_manager.get_null_user(), simulate=True
            )

        # Do not notify the user of success or failure
        return None

    return router

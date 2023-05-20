from app.config import get_config
from app.core.auth.errors import UsersException
from app.core.errors import AppHTTPError
from app.core.sys.users import schemas
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from app.core.sys.users.notifications.email import UserEmailNotifier
from app.utils.limiter import limiter
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__register() -> APIRouter:
    """
    Get the APIRouter for the users registration endpoints
    """

    router = APIRouter(prefix="/register")

    @router.post(
        "",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:register",
    )
    @limiter.limit(
        config.RATE_LIMIT_ACCOUNT_REGISTER
    )  # Must be below @router decorator
    async def sys__users__register(
        request: Request,  # Required for rate limiter
        register_request: schemas.UsersRegisterValidateRequest,
        background_tasks: BackgroundTasks,
        notifier: UserEmailNotifier = Depends(UserEmailNotifier),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Oauth2 Password Bearer authentication endpoint
        """

        try:
            await user_manager.can_create_user(register_request)
        except UsersException as ue:
            raise AppHTTPError(
                detail=ue.reason, status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            create_request = schemas.UsersRegisterRequest(**register_request.dict())
            user = await user_manager.create_user(create_request)
            verify = await user_manager.create_token_verification(user)
            background_tasks.add_task(
                notifier.notify_email_verification, user=user, token=verify.token
            )

        except UsersException as ue:
            raise AppHTTPError(
                detail=ue.reason, status_code=status.HTTP_400_BAD_REQUEST
            )

        # HTTP Status 200 and no body means registered
        return None

    @router.post(
        "/validate",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:users:register:validate",
    )
    @limiter.limit(
        config.RATE_LIMIT_ACCOUNT_REGISTER
    )  # Must be below @router decorator
    async def sys__users__register__validate(
        request: Request,  # Required for rate limiter
        register_request: schemas.UsersRegisterValidateRequest,
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Validate if a user registration request will succeeed
        """

        try:
            await user_manager.can_create_user(register_request)
        except UsersException as ue:
            raise AppHTTPError(
                detail=ue.reason, status_code=status.HTTP_400_BAD_REQUEST
            )

        # HTTP Status 200 and no body means success
        return None

    return router

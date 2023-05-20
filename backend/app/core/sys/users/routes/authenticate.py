from datetime import datetime

from app.config import get_config
from app.core.auth.errors import UserInvalidToken
from app.core.errors import AppHTTPError
from app.core.resources import constants
from app.core.sys.users import schemas
from app.core.sys.users import constants as user_constants
from app.core.sys.users.manager import UserLogicManager, get_user_manager
from app.utils.limiter import limiter
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, Depends, Request, Response, status

config = get_config()

log = get_logger(__name__)


def get_router__sys__users__auth() -> APIRouter:
    """
    Get the APIRouter for the users token authentication endpoints
    """

    router = APIRouter(prefix="/auth")

    @router.post(
        "/token",
        response_model=schemas.UsersAuthResponse,
        status_code=status.HTTP_200_OK,
        name="sys:auth:token",
    )
    @limiter.limit(config.RATE_LIMIT_ACCOUNT_SIGNIN)  # Must be below @router decorator
    async def sys__users__auth__token(
        request: Request,  # Required for rate limiter
        response: Response,
        form_data: schemas.BPOauth2PasswordRequestForm = Depends(),
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Oauth2 Password Bearer authentication endpoint
        """

        user = await user_manager.login_by_email(
            email=form_data.username, password=form_data.password
        )
        if user is None:
            raise AppHTTPError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=constants.INVALID_CREDENTIALS,
            )

        for cookie in request.cookies:
            if cookie == config.JWT_REFRESH_COOKIE_NAME:
                try:
                    await user_manager.invalidate_existing_refresh_tokens(
                        request.cookies[cookie], user
                    )
                except UserInvalidToken:
                    # We will resolve this error in the next few lines
                    pass

        # If the user selects that this is a public computer, only authenticate for the
        # active session and do not create a refresh token
        offline_access = True
        if form_data.is_public:
            offline_access = False

        tokens = await user_manager.create_token_access(
            user, fresh_auth=True, offline_access=offline_access
        )

        if (
            tokens.refresh_token is not None
            and tokens.refresh_token_expires_at is not None
        ):
            cookie_format_date = datetime.fromtimestamp(
                tokens.refresh_token_expires_at
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")

            response.set_cookie(
                key=config.JWT_REFRESH_COOKIE_NAME,
                value=tokens.refresh_token,
                expires=cookie_format_date,
                secure=config.JWT_REFRESH_COOKIE_SECURE,
                httponly=config.JWT_REFRESH_COOKIE_HTTPONLY,
                path=config.JWT_REFRESH_COOKIE_PATH,
                samesite=config.JWT_REFRESH_COOKIE_SAMESITE,  # type: ignore
                domain=config.JWT_REFRESH_COOKIE_DOMAIN,
            )

        return schemas.UsersAuthResponse(
            access_token=tokens.access_token,
            token_type=tokens.token_type,
            expires_at=tokens.expires_at,
        )

    @router.post(
        "/refresh",
        response_model=schemas.UsersAuthResponse,
        status_code=status.HTTP_200_OK,
        name="sys:auth:refresh",
    )
    @limiter.limit(config.RATE_LIMIT_ACCOUNT_SIGNIN)  # Must be below @router decorator
    async def sys__users__refresh__token(
        request: Request,  # Required for rate limiter
        response: Response,
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Use the HttpOnly cookie to refresh the access_token
        """

        refresh_token = None
        for cookie in request.cookies:
            if cookie == config.JWT_REFRESH_COOKIE_NAME:
                refresh_token = request.cookies[cookie]
                break

        if refresh_token is None:
            raise AppHTTPError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=user_constants.TOKEN_INVALID
            )

        try:
            tokens = await user_manager.rotate_refresh_token(refresh_token)

            if (
                tokens.refresh_token is not None
                and tokens.refresh_token_expires_at is not None
            ):
                cookie_format_date = datetime.fromtimestamp(
                    tokens.refresh_token_expires_at
                ).strftime("%a, %d %b %Y %H:%M:%S GMT")

                response.set_cookie(
                    key=config.JWT_REFRESH_COOKIE_NAME,
                    value=tokens.refresh_token,
                    expires=cookie_format_date,
                    secure=config.JWT_REFRESH_COOKIE_SECURE,
                    httponly=config.JWT_REFRESH_COOKIE_HTTPONLY,
                    path=config.JWT_REFRESH_COOKIE_PATH,
                    samesite=config.JWT_REFRESH_COOKIE_SAMESITE,  # type: ignore
                    domain=config.JWT_REFRESH_COOKIE_DOMAIN,
                )

            else:
                raise AppHTTPError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=user_constants.REFRESH_TOKEN_ROTATE_ERROR,
                )
        except UserInvalidToken:
            raise AppHTTPError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=user_constants.TOKEN_INVALID,
            )

        return schemas.UsersAuthResponse(
            access_token=tokens.access_token,
            token_type=tokens.token_type,
            expires_at=tokens.expires_at,
        )

    @router.post(
        "/logout",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="sys:auth:logout",
    )
    @limiter.limit(config.RATE_LIMIT_ACCOUNT_SIGNIN)  # Must be below @router decorator
    async def sys__users__logout(
        request: Request,  # Required for rate limiter
        response: Response,
        user_manager: UserLogicManager = Depends(get_user_manager),
    ):
        """
        Logs the user out by invalidating the refresh_token
        """

        refresh_token = None
        for cookie in request.cookies:
            if cookie == config.JWT_REFRESH_COOKIE_NAME:
                refresh_token = request.cookies[cookie]
                break

        if refresh_token is not None:
            try:
                user = await user_manager.get_user_from_token(refresh_token)
                await user_manager.invalidate_existing_refresh_token(
                    refresh_token, user
                )
            except UserInvalidToken:
                pass

        # Invalidate any cookies that may be lying around
        cookie_format_date = datetime.fromtimestamp(1).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        response.set_cookie(
            key=config.JWT_REFRESH_COOKIE_NAME,
            value="",
            expires=cookie_format_date,
            max_age=-1,  # Force browser to purge cookie
            secure=config.JWT_REFRESH_COOKIE_SECURE,
            httponly=config.JWT_REFRESH_COOKIE_HTTPONLY,
            path=config.JWT_REFRESH_COOKIE_PATH,
            samesite=config.JWT_REFRESH_COOKIE_SAMESITE,  # type: ignore
            domain=config.JWT_REFRESH_COOKIE_DOMAIN,
        )

        return None

    return router

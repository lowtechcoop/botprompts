import time

from app.config import BaseConfig
from app.core.error_handling import ERROR_HANDLERS
from app.utils.limiter import limiter
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

log = get_logger(__name__)

SHOW_API_DOCS_ENVIRONMENTS = ["development", "staging"]
"""
Ensure that the jsonapi, swagger, and redoc are not visible where they are not permitted
"""

EXCLUDE_PROCESS_TIME_PATHS = [
    "/auth",
]
"""
These paths, prefixed with the API_V1, are excluded from adding the 'X-Process-Time' header,
typically for security reasons
"""


class BotpromptsWebapp(FastAPI):
    """
    Wrapper class for the BotpromptsWebapp
    """

    config: BaseConfig

    def initialize_config(self, config: BaseConfig) -> None:
        """
        Initializes the webapp
        """

        self.config = config


def create_webapp(config: BaseConfig) -> BotpromptsWebapp:
    """
    Method that creates the Botprompts app
    """

    log.debug("Creating Botprompts based on supplied config")

    app_init_configuration = {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "debug": config.DEBUG,
    }

    # Hide the Swagger and OpenAPI documentation when it's not one of the
    # valid environments
    if config.APP_ENVIRONMENT not in SHOW_API_DOCS_ENVIRONMENTS:
        app_init_configuration["openapi_url"] = None
    else:
        app_init_configuration["openapi_url"] = "/openapi.json"

    app = BotpromptsWebapp(**app_init_configuration)
    app.initialize_config(config)

    ###
    ### Rate Limiter
    ###
    app.state.limiter = limiter

    ###
    ### Guest Authentication
    ###
    app.state.guest = {
        "role_name": config.AUTH_GUEST_USER_ROLE_NAME,
        "role": None,
        "permissions": [],
    }

    ###
    ### Exception handling
    ###
    for error_class in ERROR_HANDLERS:
        app.add_exception_handler(error_class, ERROR_HANDLERS[error_class])

    ###
    ### HTTP section
    ###
    if config.CORS_ENABLE:
        log.info("CORS Enabled")
        log.debug("CORS settings:")
        log.debug("\t Allow-Credentials: %s", config.CORS_ALLOW_CREDENTIALS)
        log.debug("\t Allow-Origins: %s", config.CORS_ALLOW_ORIGINS)
        log.debug("\t Allow-Methods: %s", config.CORS_ALLOW_METHODS)
        log.debug("\t Allow-Headers: %s", config.CORS_ALLOW_HEADERS)
        log.debug("\t Allow-Origin-Regex: %s", config.CORS_ALLOW_ORIGIN_REGEX)
        log.debug("\t Expose-Headers: %s", config.CORS_EXPOSE_HEADERS)
        log.debug("\t Max-Age: %s", config.CORS_MAX_AGE)

        app.add_middleware(
            CORSMiddleware,
            allow_credentials=config.CORS_ALLOW_CREDENTIALS,
            allow_origins=config.CORS_ALLOW_ORIGINS,
            allow_methods=config.CORS_ALLOW_METHODS,
            allow_headers=config.CORS_ALLOW_HEADERS,
            allow_origin_regex=config.CORS_ALLOW_ORIGIN_REGEX,
            expose_headers=config.CORS_EXPOSE_HEADERS,
            max_age=config.CORS_MAX_AGE,
        )
    else:
        log.info("CORS disabled")

    if config.PROXY_ENABLE:
        log.info("Proxy Headers enabled")
        log.debug("Proxy Headers settings:")
        log.debug("\t Trusted-Hosts: %s", config.PROXY_TRUSTED_HOSTS)

        app.add_middleware(
            ProxyHeadersMiddleware, trusted_hosts=config.PROXY_TRUSTED_HOSTS
        )
    else:
        log.info("Proxy Headers disabled")

    if config.GZIP_ENABLE:
        log.info("Gzip Enabled")
        log.debug("Gzip settings")
        log.debug("\t Gzip minimum size: %d", int(config.GZIP_MINIMUM_SIZE))

        app.add_middleware(GZipMiddleware, minimum_size=int(config.GZIP_MINIMUM_SIZE))
    else:
        log.info("Gzip Disabled")

    if config.THH_ENABLE:
        log.info("Trusted Host Headers enabled")
        log.debug("Trusted Host Headers settings:")
        log.debug("\t Trusted Host Headers allowed hosts: %s", config.THH_ALLOWED_HOSTS)

        app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=config.THH_ALLOWED_HOSTS
        )
    else:
        log.info("Trusted Host Headers disabled")

    if config.RATE_LIMIT_ENABLED:
        log.info("Enabling Global Rate Limit")
        log.debug("\t Global Rate Limit is %s", config.RATE_LIMIT_GLOBAL)
        app.add_middleware(SlowAPIMiddleware)
    else:
        log.info(
            "Global Rate Limit disabled. Note: Individual routes may still be limited"
        )

    ###
    ### Middleware section
    ###

    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        do_add_header: bool = True
        for exclude_path in EXCLUDE_PROCESS_TIME_PATHS:
            if request.url.path.startswith(f"{config.API_URL_PREFIX_V1}{exclude_path}"):
                do_add_header = False

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        if do_add_header:
            response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")

        return response

    @app.middleware("http")
    async def replace_server_name(request, call_next):
        response = await call_next(request)
        response.headers["server"] = f"{config.APP_NAME}/{config.APP_VERSION}"
        return response

    ###
    ### Router section
    ###
    main_router = APIRouter()

    from app.routes import api_router

    main_router.include_router(api_router, prefix=f"{config.API_URL_PREFIX_V1}")

    # Connect the router structure to the entire app
    app.include_router(main_router)

    log.debug("Configured routes")
    for r in app.routes:
        log.debug(
            "\t name: '%s' path:'%s' methods: %s",
            r.name,  # type: ignore
            r.path,  # type: ignore
            r.methods if hasattr(r, "methods") else "N/A",  # type: ignore
        )

    @app.on_event("startup")
    def on_startup() -> None:
        """
        Events running on startup
        """

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        """
        Events running on shutdown
        """
        pass

    return app

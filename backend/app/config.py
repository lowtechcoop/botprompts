import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.utils.types import parse_type
from attrs import asdict, define
from dotenv import load_dotenv
from dpn_pyutils.file import read_file_text

ENV_FILENAME = os.environ.get("DOTENV", ".env")


@define(auto_attribs=True, auto_detect=True, kw_only=True)
class BaseConfig:
    APP_NAME: str
    APP_SYS_NAME: str
    APP_VERSION: str
    API_URL_PREFIX_V1: str

    LOGGING_CONFIG_FILE: str
    APP_ENVIRONMENT: str
    DEBUG: bool = False
    SLUG_MAX_LENGTH: int = 12
    PROMPT_MAX_LENGTH: int = 1000

    CORS_ENABLE: bool
    CORS_ALLOW_ORIGINS: List[str]
    CORS_ALLOW_METHODS: List[str]
    CORS_ALLOW_HEADERS: List[str]
    CORS_EXPOSE_HEADERS: List[str] = []
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_ORIGIN_REGEX: str | None = None
    CORS_MAX_AGE: int = 600

    DB_IS_ASYNC: bool
    DB_ENGINE: str
    DB_USERNAME: str
    DB_PASSWORD: Optional[str] = None
    DB_PASSWORD_FILE: Optional[str] = None
    DB_HOST: str
    DB_NAME: str
    DB_OPTIONS: str
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int

    PROXY_ENABLE: bool
    PROXY_TRUSTED_HOSTS: List[str]

    GZIP_ENABLE: bool
    GZIP_MINIMUM_SIZE: int

    # Trusted Host Header middleware
    THH_ENABLE: bool
    THH_ALLOWED_HOSTS: List[str]

    # Jwt Authentication
    JWT_SECURITY_TOKEN: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_LIFETIME_SECONDS: int
    JWT_REFRESH_TOKEN_LIFETIME_SECONDS: int
    JWT_REFRESH_COOKIE_NAME: str
    JWT_REFRESH_COOKIE_DOMAIN: str
    JWT_REFRESH_COOKIE_HTTPONLY: bool
    JWT_REFRESH_COOKIE_SECURE: bool
    JWT_REFRESH_COOKIE_SAMESITE: str
    JWT_REFRESH_COOKIE_PATH: str

    @classmethod
    def from_env(cls) -> "BaseConfig":
        """
        Creates a BaseConfig class from a dotenv.
        """

        env_dict = dict(os.environ)
        return cls(
            **{
                a.name: parse_type(env_dict[a.name])
                for a in cls.__attrs_attrs__  # type: ignore
                if a.name in env_dict
            }
        )  # type: ignore


class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


@lru_cache()
def get_config() -> BaseConfig:
    """
    Get the configuration settings based on the current config environment.
    """

    configuration_environments = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    if not Path(ENV_FILENAME).exists():
        raise RuntimeError(f"Config file '{ENV_FILENAME}' does not exist.")

    load_dotenv(dotenv_path=ENV_FILENAME, override=True)

    # Override the ENV variables if they have been set with the _FILE version
    os.environ["DB_USERNAME"] = load_environ_name_or_file("DB_USERNAME", "")
    os.environ["DB_PASSWORD"] = load_environ_name_or_file("DB_PASSWORD", "")
    os.environ["DB_NAME"] = load_environ_name_or_file("DB_NAME", "")
    os.environ["DB_HOST"] = load_environ_name_or_file("DB_HOST", "")

    APP_ENVIRONMENT = os.environ.get(
        "APP_ENVIRONMENT", "UNDEFINED_APP_ENVIRONMENT_FIX_IN_DOTENV_FILE"
    )

    # Instantiate the correct config class based on the supplied environment variable
    # which assumes FASTAPI_CONFIG is one of "development", "production", or "testing"
    settings = configuration_environments[APP_ENVIRONMENT].from_env()  # type: ignore

    return settings


def load_environ_name_or_file(environ_key: str, default: str) -> str:
    """
    Load an environ from a name or a file (if it exists) returning the value or the supplied default
    """

    environ_value_file = os.environ.get(f"{environ_key.upper()}_FILE", None)
    if environ_value_file is not None:
        environ_value_file_path = Path(environ_value_file)
        if not environ_value_file_path.exists():
            raise ValueError(
                f"Environ key '{environ_key}_FILE' is set but the file does not exist or "
                f"cannot be accessed at '{environ_value_file_path.absolute()}'"
            )

        return read_file_text(environ_value_file_path).replace("\n", "")

    return os.environ.get(environ_key, default)


def get_config_dict(
    config: BaseConfig, prefix: str, exclude_keys: List[str] = []
) -> Dict[str, Any]:
    """
    Gets a set of config keys as a dictionary from base config that start with the supplied prefix,
    optionally excluding specific, full-text keys
    """

    if config is None:
        raise ValueError(
            f"Config object is null, cannot get config keys with prefix {prefix}"
        )

    config_dict = asdict(config, recurse=True)

    return {
        config_key: config_dict[config_key]
        for config_key in config_dict  # type: ignore
        if config_key not in exclude_keys and config_key.startswith(prefix)
    }

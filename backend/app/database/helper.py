import hashlib
from typing import Any, Dict, List, Literal

from app.config import BaseConfig, get_config_dict
from dpn_pyutils.common import get_logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.future import Engine

log = get_logger(__name__)


def get_connection_string(config: BaseConfig) -> str:
    """
    Gets the database connection string for this service
    """

    sql_conn = "{}://{}:{}@{}/{}".format(
        config.DB_ENGINE,
        config.DB_USERNAME,
        config.DB_PASSWORD,
        config.DB_HOST,
        config.DB_NAME,
    )

    options = config.DB_OPTIONS
    if options is not None:
        sql_conn = "{}?{}".format(sql_conn, options)

    return sql_conn


def get_db_settings_from_config(
    config: BaseConfig, exclude_keys: List[str]
) -> Dict[str, Any]:
    """
    Get all the settings from config that start with "DB_" and excludes the
    specific set of supplied keys.
    """

    config_dict = get_config_dict(
        config=config, prefix="DB_", exclude_keys=exclude_keys
    )
    return {key.replace("DB_", "").lower(): config_dict[key] for key in config_dict}


def get_db_key_from_connection_string(database_connection_string) -> str:
    """
    Gets a hashed string representing a database connection string. This ensures
    that multiple databases have their own connection.
    """

    hashed_connection_string: str = hashlib.sha256(
        database_connection_string.encode("utf-8")
    ).hexdigest()

    return hashed_connection_string


def test_connection(engine: Engine) -> bool:
    """
    Tests whether the engine is able to connect
    """

    test_select: Literal["1"] = "1"

    with engine.connect() as connection:
        with connection.begin():
            if connection is None:
                raise ValueError("Database connection is null or dropped")

            result: Any = connection.execute(  # type: ignore
                text("SELECT '{}'".format(test_select))
            ).first()[0]

    if result == test_select:
        return True

    # The result did not match what we expect or an exception was thrown
    return False


async def test_connection_async(engine: AsyncEngine) -> bool:
    """
    Tests whether the engine is able to connect in an async way
    """

    test_select: Literal["1"] = "1"

    async with engine.connect() as connection:
        async with connection.begin():
            if connection is None:
                raise ValueError("Database connection is null or dropped")

            result: Any = await connection.execute(  # type: ignore
                text("SELECT '{}'".format(test_select))
            )
            result = result.first()[0]

    if result == test_select:
        return True

    # The result did not match what we expect or an exception was thrown
    return False

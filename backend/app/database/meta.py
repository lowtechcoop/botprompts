from datetime import tzinfo
from typing import Dict

import pytz
from app.config import BaseConfig, get_config
from app.database.base import Base
from app.database.helper import (
    get_connection_string,
    get_db_key_from_connection_string,
    get_db_settings_from_config,
    test_connection,
)
from dpn_pyutils.common import get_logger
from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

log = get_logger(__name__)

config = get_config()


class DatabaseManager:
    """
    This class contains and stores the metadata about the configured database connections
    """

    config: BaseConfig
    """
    The complete application configuration object
    """

    db_connection_string: str
    """
    The connection string as specified by the env configuration
    """

    tz: tzinfo = pytz.timezone("UTC")
    """
    Default to UTC timezone for check calculations
    """

    focused_db_key: str
    """
    Currently focused database key
    """

    db: Engine
    """
    Currently focused database connection
    """

    metadata: MetaData
    """
    Currently focused database connection's metadata
    """

    session: Session
    """
    Currently focused database connection's session creation object
    """

    DB_ENGINES: Dict[str, Engine] = {}
    """
    This is a set of currently active database engines. Typically this will contain one connection,
    however if multiple databases are being used, this will contain a connection for each one.
    """

    DB_METADATA: Dict[str, MetaData] = {}
    """
    This is a set of currently active database metadata. Typically this will contain one metadata,
    however if multiple databases are being used, this will contain a metadata object for each one.
    """

    DB_SESSIONMAKER: Dict[str, Session] = {}
    """
    This is a set of currently active sessionmaker objects metadata. Typically this will contain one
    however if multiple databases are being used, this will contain a sessionmaker for each one.
    """

    DB_SETTINGS_OVERRIDE_EXCLUSION_SET = {
        "DB_IS_ASYNC",
        "DB_ENGINE",
        "DB_USERNAME",
        "DB_PASSWORD",
        "DB_PASSWORD_FILE",
        "DB_HOST",
        "DB_NAME",
        "DB_OPTIONS",
    }
    """
    This is a set of fields to exclude when looking for settings to override SqlAlchemy database
    defaults.
    The other options starting with DB_ in the config object are implicitly passed through to the
    SqlAlchemy creation method
    """

    def __init__(self, config: BaseConfig = Depends(get_config)) -> None:
        """
        Initialize the Database Meta Manager
        """

        self.config = config

        self.focused_db_key = get_db_key_from_connection_string(
            get_connection_string(self.config)
        )

        db_settings = get_db_settings_from_config(
            config=self.config,
            exclude_keys=list(self.DB_SETTINGS_OVERRIDE_EXCLUSION_SET),
        )

        self.DB_ENGINES[self.focused_db_key] = create_engine(
            get_connection_string(self.config), **db_settings
        )

        self.db = self.DB_ENGINES[self.focused_db_key]

        try:
            if test_connection(self.db):
                log.debug("Database connection test successful")

        except OperationalError as e:
            log.error(
                "Could not test connection using connection string. "
                "Attempted connection string is '%s'",
                get_connection_string(self.config),
            )

            raise e

        self.base = declarative_base()

        log.debug("Initializing database metadata for database")
        if self.focused_db_key not in self.DB_METADATA:
            self.DB_METADATA[self.focused_db_key] = MetaData()
            self.metadata = self.DB_METADATA[self.focused_db_key]

        log.debug("Creating sessionmaker for database metadata")
        if self.focused_db_key not in self.DB_SESSIONMAKER:
            self.DB_SESSIONMAKER[self.focused_db_key] = sessionmaker(bind=self.db)  # type: ignore
            self.session = self.DB_SESSIONMAKER[self.focused_db_key]

            log.debug("Reflecting existing database structures")
            self.metadata.reflect(bind=self.db)

            log.debug("Binding reflected metadata to declarative base")
            Base.metadata = self.metadata  # type: ignore

        log.debug("Ready to import declarative models")
        self.on_import_declarative_models()

    def on_import_declarative_models(self) -> None:
        """
        Override this method in a subclass and list all of the declarative models that need
        to be imported into base
        """
        import_declarative_models()


def import_declarative_models() -> None:
    """
    This method contains all the declarative models that we need to import
    """

    from app.modules.prompts.models import PromptHistoryRecord, PromptRecord  # noqa


def get_db(db_manager: DatabaseManager = Depends(DatabaseManager)) -> Engine:
    """
    Gets the configured database engine
    """
    return db_manager.db


def get_session(db_manager: DatabaseManager = Depends(DatabaseManager)):
    """
    Creates a new session and yields it for operations
    """
    with sessionmaker(db_manager.db)() as session:
        yield session

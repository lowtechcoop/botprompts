"""
Main module that bootstraps the FastAPI application and creates the app
"""
import logging
from pathlib import Path
from typing import Any, Dict

import better_exceptions
from app.config import get_config
from dpn_pyutils.common import get_logger, initialize_logging
from dpn_pyutils.file import read_file_json

# Initialize exception management and load config
better_exceptions.hook()
config = get_config()

# Initialize logging and capture warnings
logging_configuration: Dict[str, Any] = read_file_json(Path(config.LOGGING_CONFIG_FILE))
initialize_logging(logging_configuration)
logging.captureWarnings(True)
log = get_logger(config.APP_SYS_NAME)
log.info(
    "Starting '%s' (system_name=%s) version %s",
    config.APP_NAME,
    config.APP_SYS_NAME,
    config.APP_VERSION,
)

# Bootstrapped app, run by uvicorn process
from app.app import create_webapp  # noqa: E402

app = create_webapp(config)

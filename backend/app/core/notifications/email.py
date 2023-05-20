"""
This module is for methods that connect an email notification client to AWS SES
"""
from pathlib import Path
from urllib.parse import quote_plus

import boto3
from app.config import BaseConfig, get_config
from botocore.config import Config
from dpn_pyutils.common import get_logger
from fastapi import Depends, Request
from jinja2 import Environment, Template, select_autoescape
from jinja2.loaders import FileSystemLoader

log = get_logger(__name__)


class EmailNotifier:
    """
    Email notifier class
    """

    config: BaseConfig
    request: Request
    env: Environment
    # mail_client: botocore.client.SES # Does not exist at static type check time
    templates_path: Path

    def __init__(
        self,
        request: Request = Depends(Request),
        config: BaseConfig = Depends(get_config),
        templates_dir: str = "",
        # rendering_environment: Environment = Depends(get_mail_rendering_environment),
        # mail_client=Depends(get_mail_client),
    ) -> None:
        self.request = request
        self.config = config
        self.__create_rendering_environment(templates_dir)
        self.__create_mail_client(self.config)

    def __create_rendering_environment(self, templates_dir: str):
        """
        Creates a Jinja2 rendering environment
        """

        log.debug(
            "Creating mail rendering environment based on supplied template path '%s'",
            templates_dir,
        )

        self.templates_path = Path(templates_dir)
        if not self.templates_path.exists():
            log.warn(
                "Mail template path does not exist at '%s'",
                self.templates_path.absolute(),
            )

        self.env = Environment(
            loader=FileSystemLoader(self.templates_path),
            autoescape=select_autoescape(),
        )

        self.env.globals["url_for"] = self.request.url_for
        self.env.filters["quote_plus"] = lambda u: quote_plus(u)
        self.env.filters["datetime"] = lambda dt, fmt: dt.strftime(fmt)

    def __create_mail_client(self, config: BaseConfig):
        """
        Creates a boto3 AWS SES mail client
        """

        self.mail_client = boto3.client(
            "ses",
            config=Config(
                region_name=config.EMAIL_SES_REGION,
                signature_version="v4",
                retries={"max_attempts": 10, "mode": "standard"},
            ),
            aws_access_key_id=config.EMAIL_SES_ACCESS_KEY,
            aws_secret_access_key=config.EMAIL_SES_SECRET_KEY,
        )

    def get_template(self, template_name: str) -> Template:
        """
        Gets a Jinja2 template based on the supplied template name / path
        """

        candidate_template = template_name
        if not template_name.lower().endswith(".html"):
            candidate_template = f"{template_name}.html"

        return self.env.get_template(candidate_template)

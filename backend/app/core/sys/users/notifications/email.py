from app.config import BaseConfig, get_config
from app.core.notifications.email import EmailNotifier
from app.core.sys.users import models
from dpn_pyutils.common import get_logger
from fastapi import Depends, Request

log = get_logger(__name__)


class UserEmailNotifier(EmailNotifier):
    """
    User email notifier
    """

    def __init__(
        self,
        request: Request,
        config: BaseConfig = Depends(get_config),
    ) -> None:
        super().__init__(
            request=request,
            config=config,
            templates_dir="app/core/sys/users/notifications/templates",
        )

    def notify_users_account_recently_updated(self, user: models.SysUser) -> None:
        """
        Sends a user account was recently updated email
        """

        rendered_template = self.get_template("user_account_changed").render(user=user)

        if self.config.EMAIL_SERVICE_ENABLED:
            response = self.mail_client.send_email(
                Source=self.config.EMAIL_FROM,
                ReplyToAddresses=[self.config.EMAIL_REPLY_TO],
                Destination={
                    "ToAddresses": [
                        "{}".format(user.email),
                    ],
                },
                Message={
                    "Subject": {
                        "Data": "Your account was changed on #lowtech Bot Prompts",
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Text": {
                            "Data": "Please view this email with a HTML-compatible email client or "
                            "in the browser",
                            "Charset": "UTF-8",
                        },
                        "Html": {"Data": rendered_template, "Charset": "UTF-8"},
                    },
                },
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                log.error(
                    "Error while trying to send user password recovery email to "
                    "recipient '{}' (ID: '{}'). The error was {}".format(
                        user.email, str(user.id), response
                    )
                )
        else:
            log.warn(
                "Email service is disabled via config, refusing to send user password recovery "
                "token email"
            )

    def notify_users_account_recovery_token(
        self, user: models.SysUser, token: str
    ) -> None:
        """
        Sends a user account recovery email
        """

        rendered_template = self.get_template("user_password_recovery").render(
            user=user, token=token
        )

        if self.config.EMAIL_SERVICE_ENABLED:
            response = self.mail_client.send_email(
                Source=self.config.EMAIL_FROM,
                ReplyToAddresses=[self.config.EMAIL_REPLY_TO],
                Destination={
                    "ToAddresses": [
                        "{}".format(user.email),
                    ],
                },
                Message={
                    "Subject": {
                        "Data": "Your password reset link for #lowtech Bot Prompts",
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Text": {
                            "Data": "Please view this email with a HTML-compatible email client "
                            "or in the browser",
                            "Charset": "UTF-8",
                        },
                        "Html": {"Data": rendered_template, "Charset": "UTF-8"},
                    },
                },
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                log.error(
                    "Error while trying to send user password recovery email to recipient "
                    "'{}' (ID: '{}'). The error was {}".format(
                        user.email, str(user.id), response
                    )
                )
        else:
            log.warn(
                "Email service is disabled via config, refusing to send user password recovery "
                "token email"
            )

    def notify_email_verification(self, user: models.SysUser, token: str) -> None:
        """
        Sends a user email verification mail
        """
        rendered_template = self.get_template("user_verify_email").render(
            user=user, token=token
        )

        if self.config.EMAIL_SERVICE_ENABLED:
            response = self.mail_client.send_email(
                Source=self.config.EMAIL_FROM,
                ReplyToAddresses=[self.config.EMAIL_REPLY_TO],
                Destination={
                    "ToAddresses": [
                        "{}".format(user.email),
                    ],
                },
                Message={
                    "Subject": {
                        "Data": "Verify your email address for #lowtech Bot Prompts",
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Text": {
                            "Data": "Please view this email with a HTML-compatible email client "
                            "or in the browser",
                            "Charset": "UTF-8",
                        },
                        "Html": {"Data": rendered_template, "Charset": "UTF-8"},
                    },
                },
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                log.error(
                    "Error while trying to send email verification email to recipient "
                    "'{}' (ID: '{}'). The error was {}".format(
                        user.email, str(user.id), response
                    )
                )
        else:
            log.warn(
                "Email service is disabled via config, refusing to send user "
                "registration token email"
            )

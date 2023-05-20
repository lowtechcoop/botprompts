import string
from typing import Tuple

from app.config import get_config
from app.core.auth.errors import (
    PW_LACKS_DIGITS,
    PW_LACKS_LOWERCASE,
    PW_LACKS_MIN_LENGTH,
    PW_LACKS_PUNCTUATION,
    PW_LACKS_UPPERCASE,
    UserInvalidPasswordException,
)
from passlib import pwd
from passlib.context import CryptContext

config = get_config()


PASSWORD_MIN_LENGTH = 8

DEFAULT_SECURE_GENERATED_PASSWORD_LENGTH = 16


class PasswordHelper:
    """
    Configures a password helper
    """

    context: CryptContext

    def __init__(self, context: CryptContext | None = None) -> None:
        """
        Creates a password helper, optionally providing a cryptographic context
        """

        if context is None:
            self.context = CryptContext(
                schemes=[config.AUTH_CRYPT_SCHEME], deprecated="auto"
            )
        else:
            self.context = context

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> Tuple[bool, str | None]:
        return self.context.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.context.hash(password)

    def generate(self, length: int = DEFAULT_SECURE_GENERATED_PASSWORD_LENGTH) -> str:
        return pwd.genword(length=length)

    def validate_password(self, plaintext: str) -> bool:
        """
        Validates a password for complexity requirements
        """

        has_uppercase = False
        has_lowercase = False
        has_digits = False
        has_punctuation = False
        problems = []

        if len(plaintext) < PASSWORD_MIN_LENGTH:
            problems.append(PW_LACKS_MIN_LENGTH)

        for c in plaintext:
            if c in string.ascii_lowercase:
                has_lowercase = True
            elif c in string.ascii_uppercase:
                has_uppercase = True
            elif c in string.digits:
                has_digits = True
            elif c in string.punctuation:
                has_punctuation = True

        # Assess what issues are with the password plaintext itself
        if not has_lowercase:
            problems.append(PW_LACKS_LOWERCASE)
        if not has_uppercase:
            problems.append(PW_LACKS_UPPERCASE)
        if not has_digits:
            problems.append(PW_LACKS_DIGITS)
        if not has_punctuation:
            problems.append(PW_LACKS_PUNCTUATION)

        if len(problems) > 0:
            raise UserInvalidPasswordException(problems)

        return True

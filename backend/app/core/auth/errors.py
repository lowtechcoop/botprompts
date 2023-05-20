from app.core.errors import AppException

##
##  Password error states (additive)
##
PW_LACKS_LOWERCASE = "PW_LACKS_LOWERCASE"
PW_LACKS_UPPERCASE = "PW_LACKS_UPPERCASE"
PW_LACKS_DIGITS = "PW_LACKS_DIGITS"
PW_LACKS_PUNCTUATION = "PW_LACKS_PUNCTUATION"
PW_LACKS_MIN_LENGTH = "PW_LACKS_MIN_LENGTH"


class AuthException(AppException):
    """
    Exception class for all authentication, authorization, and user/role/permission exceptions
    """

class UsersException(AuthException):
    pass


class UserInvalidPasswordException(AuthException):
    pass


class UserAlreadyExists(AuthException):
    pass


class UserDoesNotExist(AuthException):
    pass


class UserInvalidToken(AuthException):
    pass


class UserLacksRequiredScopes(AuthException):
    pass


class UserLacksPermission(AuthException):
   pass

class InvalidPermission(AuthException):
    """
    Error raised when an invalid permission string is supplied
    (i.e., does not match a known permission)
    """
    pass

class UserAlreadyVerified(AuthException):
    pass


class UserInvalidVerifyToken(AuthException):
    pass


class UserInactive(AuthException):
    pass


class UserInvalidPasswordToken(AuthException):
    pass


class RoleExistsException(AuthException):
    pass


class RoleDoesNotExist(AuthException):
    pass

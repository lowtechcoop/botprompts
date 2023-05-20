TOKEN_COLUMN_LENGTH = 256
TOKEN_TYPE_COLUMN_LENGTH = 32
MIN_USER_DISPLAY_NAME_LENGTH = 5

TOKEN_TYPE_ACCESS = "access_token"
TOKEN_TYPE_REFRESH = "refresh_token"
TOKEN_TYPE_INVITE = "invite_token"
TOKEN_TYPE_VERIFICATION = "verification_token"
TOKEN_TYPE_PASSWORD_RESET = "password_reset"

ACCESS_TOKEN_AUDIENCE = "users:access"
REFRESH_TOKEN_AUDIENCE = "users:refresh"
RESET_PASSWORD_TOKEN_AUDIENCE = "users:reset"
VERIFICATION_TOKEN_AUDIENCE = "users:verify"

TOKEN_INVALID = "TOKEN_INVALID"
"""
Used when trying to validate a JWT token. Paired with a HTTP 403 Forbidden
"""

TOKEN_EXPIRED = "TOKEN_EXPIRED"
"""
Used when trying to validate a JWT token. Paired with a HTTP 403 Forbidden
"""

EMAIL_INVALID = "EMAIL_INVALID"
EMAIL_EXISTS = "EMAIL_EXISTS"
NAME_EXISTS = "NAME_EXISTS"
NAME_TOO_SHORT = "NAME_TOO_SHORT"


USER_DOES_NOT_EXIST = "USER_DOES_NOT_EXIST"

USER_ALREADY_VERIFIED = "USER_ALREADY_VERIFIED"
"""
Raised when trying to create verification tokens for a user
"""

LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
"""
Raised when there are invalid credentials on access_token or refresh_token
"""


TOKEN_FAIL_USER_MISMATCH = "TOKEN_FAIL_USER_MISMATCH"
"""
Raised when the user and jwt sub fail matching
"""

TOKEN_FAIL_REVOKED = "TOKEN_FAIL_REVOKED"
"""
Raised when the jwt token has been revoked
"""

REFRESH_TOKEN_ROTATE_ERROR = "REFRESH_TOKEN_ROTATE_ERROR"
"""
Internal error when attempting to rotate a refresh token
"""

##
##  Roles
##
ROLE_ALREADY_EXISTS = "ROLE_ALREADY_EXISTS"
ROLE_DOES_NOT_EXIST = "ROLE_DOES_NOT_EXIST"

##
##  Permissions
##
PERMISSION_ALREADY_EXISTS = "PERMISSION_ALREADY_EXISTS"
PERMISSION_DOES_NOT_EXIST = "PERMISSION_DOES_NOT_EXIST"


##
##  Verify
##
ROLE_AUTHENTICATED_USER = "authenticated_user"

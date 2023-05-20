from fastapi.security import OAuth2PasswordBearer

ACCESS_TOKEN_SCOPES_USER = "user"
ACCESS_TOKEN_SCOPES_SUPERUSER = "superuser"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/token",
    scopes={
        ACCESS_TOKEN_SCOPES_USER: "Normal user access, subject to permission checks",
        ACCESS_TOKEN_SCOPES_SUPERUSER: "Super user access, bypasses all permission checks",
    },
    auto_error=False,
)

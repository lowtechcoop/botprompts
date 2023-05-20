import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

import jwt
import pytz
from app.config import get_config
from app.core.auth import oauth2
from app.core.auth.errors import (
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInvalidPasswordException,
    UserInvalidToken,
    UsersException,
)
from app.core.auth.password import PasswordHelper
from app.core.auth.utils import decode_jwt_token_payload, get_user_roles_as_string
from app.core.resources.adapters import AdapterResources
from app.core.sys.users import constants as user_constants
from app.core.sys.users import models, schemas
from app.core.sys.users.adapters import SysUsersAdapter, SysUserTokensAdapter
from app.core.sys.variables.models import SysVariable
from app.database.meta import get_session
from dpn_pyutils.common import get_logger
from fastapi import Depends, Request
from sqlalchemy.orm import Session

COMMUNITY_NAME_BLOCKLIST_VARIABLE = "admin.blocklists.communitynames"
"""
The names in this list are not permitted verbatim
"""

COMMUNITY_NAME_BLOCKLIST_PREFIX = "admin.blocklists.communitynames.prefixnames"
"""
The names in this list are not permitted to be prefixes, such as 'admin' with any characters
"""

log = get_logger(__name__)

config = get_config()


class UserLogicManager:
    """
    Defines a class that provides user management
    """

    sys_users: SysUsersAdapter
    sys_roles: AdapterResources[models.SysRole]
    sys_permissions: AdapterResources[models.SysPermission]
    sys_variables: AdapterResources[SysVariable]
    sys_users_tokens: SysUserTokensAdapter
    password_helper: PasswordHelper

    def __init__(self, session: Session) -> None:
        """
        Initializes the user logic manager
        """

        self.sys_users = SysUsersAdapter(session=session, table=models.SysUser)
        self.sys_roles = AdapterResources(session=session, table=models.SysRole)
        self.sys_permissions = AdapterResources(
            session=session, table=models.SysPermission
        )
        self.sys_users_tokens = SysUserTokensAdapter(
            session=session, table=models.SysUserToken
        )
        self.sys_variables = AdapterResources(session=session, table=SysVariable)

        self.password_helper = PasswordHelper()

    async def login_by_email(self, email: str, password: str) -> models.SysUser | None:
        """
        Attempts to log a user in by checking passwords
        """

        user = await self.sys_users.get_by_email(email)
        if user is None or not user.is_verified:
            # Run the password hash anyway to defeat timing attacks and mitigate against CWE-208
            # https://cwe.mitre.org/data/definitions/208.html
            self.password_helper.hash(password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            password, user.password
        )
        if not verified:
            return None

        if updated_password_hash is not None:
            # Upgrade the password hash by updating the user hash in the database
            await self.sys_users.update(user, {"password": updated_password_hash})

        return user

    async def create_token_password_reset(
        self, user: models.SysUser, simulate: bool = False
    ) -> models.SysUserToken | None:
        """
        Creates a password reset token and stores it in the token table
        :param simulate: If False, it does not create the token it the database table
        """

        token_length = config.AUTH_PW_RESET_TOKEN_LENGTH
        if token_length > user_constants.TOKEN_COLUMN_LENGTH:
            log.warn(
                "Configured password reset token length (%d) is greater than database column (%d). "
                "Truncating password reset token length to %d",
                token_length,
                user_constants.TOKEN_COLUMN_LENGTH,
                user_constants.TOKEN_COLUMN_LENGTH,
            )
            token_length = user_constants.TOKEN_COLUMN_LENGTH

        verification_token = {
            "token_type": user_constants.TOKEN_TYPE_PASSWORD_RESET,
            "token": self.password_helper.generate(length=token_length),
            "user": user,
            "user_id": user.id,
            "num_uses_remaining": 1,
            "expires_at": datetime.utcnow()
            + timedelta(seconds=config.AUTH_PW_RESET_TOKEN_LIFETIME_SECONDS),
        }

        if simulate:
            return None

        return await self.sys_users_tokens.create(verification_token)

    async def create_token_access(
        self,
        user: models.SysUser,
        fresh_auth: bool = False,
        offline_access: bool = True,
    ) -> schemas.UsersAuthCompleteResponse:
        """
        Creates an access token and stores it in the token table
        :param fresh_auth:
            True when the user has just authenticated, False when using a refresh_token
        """

        access_token_expires = datetime.utcnow() + timedelta(
            seconds=config.JWT_ACCESS_TOKEN_LIFETIME_SECONDS
        )
        access_token_data = {
            "iss": config.JWT_ISS,
            "sub": str(user.id),
            "nbf": datetime.utcnow(),
            "exp": access_token_expires,
            "aud": user_constants.ACCESS_TOKEN_AUDIENCE,
            "scope": "",
        }

        valid_scopes = []
        if fresh_auth:
            valid_scopes.append("fresh")

        if offline_access:
            valid_scopes.append("offline-access")

        if user.is_superuser:
            valid_scopes.extend(
                [
                    oauth2.ACCESS_TOKEN_SCOPES_USER,
                    oauth2.ACCESS_TOKEN_SCOPES_SUPERUSER,
                ]
            )
        else:
            valid_scopes.append(oauth2.ACCESS_TOKEN_SCOPES_USER)

        user_roles_string = get_user_roles_as_string(user)
        if len(user_roles_string) > 0:
            valid_scopes.extend(user_roles_string)

        access_token_data["scope"] = " ".join(valid_scopes)
        tokens = schemas.UsersAuthCompleteResponse(
            access_token=jwt.encode(
                access_token_data,
                key=str(config.JWT_SECURITY_TOKEN),
                algorithm=config.JWT_ALGORITHM,
            ),  # type: ignore
            expires_at=int(access_token_expires.timestamp()),
            token_type="bearer",
        )

        if offline_access:
            refresh_token_expires = datetime.utcnow() + timedelta(
                seconds=config.JWT_REFRESH_TOKEN_LIFETIME_SECONDS
            )
            refresh_token_data = {
                "iss": config.JWT_ISS,
                "sub": str(user.id),
                "nbf": datetime.utcnow(),
                "exp": refresh_token_expires,
                "aud": user_constants.REFRESH_TOKEN_AUDIENCE,
            }
            refresh_token = jwt.encode(
                refresh_token_data,
                key=str(config.JWT_SECURITY_TOKEN),
                algorithm=config.JWT_ALGORITHM,
            )

            tokens.refresh_token = refresh_token  # type: ignore
            tokens.refresh_token_expires_at = int(refresh_token_expires.timestamp())

            # Add refresh token to the database
            await self.sys_users_tokens.create(
                {
                    "token_type": user_constants.TOKEN_TYPE_REFRESH,
                    "token": tokens.refresh_token,
                    "user": user,
                    "user_id": user.id,
                    "num_uses_remaining": 1,
                    "expires_at": refresh_token_expires,
                }
            )

        return tokens

    async def update_user_superuser_add(self, user: models.SysUser) -> models.SysUser:
        """
        Add is_superuser flag to a user
        """

        # This is done this way because user can be bound to a different session, especially
        # if user was provided via a FastAPI Depends() call
        return await self.sys_users.update(
            await self.sys_users.get(user.id), {"is_superuser": True}
        )

    async def update_user_superuser_remove(
        self, user: models.SysUser
    ) -> models.SysUser:
        """
        Remove is_superuser flag from a user
        """

        # This is done this way because user can be bound to a different session, especially
        # if user was provided via a FastAPI Depends() call
        return await self.sys_users.update(
            await self.sys_users.get(user.id), {"is_superuser": False}
        )

    async def invalidate_existing_refresh_tokens(
        self, token: str, user: models.SysUser
    ):
        """
        Invalidates an existing refresh token for a user
        """

        stored_refresh_token = await self.sys_users_tokens.get_by_token(
            token, token_type=user_constants.TOKEN_TYPE_REFRESH
        )
        if (
            stored_refresh_token is None
            or stored_refresh_token.user_id != user.id
            or not stored_refresh_token.is_active
            or (
                pytz.UTC.localize(datetime.utcnow())
                >= stored_refresh_token.expires_at  # type: ignore
            )
        ):
            raise UserInvalidToken(user_constants.TOKEN_FAIL_REVOKED)

        await self.sys_users_tokens.delete(stored_refresh_token, hard_delete=True)

    async def get_user_from_token(
        self, token: str, token_audience: str = user_constants.ACCESS_TOKEN_AUDIENCE
    ) -> models.SysUser:
        """
        Gets a user from a JWT token
        """

        payload = decode_jwt_token_payload(token, audience=token_audience)

        if "sub" not in payload:
            raise UserInvalidToken(user_constants.TOKEN_FAIL_USER_MISMATCH)

        user = await self.sys_users.get(payload["sub"])
        if user is None:
            raise UserInvalidToken(user_constants.TOKEN_FAIL_USER_MISMATCH)

        return user

    async def rotate_refresh_token(
        self, token: str
    ) -> schemas.UsersAuthCompleteResponse:
        """
        Rotates a refresh token if it is valid and creates a new set of tokens
        """

        try:
            user = await self.get_user_from_token(token)

            await self.invalidate_existing_refresh_token(token, user)

            tokens = await self.create_token_access(
                user=user, fresh_auth=False, offline_access=True
            )

            return tokens

        except (
            jwt.InvalidAudienceError,
            jwt.ExpiredSignatureError,
            jwt.DecodeError,
        ) as e:
            raise UserInvalidToken(str(e))

    async def invalidate_existing_refresh_token(self, token: str, user: models.SysUser):
        """
        Invalidates an existing refresh token
        """

        stored_refresh_token = await self.sys_users_tokens.get_by_token(
            token, token_type=user_constants.TOKEN_TYPE_REFRESH
        )
        if (
            stored_refresh_token is None
            or stored_refresh_token.user_id != user.id
            or not stored_refresh_token.is_active
            or (
                pytz.UTC.localize(datetime.utcnow())
                >= stored_refresh_token.expires_at  # type: ignore
            )
        ):
            raise UserInvalidToken(user_constants.TOKEN_FAIL_REVOKED)

        await self.sys_users_tokens.delete(stored_refresh_token, hard_delete=True)

    async def can_create_user(
        self,
        user_create: schemas.UsersRegisterValidateRequest,
    ) -> bool:
        """
        Tests if the requested data can be created - returns true or throws exception
        """

        problems = []

        try:
            if user_create.password is not None:
                self.password_helper.validate_password(user_create.password)
        except UserInvalidPasswordException as e:
            problems.extend([str(e) for e in e.reason])

        if user_create.email is not None:
            existing_user_by_email = await self.sys_users.get_by_email(
                user_create.email
            )
            if existing_user_by_email is not None:
                problems.append(user_constants.EMAIL_EXISTS)

        if user_create.display_name is not None:
            has_name_problem = False

            if (
                len(user_create.display_name)
                < user_constants.MIN_USER_DISPLAY_NAME_LENGTH
            ):
                has_name_problem = True
                problems.append(user_constants.NAME_TOO_SHORT)

            if not has_name_problem:
                # Only do a database lookup if the username is not too short
                existing_user_by_display_name = (
                    await self.sys_users.get_by_display_name(user_create.display_name)
                )
                if existing_user_by_display_name is not None:
                    has_name_problem = True
                    problems.append(user_constants.NAME_EXISTS)

            if not has_name_problem:
                verbatim_blocklist = await self.sys_variables.get_by_name(
                    COMMUNITY_NAME_BLOCKLIST_VARIABLE
                )
                if verbatim_blocklist is not None:
                    has_blocked_name = False
                    # Block list is stored in CSV format, remove quotes and split on commas
                    for blocked_name in verbatim_blocklist.value.replace('"', "").split(
                        ","
                    ):
                        if (
                            user_create.display_name.strip().lower()
                            == blocked_name.lower()
                        ):
                            has_blocked_name = True
                            break

                    if has_blocked_name:
                        has_name_problem = True
                        problems.append(user_constants.NAME_EXISTS)

            if not has_name_problem:
                prefix_blocklist = await self.sys_variables.get_by_name(
                    COMMUNITY_NAME_BLOCKLIST_PREFIX
                )
                if prefix_blocklist is not None:
                    has_blocked_name = False
                    # Block list is stored in CSV format, remove quotes and split on commas
                    for blocked_name in prefix_blocklist.value.replace('"', "").split(
                        ","
                    ):
                        if (
                            user_create.display_name.strip()
                            .lower()
                            .startswith(blocked_name.lower())
                        ):
                            has_blocked_name = True
                            break

                    if has_blocked_name:
                        has_name_problem = True
                        problems.append(user_constants.NAME_EXISTS)

        if len(problems) > 0:
            raise UsersException(problems)

        return True

    async def create_user(
        self,
        user_create: schemas.UsersRegisterRequest,
        safe: bool = False,
        request: Request | None = None,
    ) -> models.SysUser:
        """
        Create the user in the database
        """

        self.password_helper.validate_password(user_create.password)

        existing_user_by_email = await self.sys_users.get_by_email(user_create.email)
        if existing_user_by_email is not None:
            raise UserAlreadyExists("email")

        existing_user_by_display_name = await self.sys_users.get_by_display_name(
            user_create.display_name
        )
        if existing_user_by_display_name is not None:
            raise UserAlreadyExists("display_name")

        user_dict = user_create.dict(include={"email", "display_name", "password"})
        user_dict["password"] = self.password_helper.hash(user_dict.pop("password"))

        created_user = await self.sys_users.create(user_dict)

        return created_user

    async def update_user(
        self, user: models.SysUser, update_dict: Dict[str, Any]
    ) -> models.SysUser:
        """
        Updates a user with the changed fields. Note: the check for whether or not this should
        be allowed needs to be done before this method is called. This method does not check for
        authorization to set is_superuser=True!
        """

        if "password" in update_dict:
            update_dict["password"] = self.password_helper.hash(
                update_dict.pop("password")
            )

        return await self.sys_users.update(
            await self.sys_users.get(user.id), update_dict
        )

    async def create_token_verification(
        self, user: models.SysUser
    ) -> models.SysUserToken:
        """
        Create a verification token and stores it in the database
        """

        if user.is_verified:
            raise UserAlreadyVerified(user_constants.USER_ALREADY_VERIFIED)

        # Check and delete any existing verification tokens
        existing_verification_tokens = await self.sys_users_tokens.get_user_tokens(
            user, token_type=user_constants.TOKEN_TYPE_VERIFICATION
        )
        if (
            existing_verification_tokens is not None
            and len(existing_verification_tokens) > 0
        ):
            for t in existing_verification_tokens:
                await self.sys_users_tokens.delete(t, hard_delete=True)

        # Create new token
        token_length = config.AUTH_EMAIL_VERIFICATION_TOKEN_LENGTH
        if token_length > user_constants.TOKEN_COLUMN_LENGTH:
            log.warn(
                "Configured verification token length (%d) is greater than database column (%d). "
                "Truncating verification token length to %d",
                token_length,
                user_constants.TOKEN_COLUMN_LENGTH,
                user_constants.TOKEN_COLUMN_LENGTH,
            )
            token_length = user_constants.TOKEN_COLUMN_LENGTH

        verification_token = {
            "token_type": user_constants.TOKEN_TYPE_VERIFICATION,
            "token": self.password_helper.generate(length=token_length),
            "user": user,
            "user_id": user.id,
            "num_uses_remaining": 1,
            "expires_at": datetime.utcnow()
            + timedelta(seconds=config.AUTH_EMAIL_VERIFICATION_TOKEN_LIFETIME_SECONDS),
        }

        token = await self.sys_users_tokens.create(verification_token)
        return token

    def get_null_user(self) -> models.SysUser:
        """
        Creates a null user that can be used for token generation purposes. This is used
        as part of the sys:users:reset:request endpoint in order to defeat timing attacks
        when requesting user reset
        """

        null = models.SysUser()
        null.id = uuid.uuid4()
        null.email = "null@localhost"

        return null

    def get_user_permissions(self, user: models.SysUser) -> List[models.SysPermission]:
        """
        Gets the list of permissions from a user
        """

        permissions = []
        for r in user.roles:
            for p in r.permissions:
                if p not in permissions:
                    permissions.append(p)

        return permissions

    async def role_delete(
        self, role: models.SysRole, hard_delete: bool = False
    ) -> None:
        """
        Delete a role
        """

        await self.sys_roles.delete(role, hard_delete=hard_delete)

    async def permission_delete(
        self, permission: models.SysPermission, hard_delete: bool = False
    ) -> None:
        """
        Delete a permission
        """

        await self.sys_permissions.delete(permission, hard_delete=hard_delete)

    async def add_permissions_to_role(
        self, role: models.SysRole, permissions: List[models.SysPermission]
    ) -> models.SysRole:
        """
        Add a list of permissions to a role
        """

        if len(permissions) == 0:
            log.warn(
                "Attempting to add zero permissions to role '%s', skipping commit", role
            )
            return role

        for p in permissions:
            if p in role.permissions:
                log.warn(
                    "Role %d: '%s' already has permission %d : '%s', skipping",
                    role.id,
                    role.role_name,
                    p.id,
                    p.permission_name,
                )
            else:
                role.permissions.append(p)

        return await self.sys_roles.apply_and_commit(role)

    async def remove_permissions_from_role(
        self, role: models.SysRole, permissions: List[models.SysPermission]
    ) -> models.SysRole:
        """
        Remove permissions from a role
        """

        if len(permissions) == 0:
            log.warn(
                "Attempting to remove zero permissions to role '%s', skipping commit",
                role,
            )
            return role

        for p in permissions:
            if p not in role.permissions:
                log.warn(
                    "Role %d: '%s' does not have permission %d : '%s', skipping",
                    role.id,
                    role.role_name,
                    p.id,
                    p.permission_name,
                )
            else:
                role.permissions.remove(p)

        return await self.sys_roles.apply_and_commit(role)

    async def add_roles_to_user(
        self, user: models.SysUser, roles: List[models.SysRole]
    ) -> models.SysUser:
        """
        Add a list of roles to a user
        """

        if len(roles) == 0:
            log.warn("Attempting to add zero roles to user '%s', skipping commit", user)
            return user

        for r in roles:
            if r in user.roles:
                log.warn(
                    "User %s: '%s' already has role %d : '%s', skipping",
                    user.id,
                    user.display_name,
                    r.id,
                    r.role_name,
                )
            else:
                user.roles.append(r)

        return await self.sys_users.apply_and_commit(user)

    async def remove_roles_from_user(
        self, user: models.SysUser, roles: List[models.SysRole]
    ) -> models.SysUser:
        """
        Remove roles from a user
        """

        if len(roles) == 0:
            log.warn(
                "Attempting to remove zero roles from user '%s', skipping commit",
                user,
            )
            return user

        for r in roles:
            if r not in user.roles:
                log.warn(
                    "User %d: '%s' does not have role %d : '%s', skipping",
                    user.id,
                    user.display_name,
                    r.id,
                    r.role_name,
                )
            else:
                user.roles.remove(r)

        return await self.sys_users.apply_and_commit(user)


async def get_user_manager(session: Session = Depends(get_session)):
    yield UserLogicManager(session)

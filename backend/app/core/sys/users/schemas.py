"""
Module defines the record, create, and update schemas for resources in the sys_users package.

Note: Since these schemas derive from the ResourceRecordSchemas, they implicitly contain:
    - id: UUID
    - name: str
    - display_name: str | None
    - is_active: bool
    - updated_at: datetime
    - created_at: datetime
"""

from datetime import datetime
from typing import Generic, List
from uuid import UUID
from app.core.auth.password import PASSWORD_MIN_LENGTH

from app.core.resources import constants
from app.core.resources.schemas import (
    ID,
    ResourceRecordCreateSchema,
    ResourceRecordListSchema,
    ResourceRecordSchema,
    ResourceRecordUpdateSchema,
)
from fastapi import Form
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from pydantic.generics import GenericModel

##
##  User
##


class UserSchema(ResourceRecordSchema):
    id: UUID
    name: str | None
    display_name: str
    email: str
    roles: List["RoleUserSchema"]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserListSchema(ResourceRecordListSchema):
    data: List[UserSchema]
    total: int


class UserCreateSchema(ResourceRecordCreateSchema):
    display_name: str
    email: EmailStr


class UserUpdateSchema(ResourceRecordUpdateSchema):
    display_name: str | None
    email: EmailStr | None


##
##  Role
##


class RoleSchema(ResourceRecordSchema):
    id: int
    name: str
    display_name: str
    description: str
    parent_role_id: int | None
    is_active: bool
    permissions: List["PermissionSchema"]
    created_at: datetime
    updated_at: datetime


class RoleUserSchema(ResourceRecordSchema):
    """
    How a role displays when included in a user's object
    """

    id: int
    name: str
    display_name: str
    permissions: List["PermissionUserSchema"]


class RoleListSchema(ResourceRecordListSchema):
    data: List[RoleSchema]
    total: int


class RoleCreateSchema(ResourceRecordCreateSchema):
    name: str = Field(..., max_length=constants.MAX_NAME_LENGTH)
    display_name: str = Field(..., max_length=constants.MAX_DISPLAY_NAME_LENGTH)
    description: str = Field(..., max_length=constants.MAX_DESCRIPTION_LENGTH)
    parent_role_id: int | None = Field(None, gt=0)


class RoleUpdateSchema(ResourceRecordUpdateSchema):
    display_name: str = Field(..., max_length=constants.MAX_DISPLAY_NAME_LENGTH)
    description: str = Field(..., max_length=constants.MAX_DESCRIPTION_LENGTH)
    parent_role_id: int | None = Field(None, gt=0)

class RolePermsAddRequest(BaseModel):
    """
    Data required to add permissions to a role
    """

    permission_ids: List[int]


class UserAddRolesRequest(BaseModel):
    """
    Data required to add roles to a user
    """

    role_ids: List[int]


##
##  Permission
##


class PermissionSchema(ResourceRecordSchema):
    id: int
    name: str
    display_name: str | None
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PermissionUserSchema(ResourceRecordSchema):
    """
    How a permission displays when included in a user's object
    """

    id: int
    name: str


class PermissionListSchema(ResourceRecordListSchema):
    data: List[PermissionSchema]
    total: int


class PermissionCreateSchema(ResourceRecordCreateSchema):
    name: str = Field(..., max_length=constants.MAX_NAME_LENGTH)
    display_name: str = Field(..., max_length=constants.MAX_DISPLAY_NAME_LENGTH)
    description: str = Field(..., max_length=constants.MAX_DESCRIPTION_LENGTH)


class PermissionUpdateSchema(ResourceRecordUpdateSchema):
    display_name: str = Field(..., max_length=constants.MAX_DISPLAY_NAME_LENGTH)
    description: str = Field(..., max_length=constants.MAX_DESCRIPTION_LENGTH)


##
##  User Token
##


class UserTokenSchema(Generic[ID], GenericModel):
    """
    Schema for a user's token - note the token itself is not sent.
    """

    id: int
    token_type: str
    num_uses_remaining: int | None
    expires_at: datetime | None
    user_id: UUID | None

    class Config:
        orm_mode = True


class UserTokenListSchema(ResourceRecordListSchema):
    data: List[UserTokenSchema]
    total: int


##
##  Oauth2 Authentication
##


class UsersRegisterRequest(BaseModel):
    """
    The registration data required to register a user
    """

    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)
    display_name: str = Field(..., max_length=constants.MAX_DISPLAY_NAME_LENGTH)


class UsersRegisterValidateRequest(BaseModel):
    """
    A validation check to register a user
    """

    email: EmailStr | None
    password: str | None
    display_name: str | None


class UsersAuthRequest(BaseModel):
    """
    Authentication data for a user to get an access token
    """

    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)
    grant: str


class UsersAuthResponse(BaseModel):
    """
    User token once login has been accepted
    refresh_token is sent in Secure, HttpOnly, SameSite cookie in the same request
    """

    expires_at: int
    token_type: str
    access_token: str


class UsersAuthCompleteResponse(BaseModel):
    """
    Internal Only, data exchange class
    """

    access_token: str
    expires_at: int
    refresh_token: str | None
    refresh_token_expires_at: int | None
    token_type: str


class BPOauth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
        is_public: bool = Form(default=True),
    ):
        super().__init__(
            grant_type, username, password, scope, client_id, client_secret
        )
        self.is_public = is_public

class UsersVerifyToken(BaseModel):
    """
    The data for verification
    """

    token: str


class UsersResetTokenRequest(BaseModel):
    """
    The data for account password reset
    """

    token: str
    password: str | None


class UsersResetRequest(BaseModel):
    """
    The data for a request to reset the account password
    """

    email: EmailStr


class UserUpdateRequest(BaseModel):
    """
    Update data for a user
    """

    display_name: str | None
    email: EmailStr | None
    password: str | None
    is_active: bool | None
    is_verified: bool | None
    is_superuser: bool | None



UserSchema.update_forward_refs()
RoleSchema.update_forward_refs()
RoleUserSchema.update_forward_refs()
PermissionSchema.update_forward_refs()
UserTokenSchema.update_forward_refs()

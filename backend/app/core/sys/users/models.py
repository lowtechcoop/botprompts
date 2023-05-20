from datetime import datetime
from typing import TYPE_CHECKING, List

from app.core.resources import constants
from app.core.sys.users import constants as user_constants
from app.core.resources.models import BaseResourceIntRecord, BaseResourceUuidRecord
from app.database.types import UUID_ID, BaseRecordActiveTimestamps, BaseRecordInt
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore


class SysUser(BaseResourceUuidRecord):
    """
    Defines the sys_users table with a Uuid identifier
    """

    __tablename__ = "sys_users"

    __table_args__ = (Index("ix_email_is_active", "email", "is_active"),)

    if TYPE_CHECKING:
        email: str
        password: str
        is_superuser: bool
        is_verified: bool
        tokens: List["SysUserToken"]
        roles: List["SysRole"]
    else:
        email: Mapped[str] = mapped_column(
            String(length=constants.EMAIL_COLUMN_LENGTH),
            unique=True,
            index=True,
            nullable=False,
        )
        password: Mapped[str] = mapped_column(
            String(length=constants.HASHED_PASSWORD_COLUMN_LENGTH), nullable=False
        )
        is_superuser: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )
        is_verified: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )
        tokens: Mapped[List["SysUserToken"]] = relationship(
            back_populates="user", cascade="all, delete-orphan"
        )
        roles: Mapped[List["SysRole"]] = relationship(
            "SysRole", secondary="sys_users_roles", back_populates="users"
        )


class SysRole(BaseResourceIntRecord):
    """
    Defines the sys_roles table
    """

    __tablename__ = "sys_roles"

    if TYPE_CHECKING:
        parent_role_id: int | None
        parent_role: "SysRole" | None
        description: str
        users: List["SysUser"]
        permissions: List["SysPermission"]
    else:
        parent_role_id: Mapped[int] = mapped_column(
            Integer(), ForeignKey("sys_roles.id"), index=True, nullable=True
        )
        parent_role: Mapped["SysRole"] = relationship(
            "SysRole", remote_side="SysRole.id"
        )
        description: Mapped[str] = mapped_column(
            String(length=constants.MAX_DESCRIPTION_LENGTH),
            index=False,
            nullable=True,
        )
        users: Mapped[List["SysUser"]] = relationship(
            "SysUser", secondary="sys_users_roles", back_populates="roles"
        )
        permissions: Mapped[List["SysPermission"]] = relationship(
            "SysPermission",
            secondary="sys_roles_permissions",
            back_populates="roles",
            primaryjoin=(
                "and_("
                "SysRole.id==SysRolesPermissions.role_id, "
                "SysRolesPermissions.is_active==True"
                ")"
            ),
        )


class SysUsersRoles(BaseResourceIntRecord):
    """
    Defines the associative table between sys_users and sys_roles
    """

    __tablename__ = "sys_users_roles"

    if TYPE_CHECKING:
        user_id: int
        role_id: int
    else:
        user_id: Mapped[UUID_ID] = mapped_column(
            ForeignKey("sys_users.id"), index=True, nullable=False
        )
        role_id: Mapped[int] = mapped_column(
            ForeignKey("sys_roles.id"), index=True, nullable=False
        )


class SysPermission(BaseResourceIntRecord):
    """
    Defines the sys_permissions table
    """

    __tablename__ = "sys_permissions"

    if TYPE_CHECKING:
        description: str | None
        roles: List["SysRole"]
    else:
        description: Mapped[str] = mapped_column(
            String(length=constants.MAX_DESCRIPTION_LENGTH), nullable=True
        )
        roles: Mapped[List["SysRole"]] = relationship(
            "SysRole", secondary="sys_roles_permissions", back_populates="permissions"
        )


class SysRolesPermissions(BaseResourceIntRecord):
    """
    Defines the associative table between sys_roles and sys_permissions
    """

    __tablename__ = "sys_roles_permissions"

    if TYPE_CHECKING:
        permission_id: int
        role_id: int
    else:
        permission_id: Mapped[int] = mapped_column(
            ForeignKey("sys_permissions.id"), index=True, nullable=False
        )
        role_id: Mapped[int] = mapped_column(
            ForeignKey("sys_roles.id"), index=True, nullable=False
        )


class SysUserToken(BaseRecordInt, BaseRecordActiveTimestamps):
    """
    Defines the sys_users_tokens table
    """

    __tablename__ = "sys_users_tokens"

    if TYPE_CHECKING:
        token_type: str
        token: str
        num_uses_remaining: int | None
        user_id: UUID_ID | None
        expires_at: datetime | None
        user: "SysUser" | None
    else:
        token_type: Mapped[str] = mapped_column(
            String(length=user_constants.TOKEN_TYPE_COLUMN_LENGTH)
        )
        token: Mapped[str] = mapped_column(String(length=user_constants.TOKEN_COLUMN_LENGTH))
        num_uses_remaining: Mapped[int] = mapped_column(Integer(), nullable=True)
        user_id: Mapped[UUID_ID] = mapped_column(
            ForeignKey("sys_users.id"), index=True, nullable=True
        )
        user: Mapped["SysUser"] = relationship(back_populates="tokens")
        expires_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), nullable=True
        )

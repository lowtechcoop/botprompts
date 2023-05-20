from typing import TYPE_CHECKING, List

from app.core.resources.models import BaseResourceIntRecord
from app.core.sys.users.models import SysPermission  # type: ignore
from app.core.sys.variables import constants as vars_constants
from app.database.types import BaseRecordActiveTimestamps, BaseRecordInt
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore


class SysVariable(BaseResourceIntRecord):
    """
    Defines the sys_variables table
    """

    __tablename__ = "sys_variables"

    if TYPE_CHECKING:
        name: str
        display_name: str
        value: str
        permissions: List[SysPermission]
    else:
        # Override the underlying name and display_name columns with specific values here
        name: Mapped[str] = mapped_column(
            String(length=vars_constants.VARIABLE_MAX_NAME_LENGTH),
            unique=True,
            index=True,
            nullable=False,
        )
        display_name: Mapped[str] = mapped_column(
            String(length=vars_constants.VARIABLE_MAX_NAME_LENGTH),
            nullable=True,
        )
        value: Mapped[str] = mapped_column(Text())
        permissions: Mapped[List[SysPermission]] = relationship(
            "SysPermission",
            secondary="sys_variables_permissions",
            single_parent=True,
        )


class SysVariablePermissions(BaseRecordInt, BaseRecordActiveTimestamps):
    """
    Defines the sys_variables_permissions table
    """

    __tablename__ = "sys_variables_permissions"

    if TYPE_CHECKING:
        variable_id: int
        permission_id: int
    else:
        variable_id: Mapped[int] = mapped_column(
            ForeignKey("sys_variables.id"), index=True, nullable=False
        )
        permission_id: Mapped[int] = mapped_column(
            ForeignKey("sys_permissions.id"), index=True, nullable=False
        )

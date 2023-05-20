from typing import TYPE_CHECKING, TypeVar

from app.core.resources import constants
from app.database.types import BaseRecordActiveTimestamps, BaseRecordInt, BaseRecordUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore


class BaseResourceRecord(BaseRecordActiveTimestamps):
    """
    Defines an abstract model for a Resource record with an Integer identifier
    """

    __abstract__ = True

    if TYPE_CHECKING:
        name: str
        display_name: str | None
    else:
        name: Mapped[str] = mapped_column(
            String(length=constants.MAX_NAME_LENGTH),
            index=True,
            nullable=False,
        )
        display_name: Mapped[str] = mapped_column(
            String(length=constants.MAX_NAME_LENGTH),
            index=False,
            nullable=True,
        )


class BaseResourceIntRecord(BaseRecordInt, BaseResourceRecord):
    """
    Defines an abstract model for a Resource record with an Integer identifier
    """

    __abstract__ = True

class BaseResourceUuidRecord(BaseRecordUUID, BaseResourceRecord):
    """
    Defines an abstract model for a Resource record with a UUID identifier
    """

    __abstract__ = True

BRR = TypeVar("BRR", bound=BaseResourceRecord)
BRRInt = TypeVar("BRRInt", bound=BaseResourceIntRecord)
BRRUuid = TypeVar("BRRUuid", bound=BaseResourceUuidRecord)

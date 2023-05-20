import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from app.core.resources.schemas import ID, UUID_ID
from app.database.base import Base, utcnow
from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore
from sqlalchemy_utils import UUIDType


class BaseRecordProtocol(Protocol[ID]):
    """
    Consistent record structure for database entries.
    """

    id: ID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __init__(self, *args, **kwargs) -> None:
        ...


RecordProtocol = TypeVar("RecordProtocol", bound=BaseRecordProtocol)


class BaseRecord(Generic[RecordProtocol, ID], Base):
    """
    Base record type for all sqlalchemy models with an Integer id
    """

    __abstract__ = True


BaseRecordType = TypeVar("BaseRecordType", bound=BaseRecord)


class BaseRecordInt(BaseRecord[RecordProtocol, int]):
    """
    Base record type for all sqlalchemy models with an Integer id
    """

    __abstract__ = True

    if TYPE_CHECKING:
        id: int
    else:
        id: Mapped[Integer] = mapped_column(
            Integer, primary_key=True, autoincrement=True
        )


class BaseRecordUUID(BaseRecord[RecordProtocol, UUID_ID]):
    """
    Base record type for all sqlalchemy models with a UUID id
    """

    __abstract__ = True

    if TYPE_CHECKING:
        id: UUID_ID
    else:
        id: Mapped[UUID_ID] = mapped_column(
            UUIDType, primary_key=True, default=uuid.uuid4
        )


class BaseRecordActiveTimestamps(Base):
    """ """

    __abstract__ = True

    if TYPE_CHECKING:
        is_active: bool
        created_at: datetime
        updated_at: datetime
    else:
        is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), default=utcnow(), server_default=utcnow()
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=utcnow(),
            server_default=utcnow(),
            onupdate=utcnow(),
        )

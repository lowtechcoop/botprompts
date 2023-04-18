from datetime import datetime
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from app.database.base import Base, utcnow
from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

ID = TypeVar("ID", covariant=True)

class BaseRecordProtocol(Protocol[ID]):
    """
    Consistent record structure for database entries.
    """

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __init__(self, *args, **kwargs) -> None:
        ...


RecordProtocol = TypeVar("RecordProtocol", bound=BaseRecordProtocol)


class BaseRecord(Generic[RecordProtocol], Base):
    """
    Base record type for all sqlalchemy models.
    """

    __abstract__ = True

    if TYPE_CHECKING:
        id: int
        is_active: bool
        created_at: datetime
        updated_at: datetime
    else:
        id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
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


BaseRecordType = TypeVar("BaseRecordType", bound=BaseRecord)

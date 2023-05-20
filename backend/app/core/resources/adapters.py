"""
Adapters for resource operations
"""

import uuid
from typing import Generic, Type

from app.core.resources import models
from app.database.adapters import AdapterCRUD
from app.database.types import ID
from dpn_pyutils.common import get_logger
from sqlalchemy import select
from sqlalchemy.orm import Session

log = get_logger(__name__)


class AdapterResources(Generic[models.BRR], AdapterCRUD[models.BRR]):
    """
    Adapter for a resources table
    """

    def __init__(self, session: Session, table: Type[models.BRR]) -> None:
        super().__init__(session, table)

    async def get_by_name(
        self, name: str, include_inactive: bool = False
    ) -> models.BRR | None:
        """
        Gets a resource entry from the database by name
        """

        stmt = select(self.table).where(self.table.name == name)

        if not include_inactive:
            # SqlAlchemy requires a "cond == True" rather than the pythonic "if cond"
            stmt = stmt.where(self.table.is_active == True)  # trunk-ignore(ruff/E712)

        return self.session.execute(stmt).unique().scalar_one_or_none()

    async def get_by_name_or_id(self, name_or_id: str | ID) -> models.BRR | None:
        """
        Gets a resource entry from the database by name or ID.
        """

        if isinstance(name_or_id, int):
            # Clear look up for an int id
            return await self.get(name_or_id)

        try:
            if isinstance(name_or_id, uuid.UUID) or isinstance(
                uuid.UUID(name_or_id), uuid.UUID
            ):  # type: ignore
                # If the name_or_id can be cast to a UUID, this is likely an id
                return await self.get(name_or_id)  # type: ignore
        except ValueError:
            pass

        return await self.get_by_name(name=str(name_or_id))

    async def get_by_display_name(self, display_name: str) -> models.BRR | None:
        """
        Gets a resource entry from the database matching on display_name
        """
        stmt = select(self.table).where(
            self.table.display_name == display_name
        )  # type: ignore

        return self.session.execute(stmt).unique().scalar_one_or_none()

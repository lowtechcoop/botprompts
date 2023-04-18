import uuid
from typing import Any, Dict, Generic, List, Type

from app.database.types import BaseRecordType, RecordProtocol
from dpn_pyutils.common import get_logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

log = get_logger(__name__)


class AdapterCRUDBase(Generic[RecordProtocol]):
    """
    Base adapter for CRUD operations on a table.
    """

    async def get(self, id: int) -> RecordProtocol | None:  # type: ignore
        """
        Get a single record by id.
        """
        raise NotImplementedError(
            "You need to override this method in a child class of AdapterCRUDBase"
        )

    async def get_many(
        self,
        row_filter: Dict[str, str],
        sort_col: str,
        sort_direction: str,
        range_start: int,
        range_end: int,
    ) -> List[RecordProtocol] | None:  # type: ignore
        """
        Get a list of records by id.
        """
        raise NotImplementedError(
            "You need to override this method in a child class of AdapterCRUDBase"
        )

    async def create(self, create_model: RecordProtocol) -> RecordProtocol:
        """
        Create a new user in the database.
        """
        raise NotImplementedError(
            "You need to override this method in a child class of AdapterCRUDBase"
        )

    async def update(
        self, record: RecordProtocol, update_fields: Dict[str, Any]
    ) -> RecordProtocol:
        """
        Update an existing record in the database.
        """
        raise NotImplementedError(
            "You need to override this method in a child class of AdapterCRUDBase"
        )

    async def delete(self, record: RecordProtocol, hard_delete: bool = False) -> None:
        """
        Delete a record from the database, the default approach is a soft-delete via an update call,
        however specify the hard_delete parameter for a permanent deletion.
        """
        raise NotImplementedError(
            "You need to override this method in a child class of AdapterCRUDBase"
        )


class AdapterCRUD(AdapterCRUDBase, Generic[BaseRecordType]):
    """
    Intermediary adapter with common CRUD operations on a table.
    """

    session: Session
    table: Type[BaseRecordType]

    def __init__(self, session: Session, table: Type[BaseRecordType]) -> None:
        self.session = session
        self.table = table

    async def total_rows(self) -> int:
        """
        Get the total number of rows in the table.
        """

        return self.session.query(func.count(self.table.id)).scalar()

    async def get(self, id: int) -> BaseRecordType | None:
        """
        Get a record specified by the id.
        """

        return (
            self.session.execute(select(self.table).where(self.table.id == id))
            .unique()
            .scalar_one_or_none()
        )

    async def get_by_ids(self, ids: List[int]) -> List[BaseRecordType]:
        """
        Get a list of records by ids.
        """

        stmt = select(self.table).where(self.table.id.in_(ids))  # type: ignore
        return [r[0] for r in self.session.execute(stmt).all()]

    async def get_many(
        self,
        row_filter: Dict[str, str],
        sort_col: str,
        sort_direction: str,
        range_start: int,
        range_end: int,
    ) -> List[BaseRecordType]:
        """
        Get a list of records based on the filter, sort, and range.
        """

        stmt = select(self.table)
        column_names = self.table.__table__.columns.keys()

        for col_name in column_names:
            # Add our filter columns to statement
            for filter_col_name in row_filter:
                if filter_col_name == col_name:
                    # Handle the filter based on sql type, e.g. some types need == and others
                    # need like/ilike
                    col_sql_type = str(self.table.__table__.columns[col_name].type)
                    if (
                        isinstance(row_filter[filter_col_name], str)
                        and col_sql_type != "BINARY(16)"
                    ):
                        # The column is a generic string type, use case-insensitive match (ilike)
                        filter_statement = self.table.__table__.columns[col_name].ilike(
                            row_filter[filter_col_name]
                        )

                    else:
                        filter_value = row_filter[filter_col_name]
                        if col_sql_type == "BINARY(16)":
                            # If the SQL Column looks like a UUID column type, try to parse as
                            # a UUID otherwise do a simple equality check
                            try:
                                filter_value = uuid.UUID(filter_value)
                            except (TypeError, ValueError):
                                pass

                        filter_statement = (
                            self.table.__table__.columns[col_name] == filter_value
                        )

                    stmt = stmt.filter(filter_statement)

            # Add our sort column to statement
            if col_name == sort_col:
                if sort_direction.upper() == "DESC":
                    stmt = stmt.order_by(self.table.__table__.columns[col_name].desc())
                else:
                    stmt = stmt.order_by(self.table.__table__.columns[col_name])

        if range_start > 0:
            stmt = stmt.offset(range_start)
        else:
            stmt = stmt.offset(None)

        if range_end > 0:
            stmt = stmt.limit(range_end)
        else:
            stmt = stmt.limit(None)

        results = [r[0] for r in self.session.execute(stmt).unique().all()]

        return results

    async def apply_and_commit(self, record: BaseRecordType) -> BaseRecordType:
        """
        Add the record to the session and commits.
        """
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record

    async def create(self, create_dict: Dict[str, Any]) -> BaseRecordType:
        """
        Create and commits the record.
        """

        return await self.apply_and_commit(self.table(**create_dict))

    async def update(
        self,
        record: BaseRecordType,
        update_fields: Dict[str, Any],
        autocommit: bool = True,
    ) -> BaseRecordType:
        """
        Update a record with fields in the update_fields dictionary.
        """

        is_dirty = False
        for field, value in update_fields.items():
            if hasattr(record, field) and getattr(record, field) != value:
                setattr(record, field, value)
                is_dirty = True

        if is_dirty:
            self.session.add(record)

            if autocommit:
                self.session.commit()

            self.session.refresh(record)

        return record

    async def delete(
        self, record: BaseRecordType, hard_delete: bool = False, autocommit: bool = True
    ) -> None:
        """
        Delete a record if hard_delete is true, otherwise sets is_active to false.
        """

        if not hard_delete:
            await self.update(record, {"is_active": False})
            return

        self.session.delete(record)

        if autocommit:
            self.session.commit()

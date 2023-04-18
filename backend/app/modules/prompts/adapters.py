from typing import List, Type

from app.database.adapters import AdapterCRUD
from app.database.meta import get_session
from app.modules.prompts import models, schemas
from dpn_pyutils.common import get_logger
from fastapi import Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session

log = get_logger(__name__)


class AdapterPrompts(AdapterCRUD[models.PromptRecord]):
    """
    Implementation of Prompts adapter.
    """

    def __init__(self, session: Session, table: Type[models.PromptRecord]) -> None:
        super().__init__(session, table)

    async def get_by_slug(self, slug: str) -> models.PromptRecord | None:
        """
        Get a Prompt by slug.
        """
        # SqlAlchemy requires a "cond == True" rather than the pythonic "if cond"
        stmt = (
            select(self.table)
            .where(self.table.is_active == True)  # trunk-ignore(ruff/E712)
            .where(self.table.slug == slug)
        )

        return self.session.execute(stmt).unique().scalar_one_or_none()

    async def get_current_list(self) -> List[schemas.PromptListRow]:
        """
        Get a list of current prompts
        """

        sql_statement = text(
            """
        SELECT
            p.id, pr.id as revision_id, p.slug, p.is_active,
            pr.description, pr.prompt_text, pr.created_at, pr.updated_at
        FROM prompts p
            INNER JOIN prompts_revisions pr ON pr.prompt_id = p.id AND pr.is_current=True
        WHERE
            p.is_active=True
        ORDER BY p.slug ASC
        """
        )

        unmapped_rows = [r for r in self.session.execute(sql_statement).all()]
        current_result = []
        for um_row in unmapped_rows:
            current_result.append(
                schemas.PromptListRow(
                    id=um_row[0],
                    revision_id=um_row[1],
                    slug=um_row[2],
                    is_active=um_row[3],
                    description=um_row[4],
                    prompt_text=um_row[5],
                    created_at=um_row[6],
                    updated_at=um_row[7],
                )
            )

        return current_result


class AdapterPromptsHistory(AdapterCRUD[models.PromptRecord]):
    """
    Implementation of the PromptsHistory adapter.
    """

    def __init__(
        self, session: Session, table: Type[models.PromptHistoryRecord]
    ) -> None:
        super().__init__(session, table)


class AdapterPromptRevision(AdapterCRUD[models.PromptRevisionRecord]):
    """
    Implementation of the PromptRevision adapter.
    """

    def __init__(
        self, session: Session, table: Type[models.PromptRevisionRecord]
    ) -> None:
        super().__init__(session, table)

    async def get_by_prompt_id(
        self, prompt_id: int
    ) -> List[models.PromptRevisionRecord]:
        """
        Get a list of revisions for a given prompt
        """

        # SqlAlchemy requires a "cond == True" rather than the pythonic "if cond"
        stmt = (
            select(self.table)
            .where(self.table.is_active == True)  # trunk-ignore(ruff/E712)
            .where(self.table.prompt_id == prompt_id)
            .order_by(self.table.id.desc()) # type: ignore
        )

        return [r[0] for r in self.session.execute(stmt).all()]


async def get_db_prompts(session: Session = Depends(get_session)):
    yield AdapterPrompts(session, models.PromptRecord)


async def get_db_prompts_history(session: Session = Depends(get_session)):
    yield AdapterPromptsHistory(session, models.PromptHistoryRecord)


async def get_db_prompts_revision(session: Session = Depends(get_session)):
    yield AdapterPromptRevision(session, models.PromptRevisionRecord)

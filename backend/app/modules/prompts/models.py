from typing import TYPE_CHECKING, List

from app.config import get_config
from app.database.types import BaseRecord
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore

config = get_config()


class PromptRecord(BaseRecord):
    """
    Defines the prompts table.
    """

    __tablename__ = "prompts"

    __table_args__ = (Index("ix_slug_is_active", "slug", "is_active"),)

    if TYPE_CHECKING:
        slug: str
        revision: "PromptRevisionRecord"
        history: List["PromptRevisionRecord"] = []
    else:
        slug: Mapped[str] = mapped_column(
            String(length=config.SLUG_MAX_LENGTH), index=True, nullable=False
        )
        revision: Mapped["PromptRevisionRecord"] = relationship(
            "PromptRevisionRecord",
            back_populates="prompt",
            # trunk-ignore(ruff/E501)
            primaryjoin="and_(PromptRecord.id==PromptRevisionRecord.prompt_id, PromptRevisionRecord.is_current==True)",
            cascade="all,delete",
        )
        history: List["PromptRevisionRecord"] = []


class PromptRevisionRecord(BaseRecord):
    """
    Defines the prompts_version table.
    """

    __tablename__ = "prompts_revisions"

    if TYPE_CHECKING:
        prompt_id: int
        prompt: PromptRecord
        is_current: bool
        description: str
        prompt_text: str

    else:
        prompt_id: Mapped[int] = mapped_column(
            Integer(), ForeignKey("prompts.id"), index=True, nullable=False
        )
        prompt: Mapped["PromptRecord"] = relationship(
            "PromptRecord",
            back_populates="revision",
        )
        is_current: Mapped[bool] = mapped_column(Boolean, nullable=False)
        description: Mapped[str] = mapped_column(
            String(length=config.PROMPT_MAX_LENGTH), nullable=False
        )
        prompt_text: Mapped[str] = mapped_column(
            String(length=config.PROMPT_MAX_LENGTH), nullable=False
        )


class PromptHistoryRecord(BaseRecord):
    """
    Defines the prompts_history table.

    This table stores a record for each time a prompt is used. Aggregating the records by prompt_id
    gives the popularity of any given prompt.
    """

    __tablename__ = "prompts_history"

    if TYPE_CHECKING:
        prompt_id: int
        revision_id: int

    else:
        prompt_id: Mapped[int] = mapped_column(
            Integer(), ForeignKey("prompts.id"), index=True, nullable=False
        )
        prompt: Mapped["PromptRecord"] = relationship(
            "PromptRecord", remote_side="PromptRecord.id"
        )

        revision_id: Mapped[int] = mapped_column(
            Integer(), ForeignKey("prompts_revisions.id"), index=True, nullable=False
        )
        revision: Mapped["PromptRevisionRecord"] = relationship(
            "PromptRevisionRecord", remote_side="PromptRevisionRecord.id"
        )

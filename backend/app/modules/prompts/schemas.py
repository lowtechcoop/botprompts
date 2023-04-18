from datetime import datetime
from typing import List

from app.config import get_config
from pydantic import BaseModel, Field

config = get_config()


class PromptRevision(BaseModel):
    """
    Describes a prompt revision.
    """

    id: int
    description: str
    prompt_text: str
    is_current: bool
    # is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Prompt(BaseModel):
    """
    Describes a prompt structure.
    """

    id: int
    slug: str = Field(..., max_length=config.SLUG_MAX_LENGTH)
    revision: PromptRevision
    history: List[PromptRevision] = []
    is_active: bool
    # created_at: datetime
    # updated_at: datetime

    class Config:
        orm_mode = True

class PromptListRow(BaseModel):
    """
    Describes a list row that contains only the prompt and the current revision.
    """

    id: int
    revision_id: int
    slug: str
    description: str
    prompt_text: str
    is_active: bool
    updated_at: datetime
    created_at: datetime

class PromptCurrentList(BaseModel):
    """
    Describes a flat list of prompts based on no filtering.
    """

    prompts: List[PromptListRow]
    total: int

class PromptList(BaseModel):
    """
    Describes a list of prompts based on filter criteria.
    """

    prompts: List[Prompt]
    total: int

class PromptCreate(BaseModel):
    """
    Describes the data required for a prompt creation operation.
    """

    slug: str = Field(..., max_length=config.SLUG_MAX_LENGTH)
    """
    The slug phrase that represents this prompt
    """

    description: str = Field(..., max_length=config.PROMPT_MAX_LENGTH)
    """
    A description field for the prompt
    """

    prompt_text: str = Field(..., max_length=config.PROMPT_MAX_LENGTH)
    """
    The desired prompt text, up to the maximum length
    """

class PromptUpdate(BaseModel):
    """
    Describes the data required to update the prompt.
    """

    ids: List[int]
    data: PromptCreate

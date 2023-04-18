from app.config import get_config
from app.core.errors import AppHTTPError
from app.modules.prompts import background, schemas
from app.modules.prompts.adapters import (
    AdapterPromptRevision,
    AdapterPrompts,
    AdapterPromptsHistory,
    get_db_prompts,
    get_db_prompts_history,
    get_db_prompts_revision,
)
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from pydantic import Json
from slugify import slugify

config = get_config()

log = get_logger(__name__)


def get_router__prompts() -> APIRouter:
    """
    Get the APIRouter for the prompts REST resource.
    """

    router = APIRouter(prefix="/prompts")

    @router.get(
        "", response_model=None, status_code=status.HTTP_200_OK, name="prompts:list"
    )
    async def prompts__list(
        filter_input: Json | None = Query({}),
        sort_field: str = Query("id"),
        sort_order: str = Query("ASC"),
        range_start: int = Query(0),  # No offset
        range_end: int = Query(-1),  # No limit
        ids: Json | None = Query({}),
        history: bool = Query(False),
        db_prompts: AdapterPrompts = Depends(get_db_prompts),
        db_prompts_revision: AdapterPromptRevision = Depends(get_db_prompts_revision),
    ):
        """
        Get a list of prompts.
        """

        if ids is not None and len(ids) > 0:
            records = await db_prompts.get_by_ids(ids)
            total_rows = len(records)
        else:
            records = await db_prompts.get_many(
                row_filter=filter_input,  # type: ignore
                sort_col=sort_field,
                sort_direction=sort_order,
                range_start=range_start,
                range_end=range_end,
            )

            total_rows = await db_prompts.total_rows()

        # fetching history is an expensive operation
        if history:
            for r in records:
                r.history = await db_prompts_revision.get_by_prompt_id(r.id)

        return schemas.PromptList(
            total=total_rows,
            prompts=[schemas.Prompt.from_orm(r) for r in records],
        )

    @router.get(
        "/current",
        response_model=schemas.PromptCurrentList,
        status_code=status.HTTP_200_OK,
        name="prompts:current-list",
    )
    async def prompts__current_list(
        db_prompts: AdapterPrompts = Depends(get_db_prompts),
    ):
        """
        Get a flat list of current prompts
        """

        records = await db_prompts.get_current_list()
        total_rows = await db_prompts.total_rows()

        return schemas.PromptCurrentList(total=total_rows, prompts=records)

    @router.get(
        "/commands",
        response_model=schemas.PromptCommandsList,
        status_code=status.HTTP_200_OK,
        name="prompts:commands-list",
    )
    async def prompts__commands_list(
        db_prompts: AdapterPrompts = Depends(get_db_prompts),
    ):
        """
        Get a flat list of current commands
        """

        records = await db_prompts.get_current_commands()

        return schemas.PromptCommandsList(commands=records)



    @router.get(
        "/detail/{prompt_slug}",
        response_model=schemas.Prompt,
        status_code=status.HTTP_200_OK,
        name="prompts:single",
    )
    async def prompts__get_one(
        prompt_slug: str,
        background_tasks: BackgroundTasks,
        history: bool = Query(False),
        db_prompts: AdapterPrompts = Depends(get_db_prompts),
        db_prompts_history: AdapterPromptsHistory = Depends(get_db_prompts_history),
        db_prompts_revision: AdapterPromptRevision = Depends(get_db_prompts_revision),
    ):
        """
        Get an individual prompt by slug.
        """

        log.debug("Getting an individual prompt by slug '%s'", prompt_slug)
        existing_prompt = await db_prompts.get_by_slug(prompt_slug)
        if existing_prompt is None:
            raise AppHTTPError(
                detail="PROMPT_DOES_NOT_EXIST", status_code=status.HTTP_404_NOT_FOUND
            )

        background_tasks.add_task(
            background.update_prompt_history,
            db_prompts_history,
            existing_prompt.id,
            existing_prompt.revision.id,
        )

        existing_dto = schemas.Prompt.from_orm(existing_prompt)

        if history:
            history_records = await db_prompts_revision.get_by_prompt_id(
                existing_prompt.id
            )
            existing_dto.history = [
                schemas.PromptRevision.from_orm(h) for h in history_records
            ]

        return existing_dto

    @router.post(
        "",
        response_model=schemas.Prompt,
        status_code=status.HTTP_200_OK,
        name="prompts:create",
    )
    async def prompts__create(
        create_request: schemas.PromptCreate,
        db_prompts: AdapterPrompts = Depends(get_db_prompts),
        db_prompts_revision: AdapterPromptRevision = Depends(get_db_prompts_revision),
    ):
        """
        Create a new prompt based on supplied schema.
        """

        log.debug("Creating a new prompt")
        existing_prompt = await db_prompts.get_by_slug(create_request.slug)
        if existing_prompt is not None:
            raise AppHTTPError(
                detail="PROMPT_ALREADY_EXISTS", status_code=status.HTTP_400_BAD_REQUEST
            )

        prompt_dict = create_request.dict(include={"slug"})
        prompt_dict["slug"] = slugify(prompt_dict["slug"])

        created_prompt = await db_prompts.create(prompt_dict)

        revision_dict = create_request.dict(include={"description", "prompt_text"})
        revision_dict["prompt_id"] = created_prompt.id
        revision_dict["is_current"] = True

        created_revision = await db_prompts_revision.create(revision_dict)
        created_prompt.revision = created_revision

        return schemas.Prompt.from_orm(created_prompt)

    @router.put(
        "",
        response_model=schemas.Prompt,
        status_code=status.HTTP_200_OK,
        name="prompts:update",
    )
    async def prompts__update(
        update_request: schemas.PromptUpdate,
        db_prompts: AdapterPrompts = Depends(get_db_prompts),
        db_prompts_revision: AdapterPromptRevision = Depends(get_db_prompts_revision),
    ):
        """
        Create a new prompt based on supplied schema.
        """

        log.debug("Updating existing prompt, enforcing single-update only mode")

        if len(update_request.ids) != 1:
            raise AppHTTPError(
                detail="PROMPT_UPDATE_ONLY_ONE_PERMITTED",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        existing_prompt = await db_prompts.get(update_request.ids[0])
        if existing_prompt is None:
            raise AppHTTPError(
                detail="PROMPT_DOES_NOT_EXIST", status_code=status.HTTP_404_NOT_FOUND
            )

        # Remove existing current revision
        await db_prompts_revision.update(
            existing_prompt.revision, {"is_current": False}
        )

        # Update the prompt by creating a new revision
        revision_dict = update_request.data.dict(include={"description", "prompt_text"})
        revision_dict["prompt_id"] = existing_prompt.id
        revision_dict["is_current"] = True
        new_revision = await db_prompts_revision.create(revision_dict)

        updated_prompt = await db_prompts.update(
            existing_prompt, {"revision": new_revision}
        )

        return schemas.Prompt.from_orm(updated_prompt)

    @router.delete(
        "/{prompt_slug}",
        response_model=None,
        status_code=status.HTTP_200_OK,
        name="prompts:delete",
    )
    async def prompts__delete(
        prompt_slug: str, db_prompts: AdapterPrompts = Depends(get_db_prompts)
    ):
        """
        Delete a prompt by slug.
        """

        log.debug("Deleting prompt with slug '%s'", prompt_slug)
        existing_prompt = await db_prompts.get_by_slug(prompt_slug)
        if existing_prompt is None:
            raise AppHTTPError(
                detail="PROMPT_DOES_NOT_EXIST", status_code=status.HTTP_404_NOT_FOUND
            )

        await db_prompts.delete(existing_prompt, hard_delete=False)

    return router

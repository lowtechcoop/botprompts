from typing import Type

from app.config import get_config
from app.core.errors import AppHTTPError
from app.core.auth.authorization import get_auth
from app.core.resources import constants, models, schemas
from app.core.resources.adapters import AdapterResources
from app.core.resources.dependencies import get_adapter
from dpn_pyutils.common import get_logger
from fastapi import APIRouter, Depends, Query, Security, status
from pydantic import Json

from app.core.resources.responses import API_RESOURCE_ROUTE_RESPONSES

config = get_config()

log = get_logger(__name__)


def generate_resource_router(
    resource_name: str,
    record: Type[models.BRR] = models.BRR,
    list_schema: Type[schemas.RLS] = schemas.ResourceRecordListSchema[schemas.ID],
    record_schema: Type[schemas.RS] = schemas.ResourceRecordSchema[schemas.ID],
    create_schema: Type[schemas.RCS] = schemas.ResourceRecordCreateSchema[schemas.ID],
    update_schema: Type[schemas.RUS] = schemas.ResourceRecordUpdateSchema[schemas.ID],
    has_list=True,
    has_get=True,
    has_create=True,
    has_update=True,
    has_delete=True,
    url_prefix: str | None = None,
    route_name_prefix: str | None = None,
) -> APIRouter:
    """
    Generates a resource router with the specified routes
    """

    if url_prefix is None:
        url_prefix = f"/{resource_name}"

    if route_name_prefix is None:
        route_name_prefix = f"resource:{resource_name}"

    resource_router = APIRouter(prefix=url_prefix)

    if has_list and list_schema is not None:

        @resource_router.get(
            "",
            response_model=list_schema,
            responses=API_RESOURCE_ROUTE_RESPONSES, # type: ignore
            status_code=status.HTTP_200_OK,
            name=f"{route_name_prefix}:list",
        )
        async def resources__resource__list(
            filter_input: Json | None = Query({}),
            sort_field: str = Query("id"),
            sort_order: str = Query("ASC"),
            range_start: int = Query(0),  # No offset
            range_end: int = Query(-1),  # No limit
            ids: Json | None = Query({}),
            auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:list"]),
            adapter: AdapterResources = Depends(get_adapter(record)),
        ):
            """
            Resource list route
            """
            log.debug("Resource 'list' route for resource '%s'", resource_name)

            if ids is not None and len(ids) > 0:  # type: ignore
                results = await adapter.get_by_ids(ids)
                total_rows = len(results)
            else:
                results = await adapter.get_many(
                    row_filter=filter_input,  # type: ignore
                    sort_col=sort_field,
                    sort_direction=sort_order,
                    range_start=range_start,
                    range_end=range_end,
                )
                total_rows = await adapter.total_rows()

            return list_schema(**{"data": results, "total": total_rows})

    else:
        log.info(
            "API endpoint 'resource:%s:list' is disabled because has_list = False "
            "or no list schema defined",
            resource_name,
        )

    if has_get:

        @resource_router.get(
            "/{name_or_id}",
            response_model=record_schema,
            responses=API_RESOURCE_ROUTE_RESPONSES, # type: ignore
            status_code=status.HTTP_200_OK,
            name=f"{route_name_prefix}:get",
        )
        async def resources__resource__get_name(
            name_or_id: schemas.ID | str,
            auth=Security(get_auth, scopes=["superuser", f"{route_name_prefix}:get"]),
            adapter: AdapterResources = Depends(get_adapter(record)),
        ):
            """
            Resource 'list' route
            """
            log.debug(
                "Resource 'get' route for resource '%s:%s' (type: %s)",
                resource_name,
                name_or_id,
                type(name_or_id),
            )

            existing_record = await adapter.get_by_name_or_id(name_or_id)
            if existing_record is None:
                raise AppHTTPError(
                    detail=constants.RECORD_DOES_NOT_EXIST,
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            return record_schema.from_orm(existing_record)  # type: ignore

    else:
        log.info(
            "API endpoint 'resource:%s:get' is disabled because has_get = False",
            resource_name,
        )

    if has_create and create_schema is not None:

        @resource_router.post(
            "",
            response_model=record_schema,
            responses=API_RESOURCE_ROUTE_RESPONSES, # type: ignore
            status_code=status.HTTP_200_OK,
            name=f"{route_name_prefix}:create",
        )
        async def resources__resource__create(
            resource_create: create_schema,
            auth=Security(
                get_auth, scopes=["superuser", f"{route_name_prefix}:create"]
            ),
            adapter: AdapterResources = Depends(get_adapter(record)),
        ):
            """
            Resource create route
            """
            log.debug(
                "Resource 'create' route for resource '%s': %s",
                resource_name,
                resource_create,
            )

            existing_record = await adapter.get_by_name(name=resource_create.name)
            if existing_record is not None:
                raise AppHTTPError(
                    detail=constants.RECORD_ALREADY_EXISTS,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            new_record = await adapter.create(resource_create.dict())
            return record_schema.from_orm(new_record)  # type: ignore

    else:
        log.info(
            "API endpoint 'resource:%s:create' is disabled because has_create = False "
            "or no create schema defined",
            resource_name,
        )

    if has_update and update_schema is not None:

        @resource_router.put(
            "/{name_or_id}",
            response_model=record_schema,
            responses=API_RESOURCE_ROUTE_RESPONSES, # type: ignore
            status_code=status.HTTP_200_OK,
            name=f"{route_name_prefix}:update",
        )
        async def resources__resource__update(
            name_or_id: schemas.ID | str,
            resource_update: update_schema,
            auth=Security(
                get_auth, scopes=["superuser", f"{route_name_prefix}:update"]
            ),
            adapter: AdapterResources = Depends(get_adapter(record)),
        ):
            """
            Resource update route
            """
            log.debug(
                "Resource 'update' route for resource '%s': %s",
                resource_name,
                resource_update,
            )

            existing_record = await adapter.get_by_name_or_id(name_or_id)
            if existing_record is None:
                raise AppHTTPError(
                    detail=constants.RECORD_DOES_NOT_EXIST,
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            updated_record = await adapter.update(
                existing_record,
                resource_update.dict(),
            )

            return record_schema.from_orm(updated_record)

    else:
        log.info(
            "API endpoint 'resource:%s:update' is disabled because has_update = False "
            "or no update schema defined",
            resource_name,
        )

    if has_delete:

        @resource_router.delete(
            "/{name_or_id}",
            response_model=None,
            responses=API_RESOURCE_ROUTE_RESPONSES, # type: ignore
            status_code=status.HTTP_200_OK,
            name=f"{route_name_prefix}:delete",
        )
        async def resources__resource__delete(
            name_or_id: schemas.ID | str,
            auth=Security(
                get_auth, scopes=["superuser", f"{route_name_prefix}:delete"]
            ),
            adapter: AdapterResources = Depends(get_adapter(record)),
        ):
            """
            Resource delete route
            """
            log.debug(
                "Resource 'delete' route for resource '%s:%s'", resource_name, name_or_id
            )

            existing_record = await adapter.get_by_name_or_id(name_or_id)
            if existing_record is None:
                raise AppHTTPError(
                    detail=constants.RECORD_DOES_NOT_EXIST,
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            await adapter.delete(existing_record, hard_delete=True)

            # HTTP Status 200 and no body means success
            return None

    else:
        log.info(
            "API endpoint 'resource:%s:delete' is disabled because has_delete = False",
            resource_name,
        )

    return resource_router

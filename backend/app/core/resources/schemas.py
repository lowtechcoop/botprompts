import uuid
from typing import Generic, List, TypeVar

from pydantic import Extra
from pydantic.generics import GenericModel

UUID_ID = uuid.UUID

ID = TypeVar("ID", int, UUID_ID)


class ResourceRecordSchema(Generic[ID], GenericModel):
    """
    Defines a generic record schema that is used for a single resource view
    """

    id: ID
    name: str
    display_name: str | None

    class Config:
        orm_mode = True
        extra = Extra.forbid


class ResourceRecordListSchema(Generic[ID], GenericModel):
    """
    Defines a generic record list schema that is used for a list of resources
    """

    data: List[ResourceRecordSchema]
    total: int


class ResourceRecordCreateSchema(Generic[ID], GenericModel):
    """
    Defines a generic record create schema that is used to create a single resource
    """

    name: str
    display_name: str | None

    class Config:
        extra = Extra.forbid


class ResourceRecordUpdateSchema(Generic[ID], GenericModel):
    """
    Defines a generic record update schema that is used to update a single resource
    """

    display_name: str | None

    class Config:
        extra = Extra.forbid


RS = TypeVar("RS", bound=ResourceRecordSchema)
RLS = TypeVar("RLS", bound=ResourceRecordListSchema)
RCS = TypeVar("RCS", bound=ResourceRecordCreateSchema)
RUS = TypeVar("RUS", bound=ResourceRecordUpdateSchema)

ResourceRecordSchema.update_forward_refs()
ResourceRecordCreateSchema.update_forward_refs()
ResourceRecordUpdateSchema.update_forward_refs()

"""
Module defines the record, create, and update schemas for resources in the sys_variables package.

Note: Since these schemas derive from the ResourceRecordSchemas, they implicitly contain:
    - id: int
    - name: str
    - display_name: str | None
    - is_active: bool
    - updated_at: datetime
    - created_at: datetime
"""

from typing import List

from app.core.resources.schemas import (
    ResourceRecordCreateSchema,
    ResourceRecordListSchema,
    ResourceRecordSchema,
    ResourceRecordUpdateSchema,
)
from app.core.sys.users.schemas import PermissionSchema


class VariableSchema(ResourceRecordSchema):
    value: str
    permissions: List[PermissionSchema]


class VariableListSchema(ResourceRecordListSchema):
    data: List[VariableSchema]
    total: int


class VariableCreateSchema(ResourceRecordCreateSchema):
    name: str
    display_name: str
    value: str
    permissions: List[str] | None


class VariableUpdateSchema(ResourceRecordUpdateSchema):
    value: str | None
    permissions: List[str] | None


VariableSchema.update_forward_refs()
VariableListSchema.update_forward_refs()
